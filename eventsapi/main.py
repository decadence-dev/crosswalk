import os
import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pydantic.types import conint

from models import Event, EventType, EventUpdate, EventCreate, User


DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', 27017)
DATABASE_NAME = os.getenv('DATABASE_NAME', 'crosswalk')


app = FastAPI()


async def get_collection():
    client = AsyncIOMotorClient(DATABASE_HOST, DATABASE_PORT, uuidRepresentation='standard')
    yield client[DATABASE_NAME].events
    client.close()


async def get_user():
    return User(
        id=uuid.uuid4(),
        name='mockuser'
    )


@app.get('/types', response_model=List[str])
async def list_types():
    return list(EventType)


@app.get('/events', response_model=List[Event])
async def list_events(
        limit: conint(ge=0) = 100,
        offset: conint(ge=0) = 0,
        collection: AsyncIOMotorCollection = Depends(get_collection)
):
    cursor = collection.aggregate([
        {'$skip': offset},
        {'$limit': limit}
    ])
    return [Event(**itm) async for itm in cursor]


@app.post('/events', response_model=Event)
async def create_event(
        data: EventCreate,
        collection: AsyncIOMotorCollection = Depends(get_collection),
        user: User = Depends(get_user)
):
    instance = Event(
        **data.dict(),
        created_by=user,
        changed_by=user
    )
    await collection.insert_one(instance.dict())
    return instance


@app.get('/events/{pk}', response_model=Event)
async def retrieve_event(
        pk: uuid.UUID,
        collection: AsyncIOMotorCollection = Depends(get_collection)
):
    doc = await collection.find_one({'id': pk})
    if doc is None:
        raise HTTPException(status_code=404, detail='Event not found')
    return Event(**doc)


@app.patch('/events/{pk}', response_model=Event)
async def update_event(
        pk: uuid.UUID,
        data: EventUpdate,
        collection: AsyncIOMotorCollection = Depends(get_collection),
        user: User = Depends(get_user)
):
    doc = await collection.find_one({'id': pk})
    if doc is None:
        raise HTTPException(status_code=404, detail='Event not found')
    doc.update(data.dict(exclude_unset=True), changed_by=user)
    instance = Event(**doc)
    await collection.update_one({'id': pk}, {'$set': instance.dict()})
    return instance


@app.delete('/events/{pk}')
async def delete_event(
        pk: uuid.UUID,
        collection: AsyncIOMotorCollection = Depends(get_collection)
):
    doc = await collection.find_one({'id': pk})

    if doc is None:
        raise HTTPException(status_code=404, detail='Event not found')
    await collection.delete_one({'id': pk})
    return 'Ok'
