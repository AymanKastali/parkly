"""initial_schema

Revision ID: 35765084c52a
Revises:
Create Date: 2026-02-11 16:55:16.779513

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "35765084c52a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parking_facilities",
        sa.Column("pk", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ulid", sa.String(26), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("facility_type", sa.String(20), nullable=False),
        sa.Column("access_control", sa.String(20), nullable=False),
        sa.Column("total_capacity", sa.Integer, nullable=False),
    )
    op.create_index(
        "ix_facilities_lat_lng",
        "parking_facilities",
        ["latitude", "longitude"],
    )

    op.create_table(
        "parking_spots",
        sa.Column("pk", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ulid", sa.String(26), unique=True, index=True, nullable=False),
        sa.Column(
            "facility_pk",
            sa.Integer,
            sa.ForeignKey("parking_facilities.pk", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("spot_number", sa.String(50), nullable=False),
        sa.Column("spot_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.UniqueConstraint(
            "facility_pk", "spot_number", name="uq_spot_facility_number"
        ),
    )

    op.create_table(
        "reservations",
        sa.Column("pk", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ulid", sa.String(26), unique=True, index=True, nullable=False),
        sa.Column("facility_ulid", sa.String(26), index=True, nullable=False),
        sa.Column("spot_ulid", sa.String(26), index=True, nullable=False),
        sa.Column("vehicle_ulid", sa.String(26), index=True, nullable=False),
        sa.Column(
            "time_slot_start",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "time_slot_end",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("cost_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_currency", sa.String(3), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_reservations_spot_time",
        "reservations",
        ["spot_ulid", "time_slot_start", "time_slot_end"],
    )

    op.create_table(
        "vehicles",
        sa.Column("pk", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ulid", sa.String(26), unique=True, index=True, nullable=False),
        sa.Column("owner_ulid", sa.String(26), index=True, nullable=False),
        sa.Column("license_plate_value", sa.String(20), nullable=False),
        sa.Column("license_plate_region", sa.String(10), nullable=False),
        sa.Column("vehicle_type", sa.String(20), nullable=False),
        sa.Column("is_ev", sa.Boolean, nullable=False),
        sa.UniqueConstraint(
            "license_plate_value",
            "license_plate_region",
            name="uq_vehicle_plate",
        ),
    )

    op.create_table(
        "parking_sessions",
        sa.Column("pk", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ulid", sa.String(26), unique=True, index=True, nullable=False),
        sa.Column("reservation_ulid", sa.String(26), nullable=True, index=True),
        sa.Column("facility_ulid", sa.String(26), index=True, nullable=False),
        sa.Column("spot_ulid", sa.String(26), index=True, nullable=False),
        sa.Column("vehicle_ulid", sa.String(26), index=True, nullable=False),
        sa.Column(
            "entry_time",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "exit_time",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("cost_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_currency", sa.String(3), nullable=False),
    )
    op.create_index(
        "ix_sessions_spot_exit",
        "parking_sessions",
        ["spot_ulid", "exit_time"],
    )


def downgrade() -> None:
    op.drop_table("parking_sessions")
    op.drop_table("vehicles")
    op.drop_table("reservations")
    op.drop_table("parking_spots")
    op.drop_table("parking_facilities")
