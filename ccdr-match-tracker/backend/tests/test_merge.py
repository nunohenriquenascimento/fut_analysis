from datetime import timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import event, select, text
from sqlalchemy.exc import IntegrityError

from app import merge_service
from app.enums import MatchStatus
from app.models import Match, MatchEvent, MatchSquad, Player
from test_matches import games, create, squad  # noqa: F401


@pytest.fixture
def merge_games(games):
    client, db, payload, ids = games
    principal = create(client, {**payload, "opponent_name": "Seia"})
    continuation = create(client, {**payload, "opponent_name": "Seia FC", "matchday": 4,
                                   "kickoff_at": "2026-10-04T17:00:00+01:00"})
    other = create(client, {**payload, "matchday": 5})
    a, b = db.get(Match, principal["id"]), db.get(Match, continuation["id"])
    a.status, a.elapsed_seconds = MatchStatus.FINISHED, 3780
    b.status, b.elapsed_seconds = MatchStatus.FINISHED, 900
    db.commit()
    assert client.put(f"/matches/{a.id}/squad", json=squad((ids[0], True))).status_code == 200
    assert client.put(f"/matches/{b.id}/squad", json=squad((ids[0], False), (ids[1], False), (ids[2], True))).status_code == 200
    # Principal scorer and continuation events with assist, own goal and substitution.
    assert client.post(f"/matches/{a.id}/reopen").status_code == 200
    from app.models import User
    author = db.scalar(select(User.id).where(User.email == "admin@test.local"))
    a.status = MatchStatus.FINISHED
    rows = [MatchEvent(match_id=a.id, event_type="GOAL", team="US", player_id=ids[0],
                       period=2, elapsed_seconds=3700, recorded_by_id=author)]
    for kind, seconds, player, related in [
        ("GOAL", 270, ids[1], ids[0]), ("OWN_GOAL", 300, ids[0], None),
        ("SHOT_ON_TARGET", 330, ids[1], None), ("YELLOW_CARD", 400, ids[0], None),
        ("SUBSTITUTION", 500, ids[0], ids[1]),
    ]:
        rows.append(MatchEvent(match_id=b.id, event_type=kind, team="US", player_id=player,
                              related_player_id=related, period=1, elapsed_seconds=seconds,
                              recorded_by_id=author, notes=f"Original {kind}"))
    db.add_all(rows); db.commit()
    selection = {"principal_id": a.id, "continuation_id": b.id, "final_status": "FINISHED"}
    return client, db, selection, ids, other["id"]


def preview(client, selection):
    response = client.post("/matches/merge/preview", json=selection)
    assert response.status_code == 200, response.text
    return response.json()


def execute(client, selection, plan):
    return client.post("/matches/merge", json={**selection, "preview_token": plan["preview_token"], "confirmation": "UNIR JOGOS"})


def stored(db):
    return {model.__tablename__: [{column.name: getattr(row, column.name) for column in model.__table__.columns}
            for row in db.scalars(select(model).order_by(model.id))] for model in [Match, MatchEvent, MatchSquad, Player]}


def test_preview_is_read_only_and_explicit(merge_games):
    client, db, selection, ids, _ = merge_games
    before = stored(db)
    plan = preview(client, selection)
    assert stored(db) == before
    assert plan["can_merge"] and plan["preview_token"]
    assert plan["principal"]["match"]["opponent_name"] == "Seia"
    assert plan["continuation"]["match"]["opponent_name"] == "Seia FC"
    assert plan["principal"]["period"] == 2
    assert plan["predicted_elapsed_seconds"] == 4680
    assert plan["predicted_score"] == {"us": 2, "opponent": 1}
    assert {row["player"]["id"] for row in plan["continuation_only_players"]} == {ids[1], ids[2]}
    assert any("Adversários diferentes" in warning for warning in plan["warnings"])
    assert any("Jornadas diferentes" in warning for warning in plan["warnings"])
    assert any("Datas/horas diferentes" in warning for warning in plan["warnings"])
    assert any("Titular/suplente" in warning for warning in plan["warnings"])
    assert all(row["original"]["period"] == 1 and row["new_period"] == 2 for row in plan["transfers"])
    assert plan["transfers"][0]["new_elapsed_seconds"] == 4050  # 63:00 + 04:30 = 67:30


@pytest.mark.parametrize("final_status", ["FINISHED", "SECOND_HALF"])
def test_merge_preserves_records_and_reconciles_statistics(merge_games, final_status):
    client, db, selection, ids, other_id = merge_games
    selection["final_status"] = final_status
    before = stored(db)
    main_before = client.get(f"/matches/{selection['principal_id']}/live").json()
    stats_before = client.get("/statistics/season").json()
    plan = preview(client, selection)
    response = execute(client, selection, plan)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["match"]["status"] == final_status and result["match"]["clock_started_at"] is None
    assert result["match"]["elapsed_seconds"] == result["clock_elapsed_seconds"] == 4680
    for key, value in main_before["match"].items():
        if key not in {"status", "elapsed_seconds"}:
            assert result["match"][key] == value
    assert result["score"] == plan["predicted_score"]
    assert db.get(Match, selection["continuation_id"]) is None
    assert db.get(Match, other_id) is not None
    assert len(result["events"]) == 6
    assert result["events"][0] == main_before["events"][0]
    after = stored(db)
    assert after["players"] == before["players"]
    original_events = {row["id"]: row for row in before["match_events"]}
    for row in after["match_events"]:
        original = original_events[row["id"]]
        for key in original.keys() - {"match_id", "period", "elapsed_seconds"}:
            assert row[key] == original[key]
        assert row["match_id"] == selection["principal_id"]
        assert row["elapsed_seconds"] == original["elapsed_seconds"] + (3780 if original["match_id"] == selection["continuation_id"] else 0)
        assert row["period"] == 2
    selected = {row["player_id"]: row for row in after["match_squads"]}
    assert set(selected) == set(ids[:3])
    assert selected[ids[0]]["is_starter"] is True  # principal role wins
    assert selected[ids[1]]["is_starter"] is False
    assert selected[ids[2]]["is_starter"] is True  # continuation-only historical starter
    assert selected[ids[0]]["id"] == next(row["id"] for row in before["match_squads"] if row["match_id"] == selection["principal_id"])
    stats = client.get("/statistics/season").json()
    assert stats["total_matches"] == stats_before["total_matches"] - 1
    assert stats["total_events"] == stats_before["total_events"]
    assert stats["comparison"] == stats_before["comparison"] and stats["rankings"] == stats_before["rankings"]
    assert stats["competitive"]["matches"] == (1 if final_status == "FINISHED" else 0)
    if final_status == "FINISHED":
        assert stats["competitive"]["losses"] == 0 and stats["competitive"]["wins"] == 1
    assert all(row["matches_called_up"] == 1 for row in stats["players"] if row["player"]["id"] in ids[:3])
    assert client.get(f"/matches/{selection['principal_id']}/stats").json()["total_events"] == 6
    if final_status == "SECOND_HALF":
        assert client.post(f"/matches/{selection['principal_id']}/resume").status_code == 200


@pytest.mark.parametrize("change", ["season", "team", "running", "event_time", "squad"])
def test_preview_blocks_incompatible_or_inconsistent_games(merge_games, change):
    client, db, selection, ids, _ = merge_games
    continuation = db.get(Match, selection["continuation_id"])
    if change == "season": continuation.season_id = db.get(Player, ids[5]).season_id
    elif change == "team": continuation.team_id = db.get(Player, ids[4]).team_id
    elif change == "running": continuation.clock_started_at = continuation.kickoff_at
    elif change == "event_time": db.scalar(select(MatchEvent).where(MatchEvent.match_id == continuation.id)).elapsed_seconds = 901
    else: db.scalar(select(MatchSquad).where(MatchSquad.match_id == continuation.id, MatchSquad.player_id == ids[1])).player_id = ids[4]
    db.commit()
    before = stored(db)
    plan = preview(client, selection)
    assert not plan["can_merge"] and plan["conflicts"] and plan["preview_token"] is None
    assert client.post("/matches/merge", json={**selection, "preview_token": "invalid", "confirmation": "UNIR JOGOS"}).status_code == 409
    assert stored(db) == before


def test_multiple_periods_are_explicit_and_ordered(merge_games):
    client, db, selection, _, _ = merge_games
    row = db.scalar(select(MatchEvent).where(MatchEvent.match_id == selection["continuation_id"], MatchEvent.event_type == "SUBSTITUTION"))
    row.period = 2
    db.commit()
    plan = preview(client, selection)
    assert plan["can_merge"] and any("vários períodos" in warning for warning in plan["warnings"])
    result = execute(client, selection, plan).json()
    keys = [(row["period"], row["elapsed_seconds"], row["id"]) for row in result["events"]]
    assert keys == sorted(keys) and all(row["period"] == 2 for row in result["events"])


@pytest.mark.parametrize("change", ["event", "clock", "squad", "metadata", "status", "target_status", "tampered", "expired"])
def test_stale_or_invalid_preview_is_rejected_without_mutations(merge_games, change, monkeypatch):
    client, db, selection, _, _ = merge_games
    plan = preview(client, selection)
    main = db.get(Match, selection["principal_id"])
    if change == "event": db.scalar(select(MatchEvent)).notes = "Changed"
    elif change == "clock": main.elapsed_seconds += 1
    elif change == "squad": db.scalar(select(MatchSquad)).is_starter = False
    elif change == "metadata": main.venue = "Changed"
    elif change == "status": main.status = MatchStatus.SECOND_HALF
    elif change == "target_status": selection["final_status"] = "SECOND_HALF"
    elif change == "tampered": plan["preview_token"] = plan["preview_token"][:-1] + ("0" if plan["preview_token"][-1] != "0" else "1")
    elif change == "expired":
        current = merge_service.time.time()
        monkeypatch.setattr(merge_service.time, "time", lambda: current + 1801)
    db.commit()
    before = stored(db)
    assert execute(client, selection, plan).status_code == 409
    assert stored(db) == before


def test_same_id_missing_confirmation_and_unknown_game(merge_games):
    client, db, selection, _, _ = merge_games
    before = stored(db)
    assert client.post("/matches/merge/preview", json={**selection, "continuation_id": selection["principal_id"]}).status_code == 409
    assert client.post("/matches/merge/preview", json={**selection, "continuation_id": 2147483647}).status_code == 404
    plan = preview(client, selection)
    assert client.post("/matches/merge", json={**selection, "preview_token": plan["preview_token"], "confirmation": "UNIR"}).status_code == 422
    assert client.post("/matches/merge", json={**selection, "confirmation": "UNIR JOGOS"}).status_code == 422
    assert stored(db) == before


@pytest.mark.parametrize("failure", ["flush", "validation", "delete"])
def test_merge_failure_rolls_back_all_moves(merge_games, failure, monkeypatch):
    client, db, selection, _, _ = merge_games
    plan = preview(client, selection)
    before = stored(db)
    def fail(*args):
        raise IntegrityError("injected", {}, Exception("test"))
    if failure == "validation":
        from app import live_service
        original = live_service.score
        calls = [0]
        def wrong(rows):
            calls[0] += 1
            result = original(rows)
            if calls[0] >= 4: result.us += 1
            return result
        monkeypatch.setattr(live_service, "score", wrong)
    elif failure == "delete":
        event.listen(Match, "before_delete", fail)
    else:
        event.listen(db, "before_flush", fail, once=True)
    try:
        assert execute(client, selection, plan).status_code == 409
    finally:
        if failure == "flush": event.remove(db, "before_flush", fail)
        elif failure == "delete": event.remove(Match, "before_delete", fail)
    assert stored(db) == before


def test_unknown_foreign_key_prevents_delete_and_rolls_back_transfers(merge_games):
    client, db, selection, _, _ = merge_games
    # This table exists only inside the fixture's disposable schema/transaction.
    db.execute(text("CREATE TABLE merge_guard (match_id integer REFERENCES matches(id))"))
    db.execute(text("INSERT INTO merge_guard VALUES (:id)"), {"id": selection["continuation_id"]})
    db.commit()
    plan = preview(client, selection)
    before = stored(db)
    assert execute(client, selection, plan).status_code == 409
    assert stored(db) == before


def test_preview_token_is_bound_to_actor_and_pair(merge_games):
    client, db, selection, _, other_id = merge_games
    db.get(Match, other_id).status = MatchStatus.FINISHED
    db.commit()
    plan = preview(client, selection)
    before = stored(db)
    # A genuine token still cannot authorise a different match selection.
    assert execute(client, {**selection, "principal_id": other_id}, plan).status_code == 409
    digest = plan["preview_token"].split(".")[1]
    with pytest.raises(HTTPException) as error:
        merge_service.verify_token(plan["preview_token"], digest, 2147483647)
    assert error.value.status_code == 409
    assert stored(db) == before
