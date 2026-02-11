from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ParkingFacilityORM(Base):
    __tablename__ = "parking_facilities"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ulid: Mapped[str] = mapped_column(String(26), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    address: Mapped[str] = mapped_column(String(500))
    facility_type: Mapped[str] = mapped_column(String(20))
    access_control: Mapped[str] = mapped_column(String(20))
    total_capacity: Mapped[int] = mapped_column(Integer)

    spots: Mapped[list["ParkingSpotORM"]] = relationship(
        back_populates="facility",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("ix_facilities_lat_lng", "latitude", "longitude"),)


class ParkingSpotORM(Base):
    __tablename__ = "parking_spots"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ulid: Mapped[str] = mapped_column(String(26), unique=True, index=True)
    facility_pk: Mapped[int] = mapped_column(
        Integer, ForeignKey("parking_facilities.pk", ondelete="CASCADE")
    )
    spot_number: Mapped[str] = mapped_column(String(50))
    spot_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))

    facility: Mapped["ParkingFacilityORM"] = relationship(back_populates="spots")

    __table_args__ = (
        UniqueConstraint("facility_pk", "spot_number", name="uq_spot_facility_number"),
    )


class ReservationORM(Base):
    __tablename__ = "reservations"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ulid: Mapped[str] = mapped_column(String(26), unique=True, index=True)
    facility_ulid: Mapped[str] = mapped_column(String(26), index=True)
    spot_ulid: Mapped[str] = mapped_column(String(26), index=True)
    vehicle_ulid: Mapped[str] = mapped_column(String(26), index=True)
    time_slot_start: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    time_slot_end: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    status: Mapped[str] = mapped_column(String(20))
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    cost_currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    __table_args__ = (
        Index(
            "ix_reservations_spot_time",
            "spot_ulid",
            "time_slot_start",
            "time_slot_end",
        ),
    )


class VehicleORM(Base):
    __tablename__ = "vehicles"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ulid: Mapped[str] = mapped_column(String(26), unique=True, index=True)
    owner_ulid: Mapped[str] = mapped_column(String(26), index=True)
    license_plate_value: Mapped[str] = mapped_column(String(20))
    license_plate_region: Mapped[str] = mapped_column(String(10))
    vehicle_type: Mapped[str] = mapped_column(String(20))
    is_ev: Mapped[bool] = mapped_column(Boolean)

    __table_args__ = (
        UniqueConstraint(
            "license_plate_value",
            "license_plate_region",
            name="uq_vehicle_plate",
        ),
    )


class ParkingSessionORM(Base):
    __tablename__ = "parking_sessions"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ulid: Mapped[str] = mapped_column(String(26), unique=True, index=True)
    reservation_ulid: Mapped[str | None] = mapped_column(
        String(26), nullable=True, index=True
    )
    facility_ulid: Mapped[str] = mapped_column(String(26), index=True)
    spot_ulid: Mapped[str] = mapped_column(String(26), index=True)
    vehicle_ulid: Mapped[str] = mapped_column(String(26), index=True)
    entry_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    exit_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    cost_currency: Mapped[str] = mapped_column(String(3))

    __table_args__ = (Index("ix_sessions_spot_exit", "spot_ulid", "exit_time"),)
