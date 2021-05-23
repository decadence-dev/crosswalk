import pytest
from httpx import AsyncClient

import main
from models import Event, EventType, Location, User


@pytest.fixture
def limit():
    return 1


@pytest.fixture
def offset():
    return 100


@pytest.fixture
@pytest.mark.usefixtures('collection')
async def events(collection):
    def events_gen():
        for _ in range(200):
            yield Event(
                name='first',
                type=EventType.ROBBERY,
                user=User(name='testuser'),
                address='test_address',
                location=Location(coordinates=[12.3, 244.5])
            ).dict()
    await collection.insert_many(list(events_gen()))


@pytest.mark.asyncio
@pytest.mark.usefixtures('events')
@pytest.mark.parametrize(
    'limit', [1, 30, 100]
)
@pytest.mark.parametrize(
    'offset', [100, 180]
)
async def test_success_list(limit, offset):
    async with AsyncClient(app = main.app, base_url = 'http://localhost:8000') as ac:
        response = await ac.get("/events", params={'limit': limit, 'offset': offset})
        assert response.status_code == 200
        count = 200 - offset if 200 - offset < limit else limit
        assert len(response.json()) == count


@pytest.mark.asyncio
@pytest.mark.usefixtures('events')
@pytest.mark.parametrize(
    'limit', [None, -1]
)
@pytest.mark.parametrize(
    'offset', [None, -1]
)
async def test_fail_list(limit, offset):
    async with AsyncClient(app = main.app, base_url = 'http://localhost:8000') as ac:
        response = await ac.get("/events", params={'limit': limit, 'offset': offset})
        assert response.status_code == 422
