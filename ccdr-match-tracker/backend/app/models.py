from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import EventTeam, EventType, MatchStatus, PlayerPosition, UserRole


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    # No passwords or login yet. Authentication will be introduced separately.
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Season(TimestampMixin, Base):
    __tablename__ = "seasons"
    __table_args__ = (CheckConstraint("ends_on >= starts_on", name="valid_dates"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    starts_on: Mapped[date]
    ends_on: Mapped[date]


class Team(TimestampMixin, Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True)


class Player(TimestampMixin, Base):
    """A roster registration for one season; retained for historical matches."""
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("season_id", "team_id", "shirt_number"),
        CheckConstraint("shirt_number BETWEEN 1 AND 99", name="shirt_number_range"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    position: Mapped[PlayerPosition] = mapped_column(Enum(PlayerPosition, name="player_position"))
    shirt_number: Mapped[int | None]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Match(TimestampMixin, Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("team_id <> opponent_id", name="different_teams"),
        CheckConstraint("elapsed_seconds >= 0", name="positive_elapsed"),
        CheckConstraint("matchday > 0", name="positive_matchday"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    opponent_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    # Existing games may have no known matchday; new API writes require one.
    matchday: Mapped[int | None]
    opponent: Mapped[Team] = relationship(foreign_keys=[opponent_id], lazy="joined")
    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_home: Mapped[bool] = mapped_column(Boolean, default=True)
    venue: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus, name="match_status"), default=MatchStatus.SCHEDULED)
    # Played seconds accumulated at stoppages, plus time since clock_started_at.
    elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    clock_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def opponent_name(self) -> str:
        return self.opponent.name


class MatchSquad(TimestampMixin, Base):
    __tablename__ = "match_squads"
    __table_args__ = (UniqueConstraint("match_id", "player_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    is_starter: Mapped[bool] = mapped_column(Boolean, default=False)


class MatchEvent(TimestampMixin, Base):
    __tablename__ = "match_events"
    __table_args__ = (
        CheckConstraint("elapsed_seconds >= 0", name="positive_elapsed"),
        CheckConstraint("period IN (1, 2)", name="valid_period"),
        CheckConstraint("team = 'US' OR (player_id IS NULL AND related_player_id IS NULL)", name="opponent_no_roster_player"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType, name="event_type"))
    team: Mapped[EventTeam] = mapped_column(Enum(EventTeam, name="event_team"))
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"), index=True)
    # GOAL: scorer / assist. SUBSTITUTION: player leaving / player entering.
    related_player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    recorded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    period: Mapped[int]
    elapsed_seconds: Mapped[int]
    notes: Mapped[str | None] = mapped_column(String(500))
