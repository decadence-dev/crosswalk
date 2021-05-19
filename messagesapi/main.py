import os
import re
import uuid
from typing import Optional, List

from fastapi import FastAPI, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient

from models import Message

app = FastAPI()

client: AsyncIOMotorClient = None


async def get_client():
    return client


@app.on_event('startup')
async def startup():
    global client
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', 27017)
    client = AsyncIOMotorClient(DATABASE_HOST, DATABASE_PORT, uuidRepresentation='standard')


@app.on_event('shutdown')
async def shutdown():
    await client.close()


def ignoremptypipes(*pipelines):
    def get_pipeline_value(pipeline):
        for key, value in pipeline.items():
            if isinstance(value, dict):
                value = get_pipeline_value(value)
            return value

    for pipeline in pipelines:
        value = get_pipeline_value(pipeline)
        if value is not None:
            if isinstance(value, re.Pattern) and value.pattern == '.*None.*':
                continue
            yield pipeline


@app.get('/messages/{event_pk}', response_model=List[Message])
async def list_messages(
        event_pk: uuid.UUID,
        client=Depends(get_client),
        parent: Optional[List[uuid.UUID]]=Query(None),
):
    pipelines = list(
        ignoremptypipes(
            {'$match': {'event': event_pk}},
            {'$match': {'parent': {'$in': parent}}}
        )
    )
    collectiion = client.messages.messages.aggregate(pipelines)
    return [Message(**doc) async for doc in collectiion]
