import os
import re
import uuid
from typing import Optional, List

from fastapi import FastAPI, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from models import Message, MessageCreate, MessageUpdate, User


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


async def get_user():
    return User(
        id=uuid.uuid4(),
        name='mockuser'
    )


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


@app.get('/events/{pk}/messages', response_model=List[Message])
async def list_messages(
        pk: uuid.UUID,
        is_root: Optional[bool] = False,
        client: AsyncIOMotorClient = Depends(get_client),
        parent: Optional[List[uuid.UUID]]=Query(None)
):
    pipelines = [{'$match': {'parent': None if is_root else {'$ne': None}}}]
    pipelines += list(
        ignoremptypipes(
            {'$match': {'event': pk}},
            {'$match': {'parent': {'$in': parent}}},
        ),
    )
    collectiion = client.messages.messages.aggregate(pipelines)
    return [Message(**doc) async for doc in collectiion]


@app.post('/events/{pk}/messages', response_model=Message)
async def create_message(
        pk: uuid.UUID,
        data: MessageCreate,
        client: AsyncIOMotorClient = Depends(get_client),
        user: User = Depends(get_user)
):
    message = Message(
        **data.dict(),
        event=pk,
        user=user
    )
    await client.messages.messages.insert_one(message.dict())
    return message


@app.get('/messages/{pk}', response_model=Message)
async def retrieve_message(
        pk: uuid.UUID,
        client: AsyncIOMotorClient = Depends(get_client)
):
    doc = await client.messages.messages.find_one({'id': pk})
    return Message(**doc)


@app.patch('/messages/{pk}', response_model=Message)
async def update_message(
        pk: uuid.UUID,
        data: MessageUpdate,
        client: AsyncIOMotorClient = Depends(get_client)
):
    doc = await client.messages.messages.find_one({'id': pk})
    if doc is None:
        raise HTTPException(status_code=404, detail='Message not found')
    instance = Message(**doc)
    updated = instance.copy(
        update=data.dict(exclude_unset=True, exclude_none=True)
    )
    await client.messages.messages.update_one({'id': pk}, {'$set': updated.dict()})
    return updated


@app.delete('/messages/{pk}')
async def delete_message(
        pk: uuid.UUID,
        client: AsyncIOMotorClient = Depends(get_client)
):
    doc = await client.messages.messages.find_one({'id': pk})
    if doc is None:
        raise HTTPException(status_code=404, detail='Message not found')
    await client.messages.messages.delete_one({'id': pk})
    return 'Ok'
