"""Initial schema. Definitions are frozen here independently of application models."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

user_role = sa.Enum("ADMIN", "COACH", "VIEWER", name="user_role")
position = sa.Enum("GOALKEEPER", "DEFENDER", "MIDFIELDER", "FORWARD", name="player_position")
match_status = sa.Enum("SCHEDULED", "FIRST_HALF", "HALF_TIME", "SECOND_HALF", "FINISHED", "CANCELLED", name="match_status")
event_team = sa.Enum("US", "OPPONENT", name="event_team")
event_type = sa.Enum("GOAL", "OWN_GOAL", "SHOT", "SHOT_ON_TARGET", "SHOT_OFF_TARGET", "SHOT_BLOCKED", "CORNER", "FREE_KICK", "FOUL", "YELLOW_CARD", "RED_CARD", "OFFSIDE", "SUBSTITUTION", "PENALTY", "SAVE", name="event_type")


def identity():
    return sa.Column("id", sa.Integer(), primary_key=True)


def timestamp():
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def reference(name, target, nullable=False):
    return sa.Column(name, sa.Integer(), sa.ForeignKey(target), nullable=nullable)


def upgrade() -> None:
    op.create_table("users", identity(), timestamp(),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False))
    op.create_table("seasons", identity(), timestamp(),
        sa.Column("name", sa.String(30), nullable=False, unique=True),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.CheckConstraint("ends_on >= starts_on", name="valid_dates"))
    op.create_table("teams", identity(), timestamp(),
        sa.Column("name", sa.String(160), nullable=False, unique=True))
    op.create_table("players", identity(), timestamp(),
        reference("season_id", "seasons.id"), reference("team_id", "teams.id"),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("position", position, nullable=False),
        sa.Column("shirt_number", sa.Integer()),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("season_id", "team_id", "shirt_number"),
        sa.CheckConstraint("shirt_number BETWEEN 1 AND 99", name="shirt_number_range"))
    op.create_table("matches", identity(), timestamp(),
        reference("season_id", "seasons.id"), reference("team_id", "teams.id"), reference("opponent_id", "teams.id"),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_home", sa.Boolean(), nullable=False),
        sa.Column("venue", sa.String(160)),
        sa.Column("status", match_status, nullable=False),
        sa.Column("elapsed_seconds", sa.Integer(), nullable=False),
        sa.Column("clock_started_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("team_id <> opponent_id", name="different_teams"),
        sa.CheckConstraint("elapsed_seconds >= 0", name="positive_elapsed"))
    op.create_table("match_squads", identity(), timestamp(),
        reference("match_id", "matches.id"), reference("player_id", "players.id"),
        sa.Column("is_starter", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("match_id", "player_id"))
    op.create_table("match_events", identity(), timestamp(),
        reference("match_id", "matches.id"),
        sa.Column("event_type", event_type, nullable=False),
        sa.Column("team", event_team, nullable=False),
        reference("player_id", "players.id", True), reference("related_player_id", "players.id", True),
        reference("recorded_by_id", "users.id", True),
        sa.Column("period", sa.Integer(), nullable=False),
        sa.Column("elapsed_seconds", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(500)),
        sa.CheckConstraint("elapsed_seconds >= 0", name="positive_elapsed"),
        sa.CheckConstraint("period IN (1, 2)", name="valid_period"),
        sa.CheckConstraint("team = 'US' OR (player_id IS NULL AND related_player_id IS NULL)", name="opponent_no_roster_player"))
    for table, columns in {
        "players": ["season_id", "team_id"],
        "matches": ["season_id", "team_id", "opponent_id", "kickoff_at"],
        "match_squads": ["match_id", "player_id"],
        "match_events": ["match_id", "player_id"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade() -> None:
    for table in ["match_events", "match_squads", "matches", "players", "teams", "seasons", "users"]:
        op.drop_table(table)
    for enum in [event_type, event_team, match_status, position, user_role]:
        enum.drop(op.get_bind(), checkfirst=True)
