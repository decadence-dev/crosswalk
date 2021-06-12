import json

import pytest
from httpx import AsyncClient

import main


@pytest.mark.asyncio
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
        'First test description', 'Описание события', None,
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
async def test_success_create(name, type, description, address, location):
    async with AsyncClient(app = main.app, base_url = 'http://localhost:8000') as ac:
        body = {
            'name': name,
            'type': type,
            'description': description,
            'address': address,
            'location': location
        }
        response = await ac.post('/events', content=json.dumps(body))
        assert response.status_code == 200


@pytest.mark.asyncio
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
async def test_fail_create(name, type, description, address, location):
    async with AsyncClient(app=main.app, base_url='http://localhost:8000') as ac:
        body = {
            'name': name,
            'type': type,
            'description': description,
            'address': address,
            'location': location
        }
        response = await ac.post('/events', content=json.dumps(body))
        assert response.status_code == 422
