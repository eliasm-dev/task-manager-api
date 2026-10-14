
"""create tasks table"""

from alembic import op
import sqlalchemy as sa

# Keep these two values from your existing migration file.
revision = "2c054e638ee3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"], unique=False)


def downgrade():
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")
