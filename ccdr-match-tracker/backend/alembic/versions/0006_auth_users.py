"""Passwords, revocable sessions and durable login throttling.

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("uq_users_email_normalized", "users", [sa.text("lower(email)")], unique=True)
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.create_table("auth_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("csrf_token", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_table("login_throttles",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("resets_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_login_throttles_resets_at", "login_throttles", ["resets_at"])


def downgrade():
    op.drop_table("login_throttles")
    op.drop_table("auth_sessions")
    op.drop_column("users", "password_hash")
    op.drop_index("uq_users_email_normalized", table_name="users")
