import random
import uuid
from datetime import datetime

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
async def event_global_id(event_id):
    return to_global_id("Event", str(event_id))


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "event_id", "event_name", "user")
async def event(db, faker, event_id, event_name, user):
    doc = {
        "id": event_id,
        "name": event_name,
        "type": random.randrange(1, 8),
        "description": faker.text(),
        "address": faker.address(),
        "location": [0, 0],
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
        for _ in range(100):
            yield {
                "id": uuid.uuid4(),
                "name": faker.name(),
                "type": random.randrange(1, 8),
                "description": faker.text(),
                "address": faker.address(),
                "location": [0, 0],
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
@pytest.mark.usefixtures("user", "event_global_id", "event_name", "event")
async def test_retrieve(user, event_global_id, event_name):
    response = await graphql(
        """
        query getEvent($id: ID!) {
            event(id: $id) {
                id
                name   
            }
        }
        """,
        creadentials=user,
        id=event_global_id,
    )

    assert response.status_code == 200
    assert response.json()["data"]["event"]["name"] == event_name


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "name": "New event",
                "type": "ROBBERY",
                "address": "some address",
                "location": [1, 2],
            },
            {"data": {"createEvent": {"name": "New event"}}},
        )
    ],
)
async def test_create(db, user, input, result):
    response = await graphql(
        """
        mutation createEvent($name: String!, $type: EventType!, $address: String!, $location: [Float!]!) {
            createEvent (input: {name: $name, type: $type, address: $address, location: $location}) {
                name
            }
        }
        """,
        creadentials=user,
        **input
    )

    assert response.status_code == 200
    assert response.json() == result

    doc = await db.events.find_one({}, {"_id": 0, "events": 1, "name": 1, "value": 1})
    assert "New event" == doc["name"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user", "event_global_id", "event")
@pytest.mark.parametrize(
    "input,result",
    [({"name": "Updated event"}, {"data": {"updateEvent": {"name": "Updated event"}}})],
)
async def test_update(db, user, event_global_id, input, result):
    response = await graphql(
        """
        mutation updateEvent($id: ID!, $name: String) {
            updateEvent (input: {id: $id, name: $name}) {
                name
            }
        }
        """,
        creadentials=user,
        id=event_global_id,
        **input
    )

    assert response.status_code == 200
    assert response.json() == result

    doc = await db.events.find_one({}, {"_id": 0, "events": 1, "name": 1, "value": 1})
    assert "Updated event" == doc["name"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user", "event_name", "event_global_id", "event")
async def test_delete(db, user, event_name, event_global_id):
    response = await graphql(
        """
        mutation deleteEvent($id: ID!) {
            deleteEvent (input: {id: $id}) {
                name
            }
        }
        """,
        creadentials=user,
        id=event_global_id,
    )

    assert response.status_code == 200
    assert response.json()["data"]["deleteEvent"]["name"] == event_name

    doc = await db.events.find_one({}, {"_id": 0, "events": 1, "name": 1, "value": 1})
    assert not doc
