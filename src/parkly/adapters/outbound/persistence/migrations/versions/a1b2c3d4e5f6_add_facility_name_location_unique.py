"""add facility name location unique constraint

Revision ID: a1b2c3d4e5f6
Revises: 35765084c52a
Create Date: 2026-02-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "35765084c52a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove duplicate (name, latitude, longitude) rows, keeping the one
    # with the lowest pk (i.e. the earliest inserted).
    op.execute(
        sa.text("""
            DELETE FROM parking_facilities
            WHERE pk NOT IN (
                SELECT MIN(pk)
                FROM parking_facilities
                GROUP BY name, latitude, longitude
            )
        """)
    )
    op.create_unique_constraint(
        "uq_facility_name_location",
        "parking_facilities",
        ["name", "latitude", "longitude"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_facility_name_location",
        "parking_facilities",
        type_="unique",
    )
