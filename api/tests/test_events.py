import random
import uuid
from datetime import datetime, timedelta

import pytest
from graphql_relay import to_global_id

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
    return '!@someTest_address'


@pytest.fixture
async def event_global_id(event_id):
    return to_global_id("Event", str(event_id))


@pytest.fixture
@pytest.mark.usefixtures(
    "db", "faker", "event_id", "event_address", "event_longitude", "event_latitude", "user"
)
async def event(db, faker, event_id, event_address, event_longitude, event_latitude, user):
    doc = {
        "id": event_id,
        "type": random.randrange(1, 8),
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
            yield {
                "id": uuid.uuid4(),
                "type": random.randrange(1, 8),
                "description": faker.text(),
                "address": f'address-{idx}',
                "location": {"type": "Point", "coordinates": [0, 0]},
                "created_by": user,
                "created_date": datetime.now() + timedelta(seconds=1 + idx),
                "changed_date": datetime.now() + timedelta(seconds=1 + idx),
            }

    _events = list(gen_events())
    collection = db.events
    await collection.insert_many(_events.copy())
    yield _events
    await collection.delete_many({"if": {"$in": [itm["id"] for itm in _events]}})


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user", 'event_address')
async def events_with_sprcific_address(db, faker, user, event_address):
    def gen_events():
        for idx in range(1, 21):
            yield {
                "id": uuid.uuid4(),
                "type": random.randrange(1, 8),
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
@pytest.mark.usefixtures("user", "events")
async def test_list(user):
    response = await graphql(
        """
        {
            events {
                edges {
                    node {
                        id
                    }
                }
            }
        }
        """,
        creadentials=user,
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["edges"]) == 100


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events", "events_with_sprcific_address")
@pytest.mark.parametrize(
    "variables,expected_count", [({}, 120), ({"search": '!@someTest_address'}, 20)]
)
async def test_list_search(user, variables, expected_count):
    response = await graphql(
        """
        query fetchEvents ($search: String) {
            events (search: $search) {
                edges {
                    node {
                        id
                    }
                }
            }
        }
        """,
        creadentials=user,
        **variables,
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["edges"]) == expected_count


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_events_order(user):
    response = await graphql(
        """
        {
            events {
                edges {
                    node {
                        address
                    }
                }
            }
        }
        """,
        creadentials=user,
    )

    assert response.status_code == 200
    events = response.json()["data"]["events"]["edges"]
    max_address = max(map(lambda itm: itm["node"]["address"], events))
    assert events[0]["node"]["address"] == max_address


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    "user",
    "event_global_id",
    "event_longitude",
    "event_latitude",
    "event",
)
async def test_retrieve(
    user, event_global_id, event_longitude, event_latitude
):
    response = await graphql(
        """
        query getEvent($id: ID!) {
            event(id: $id) {
                id
                longitude
                latitude
            }
        }
        """,
        creadentials=user,
        id=event_global_id,
    )

    assert response.status_code == 200
    assert response.json()["data"]["event"]["longitude"] == event_longitude
    assert response.json()["data"]["event"]["latitude"] == event_latitude


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "type": "ROBBERY",
                "address": "some address",
                "longitude": 1,
                "latitude": 2,
            },
            {
                "data": {
                    "createEvent": {
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
            $type: EventType!,
            $address: String!,
            $longitude: Float!,
            $latitude: Float!
        ) {
            createEvent (
                input: {
                    type: $type,
                    address: $address,
                    longitude: $longitude
                    latitude: $latitude
                }
            ) {
                address
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
    [({"address": "Updated event"}, {"data": {"updateEvent": {"address": "Updated event"}}})],
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
