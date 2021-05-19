import os
import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from models import Event, EventType, EventUpdate, EventCreate


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
    client.close()


@app.get('/types', response_model=List[str])
async def list_types():
    return list(EventType)


@app.get('/events', response_model=List[Event])
async def list_events(client=Depends(get_client)):
    collection = client.events.events.aggregate([])
    return [Event(**itm) async for itm in collection]


@app.post('/events', response_model=Event)
async def created_event(event_data: EventCreate, client=Depends(get_client)):
    event = Event.parse_obj(event_data)
    await client.events.events.insert_one(event.dict())
    return event


@app.get('/events/{pk}', response_model=Event)
async def retrieve_event(pk: uuid.UUID, client=Depends(get_client)):
    doc = await client.events.events.find_one({'id': pk})
    return Event(**doc)


@app.patch('/events/{pk}', response_model=Event)
async def update_event(pk: uuid.UUID, event_data: EventUpdate, client=Depends(get_client)):
    doc = await client.events.events.find_one({'id': pk})
    if doc is None:
        raise HTTPException(status_code=404, detail='Event not found')
    instance = Event(**doc)
    updated = instance.copy(update=event_data.dict(exclude_unset=True))
    await client.events.events.update_one({'id': pk}, {'$set': updated.dict()})
    return updated


@app.delete('/events/{pk}')
async def delete_event(pk: uuid.UUID, client=Depends(get_client)):
    doc = await client.events.events.find_one({'id': pk})

    if doc is None:
        raise HTTPException(status_code=404, detail='Event not found')
    await client.events.events.delete_one({'id': pk})
    return 'Ok'
