import uuid

import pytest
from httpx import AsyncClient

import main
from models import Event, EventType, User, Location


@pytest.fixture
@pytest.mark.usefixtures('collections')
async def event(collection):
    instance = Event(
        name='first',
        type=EventType.ROBBERY,
        user=User(name='testuser'),
        address='test_address',
        location=Location(coordinates=[12.3, 244.5])
    )
    await collection.insert_one(instance.dict())
    return instance


@pytest.mark.asyncio
@pytest.mark.usefixtures('event')
async def test_success_retrieve(event):
    async with AsyncClient(app=main.app, base_url='http://localhost:8000') as ac:
        response = await ac.get(f'/events/{str(event.id)}')
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.usefixtures('event')
async def test_not_found_retrieve():
    async with AsyncClient(app=main.app, base_url='http://localhost:8000') as ac:
        response = await ac.get(f'/events/{str(uuid.uuid4())}')
        assert response.status_code == 404

