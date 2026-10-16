"""Joint import of the two unmodified real FPF round responses."""
from pathlib import Path

import pytest
from sqlalchemy import select

from app.models import Match, MatchEvent, MatchSquad, Player
from test_auth_fpf import fpf_account, apply, accounts, password_hash, games, create  # noqa: F401
from test_auth_fpf_conflicts import fingerprint

FIXTURES = Path(__file__).parent / 'fixtures/fpf'
EXPECTED = {
    1: [('Ad S. Romão','Seia Fc',4,0), ('Adrc Aguiar Beira','Cf Os Vilanovenses',5,0),
        ('V. Cortez Mondego-Guarda','Sc Celoricense',0,1), ('Ad Fornos Algodres','Guarda Fc',None,None)],
    2: [('Seia Fc','V. Cortez Mondego-Guarda',2,1), ('Sc Celoricense','Adrc Aguiar Beira',1,4),
        ('Guarda Fc','Ad S. Romão',3,3), ('Cf Os Vilanovenses','Ad Fornos Algodres',2,0)],
}
TABLE = {
    'Adrc Aguiar Beira': (2,6,9,1), 'Ad S. Romão': (2,4,7,3), 'Seia Fc': (2,3,2,5),
    'Sc Celoricense': (2,3,2,4), 'Cf Os Vilanovenses': (2,3,2,5), 'Guarda Fc': (1,1,3,3),
    'Ad Fornos Algodres': (1,0,0,2), 'V. Cortez Mondego-Guarda': (2,0,1,3),
}


def documents():
    return [dict(html=(FIXTURES/f'fixture_{fid}.html').read_text(encoding='utf-8-sig'),
                 source_url=f'https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId={fid}',
                 competition_id=30369,season_id=106,series_id=99718) for fid in (677921,677922)]


@pytest.mark.parametrize('internal', [False,True])
def test_joint_real_rounds_results_standings_and_internal_preservation(fpf_account,internal):
    client,db,cid,capture,match_payload,players,users=fpf_account
    mid=None
    if internal:
        match=create(client,{**match_payload,'opponent_name':'Sc Celoricense','matchday':1})
        mid=match['id']; db.get(Match,mid).status='FINISHED'
        db.add(MatchSquad(match_id=mid,player_id=players[0],is_starter=True))
        db.add(MatchEvent(match_id=mid,event_type='GOAL',team='US',period=1,elapsed_seconds=10,
                          player_id=players[0],recorded_by_id=users['ADMIN'].id)); db.commit()
    before=fingerprint(db,cid)[1]
    docs=documents()
    inspected=client.post(f'/competitions/{cid}/fpf/documents',json={'files':[
        {'name':'competition.html','html':capture['competition_html']},
        *[{'name':f'nome-sem-jornada-{i}.html','html':doc['html'],'source_url':doc['source_url']} for i,doc in enumerate(docs)]]})
    assert [d['data']['matchday'] for d in inspected.json()['documents'][1:]]==[1,2]
    request={**capture,'match_htmls':[],'fixture_htmls':docs}
    response=apply(client,cid,request)
    assert response.status_code==200,response.text
    assert response.json()['summary']['created']==12  # also retains the 4 visible round-3 games from competition HTML
    calendar=client.get(f'/competitions/{cid}/calendar').json()
    ids=[g['id'] for g in calendar]
    for _ in range(2):
        again=apply(client,cid,request)
        assert again.json()['summary']==dict(created=0,updated=0,ignored=12,rejected=0)
    assert [g['id'] for g in client.get(f'/competitions/{cid}/calendar').json()]==ids
    groups=client.get(f'/competitions/{cid}/matchdays').json()
    selected={r['matchday']:r['fixtures'] for r in groups if r['matchday'] in (1,2)}
    assert sum(map(len,selected.values()))==8
    for day,expected in EXPECTED.items():
        wanted={(capture['team_mapping'][h],capture['team_mapping'][a],hg,ag) for h,a,hg,ag in expected}
        if internal and day==1:
            wanted.remove((match_payload['team_id'],capture['team_mapping']['Sc Celoricense'],0,1))
            wanted.add((match_payload['team_id'],capture['team_mapping']['Sc Celoricense'],1,0))
        assert {(g['home_team_id'],g['away_team_id'],g['home_goals'],g['away_goals']) for g in selected[day]}==wanted
    future,=[g for g in selected[1] if g['status']=='SCHEDULED']
    assert future['schedule_text']=='1 nov 16:00' and future['home_goals'] is None and future['away_goals'] is None
    assert all(g['status']=='FINISHED' for g in selected[2])
    table=client.get(f'/competitions/{cid}/standings').json()
    assert table['completed_fixtures']==7
    expected_table=dict(TABLE)
    if internal:
        expected_table['V. Cortez Mondego-Guarda']=(2,3,2,2)
        expected_table['Sc Celoricense']=(2,0,1,5)
    assert {r['team_id']:(r['played'],r['points'],r['goals_for'],r['goals_against']) for r in table['rows']}=={
        capture['team_mapping'][name]:values for name,values in expected_table.items()}
    assert table['rows'][0]['name']=='Adrc Aguiar Beira' and table['rows'][0]['rank']==1
    after=fingerprint(db,cid)[1]
    for model in (Match,MatchEvent,MatchSquad,Player):
        assert before[model.__tablename__]==after[model.__tablename__]
    # Existing individual sheet is the same match as round 2, never an extra fixture.
    response=apply(client,cid,{**request,'match_htmls':capture['match_htmls']})
    assert response.status_code==200,response.text
    assert len(client.get(f'/competitions/{cid}/calendar').json())==12


def test_rounds_imported_in_separate_batches_are_also_idempotent(fpf_account):
    client,db,cid,capture,*_=fpf_account
    request={**capture,'match_htmls':[]}
    assert apply(client,cid,request).json()['summary']['created']==4
    for doc in documents():
        result=apply(client,cid,{**request,'fixture_htmls':[doc]})
        assert result.status_code==200,result.text
        assert result.json()['summary']['created']==4
    for doc in reversed(documents()):
        result=apply(client,cid,{**request,'fixture_htmls':[doc]})
        assert result.json()['summary']['created']==0 and result.json()['summary']['updated']==0
    assert len(client.get(f'/competitions/{cid}/calendar').json())==12
    assert client.get(f'/competitions/{cid}/standings').json()['completed_fixtures']==7
