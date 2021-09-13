import pytest
from motor.motor_asyncio import AsyncIOMotorClient

import main


@pytest.fixture
async def user():
    return {"id": "00000000-0000-0000-0000-000000000000", "username": "mockuser"}


@pytest.fixture
async def db():
    client = AsyncIOMotorClient(
        main.DATABASE_HOST, main.DATABASE_PORT, uuidRepresentation="standard"
    )
    yield client[main.DATABASE_NAME]
    client.drop_database("test")
