import uuid
from datetime import datetime

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from main import settings
from models import Event, EventType


@pytest.fixture
async def user():
    return {"id": "00000000-0000-0000-0000-000000000000", "username": "mockuser"}


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user", "created_date", "changed_date")
async def event(db, faker, user):
    collection = db.events
    instance = Event(
        id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        event_type=EventType.ACCEDENT.value,
        description=(
            "City point during. Maybe movement few record baby."
            "Interesting use throughout responsibility."
            "Team almost by continue run professional."
        ),
        address="7607 Jennifer Canyon Foleyville, MN 60927",
        location={"type": "Point", "coordinates": [-159.243865, 168.469047]},
        created_by=user,
        created_date=datetime(1111, 1, 1),
        changed_date=datetime(1111, 1, 1),
    )
    await collection.insert_one(instance.dict())
    yield instance
    await collection.delete_one({"id": instance.id})


@pytest.fixture
async def event_mock():
    class MockedEvent(Event):
        """
        Event mock object

        For id, created_date, changed_date fields event we have set default_factory,
        which makes for us imposible patch of datetime and uuid modules,
        because of default_factory works on metaclass layer
        and at the moment we are using Event model in mutation,
        model patch just will not have any effect for already defined fields values.

        To resolve this issue we've created PreparedEvent model,
        which allow us to set values of id, created_date and changed_date explicitly.
        """

        def __init__(self, **kwargs):
            super().__init__(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                created_date=datetime(1234, 5, 6),
                changed_date=datetime(1234, 5, 6),
                **kwargs
            )

    return MockedEvent


@pytest.fixture
async def db():
    client = AsyncIOMotorClient(
        settings.database_host, settings.database_port, uuidRepresentation="standard"
    )
    yield client[settings.database_name if not settings.test else "test"]
    client.drop_database("test")
