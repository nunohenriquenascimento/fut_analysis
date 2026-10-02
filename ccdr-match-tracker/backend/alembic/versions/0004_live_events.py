"""Remove ambiguous SHOT without guessing the outcome of historical shots."""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

VALUES = "'GOAL', 'OWN_GOAL', 'SHOT_ON_TARGET', 'SHOT_OFF_TARGET', 'SHOT_BLOCKED', 'CORNER', 'FREE_KICK', 'FOUL', 'YELLOW_CARD', 'RED_CARD', 'OFFSIDE', 'SUBSTITUTION', 'PENALTY', 'SAVE'"


def upgrade() -> None:
    op.execute("LOCK TABLE match_events IN ACCESS EXCLUSIVE MODE")
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM match_events WHERE event_type::text = 'SHOT') THEN
            RAISE EXCEPTION 'Cannot migrate legacy SHOT events: manually classify each as SHOT_ON_TARGET, SHOT_OFF_TARGET or SHOT_BLOCKED first';
        END IF;
    END $$""")
    op.execute(f"CREATE TYPE event_type_new AS ENUM ({VALUES})")
    op.execute("ALTER TABLE match_events ALTER COLUMN event_type TYPE event_type_new USING event_type::text::event_type_new")
    op.execute("DROP TYPE event_type")
    op.execute("ALTER TYPE event_type_new RENAME TO event_type")


def downgrade() -> None:
    legacy = VALUES.replace("'OWN_GOAL',", "'OWN_GOAL', 'SHOT',")
    op.execute(f"CREATE TYPE event_type_old AS ENUM ({legacy})")
    op.execute("ALTER TABLE match_events ALTER COLUMN event_type TYPE event_type_old USING event_type::text::event_type_old")
    op.execute("DROP TYPE event_type")
    op.execute("ALTER TYPE event_type_old RENAME TO event_type")
