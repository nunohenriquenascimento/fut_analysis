"""Local conversion regressions. Synthetic HTML is never imported into production."""
from datetime import datetime, timezone
from sqlalchemy import select, func

from app.models import Competition, CompetitionFixture, Match, MatchEvent, MatchSquad, Player
from test_auth_fpf import fpf_account, apply, accounts, password_hash, games, create  # noqa: F401


def round_html(fixture_id=677922, score="2 - 1", match_id=2682548):
    # Contract test using the real sheet's participants/result, not a new official capture.
    center = f'<a href="/Match/GetMatchInformation?matchId={match_id}"><div class="text-center">{score}</div></a>'
    if score is None:
        center = '<span class="game-schedule">17 out 16:00</span>'
    return f'''<meta property="og:url" content="https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId={fixture_id}">
        <div id="matches"><div class="game"><div class="home-team">Seia Fc</div>
        {center}<div class="away-team">V. Cortez Mondego-Guarda</div></div></div>'''


def test_sheet_becomes_local_result_and_reimport_updates_same_id(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    capture = {**capture, "match_rounds": {"2682548": 677922}}
    response = apply(client, cid, capture)
    assert response.status_code == 200, response.text
    assert response.json()["summary"] == dict(created=5, updated=0, ignored=0, rejected=0)
    calendar = client.get(f"/competitions/{cid}/calendar").json()
    completed, = [g for g in calendar if g["status"] == "FINISHED"]
    assert (completed["home_goals"], completed["away_goals"]) == (2, 1)
    assert completed["internal_match_id"] is None
    assert datetime.fromisoformat(completed["kickoff_at"]).astimezone(timezone.utc).isoformat() == "2026-10-10T15:00:00+00:00"
    assert len([g for g in calendar if g["status"] == "SCHEDULED"]) == 4
    table = client.get(f"/competitions/{cid}/standings").json()
    assert table["completed_fixtures"] == 1
    seia = next(r for r in table["rows"] if r["team_id"] == capture["team_mapping"]["Seia Fc"])
    assert (seia["played"], seia["points"], seia["goals_for"]) == (1, 3, 2)
    assert client.get(f"/competitions/{cid}/matchdays").json()[0]["matchday"] == 2
    again = apply(client, cid, capture)
    assert again.json()["summary"] == dict(created=0, updated=0, ignored=5, rejected=0)
    correction = {**capture, "match_htmls": [capture["match_htmls"][0].replace("<strong>2 - 1</strong>", "<strong>3 - 1</strong>")]}
    updated = apply(client, cid, correction)
    assert updated.json()["summary"]["updated"] == 1
    current = db.scalar(select(CompetitionFixture).where(CompetitionFixture.id == completed["id"]))
    assert current.home_goals == 3
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 5


def test_round_upload_assigns_sheet_round_and_preserves_known_result(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    capture = {**capture, "fixture_htmls": [round_html()]}
    inspected = client.post(f"/competitions/{cid}/fpf/documents", json={"files": [{"name": "round.html", "html": round_html()}]})
    assert inspected.json()["documents"][0]["supported"]
    assert apply(client, cid, capture).status_code == 200
    assert db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == "fpf:match:2682548")).home_goals == 2
    scheduled = {**capture, "fixture_htmls": [round_html(score=None)], "match_htmls": []}
    assert apply(client, cid, scheduled).status_code == 200
    db.expire_all()
    assert db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == "fpf:match:2682548")).home_goals == 2


def test_legacy_key_is_preserved_when_sheet_adds_fpf_id(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    initial = {**capture, "fixture_htmls": [round_html(score=None)], "match_htmls": []}
    assert apply(client, cid, initial).status_code == 200
    original = db.scalar(select(CompetitionFixture).where(CompetitionFixture.matchday == 2))
    original_id, original_key = original.id, original.external_key
    assert original_key.startswith("fpf:106:")
    assert apply(client, cid, {**capture, "fixture_htmls": [round_html()]}).status_code == 200
    db.expire_all()
    current = db.get(CompetitionFixture, original_id)
    assert current.external_key == original_key and current.home_goals == 2
    assert current.source.endswith("matchId=2682548")
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 5


def test_internal_events_take_precedence_and_all_internal_data_stays_identical(fpf_account):
    client, db, cid, capture, payload, players, users = fpf_account
    match = create(client, {**payload, "opponent_name": "Seia Fc", "matchday": 2, "is_home": False})
    stored = db.get(Match, match["id"])
    stored.status = "FINISHED"
    db.add(MatchSquad(match_id=stored.id, player_id=players[0], is_starter=True))
    db.add(MatchEvent(match_id=stored.id, event_type="GOAL", team="US", period=1,
                      elapsed_seconds=10, player_id=players[0], recorded_by_id=users["ADMIN"].id))
    db.commit()
    def fingerprint():
        return {model.__tablename__: [tuple(getattr(r, c.name) for c in model.__table__.columns)
                for r in db.scalars(select(model).order_by(model.id))]
                for model in (Match, MatchEvent, MatchSquad, Player)}
    before = fingerprint()
    capture = {**capture, "match_rounds": {"2682548": 677922}}
    assert apply(client, cid, capture).status_code == 200
    assert fingerprint() == before
    fixture = db.scalar(select(CompetitionFixture).where(CompetitionFixture.internal_match_id == stored.id))
    assert fixture.home_goals is None and fixture.away_goals is None
    result = next(g for g in client.get(f"/competitions/{cid}/calendar").json() if g["id"] == fixture.id)
    assert (result["home_goals"], result["away_goals"]) == (0, 1)


def test_contradictory_round_or_id_rejects_atomic_batch(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    response = apply(client, cid, {**capture, "fixture_htmls": [round_html()], "match_rounds": {"2682548": 677923}})
    assert response.status_code == 409
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 0
    response = apply(client, cid, {**capture, "fixture_htmls": [round_html(fixture_id=999)]})
    assert response.status_code == 409
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 0


def test_external_fpf_id_can_move_round_without_duplicate(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    initial = {**capture, "match_rounds": {"2682548": 677922}}
    assert apply(client, cid, initial).status_code == 200
    original = db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == "fpf:match:2682548"))
    original_id = original.id
    assert apply(client, cid, {**capture, "match_rounds": {"2682548": 677921}}).status_code == 200
    db.expire_all()
    assert db.get(CompetitionFixture, original_id).matchday == 1
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 5


def test_ambiguous_internal_games_are_reported_not_guessed(fpf_account):
    client, db, cid, capture, payload, *_ = fpf_account
    for _ in range(2):
        create(client, {**payload, "opponent_name": "Guarda Fc", "matchday": 3})
    plan = client.post(f"/competitions/{cid}/fpf/preview", json=capture).json()
    assert len(plan["pending_internal_links"]) == 1
    assert len(plan["fixtures"]) == 3
    assert plan["summary"]["ignored"] == 2  # ambiguous game plus sheet without round
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 0


def test_old_snapshot_without_match_rounds_recovers_existing_fpf_identity(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    assert apply(client, cid, {**capture, "match_rounds": {"2682548": 677922}}).status_code == 200
    competition = db.get(Competition, cid)
    competition.fpf_data = {k: v for k, v in competition.fpf_data.items() if k != "match_rounds"}
    db.commit()
    result = apply(client, cid, {k: v for k, v in capture.items() if k != "competition_html"})
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == dict(created=0, updated=0, ignored=5, rejected=0)
    assert db.get(Competition, cid).fpf_data["match_rounds"]["2682548"] == 677922
