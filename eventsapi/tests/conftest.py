import pytest
from motor.motor_asyncio import AsyncIOMotorClient

import main


@pytest.fixture
async def collection():
    client = AsyncIOMotorClient(
        main.DATABASE_HOST, main.DATABASE_PORT, uuidRepresentation='standard'
    )
    yield client[main.DATABASE_NAME].events
    client.drop_database('test')
