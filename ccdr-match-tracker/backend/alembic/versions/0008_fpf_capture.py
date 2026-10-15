"""Preserve the last FPF capture on the existing competition."""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("competitions", sa.Column("fpf_data", sa.JSON(), nullable=True))


def downgrade():
    if op.get_bind().execute(sa.text("SELECT EXISTS (SELECT 1 FROM competitions WHERE fpf_data IS NOT NULL)")).scalar():
        raise RuntimeError("Downgrade recusado: existem capturas FPF.")
    op.drop_column("competitions", "fpf_data")
