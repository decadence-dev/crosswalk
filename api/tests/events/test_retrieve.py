import pytest
import pytz

from models import Event, EventType
from tests.utils import graphql


@pytest.fixture
@pytest.mark.usefixtures("faker")
async def created_date(faker):
    return faker.date_time()


@pytest.fixture
@pytest.mark.usefixtures("faker")
async def changed_date(faker):
    return faker.date_time()


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user", "created_date", "changed_date")
async def event(db, faker, user, created_date, changed_date):
    collection = db.events
    instance = Event(
        event_type=faker.random_element(EventType),
        description=faker.text(),
        address=faker.address(),
        location={"type": "Point", "coordinates": [0.0, 0.0]},
        created_by=user,
        created_date=created_date,
        changed_date=changed_date,
    )
    await collection.insert_one(instance.dict())
    yield instance
    await collection.delete_one({"id": instance.id})


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
async def test_event_coordinates_properties(user, event):
    response = await graphql(
        """
        query getEvent($id: UUID!) {
            event(id: $id) {
                longitude
                latitude
            }
        }
        """,
        creadentials=user,
        id=str(event.id),
    )

    assert response.status_code == 200
    assert response.json()["data"]["event"]["longitude"] == 0.0
    assert response.json()["data"]["event"]["latitude"] == 0.0


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
async def test_event_location(user, event):
    """
    Test event location field

    Clients should not to be able to get or set location directly.
    """
    response = await graphql(
        """
        query getEvent($id: UUID!) {
            event(id: $id) {
                location
            }
        }
        """,
        creadentials=user,
        id=str(event.id),
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event", "created_date")
@pytest.mark.parametrize(
    "timezone", ["UTC", "America/New_York", "Australia/Sydney", "Europe/Moscow"]
)
async def test_event_created_date_with_timezone(user, event, created_date, timezone):
    """
    Test event location field

    Clients should not to be able to get or set location directly.
    """
    response = await graphql(
        """
        query getEvent($id: UUID!) {
            event(id: $id) {
                createdDate
                changedDate
            }
        }
        """,
        creadentials=user,
        cookies={"timezone": timezone},
        id=str(event.id),
    )

    assert response.status_code == 200
    timezoned_date = created_date.astimezone(pytz.timezone(timezone))
    timezoned_string = str(timezoned_date).replace(" ", "T")
    assert response.json()["data"]["event"]["createdDate"] == timezoned_string


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event", "changed_date")
@pytest.mark.parametrize(
    "timezone", ["UTC", "America/New_York", "Australia/Sydney", "Europe/Moscow"]
)
async def test_event_changed_date_with_timezone(user, event, changed_date, timezone):
    """
    Test event location field

    Clients should not to be able to get or set location directly.
    """
    response = await graphql(
        """
        query getEvent($id: UUID!) {
            event(id: $id) {
                createdDate
                changedDate
            }
        }
        """,
        creadentials=user,
        cookies={"timezone": timezone},
        id=str(event.id),
    )

    assert response.status_code == 200
    timezoned_date = changed_date.astimezone(pytz.timezone(timezone))
    timezoned_string = str(timezoned_date).replace(" ", "T")
    assert response.json()["data"]["event"]["changedDate"] == timezoned_string
