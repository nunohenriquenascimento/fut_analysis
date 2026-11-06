"""Real PostgreSQL evidence tests; only disposable schemas from conftest are used."""
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.ai import tools
from app.ai.schemas import AuthorizedMatchContext, MatchStatisticsEvidence, MatchStatisticsInput
from app.database import Base
from app.enums import EventTeam, EventType, MatchStatus, PlayerPosition
from app.models import Match, MatchEvent, Player, Season, Team
from app.statistics_service import match_statistics


@pytest.fixture
def evidence_database(postgres_schema):
    # postgres_schema creates a fresh, random schema, never application tables.
    engine = create_engine(postgres_schema())
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            seasons = [Season(name=name, starts_on=date(year, 7, 1), ends_on=date(year + 1, 6, 30))
                       for name, year in [("Evidence 2026/27", 2026), ("Evidence 2027/28", 2027)]]
            teams = [Team(name=name) for name in ["Evidence club", "Evidence opponent", "Other club"]]
            db.add_all([*seasons, *teams])
            db.flush()
            player = Player(name="Evidence player", team_id=teams[0].id, season_id=seasons[0].id,
                            position=PlayerPosition.MC, shirt_number=8)
            db.add(player)
            matches = [Match(team_id=team, season_id=season, opponent_id=teams[1].id,
                             matchday=1, kickoff_at=datetime(2026, 10, 4, 15, tzinfo=timezone.utc),
                             is_home=True, status=MatchStatus.FINISHED)
                       for team, season in [(teams[0].id, seasons[0].id),
                                            (teams[2].id, seasons[0].id),
                                            (teams[0].id, seasons[1].id)]]
            db.add_all(matches)
            db.flush()
            context = AuthorizedMatchContext(team_id=teams[0].id, season_id=seasons[0].id)
            ids = [match.id for match in matches]
            player_id = player.id
            db.commit()
        yield engine, context, ids, player_id
    finally:
        engine.dispose()


def add_events(engine, match_id, player_id):
    with Session(engine) as db:
        for kind, side, seconds in [
            (EventType.GOAL, EventTeam.US, 90),
            (EventType.OWN_GOAL, EventTeam.US, 30),
            (EventType.OWN_GOAL, EventTeam.OPPONENT, 60),
            (EventType.SHOT_ON_TARGET, EventTeam.US, 120),
            (EventType.SHOT_OFF_TARGET, EventTeam.OPPONENT, 150),
            (EventType.SHOT_BLOCKED, EventTeam.US, 180),
            (EventType.YELLOW_CARD, EventTeam.US, 210),
        ]:
            db.add(MatchEvent(match_id=match_id, event_type=kind, team=side,
                              player_id=player_id if side == EventTeam.US else None,
                              elapsed_seconds=seconds, period=1))
        db.commit()


def test_equivalent_statistics_sources_and_utc_timestamp(evidence_database):
    engine, context, ids, player_id = evidence_database
    add_events(engine, ids[0], player_id)
    with Session(engine) as db:
        expected = match_statistics(db, ids[0])
    before = datetime.now(timezone.utc)
    result = tools.get_match_statistics(ids[0], context=context, engine=engine)
    after = datetime.now(timezone.utc)
    assert result.statistics == expected
    assert result.scope.model_dump() == dict(match_id=ids[0], team_id=context.team_id,
        season_id=context.season_id, events="ALL_RECORDED_MATCH_EVENTS", perspective="MATCH_TEAM")
    assert before <= result.queried_at <= after
    assert result.queried_at.utcoffset().total_seconds() == 0
    assert result.service == "app.statistics_service.match_statistics"
    sources = {source.entity: source.record_ids for source in result.sources}
    assert sources == {
        "matches": [ids[0]], "match_events": [row.id for row in expected.timeline],
        "players": [player_id], "teams": [expected.match.team_id, expected.match.opponent_id],
    }
    assert MatchStatisticsEvidence.model_validate_json(result.model_dump_json()) == result
    assert "UNVERIFIED_COVERAGE" in {item.code for item in result.limitations}


@pytest.mark.parametrize("side, expected", [(EventTeam.US, (0, 1)), (EventTeam.OPPONENT, (1, 0))])
def test_own_goal_credits_the_other_side(evidence_database, side, expected):
    engine, context, ids, player_id = evidence_database
    with Session(engine) as db:
        db.add(MatchEvent(match_id=ids[0], event_type=EventType.OWN_GOAL, team=side,
                         player_id=player_id if side == EventTeam.US else None,
                         elapsed_seconds=60, period=1))
        db.commit()
    result = tools.get_match_statistics(ids[0], context=context, engine=engine).statistics
    assert (result.score.us, result.score.opponent) == expected
    assert (result.comparison.us.goals, result.comparison.opponent.goals) == expected
    assert result.comparison.us.shots_total == result.comparison.opponent.shots_total == 0


@pytest.mark.parametrize("status", list(MatchStatus))
def test_empty_events_preserve_status_and_warn_about_coverage(evidence_database, status):
    engine, context, ids, _ = evidence_database
    with Session(engine) as db:
        db.get(Match, ids[0]).status = status
        db.commit()
    result = tools.get_match_statistics(ids[0], context=context, engine=engine)
    assert result.statistics.total_events == 0
    assert result.statistics.timeline == result.statistics.players == []
    assert result.statistics.score.model_dump() == {"us": 0, "opponent": 0}
    assert result.statistics.is_final == (status == MatchStatus.FINISHED)
    codes = {item.code for item in result.limitations}
    assert {"NO_EVENTS", "UNVERIFIED_COVERAGE"} <= codes
    assert ("NON_FINAL_MATCH" in codes) == (status != MatchStatus.FINISHED)
    assert ("CANCELLED_MATCH" in codes) == (status == MatchStatus.CANCELLED)


@pytest.mark.parametrize("target", ["missing", "other_team", "other_season"])
def test_missing_and_out_of_scope_games_are_indistinguishable(evidence_database, monkeypatch, target):
    engine, context, ids, _ = evidence_database
    match_id = {"missing": 2_147_483_647, "other_team": ids[1], "other_season": ids[2]}[target]

    def forbidden_service(*args):
        pytest.fail("Statistics must not be read before authorization")

    monkeypatch.setattr(tools, "match_statistics", forbidden_service)
    with pytest.raises(HTTPException) as error:
        tools.get_match_statistics(match_id, context=context, engine=engine)
    assert error.value.status_code == 404
    assert error.value.detail == "Jogo não encontrado."


@pytest.mark.parametrize("value", [0, -1, 2_147_483_648, True, "1", 1.0, None])
def test_invalid_match_id_is_rejected_before_database_access(value):
    context = AuthorizedMatchContext(team_id=1, season_id=1)
    with pytest.raises(ValidationError):
        tools.get_match_statistics(value, context=context, engine=None)


@pytest.mark.parametrize("field", ["context", "team_id", "season_id", "role", "permissions"])
def test_tool_arguments_cannot_supply_authorization(field):
    with pytest.raises(ValidationError):
        MatchStatisticsInput.model_validate({"match_id": 1, field: "ADMIN"})


def test_server_context_is_required_validated_and_immutable():
    with pytest.raises(TypeError):
        tools.get_match_statistics(1, context={"team_id": 1, "season_id": 1}, engine=None)
    with pytest.raises(ValidationError):
        AuthorizedMatchContext(team_id=True, season_id=1)
    with pytest.raises(ValidationError):
        AuthorizedMatchContext(team_id=1, season_id=0)
    context = AuthorizedMatchContext(team_id=1, season_id=1)
    with pytest.raises(ValidationError):
        context.team_id = 2
    with pytest.raises(ValidationError):
        AuthorizedMatchContext(team_id=1, season_id=1, role="ADMIN")


def test_transaction_is_read_only_consistent_and_never_commits(evidence_database, monkeypatch):
    engine, context, ids, _ = evidence_database
    statements, commits = [], []

    def record(connection, cursor, statement, parameters, execution_context, executemany):
        statements.append(statement)

    def committed(connection):
        commits.append(True)

    def checked_service(db, match_id):
        assert db.scalar(text("SHOW transaction_read_only")) == "on"
        assert db.scalar(text("SHOW transaction_isolation")) == "repeatable read"
        return match_statistics(db, match_id)

    monkeypatch.setattr(tools, "match_statistics", checked_service)
    event.listen(engine, "before_cursor_execute", record)
    event.listen(engine, "commit", committed)
    try:
        tools.get_match_statistics(ids[0], context=context, engine=engine)
    finally:
        event.remove(engine, "before_cursor_execute", record)
        event.remove(engine, "commit", committed)
    assert not commits
    assert all(statement.lstrip().split()[0].upper() in {"SELECT", "SET", "SHOW"} for statement in statements)
    with engine.connect() as connection:
        # The pooled connection must not leak transaction settings to writers.
        assert connection.scalar(text("SHOW transaction_read_only")) == "off"


def test_postgresql_blocks_accidental_service_writes_and_rolls_back(evidence_database, monkeypatch):
    engine, context, ids, _ = evidence_database

    def accidental_write(db, match_id):
        db.execute(text("UPDATE matches SET venue = 'unexpected write' WHERE id = :id"), {"id": match_id})
        pytest.fail("PostgreSQL should reject writes")

    monkeypatch.setattr(tools, "match_statistics", accidental_write)
    with pytest.raises(DBAPIError) as error:
        tools.get_match_statistics(ids[0], context=context, engine=engine)
    assert error.value.orig.sqlstate == "25006"  # read_only_sql_transaction
    with Session(engine) as db:
        assert db.get(Match, ids[0]).venue is None
        assert db.scalar(text("SHOW transaction_read_only")) == "off"


def test_callers_pending_changes_are_not_flushed_or_returned(evidence_database):
    engine, context, ids, _ = evidence_database
    with Session(engine) as caller:
        match = caller.get(Match, ids[0])
        match.venue = "Pending venue"
        new_team = Team(name="Pending team")
        caller.add(new_team)
        result = tools.get_match_statistics(ids[0], context=context, engine=engine)
        assert result.statistics.match.venue is None
        assert match in caller.dirty and new_team in caller.new
        assert new_team.id is None
    with Session(engine) as db:
        assert db.get(Match, ids[0]).venue is None
        assert db.scalar(select(Team).where(Team.name == "Pending team")) is None


def test_non_postgresql_engine_fails_closed():
    engine = create_engine("sqlite://")
    try:
        with pytest.raises(ValueError, match="PostgreSQL"):
            tools.get_match_statistics(1, context=AuthorizedMatchContext(team_id=1, season_id=1), engine=engine)
    finally:
        engine.dispose()
