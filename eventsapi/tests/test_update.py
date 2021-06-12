import json
import uuid

import pytest
from httpx import AsyncClient

import main
from models import Event, EventType, User, Location


@pytest.fixture
def name():
    return 'test'


@pytest.fixture
def type():
    return 'ROBBERY'


@pytest.fixture
def description():
    return 'description'


@pytest.fixture
def address():
    return 'address'


@pytest.fixture
def location():
    return [123, 321]


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
@pytest.mark.parametrize(
    'name', [
        'Значение с кирилицей',
        pytest.param('', marks=pytest.mark.xfail)
    ]
)
@pytest.mark.parametrize(
    'type', ['ROBBERY', 'FIGHT', 'DEATH', 'GUN', 'INADEQUATE', 'ACCEDENT', 'FIRE', 'POLICE']
)
@pytest.mark.parametrize(
    'description', [
        'Описание события', None,
        pytest.param('', marks=pytest.mark.xfail)
    ]
)
@pytest.mark.parametrize(
    'address', [
        'Ленина 12',
        pytest.param('', marks=pytest.mark.xfail)
    ]
)
@pytest.mark.parametrize(
    'location', [[123, 321], [1.23, 321.221]]
)
@pytest.mark.parametrize(
    'attachments', [
        [], None,
        pytest.param([None], marks=pytest.mark.xfail)
    ]
)
async def test_success_update(event, name, type, description, address, location, attachments):
    async with AsyncClient(app=main.app, base_url='http://localhost:8000') as ac:
        body = {
            'name': name,
            'type': type,
            'description': description,
            'address': address,
            'location': location,
            'attachments': attachments
        }
        response = await ac.patch(f'/events/{str(event.id)}', content=json.dumps(body))
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.usefixtures('event')
@pytest.mark.parametrize(
    'name', [None, 123, '']
)
@pytest.mark.parametrize(
    'type', ['Любое другое значение', None, 123, '']
)
@pytest.mark.parametrize(
    'description', [123, True]
)
@pytest.mark.parametrize(
    'address', [None, 123, '']
)
@pytest.mark.parametrize(
    'location', [None, 123, '', [None, 321], ['1.23', 321.221]]
)
async def test_fail_update(event, name, type, description, address, location):
    async with AsyncClient(app=main.app, base_url='http://localhost:8000') as ac:
        body = {
            'name': name,
            'type': type,
            'description': description,
            'address': address,
            'location': location
        }
        response = await ac.patch(f'/events/{str(event.id)}', content=json.dumps(body))
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.usefixtures('event')
async def test_not_found_update(name, type, description, address, location):
    async with AsyncClient(app=main.app, base_url='http://localhost:8000') as ac:
        body = {
            'name': name,
            'type': type,
            'description': description,
            'address': address,
            'location': location
        }
        response = await ac.patch(f'/events/{str(uuid.uuid4())}', content=json.dumps(body))
        assert response.status_code == 404
