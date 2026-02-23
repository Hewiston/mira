"""make payment_id unique and not null

Revision ID: 6a3d8fb6d6c1
Revises: 93e6d4a8e02f
Create Date: 2026-02-22 16:05:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6a3d8fb6d6c1"
down_revision: Union[str, Sequence[str], None] = "93e6d4a8e02f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM payments WHERE payment_id IS NULL")
    op.alter_column(
        "payments",
        "payment_id",
        existing_type=sa.String(length=128),
        nullable=False,
    )
    op.create_unique_constraint("uq_payments_payment_id", "payments", ["payment_id"])


def downgrade() -> None:
    op.drop_constraint("uq_payments_payment_id", "payments", type_="unique")
    op.alter_column(
        "payments",
        "payment_id",
        existing_type=sa.String(length=128),
        nullable=True,
    )
