from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from parkly.application.command.create_parking_facility import (
    CreateParkingFacility,
    CreateParkingFacilityHandler,
)
from parkly.domain.exception.exceptions import DuplicateFacilityError
from parkly.domain.model.identifiers import FacilityId


@pytest.fixture
def facility_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.exists_by_name_and_location.return_value = False
    return repo


@pytest.fixture
def id_generator() -> MagicMock:
    gen = MagicMock()
    gen.generate.return_value = FacilityId("01ABC123DEF456GHI789JKL0MN")
    return gen


@pytest.fixture
def clock() -> MagicMock:
    c = MagicMock()
    c.now.return_value = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return c


@pytest.fixture
def event_publisher() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def logger() -> MagicMock:
    return MagicMock()


@pytest.fixture
def handler(
    facility_repo: AsyncMock,
    id_generator: MagicMock,
    clock: MagicMock,
    event_publisher: AsyncMock,
    logger: MagicMock,
) -> CreateParkingFacilityHandler:
    return CreateParkingFacilityHandler(
        facility_repo=facility_repo,
        id_generator=id_generator,
        clock=clock,
        event_publisher=event_publisher,
        logger=logger,
    )


def _make_command(
    name: str = "Central Garage",
    latitude: Decimal = Decimal("40.7128000"),
    longitude: Decimal = Decimal("-74.0060000"),
    address: str = "123 Main St",
    facility_type: str = "public",
    access_control: str = "lpr",
    total_capacity: int = 100,
) -> CreateParkingFacility:
    return CreateParkingFacility(
        name=name,
        latitude=latitude,
        longitude=longitude,
        address=address,
        facility_type=facility_type,
        access_control=access_control,
        total_capacity=total_capacity,
    )


class TestCreateParkingFacilityHandler:
    async def test_creates_facility_successfully(
        self,
        handler: CreateParkingFacilityHandler,
        facility_repo: AsyncMock,
    ) -> None:
        command = _make_command()

        result = await handler.handle(command)

        assert result == "01ABC123DEF456GHI789JKL0MN"
        facility_repo.save.assert_awaited_once()

    async def test_raises_duplicate_facility_error_when_name_and_location_exist(
        self,
        handler: CreateParkingFacilityHandler,
        facility_repo: AsyncMock,
    ) -> None:
        facility_repo.exists_by_name_and_location.return_value = True
        command = _make_command()

        with pytest.raises(DuplicateFacilityError) as exc_info:
            await handler.handle(command)

        assert command.name in str(exc_info.value)
        facility_repo.save.assert_not_awaited()

    async def test_allows_same_name_at_different_location(
        self,
        handler: CreateParkingFacilityHandler,
        facility_repo: AsyncMock,
    ) -> None:
        facility_repo.exists_by_name_and_location.return_value = False
        command = _make_command(
            latitude=Decimal("51.5074000"),
            longitude=Decimal("-0.1278000"),
        )

        result = await handler.handle(command)

        assert result == "01ABC123DEF456GHI789JKL0MN"
        facility_repo.save.assert_awaited_once()
