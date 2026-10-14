
"""add task ownership

Revision ID: 635fce8bc519
Revises: 6225e5dd635b
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "635fce8bc519"
down_revision: Union[str, Sequence[str], None] = "6225e5dd635b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        "ix_tasks_owner_id",
        "tasks",
        ["owner_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_tasks_owner_id_users",
        "tasks",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_tasks_owner_id_users",
        "tasks",
        type_="foreignkey",
    )

    op.drop_index("ix_tasks_owner_id", table_name="tasks")
    op.drop_column("tasks", "owner_id")
