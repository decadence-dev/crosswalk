import random
import uuid
from datetime import datetime, timedelta

import pytest
from graphql_relay import to_global_id

from models import EventType, Event
from tests.utils import graphql


@pytest.fixture
async def event_id():
    return uuid.uuid4()


@pytest.fixture
@pytest.mark.usefixtures("faker")
async def event_name(faker):
    return faker.name()


@pytest.fixture
async def event_longitude():
    return 0


@pytest.fixture
async def event_latitude():
    return 0


@pytest.fixture
async def event_address():
    return "!@someTest_address"


@pytest.fixture
async def event_global_id(event_id):
    return to_global_id("Event", str(event_id))


@pytest.fixture
@pytest.mark.usefixtures(
    "db",
    "faker",
    "event_id",
    "event_address",
    "event_longitude",
    "event_latitude",
    "user",
)
async def event(
    db, faker, event_id, event_address, event_longitude, event_latitude, user
):
    doc = {
        "id": event_id,
        "event_type": random.randrange(1, 8),
        "description": faker.text(),
        "address": event_address,
        "location": {"type": "Point", "coordinates": [event_longitude, event_latitude]},
        "created_by": user,
        "created_date": datetime.now(),
        "changed_date": datetime.now(),
    }
    await db.events.insert_one(doc.copy())
    yield doc
    await db.events.delete_one({"id": event_id})


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user")
async def events(db, faker, user):
    def gen_events():
        for idx in range(0, 100):
            yield Event(
                event_type=faker.random_element(EventType),
                description=faker.text(),
                address=faker.address(),
                location={"type": "Point", "coordinates": faker.latlng()},
                created_by=user,
                created_date=faker.date_time(),
                changed_date=faker.date_time()
            ).dict()

    _events = list(gen_events())
    import ipdb; ipdb.set_trace()
    collection = db.events
    await collection.insert_many(_events.copy())
    yield _events
    await collection.delete_many({"if": {"$in": [itm["id"] for itm in _events]}})


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user", "event_address")
async def events_with_sprcific_address(db, faker, user, event_address):
    def gen_events():
        for idx in range(1, 21):
            yield {
                "id": uuid.uuid4(),
                "event_type": random.randrange(1, 8),
                "description": faker.text(),
                "address": event_address,
                "location": {"type": "Point", "coordinates": [0, 0]},
                "created_by": user,
                "created_date": datetime.now(),
                "changed_date": datetime.now(),
            }

    _events = list(gen_events())
    collection = db.events
    await collection.insert_many(_events.copy())
    yield _events
    await collection.delete_many({"if": {"$in": [itm["id"] for itm in _events]}})





@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "eventType": "ROBBERY",
                "address": "some address",
                "longitude": 1,
                "latitude": 2,
            },
            {
                "data": {
                    "createEvent": {
                        "eventType": "ROBBERY",
                        "address": "some address",
                        "createdBy": {"username": "mockuser"},
                        "longitude": 1.0,
                        "latitude": 2.0,
                    }
                }
            },
        )
    ],
)
async def test_create(db, user, input, result):
    response = await graphql(
        """
        mutation createEvent(
            $eventType: EventType!,
            $address: String!,
            $longitude: Float!,
            $latitude: Float!
        ) {
            createEvent (
                input: {
                    eventType: $eventType,
                    address: $address,
                    longitude: $longitude
                    latitude: $latitude
                }
            ) {
                address
                eventType
                longitude
                latitude
                createdBy {
                    username
                }
            }
        }
        """,
        creadentials=user,
        **input,
    )

    assert response.status_code == 200
    assert response.json() == result

    doc = await db.events.find_one({}, {"_id": 0, "events": 1, "address": 1})
    assert doc["address"] == "some address"


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user", "event_global_id", "event")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {"address": "Updated event"},
            {"data": {"updateEvent": {"address": "Updated event"}}},
        )
    ],
)
async def test_update(db, user, event_global_id, input, result):
    response = await graphql(
        """
        mutation updateEvent($id: ID!, $address: String) {
            updateEvent (input: {id: $id, address: $address}) {
                address
            }
        }
        """,
        creadentials=user,
        id=event_global_id,
        **input,
    )

    assert response.status_code == 200
    assert response.json() == result

    doc = await db.events.find_one({}, {"_id": 0, "events": 1, "address": 1})
    assert doc["address"] == "Updated event"


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user", "event_address", "event_global_id", "event")
async def test_delete(db, user, event_address, event_global_id):
    response = await graphql(
        """
        mutation deleteEvent($id: ID!) {
            deleteEvent (input: {id: $id}) {
                address
            }
        }
        """,
        creadentials=user,
        id=event_global_id,
    )

    assert response.status_code == 200
    assert response.json()["data"]["deleteEvent"]["address"] == event_address

    doc = await db.events.find_one({}, {"_id": 0, "events": 1, "address": 1})
    assert not doc
