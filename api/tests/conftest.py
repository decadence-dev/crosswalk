import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from main import settings


@pytest.fixture
async def user():
    return {"id": "00000000-0000-0000-0000-000000000000", "username": "mockuser"}


@pytest.fixture
async def db():
    client = AsyncIOMotorClient(
        settings.database_host, settings.database_port, uuidRepresentation="standard"
    )
    yield client[settings.database_name]
    client.drop_database("test")
