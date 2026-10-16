from copy import deepcopy
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.enums import MatchStatus
from app.fpf_parser import parse_competition
from app.fpf_source import FPFSourceUnavailable
from app.models import Competition, CompetitionFixture, Match, MatchEvent, MatchSquad
from test_auth import accounts, password_hash, login  # noqa: F401
from test_matches import games, create  # noqa: F401

CAPTURES = Path(__file__).parent / "fixtures/fpf"


@pytest.mark.parametrize("contents", [["á" * 1_000_001], ["a" * 1_500_000] * 3])
def test_document_limits_count_utf8_bytes_without_database(contents):
    from pydantic import ValidationError
    from app.fpf_api import FPFDocuments
    with pytest.raises(ValidationError):
        FPFDocuments(files=[{"name": f"{index}.html", "html": html} for index, html in enumerate(contents)])


@pytest.fixture
def fpf_account(accounts):
    client, db, payload, players, users = accounts
    login(client)
    html = (CAPTURES / "competition_30369_season_106.html").read_text(encoding="utf-8-sig")
    sheet = (CAPTURES / "match_2682548.html").read_text(encoding="utf-8-sig")
    names = [r["name"] for r in parse_competition(html)["series"][0]["standings"]]
    mapping = {}
    for name in names:
        if name == "V. Cortez Mondego-Guarda":
            mapping[name] = payload["team_id"]
        else:
            response = client.post("/teams", json={"name": name})
            assert response.status_code == 201, response.text
            mapping[name] = response.json()["id"]
    response = client.post("/competitions", json=dict(name="FPF integration", season_id=payload["season_id"],
        internal_team_id=payload["team_id"], team_ids=list(mapping.values())))
    assert response.status_code == 201, response.text
    cid = response.json()["id"]
    capture = dict(competition_html=html, series_id=99718, team_mapping=mapping, match_htmls=[sheet])
    return client, db, cid, capture, payload, players, users


def apply(client, cid, capture):
    return client.put(f"/competitions/{cid}/fpf", json={**capture, "confirmation": "SINCRONIZAR FPF"})


def test_capture_preview_apply_idempotence_and_internal_preservation(fpf_account):
    client, db, cid, capture, payload, players, users = fpf_account
    match = create(client, {**payload, "opponent_name": "Seia Fc", "matchday": 2})
    stored = db.get(Match, match["id"])
    stored.status = MatchStatus.FINISHED
    db.add(MatchSquad(match_id=stored.id, player_id=players[0], is_starter=True))
    db.add(MatchEvent(match_id=stored.id, event_type="GOAL", team="US", period=1,
                      elapsed_seconds=10, player_id=players[0], recorded_by_id=users["ADMIN"].id))
    db.commit()
    paths = [f"/matches/{stored.id}", f"/matches/{stored.id}/squad", f"/matches/{stored.id}/stats"]
    before = [client.get(path).json() for path in paths]
    preview = client.post(f"/competitions/{cid}/fpf/preview", json=capture)
    assert preview.status_code == 200, preview.text
    assert len(preview.json()["fixtures"]) == 4
    assert len(preview.json()["pending_internal_links"]) == 0
    assert preview.json()["ignored"][0]["match_id"] == 2682548
    assert db.get(Competition, cid).fpf_data is None
    for _ in range(2):
        response = apply(client, cid, capture)
        assert response.status_code == 200, response.text
        assert response.json()["imported"] == 4
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 4
    assert [client.get(path).json() for path in paths] == before
    official = client.get(f"/competitions/{cid}/fpf").json()
    assert official["source"] == "FPF" and official["available"]
    assert official["snapshot"]["mode"] == "captured_html"
    assert official["snapshot"]["match_sheets"]["2682548"]["home_goals"] == 2
    assert client.get(f"/competitions/{cid}/standings").json()["provisional"]
    assert client.get(f"/competitions/{cid}/standings").json()["completed_fixtures"] == 0


@pytest.mark.parametrize("role", ["COACH", "VIEWER"])
@pytest.mark.parametrize("method,suffix", [("POST", "/fpf/preview"), ("PUT", "/fpf"), ("POST", "/fpf/sync"), ("POST", "/fpf/documents")])
def test_fpf_writes_are_admin_only(fpf_account, role, method, suffix):
    client, _, cid, capture, *_ = fpf_account
    login(client, role)
    response = client.request(method, f"/competitions/{cid}{suffix}", json={**capture, "confirmation": "SINCRONIZAR FPF"})
    assert response.status_code == 403


def test_403_preserves_last_capture_and_calendar(fpf_account, monkeypatch):
    client, db, cid, capture, *_ = fpf_account
    assert apply(client, cid, capture).status_code == 200
    previous = deepcopy(db.get(Competition, cid).fpf_data)
    calendar = client.get(f"/competitions/{cid}/calendar").json()
    def unavailable(*_):
        raise FPFSourceUnavailable("access_denied")
    monkeypatch.setattr("app.fpf_api.FPFClient.competition", unavailable)
    result = client.post(f"/competitions/{cid}/fpf/sync", json={"confirmation": "SINCRONIZAR FPF"})
    assert result.status_code == 503
    assert db.get(Competition, cid).fpf_data == previous
    assert client.get(f"/competitions/{cid}/calendar").json() == calendar
    assert client.get(f"/competitions/{cid}/fpf").json()["available"]


def test_mapping_conflicts_confirmation_and_invalid_html_do_not_write(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    assert client.put(f"/competitions/{cid}/fpf", json=capture).status_code == 422
    assert apply(client, cid, {**capture, "competition_html": "<html>Forbidden</html>"}).status_code == 422
    mapping = dict(capture["team_mapping"])
    mapping.pop("Guarda Fc")
    assert apply(client, cid, {**capture, "team_mapping": mapping}).status_code == 409
    assert db.get(Competition, cid).fpf_data is None
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 0


def test_manual_calendar_conflict_rolls_back_entire_import(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    plan = client.post(f"/competitions/{cid}/fpf/preview", json=capture).json()
    row = {**plan["fixtures"][0], "external_key": "manual", "source": "Manual entry"}
    assert client.post(f"/competitions/{cid}/fixtures/import", json={"fixtures": [row]}).status_code == 200
    assert apply(client, cid, capture).status_code == 409
    assert db.get(Competition, cid).fpf_data is None
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 1


def test_manual_correction_of_synced_row_is_not_overwritten(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    plan = client.post(f"/competitions/{cid}/fpf/preview", json=capture).json()
    assert apply(client, cid, capture).status_code == 200
    row = {**plan["fixtures"][0], "source": "Correção manual", "home_goals": 2, "away_goals": 0}
    assert client.post(f"/competitions/{cid}/fixtures/import", json={"fixtures": [row]}).status_code == 200
    assert apply(client, cid, capture).status_code == 409
    result = db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == row["external_key"]))
    assert result.home_goals == 2 and result.source == "Correção manual"


def test_explicit_internal_link_uses_existing_game_without_official_score(fpf_account):
    client, db, cid, capture, payload, *_ = fpf_account
    match = create(client, {**payload, "opponent_name": "Guarda Fc", "matchday": 3})
    plan = client.post(f"/competitions/{cid}/fpf/preview", json=capture).json()
    key = next(f["external_key"] for f in plan["fixtures"] if f["internal_match_id"] == match["id"])
    response = apply(client, cid, {**capture, "internal_match_links": {key: match["id"]}})
    assert response.status_code == 200, response.text
    linked = db.scalar(select(CompetitionFixture).where(CompetitionFixture.internal_match_id == match["id"]))
    assert linked.home_goals is None and linked.away_goals is None
    assert not client.get(f"/matches/{match['id']}").json()["can_delete"]


def test_oversized_calendar_field_is_validation_error_not_partial_write(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    modified = {**capture, "competition_html": capture["competition_html"].replace(
        "Estadio Municipal Aguiar Da Beira", "x" * 161)}
    assert apply(client, cid, modified).status_code == 422
    assert db.get(Competition, cid).fpf_data is None
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 0


def test_fpf_apply_requires_csrf(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    client.headers["X-CSRF-Token"] = ""
    assert apply(client, cid, capture).status_code == 403
    assert db.get(Competition, cid).fpf_data is None


def test_verified_match_score_can_update_external_fixture_without_duplication(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    # In this synthetic test competition, Aguiar is the internal club. Thus the
    # real Seia/Cortez sheet is an external game; no actual club data is changed.
    db.get(Competition, cid).internal_team_id = capture["team_mapping"]["Adrc Aguiar Beira"]
    db.commit()
    capture = {**capture, "match_rounds": {"2682548": 677922}}
    assert apply(client, cid, capture).status_code == 200
    key = "fpf:match:2682548"
    original = db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == key))
    assert (original.home_goals, original.away_goals) == (2, 1)
    original_id = original.id
    # Synthetic correction of the captured headline only, NOT a claimed FPF result.
    correction = {**capture, "match_htmls": [capture["match_htmls"][0].replace('<strong>2 - 1</strong>', '<strong>3 - 1</strong>')]}
    assert apply(client, cid, correction).status_code == 200
    db.expire_all()
    corrected = db.scalar(select(CompetitionFixture).where(CompetitionFixture.external_key == key))
    assert corrected.id == original_id and (corrected.home_goals, corrected.away_goals) == (3, 1)
    assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 5


def test_document_detection_uses_real_parsers_without_writes(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    result = client.post(f"/competitions/{cid}/fpf/documents", json={"files": [
        {"name": "competition.html", "html": capture["competition_html"]},
        {"name": "match.html", "html": capture["match_htmls"][0]},
    ]})
    assert result.status_code == 200, result.text
    competition, match = result.json()["documents"]
    assert competition["kind"] == "competition" and competition["supported"]
    assert len(competition["data"]["series"][0]["standings"]) == 8
    assert match["kind"] == "match" and match["data"]["match_id"] == 2682548
    assert db.get(Competition, cid).fpf_data is None


def test_invalid_and_unverified_fixture_documents_are_not_applied(fpf_account):
    client, db, cid, *_ = fpf_account
    result = client.post(f"/competitions/{cid}/fpf/documents", json={"files": [
        {"name": "blocked.html", "html": "<html>Forbidden</html>"},
        {"name": "fixture.html", "html": '<div id="classification"></div><div id="matches"></div>'},
    ]})
    assert result.status_code == 200
    invalid, fixture = result.json()["documents"]
    assert invalid["kind"] == "invalid" and not invalid["supported"]
    assert fixture["kind"] == "fixture" and not fixture["supported"]
    assert db.get(Competition, cid).fpf_data is None


def test_preview_diff_and_stale_state_are_revalidated(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    plan = client.post(f"/competitions/{cid}/fpf/preview", json=capture).json()
    assert all(change["action"] == "create" for change in plan["changes"])
    assert apply(client, cid, {**capture, "expected_state": plan["state_token"]}).status_code == 200
    assert apply(client, cid, {**capture, "expected_state": plan["state_token"]}).status_code == 409
    refreshed = client.post(f"/competitions/{cid}/fpf/preview", json=capture).json()
    assert all(change["action"] == "unchanged" for change in refreshed["changes"])


def test_match_only_upload_reuses_capture_and_preserves_round_coverage(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    assert apply(client, cid, capture).status_code == 200
    payload = {key: value for key, value in capture.items() if key != "competition_html"}
    assert apply(client, cid, payload).status_code == 200
    stored = db.get(Competition, cid).fpf_data
    assert stored["round_captures"]["99718:677923"]["complete"]
    assert len(stored["round_captures"]) == 1
    assert "2682548" in stored["match_sheets"]


def test_duplicate_documents_are_explicitly_refused(fpf_account):
    client, db, cid, capture, *_ = fpf_account
    document = {"name": "competition.html", "html": capture["competition_html"]}
    result = client.post(f"/competitions/{cid}/fpf/documents", json={"files": [document, document]})
    assert result.status_code == 200
    assert result.json()["documents"][0]["supported"]
    assert not result.json()["documents"][1]["supported"]
    assert db.get(Competition, cid).fpf_data is None
