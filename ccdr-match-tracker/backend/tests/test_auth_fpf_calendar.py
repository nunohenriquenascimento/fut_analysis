"""All 56 real fixtures, bounded batches, read models and internal preservation."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256

import pytest

from app.models import Match, MatchEvent, MatchSquad, Player
from fpf_calendar_data import calendar_data, SOURCES, FIXTURES
from test_auth_fpf import fpf_account, apply, accounts, password_hash, games, create  # noqa: F401
from test_auth_fpf_conflicts import fingerprint
from test_auth_fpf_rounds import TABLE


def test_full_real_calendar_has_no_missing_rounds_duplicate_pairs_or_ids():
    competition, games, documents = calendar_data()
    assert (competition['competition_id'], competition['season_id']) == (30369,106)
    assert len(documents) == 13 and len(games) == 56
    assert Counter(g['matchday'] for g in games) == {day:4 for day in range(1,15)}
    assert len({(g['home_name'],g['away_name']) for g in games}) == 56
    assert set(Counter(g['home_name'] for g in games).values()) == {7}
    assert set(Counter(g['away_name'] for g in games).values()) == {7}
    ids = [g['match_id'] for g in games if g['match_id'] is not None]
    assert len(ids) == len(set(ids)) == 7
    assert sum(g['home_goals'] is not None for g in games) == 7
    assert sum(g['home_goals'] is None for g in games) == 49
    assert all(g['venue'] and g['schedule_text'] for g in games)
    assert len({sha256((FIXTURES/name).read_bytes()).hexdigest() for name in SOURCES.values()}) == 13


@pytest.mark.parametrize('internal', [False, True])
def test_all_rounds_batched_import_reimport_standings_and_preservation(fpf_account,internal):
    client,db,cid,capture,match_payload,players,users = fpf_account
    _, expected_games, docs = calendar_data()
    mid = None
    if internal:
        match = create(client,{**match_payload,'opponent_name':'Guarda Fc','matchday':3})
        mid = match['id']; db.get(Match,mid).status = 'FINISHED'
        db.add(MatchSquad(match_id=mid,player_id=players[0],is_starter=True))
        db.add(MatchEvent(match_id=mid,event_type='GOAL',team='US',period=1,elapsed_seconds=10,
                          player_id=players[0],recorded_by_id=users['ADMIN'].id)); db.commit()
    original_internal = fingerprint(db,cid)[1]
    initial = {**capture,'match_htmls':[],'fixture_htmls':docs[:8]}
    second = {k:v for k,v in initial.items() if k!='competition_html'}
    second['fixture_htmls'] = docs[8:]
    for request, created in ((initial,36),(second,20)):
        inspection = client.post(f'/competitions/{cid}/fpf/documents', json={'files':[
            *([{'name':'competition.html','html':capture['competition_html']}] if 'competition_html' in request else []),
            *[{'name':f'capture-{i}.html','html':doc['html'],'source_url':doc['source_url']} for i,doc in enumerate(request['fixture_htmls'])]]})
        assert all(d['supported'] for d in inspection.json()['documents']), inspection.text
        preview = client.post(f'/competitions/{cid}/fpf/preview',json=request)
        assert preview.status_code == 200, preview.text
        response = apply(client,cid,{**request,'expected_state':preview.json()['state_token']})
        assert response.status_code == 200, response.text
        assert response.json()['summary']['created'] == created
    calendar = client.get(f'/competitions/{cid}/calendar').json()
    assert len(calendar) == 56
    ids = {(g['matchday'],g['home_team_id'],g['away_team_id']):g['id'] for g in calendar}
    assert len(ids) == 56
    for _ in range(2):
        for request in (second,initial):
            response = apply(client,cid,request)
            assert response.status_code == 200,response.text
            assert response.json()['summary']['created'] == response.json()['summary']['updated'] == 0
    current = client.get(f'/competitions/{cid}/calendar').json()
    assert {(g['matchday'],g['home_team_id'],g['away_team_id']):g['id'] for g in current} == ids
    by_identity = {(g['matchday'],g['home_team_id'],g['away_team_id']):g for g in current}
    mapping = capture['team_mapping']
    for expected in expected_games:
        game = by_identity[expected['matchday'],mapping[expected['home_name']],mapping[expected['away_name']]]
        if game['internal_match_id'] is not None:
            assert game['internal_match_id'] == mid
            assert (game['home_goals'],game['away_goals'],game['status']) == (1,0,'FINISHED')
        else:
            assert (game['home_goals'],game['away_goals']) == (expected['home_goals'],expected['away_goals'])
            assert game['status'] == ('SCHEDULED' if expected['home_goals'] is None else 'FINISHED')
            assert game['schedule_text'] == expected['schedule_text']
            assert game['venue'] == expected['venue']
            assert game['kickoff_at'] is None  # raw dates do not include year
            if expected['match_id']:
                assert game['source'].endswith(f"matchId={expected['match_id']}")
    results = client.get(f'/competitions/{cid}/matchdays').json()
    assert [g['matchday'] for g in results] == list(range(1,15))
    assert all(len(r['fixtures']) == 4 for r in results)
    table = client.get(f'/competitions/{cid}/standings').json()
    assert table['completed_fixtures'] == (8 if internal else 7)
    expected_table = deepcopy(TABLE)
    if internal:
        expected_table['V. Cortez Mondego-Guarda'] = (3,3,2,3)
        expected_table['Guarda Fc'] = (2,1,3,4)
    assert {r['team_id']:(r['played'],r['points'],r['goals_for'],r['goals_against']) for r in table['rows']} == {
        mapping[name]:value for name,value in expected_table.items()}
    after = fingerprint(db,cid)
    for model in (Match,MatchEvent,MatchSquad,Player):
        assert after[1][model.__tablename__] == original_internal[model.__tablename__]
    conflict = deepcopy(docs[0]); conflict['html'] = conflict['html'].replace('4 - 0','9 - 0')
    response = apply(client,cid,{**second,'fixture_htmls':[docs[0],conflict,docs[-1]]})
    assert response.status_code == 409,response.text
    assert response.json()['detail']['code'] == 'FPF_RESULT_CONFLICT'
    assert fingerprint(db,cid) == after
