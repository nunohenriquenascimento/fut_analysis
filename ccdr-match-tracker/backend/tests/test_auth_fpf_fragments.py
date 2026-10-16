"""Regression tests using the unmodified operator-supplied AJAX response."""
from pathlib import Path

import pytest
from sqlalchemy import select

from app.fpf_parser import FPFHTMLInvalid, parse_fixture
from app.models import CompetitionFixture, Match, MatchEvent, MatchSquad, Player
from test_auth_fpf import fpf_account, apply, accounts, password_hash, games, create  # noqa: F401
from test_auth_fpf_conflicts import fingerprint

CAPTURE = Path(__file__).parent / 'fixtures/fpf/fixture_677921.html'
URL = 'https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=677921'


def fragment(**changes):
    return dict(html=CAPTURE.read_text(encoding='utf-8-sig'), source_url=URL,
                competition_id=30369, season_id=106, series_id=99718, **changes)


def payload(capture, document=None):
    return {**capture, 'match_htmls': [], 'fixture_htmls': [document or fragment()]}


def test_original_fragment_scores_schedule_stadiums_and_links():
    html = CAPTURE.read_text(encoding='utf-8-sig')
    assert 'og:url' not in html
    data = parse_fixture(html, source_url=URL)
    assert data['fixture_id'] == 677921
    assert [(g['match_id'], g['home_goals'], g['away_goals']) for g in data['matches']] == [
        (2682543, 4, 0), (2682545, 5, 0), (2682544, 0, 1), (None, None, None)]
    assert [g['schedule_text'] for g in data['matches']] == ['3 out', '3 out', '3 out', '1 nov 16:00']
    assert all(g['venue'] for g in data['matches'])
    with pytest.raises(FPFHTMLInvalid):
        parse_fixture(html)


@pytest.mark.parametrize('url', [URL.replace('https:', 'http:'), URL.replace('resultados.fpf.pt', 'evil.test'),
    URL + '&fixtureId=677922', URL + '&competitionId=30369', URL + '#fragment', URL.replace('677921', '0'),
    'https://[', URL + '&fixtureId='])
def test_fragment_invalid_source_is_rejected(url):
    with pytest.raises(FPFHTMLInvalid):
        parse_fixture(CAPTURE.read_text(encoding='utf-8-sig'), source_url=url)


def test_real_fragment_import_reimport_read_models(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    doc = fragment()
    inspection = client.post(f'/competitions/{cid}/fpf/documents', json={'files': [
        {'name': 'competition.html', 'html': capture['competition_html']},
        {'name': 'nome-sem-jornada.html', 'html': doc['html'], 'source_url': URL}]})
    inspected = inspection.json()['documents'][1]
    assert inspected['supported'], inspection.text
    assert (inspected['data']['competition_id'], inspected['data']['season_id'], inspected['data']['series_id'], inspected['data']['matchday']) == (30369,106,99718,1)
    request = payload(capture)
    assert apply(client, cid, request).json()['summary']['created'] == 8
    before = fingerprint(db, cid)
    response = apply(client, cid, request)
    assert response.json()['summary'] == dict(created=0,updated=0,ignored=8,rejected=0)
    assert fingerprint(db, cid)[1] == before[1]
    calendar = client.get(f'/competitions/{cid}/calendar').json()
    round1 = [g for g in calendar if g['matchday'] == 1]
    assert len(round1) == 4
    future, = [g for g in round1 if g['status'] == 'SCHEDULED']
    assert future['home_goals'] is None and future['away_goals'] is None
    assert future['kickoff_at'] is None and future['schedule_text'] == '1 nov 16:00'
    assert future['external_key'].startswith('fpf:106:30369:99718:677921:')
    assert client.get(f'/competitions/{cid}/standings').json()['completed_fixtures'] == 3
    assert len(client.get(f'/competitions/{cid}/matchdays').json()[0]['fixtures']) == 4


@pytest.mark.parametrize('field,value', [('competition_id',1),('season_id',1),('series_id',1),('source_url',URL.replace('677921','999999'))])
def test_context_mismatch_rejects_entire_batch(fpf_account, field, value):
    client, db, cid, capture, *_ = fpf_account
    before = fingerprint(db,cid)
    doc = fragment(); doc[field] = value
    response = apply(client,cid,payload(capture,doc))
    assert response.status_code in (409,422), response.text
    assert fingerprint(db,cid) == before


def test_no_match_id_can_gain_id_without_duplicate(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    assert apply(client,cid,payload(capture)).status_code == 200
    original = next(g for g in client.get(f'/competitions/{cid}/calendar').json() if g['matchday']==1 and g['home_goals'] is None)
    doc = fragment()
    # Mutation of the real response, explicitly representing a later FPF ID assignment.
    doc['html'] = doc['html'].replace('<div class="game" style="min-height: 31px">\n\n\n    <div class="home-team  col-md-4 col-sm-4 col-xs-4 no-padding text-left">Ad Fornos Algodres', '<div class="game" href="/Match/GetMatchInformation?matchId=999999" style="min-height: 31px">\n\n\n    <div class="home-team  col-md-4 col-sm-4 col-xs-4 no-padding text-left">Ad Fornos Algodres')
    assert doc['html'] != fragment()['html']
    for _ in range(2):
        response = apply(client,cid,payload(capture,doc)); assert response.status_code==200,response.text
    db.expire_all()
    row = db.get(CompetitionFixture,original['id'])
    assert row.external_key==original['external_key'] and row.source.endswith('matchId=999999')
    assert len(client.get(f'/competitions/{cid}/calendar').json())==8


def test_fragment_conflict_atomic_and_internal_events_preserved(fpf_account):
    client,db,cid,capture,match_payload,players,users=fpf_account
    match=create(client,{**match_payload,'opponent_name':'Sc Celoricense','matchday':1})
    row=db.get(Match,match['id']); row.status='FINISHED'
    db.add(MatchSquad(match_id=row.id,player_id=players[0],is_starter=True))
    db.add(MatchEvent(match_id=row.id,event_type='GOAL',team='US',period=1,elapsed_seconds=10,player_id=players[0],recorded_by_id=users['ADMIN'].id));db.commit()
    before=fingerprint(db,cid)
    assert apply(client,cid,payload(capture)).status_code==200
    after=fingerprint(db,cid)
    for model in (Match,MatchEvent,MatchSquad,Player):
        assert before[1][model.__tablename__]==after[1][model.__tablename__]
    actual=next(g for g in client.get(f'/competitions/{cid}/calendar').json() if g['internal_match_id']==row.id)
    assert (actual['home_goals'],actual['away_goals'])==(1,0)
    conflict=fragment(); conflict['html']=conflict['html'].replace('4 - 0','9 - 0')
    response=apply(client,cid,{**payload(capture),'fixture_htmls':[fragment(),conflict]})
    assert response.status_code==409,response.text
    assert response.json()['detail']['code']=='FPF_RESULT_CONFLICT'
    assert fingerprint(db,cid)==after


def test_fragment_context_is_required_and_round_cannot_be_injected(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    raw = fragment()['html']
    assert apply(client,cid,{**payload(capture),'fixture_htmls':[raw]}).status_code==422
    response=apply(client,cid,payload(capture,{**fragment(),'matchday':14}))
    assert response.status_code==422
    inspection=client.post(f'/competitions/{cid}/fpf/documents',json={'files':[{'name':'Jornada 1.html','html':raw,'source_url':URL}]})
    assert not inspection.json()['documents'][0]['supported']  # no competition has yet been confirmed
    assert apply(client,cid,{**capture,'match_htmls':[]}).status_code==200
    inspection=client.post(f'/competitions/{cid}/fpf/documents',json={'files':[{'name':'Jornada 14.html','html':raw,'source_url':URL}]})
    doc=inspection.json()['documents'][0]
    assert doc['supported'] and doc['data']['matchday']==1
    assert all(g['matchday']==1 for g in doc['data']['matches'])


def test_url_and_embedded_canonical_must_agree():
    html=fragment()['html']+'<meta property="og:url" content="'+URL.replace('677921','677922')+'">'
    with pytest.raises(FPFHTMLInvalid):
        parse_fixture(html,source_url=URL)


def test_later_assignment_survives_replaying_original_fragment(fpf_account):
    client,db,cid,capture,*_=fpf_account
    assert apply(client,cid,payload(capture)).status_code==200
    original=next(g for g in client.get(f'/competitions/{cid}/calendar').json() if g['matchday']==1 and g['home_goals'] is None)
    doc=fragment()
    marker='<div class="game" style="min-height: 31px">'
    position=doc['html'].rindex(marker)
    doc['html']=doc['html'][:position]+doc['html'][position:].replace(marker,'<div class="game" href="/Match/GetMatchInformation?matchId=999999" style="min-height: 31px">',1)
    assert apply(client,cid,payload(capture,doc)).status_code==200
    assert apply(client,cid,payload(capture)).status_code==200
    db.expire_all()
    assert db.get(CompetitionFixture,original['id']).source.endswith('matchId=999999')
    assert len(client.get(f'/competitions/{cid}/calendar').json())==8
