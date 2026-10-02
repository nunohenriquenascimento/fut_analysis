from sqlalchemy import select

from app.enums import EventTeam, EventType, MatchStatus
from app.models import Match, MatchEvent, MatchSquad, Player
from test_matches import games, create  # noqa: F401 -- shared isolated PostgreSQL fixture


def add_match(client, db, payload, status="FINISHED"):
    row = create(client, payload)
    match = db.get(Match, row["id"])
    match.status = MatchStatus(status)
    db.commit()
    return match


def add_event(db, match, kind, team="US", player=None, assist=None, seconds=60, period=1):
    row = MatchEvent(match_id=match.id, event_type=EventType(kind), team=EventTeam(team),
        player_id=player, related_player_id=assist, elapsed_seconds=seconds, period=period)
    db.add(row)
    db.commit()
    return row


def test_match_comparison_score_shots_cards_and_timeline(games):
    client, db, payload, ids = games
    match = add_match(client, db, payload)
    for kind, team in [("GOAL", "US"), ("GOAL", "OPPONENT"), ("OWN_GOAL", "US"), ("OWN_GOAL", "OPPONENT")]:
        add_event(db, match, kind, team, player=ids[0] if team == "US" else None)
    metrics = {"SHOT_ON_TARGET": "shots_on_target", "SHOT_OFF_TARGET": "shots_off_target",
        "SHOT_BLOCKED": "shots_blocked", "CORNER": "corners", "FREE_KICK": "free_kicks",
        "FOUL": "fouls", "OFFSIDE": "offsides", "PENALTY": "penalties",
        "YELLOW_CARD": "yellow_cards", "RED_CARD": "red_cards", "SAVE": "saves"}
    for kind in metrics:
        add_event(db, match, kind, "US", ids[0], seconds=120, period=2)
        add_event(db, match, kind, "OPPONENT", seconds=30)
    response = client.get(f"/matches/{match.id}/stats")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["score"] == {"us": 2, "opponent": 2}
    assert data["is_final"] is True and data["total_events"] == 26
    assert data["team_name"] == "CCDR Vila Cortez do Mondego"
    for side in ["us", "opponent"]:
        assert data["comparison"][side]["goals"] == 2
        assert data["comparison"][side]["shots_total"] == 3
        for field in metrics.values():
            assert data["comparison"][side][field] == 1
    order = [(row["period"], row["elapsed_seconds"], row["id"]) for row in data["timeline"]]
    assert order == sorted(order)
    assert data["players"][0]["id"] == ids[0]


def test_season_finished_only_for_competition_all_events_for_activity(games):
    client, db, payload, ids = games
    for status, ours, theirs in [("FINISHED", 2, 1), ("FINISHED", 1, 1), ("FINISHED", 0, 2),
        ("FIRST_HALF", 5, 0), ("CANCELLED", 7, 0), ("SCHEDULED", 0, 0)]:
        match = add_match(client, db, payload, status)
        for _ in range(ours):
            add_event(db, match, "GOAL", player=ids[0])
        for _ in range(theirs):
            add_event(db, match, "GOAL", "OPPONENT")
    # Games of another team/season must not leak into any totals.
    for changes in [{"season_id": db.get(Player, ids[5]).season_id}, {"team_id": db.get(Player, ids[4]).team_id}]:
        other = add_match(client, db, {**payload, **changes})
        add_event(db, other, "GOAL", "OPPONENT")
    data = client.get("/statistics/season").json()
    assert data["competitive"] == {"matches": 3, "wins": 1, "draws": 1, "losses": 1,
        "goals_for": 3, "goals_against": 4, "goal_difference": -1}
    assert data["total_matches"] == 6 and data["matches_with_events"] == 5 and data["total_events"] == 19
    assert data["comparison"]["us"]["goals"] == 15
    assert data["comparison"]["opponent"]["goals"] == 4
    assert data["scope"] == {"competitive": "FINISHED", "events": "ALL_MATCHES_WITH_EVENTS", "callups": "ALL_MATCHES_INCLUDING_SCHEDULED"}


def test_individual_callups_assists_shots_rankings_and_ties(games):
    client, db, payload, ids = games
    db.get(Player, ids[0]).name = "Zeca"
    db.get(Player, ids[1]).name = "Álvaro"
    db.get(Player, ids[1]).is_active = False
    db.commit()
    played = add_match(client, db, payload)
    scheduled = add_match(client, db, payload, "SCHEDULED")
    db.add_all([MatchSquad(match_id=played.id, player_id=ids[0], is_starter=True),
                MatchSquad(match_id=played.id, player_id=ids[1], is_starter=False),
                MatchSquad(match_id=scheduled.id, player_id=ids[0], is_starter=False)])
    db.commit()
    for player, assist in [(ids[0], ids[1]), (ids[1], ids[0])]:
        add_event(db, played, "GOAL", player=player, assist=assist)
        for kind in ["SHOT_ON_TARGET", "SHOT_OFF_TARGET", "SHOT_BLOCKED", "YELLOW_CARD", "RED_CARD", "FOUL", "OFFSIDE"]:
            add_event(db, played, kind, player=player)
    add_event(db, played, "SUBSTITUTION", player=ids[0], assist=ids[1])
    add_event(db, played, "OWN_GOAL", player=ids[0])
    add_event(db, played, "OWN_GOAL", "OPPONENT")
    data = client.get("/statistics/players").json()
    players = {row["player"]["id"]: row for row in data["players"]}
    assert set(players) == set(ids[:4])  # Own roster only; includes inactive and zero activity.
    for player_id in ids[:2]:
        row = players[player_id]
        assert row["goals"] == 1 and row["assists"] == 1 and row["shots_total"] == 3
        for key in ["shots_on_target", "shots_off_target", "shots_blocked", "yellow_cards", "red_cards", "fouls", "offsides"]:
            assert row[key] == 1
        assert "minutes" not in row
    assert players[ids[0]]["matches_called_up"] == 2 and players[ids[0]]["matches_started"] == 1
    assert players[ids[1]]["matches_called_up"] == 1 and players[ids[1]]["matches_started"] == 0
    for ranking in data["rankings"].values():
        assert [entry["name"] for entry in ranking] == ["Álvaro", "Zeca"]
    season = client.get("/statistics/season").json()
    assert season["players"] == data["players"] and season["rankings"] == data["rankings"]
    assert season["competitive"]["goals_for"] == 3  # Opponent own-goal is not a player's goal.


def test_edit_and_delete_events_recompute_all_statistics(games):
    client, db, payload, ids = games
    match = add_match(client, db, payload)
    db.add_all([MatchSquad(match_id=match.id, player_id=ids[0]), MatchSquad(match_id=match.id, player_id=ids[1])])
    db.commit()
    goal = add_event(db, match, "GOAL", player=ids[0], assist=ids[1])
    assert client.get("/statistics/season").json()["competitive"]["wins"] == 1
    path = f"/matches/{match.id}/events/{goal.id}"
    assert client.patch(path, json={"event_type": "SHOT_ON_TARGET", "related_player_id": None}).status_code == 200
    season = client.get("/statistics/season").json()
    assert season["competitive"]["wins"] == 0 and season["competitive"]["draws"] == 1
    assert season["rankings"]["goals"] == [] and season["rankings"]["assists"] == []
    assert season["comparison"]["us"]["shots_total"] == 1
    assert client.delete(path).status_code == 200
    assert client.get(f"/matches/{match.id}/stats").json()["total_events"] == 0
    assert client.get("/statistics/season").json()["rankings"]["shots_total"] == []


def test_own_goal_edit_and_delete_recompute_match_season_and_players(games):
    client, db, payload, ids = games
    match = add_match(client, db, payload)
    db.add_all([MatchSquad(match_id=match.id, player_id=ids[0], is_starter=True),
                MatchSquad(match_id=match.id, player_id=ids[1])])
    db.commit()
    goal = add_event(db, match, "GOAL", player=ids[0], assist=ids[1])
    path = f"/matches/{match.id}/events/{goal.id}"

    def check(ours, theirs, wins, draws, losses, goals, assists, event_count):
        game = client.get(f"/matches/{match.id}/stats").json()
        season = client.get("/statistics/season").json()
        players = client.get("/statistics/players").json()
        assert game["score"] == {"us": ours, "opponent": theirs}
        assert game["total_events"] == len(game["timeline"]) == event_count
        assert season["competitive"] == {"matches": 1, "wins": wins, "draws": draws,
            "losses": losses, "goals_for": ours, "goals_against": theirs,
            "goal_difference": ours - theirs}
        assert season["comparison"] == game["comparison"]
        assert season["total_events"] == event_count
        assert season["matches_with_events"] == event_count
        assert players["players"] == season["players"]
        assert players["rankings"] == season["rankings"]
        totals = {row["player"]["id"]: row for row in players["players"]}
        assert totals[ids[0]]["goals"] == goals
        assert totals[ids[1]]["assists"] == assists
        assert totals[ids[0]]["matches_called_up"] == totals[ids[0]]["matches_started"] == 1
        assert totals[ids[1]]["matches_called_up"] == 1
        for metric, player_id, value in [("goals", ids[0], goals), ("assists", ids[1], assists)]:
            assert [(row["player_id"], row["value"]) for row in players["rankings"][metric]] == (
                [(player_id, value)] if value else [])
        assert all(not players["rankings"][metric] for metric in ["shots_total", "yellow_cards", "red_cards"])

    check(1, 0, 1, 0, 0, 1, 1, 1)
    assert client.patch(path, json={"event_type": "OWN_GOAL", "related_player_id": None}).status_code == 200
    check(0, 1, 0, 0, 1, 0, 0, 1)
    assert client.patch(path, json={"team": "OPPONENT", "player_id": None}).status_code == 200
    check(1, 0, 1, 0, 0, 0, 0, 1)
    assert client.delete(path).status_code == 200
    check(0, 0, 0, 1, 0, 0, 0, 0)


def test_empty_season_empty_match_and_missing_match(games):
    client, db, payload, _ = games
    data = client.get("/statistics/season").json()
    assert data["total_matches"] == data["matches_with_events"] == data["total_events"] == 0
    assert all(value == 0 for value in data["competitive"].values())
    assert all(value == 0 for side in data["comparison"].values() for value in side.values())
    assert all(not ranking for ranking in data["rankings"].values())
    match = add_match(client, db, payload, "SCHEDULED")
    data = client.get(f"/matches/{match.id}/stats").json()
    assert data["is_final"] is False and data["timeline"] == []
    assert data["score"] == {"us": 0, "opponent": 0}
    assert client.get("/matches/2147483647/stats").status_code == 404
