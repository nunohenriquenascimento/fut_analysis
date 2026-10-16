"""Simultaneous FPF observations must agree; later corrections are allowed."""
from copy import deepcopy

import pytest
from sqlalchemy import select

from app.models import Competition, CompetitionFixture, CompetitionTeam, Match, MatchEvent, MatchSquad, Player
from test_auth_fpf import fpf_account, apply, accounts, password_hash, games, create  # noqa: F401
from test_auth_fpf_local import round_html


def fingerprint(db, cid):
    db.expire_all()
    return (
        deepcopy(db.get(Competition, cid).fpf_data),
        {model.__tablename__: [tuple(deepcopy(getattr(row, col.name)) for col in model.__table__.columns)
                              for row in db.scalars(select(model).order_by(*model.__table__.primary_key.columns))]
         for model in (CompetitionFixture, CompetitionTeam, Match, MatchEvent, MatchSquad, Player)},
    )


@pytest.mark.parametrize('persisted', [False, True])
@pytest.mark.parametrize('method', ['preview', 'apply'])
@pytest.mark.parametrize('sources', ['round_sheet', 'round_round', 'sheet_sheet'])
def test_conflicting_results_reject_entire_batch(fpf_account, persisted, method, sources):
    client, db, cid, capture, *_ = fpf_account
    if persisted:
        assert apply(client, cid, {**capture, 'fixture_htmls': [round_html()]}).status_code == 200
    before = fingerprint(db, cid)
    payload = {**capture, 'fixture_htmls': [round_html(score='9 - 0')]}
    if sources == 'round_round':
        payload.update(match_htmls=[], fixture_htmls=[round_html(score='9 - 0'), round_html()])
    elif sources == 'sheet_sheet':
        payload.update(fixture_htmls=[], match_htmls=[capture['match_htmls'][0], capture['match_htmls'][0].replace('<strong>2 - 1</strong>', '<strong>9 - 0</strong>')])
    response = (client.post(f'/competitions/{cid}/fpf/preview', json=payload) if method == 'preview' else apply(client, cid, payload))
    assert response.status_code == 409, response.text
    detail = response.json()['detail']
    assert detail['code'] == 'FPF_RESULT_CONFLICT'
    conflict, = detail['conflicts']
    assert conflict['match_id'] == 2682548
    assert {(s['home_goals'], s['away_goals']) for s in conflict['sources']} == {(9, 0), (2, 1)}
    assert len({s['source'] for s in conflict['sources']}) == 2
    assert bool(conflict['persisted']) == persisted
    assert fingerprint(db, cid) == before


@pytest.mark.parametrize('source', ['round', 'sheet'])
def test_later_correction_overrides_history_and_remains_idempotent(fpf_account, source):
    client, db, cid, capture, *_ = fpf_account
    assert apply(client, cid, {**capture, 'fixture_htmls': [round_html()]}).status_code == 200
    original = db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == 'fpf:match:2682548'))
    original_id = original.id
    # Reuse persisted competition/sheet data, not a simultaneous new observation.
    correction = {k: v for k, v in capture.items() if k != 'competition_html'}
    correction.update(match_htmls=[], fixture_htmls=[])
    if source == 'round':
        correction['fixture_htmls'] = [round_html(score='3 - 1')]
    else:
        correction['match_htmls'] = [capture['match_htmls'][0].replace('<strong>2 - 1</strong>', '<strong>3 - 1</strong>')]
    preview = client.post(f'/competitions/{cid}/fpf/preview', json=correction)
    assert preview.status_code == 200, preview.text
    change, = [c for c in preview.json()['changes'] if c['external_key'] == original.external_key]
    assert (change['before']['home_goals'], change['after']['home_goals']) == (2, 3)
    assert apply(client, cid, correction).json()['summary']['updated'] == 1
    assert apply(client, cid, correction).json()['summary']['updated'] == 0
    # A replay without new scores cannot resurrect the old saved sheet.
    replay = {**correction, 'fixture_htmls': [], 'match_htmls': []}
    assert apply(client, cid, replay).status_code == 200
    db.expire_all()
    assert db.get(CompetitionFixture, original_id).home_goals == 3
    table = client.get(f'/competitions/{cid}/standings').json()
    assert next(r for r in table['rows'] if r['team_id'] == capture['team_mapping']['Seia Fc'])['goals_for'] == 3


def test_matching_sources_are_idempotent_and_unknown_score_is_not_conflict(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    payload = {**capture, 'fixture_htmls': [round_html(), round_html(score=None)]}
    # Same-round documents with different structure remain an identity conflict;
    # a scheduled row plus a sheet is the supported complementary pair.
    payload['fixture_htmls'] = [round_html(score=None)]
    payload['match_rounds'] = {'2682548': 677922}
    assert apply(client, cid, payload).status_code == 200
    assert apply(client, cid, payload).json()['summary']['created'] == 0
    assert apply(client, cid, {**payload, 'fixture_htmls': [round_html()]}).json()['summary']['updated'] == 0


def competition_result_html(capture, score):
    # Synthetic variant of the real competition capture, using its verified markup.
    import re
    html = capture['competition_html']
    start = html.index('<div class="game"')
    end = html.index('<div class="game-list-stadium"', start)
    game = html[start:end].replace('Adrc Aguiar Beira', 'Seia Fc').replace('text-right">Seia Fc', 'text-right">V. Cortez Mondego-Guarda')
    game = re.sub(r'<span class="game-schedule">.*?</span>', f'<a href="/Match/GetMatchInformation?matchId=2682548">{score}</a>', game, flags=re.S)
    return html[:start] + game + html[end:]


def test_competition_page_conflicts_with_individual_sheet(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    before = fingerprint(db, cid)
    response = apply(client, cid, {**capture, 'competition_html': competition_result_html(capture, '9 - 0')})
    assert response.status_code == 409, response.text
    conflict, = response.json()['detail']['conflicts']
    assert {s['source'] for s in conflict['sources']} == {'competition_html', 'match_htmls[0]:2682548'}
    assert fingerprint(db, cid) == before


def test_saved_competition_result_cannot_override_later_sheet_correction(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    assert apply(client, cid, {**capture, 'competition_html': competition_result_html(capture, '2 - 1')}).status_code == 200
    correction = {k: v for k, v in capture.items() if k != 'competition_html'}
    correction['match_htmls'] = [capture['match_htmls'][0].replace('<strong>2 - 1</strong>', '<strong>3 - 1</strong>')]
    assert apply(client, cid, correction).status_code == 200
    assert apply(client, cid, {**correction, 'match_htmls': []}).status_code == 200
    db.expire_all()
    fixture = db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == 'fpf:match:2682548'))
    assert fixture.home_goals == 3


def test_internal_results_stay_event_derived_after_fpf_correction_and_conflict(fpf_account):
    client, db, cid, capture, payload, players, users = fpf_account
    match = create(client, {**payload, 'opponent_name': 'Seia Fc', 'matchday': 2, 'is_home': False})
    stored = db.get(Match, match['id'])
    stored.status = 'FINISHED'
    db.add(MatchSquad(match_id=stored.id, player_id=players[0], is_starter=True))
    db.add(MatchEvent(match_id=stored.id, event_type='GOAL', team='US', period=1,
                      elapsed_seconds=10, player_id=players[0], recorded_by_id=users['ADMIN'].id))
    db.commit()
    initial = {**capture, 'fixture_htmls': [round_html()]}
    assert apply(client, cid, initial).status_code == 200
    internal_before = fingerprint(db, cid)[1]
    correction = {**capture, 'match_htmls': [], 'fixture_htmls': [round_html(score='9 - 0')]}
    assert apply(client, cid, correction).status_code == 200
    for model in (Match, MatchEvent, MatchSquad, Player):
        assert fingerprint(db, cid)[1][model.__tablename__] == internal_before[model.__tablename__]
    fixture = next(g for g in client.get(f'/competitions/{cid}/calendar').json() if g['internal_match_id'] == stored.id)
    assert (fixture['home_goals'], fixture['away_goals']) == (0, 1)
    before = fingerprint(db, cid)
    assert apply(client, cid, {**correction, 'match_htmls': capture['match_htmls']}).status_code == 409
    assert fingerprint(db, cid) == before
