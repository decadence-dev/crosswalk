from datetime import datetime

import pytest

from models import Event, EventType
from tests.utils import graphql


@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user")
async def events(db, faker, user):
    collection = db.events
    result = await collection.insert_many(
        map(
            lambda itm: Event(
                event_type=faker.random_element(EventType),
                description=faker.text(),
                address=faker.address(),
                location={"type": "Point", "coordinates": faker.latlng()},
                created_by=user,
                created_date=faker.date_time(),
                changed_date=faker.date_time()
            ).dict(),
            range(0, 100)
        )
    )
    yield result.inserted_ids
    await collection.delete_many({"id": {"$in": result.inserted_ids}})


@pytest.fixture
@pytest.mark.usefixtures('db', 'faker', 'user')
async def iwakura_events(db, faker, user):
    collection = db.events
    result = await collection.insert_many(
        map(
            lambda itm: Event(
                event_type=faker.random_element(EventType),
                description=faker.text(),
                address='Iwakura',
                location={"type": "Point", "coordinates": faker.latlng()},
                created_by=user,
                created_date=faker.date_time(),
                changed_date=faker.date_time()
            ).dict(),
            range(0, 10)
        )
    )
    yield result.inserted_ids
    await collection.delete_many({"id": {"$in": result.inserted_ids}})


@pytest.fixture
@pytest.mark.usefixtures('db', 'faker', 'user')
async def february_events(db, faker, user):
    docs = [
        {
            "event_type": faker.random_element(EventType),
            "description": faker.text(),
            "address": 'Iwakura',
            "location": {"type": "Point", "coordinates": faker.latlng()},
            "created_by": user,
            "created_date": faker.date_time(),
            "changed_date": datetime.strptime('01.02.2030', '%d.%m.%Y')
        },
        {
            "event_type": faker.random_element(EventType),
            "description": faker.text(),
            "address": 'Inazawa',
            "location": {"type": "Point", "coordinates": faker.latlng()},
            "created_by": user,
            "created_date": faker.date_time(),
            "changed_date": datetime.strptime('16.02.2030', '%d.%m.%Y')
        },
        {
            "event_type": faker.random_element(EventType),
            "description": faker.text(),
            "address": 'Nagakute',
            "location": {"type": "Point", "coordinates": faker.latlng()},
            "created_by": user,
            "created_date": faker.date_time(),
            "changed_date": datetime.strptime('24.02.2030', '%d.%m.%Y')
        }
    ]
    collection = db.events
    result = await collection.insert_many(
        map(lambda doc: Event(**doc).dict(), docs)
    )
    yield result.inserted_ids
    await collection.delete_many({"id": {"$in": result.inserted_ids}})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'limit', (None, 0, 110)
)
@pytest.mark.usefixtures("user", "events", 'limit')
async def test_list_unlimited_query(user, limit):
    response = await graphql(
        """
        query fetchEventsWithNoLimits($limit: Int) {
            events(limit: $limit) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        limit=limit
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 100
    assert response.json()["data"]["events"]["count"] == 100
    assert response.json()["data"]["events"]["hasNext"] == False


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_with_limit_10(user):
    response = await graphql(
        """
        query fetchFirstTenEvents($limit: Int) {
            events(limit: $limit) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        limit=10
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 10
    assert response.json()["data"]["events"]["count"] == 100
    assert response.json()["data"]["events"]["hasNext"] == True


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_with_negative_limit(user):
    response = await graphql(
        """
        query fetchLastTenEvents($limit: Int) {
            events(limit: $limit) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        limit=-10
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_with_offset_10(user):
    response = await graphql(
        """
        query fetchWithFirstTenEventsSkip($offset: Int) {
            events(offset: $offset) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        offset=10
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 90
    assert response.json()["data"]["events"]["count"] == 100
    assert response.json()["data"]["events"]["hasNext"] == False


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_with_offset_110(user):
    response = await graphql(
        """
        query fetchWithAllEventsSkip($offset: Int) {
            events(offset: $offset) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        offset=110
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 0
    assert response.json()["data"]["events"]["count"] == 100
    assert response.json()["data"]["events"]["hasNext"] == False


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_with_negative_offset(user):
    response = await graphql(
        """
        query fetchWithLastTenEventsSkip($offset: Int) {
            events(offset: $offset) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        offset=-10
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_from_the_middle(user):
    response = await graphql(
        """
        query fetchThirdPageEvents($offset: Int, $limit: Int) {
            events(offset: $offset, limit: $limit) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        offset=20,
        limit=10
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 10
    assert response.json()["data"]["events"]["count"] == 100
    assert response.json()["data"]["events"]["hasNext"] == True


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events")
async def test_list_query_from_the_end(user):
    response = await graphql(
        """
        query fetchLastPageEvents($offset: Int, $limit: Int) {
            events(offset: $offset, limit: $limit) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        offset=95,
        limit=10
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 5
    assert response.json()["data"]["events"]["count"] == 100
    assert response.json()["data"]["events"]["hasNext"] == False


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events", 'iwakura_events')
@pytest.mark.parametrize(
    'address', ['iwakura', 'iwa', 'Iwakura', 'IwaKUrA']
)
async def test_search(user, address):
    """
    Test search with Iwakura events with addres in different uppercases

    Response items and count should be limited by Iwakura only events,
    because only 10 of events in database places in Iwakura city.
    """
    response = await graphql(
        """
        query fetchIwakuraEvents($search: String) {
            events(search: $search) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        search=address
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 10
    assert response.json()["data"]["events"]["count"] == 10
    assert response.json()["data"]["events"]["hasNext"] == False


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "events", 'iwakura_events')
@pytest.mark.parametrize(
    'address', ['yuzawa', 'awa', 'Yuzawa', 'yUZaWa']
)
async def test_search_with_undexsisting_address(user, address):
    """
    Test search with Yuzawa events with addres in different uppercases

    Response should not contain aly events,
    because in database we don't any events in Yuzawa.
    """
    response = await graphql(
        """
        query fetchYuzawaEvents($search: String) {
            events(search: $search) {
                count
                hasNext
                items {
                    id
                }
            }
        }
        """,
        creadentials=user,
        search=address
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["events"]["items"]) == 0
    assert response.json()["data"]["events"]["count"] == 0
    assert response.json()["data"]["events"]["hasNext"] == False


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "february_events")
async def test_sort(user):
    response = await graphql(
        """
        {
            events {
                items {
                    address
                }
            }
        }
        """,
        creadentials=user
    )

    assert response.status_code == 200
    items  = [itm['address'] for itm in response.json()["data"]["events"]["items"]]
    assert ['Nagakute', 'Inazawa', 'Iwakura'] == items
