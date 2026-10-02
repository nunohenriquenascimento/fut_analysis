"""Optional local image references, preserving existing records."""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("teams", sa.Column("crest_path", sa.String(500), nullable=True))
    op.add_column("players", sa.Column("photo_path", sa.String(500), nullable=True))


def downgrade():
    op.drop_column("players", "photo_path")
    op.drop_column("teams", "crest_path")
