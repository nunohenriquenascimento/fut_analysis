"""Add a matchday without inventing values for existing matches."""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("matchday", sa.Integer(), nullable=True))
    op.create_check_constraint("positive_matchday", "matches", "matchday > 0")


def downgrade() -> None:
    # Match records and squads survive; matchday values are necessarily lost.
    op.drop_constraint(op.f("ck_matches_positive_matchday"), "matches", type_="check")
    op.drop_column("matches", "matchday")
