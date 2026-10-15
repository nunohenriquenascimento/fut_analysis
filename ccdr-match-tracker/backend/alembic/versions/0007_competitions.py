"""Add isolated competition fixtures; preserve all internal game tables."""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("competitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("internal_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("rules", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("season_id", "name"))
    op.create_table("competition_teams",
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id"), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), primary_key=True))
    op.create_table("competition_fixtures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id"), nullable=False),
        sa.Column("external_key", sa.String(120), nullable=False),
        sa.Column("matchday", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("venue", sa.String(160), nullable=True),
        sa.Column("internal_match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("home_goals", sa.Integer(), nullable=True),
        sa.Column("away_goals", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("competition_id", "external_key", name="uq_fixture_external_key"),
        sa.UniqueConstraint("competition_id", "matchday", "home_team_id", "away_team_id", name="uq_fixture_pair_matchday"),
        sa.UniqueConstraint("internal_match_id"),
        sa.CheckConstraint("home_team_id <> away_team_id", name="fixture_different_teams"),
        sa.CheckConstraint("matchday > 0", name="fixture_positive_matchday"),
        sa.CheckConstraint("(home_goals IS NULL AND away_goals IS NULL) OR (home_goals >= 0 AND away_goals >= 0 AND home_goals IS NOT NULL AND away_goals IS NOT NULL)", name="fixture_valid_score"),
        sa.CheckConstraint("internal_match_id IS NULL OR (home_goals IS NULL AND away_goals IS NULL)", name="fixture_internal_no_score"))


def downgrade():
    connection = op.get_bind()
    if connection.execute(sa.text("SELECT EXISTS(SELECT 1 FROM competitions)")).scalar():
        raise RuntimeError("Downgrade recusado: existem dados de competições.")
    op.drop_table("competition_fixtures")
    op.drop_table("competition_teams")
    op.drop_table("competitions")
