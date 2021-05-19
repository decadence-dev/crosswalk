import os
import uuid
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from schemas import User, Reaction, ReactionCreate, ReactionType


app = FastAPI()

client: AsyncIOMotorClient = None


async def get_client():
    return client


async def get_user():
    return User(
        id=uuid.UUID("a6f974d2-7823-44ba-b5d6-d0c5a0399a28"),
        name='mockuser'
    )


@app.on_event('startup')
async def startup():
    global client
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', 27017)
    client = AsyncIOMotorClient(DATABASE_HOST, DATABASE_PORT, uuidRepresentation='standard')


@app.on_event('shutdown')
def shutdown():
    client.close()


@app.get('/types', response_model=List[str])
async def list_types():
    return list(ReactionType)


@app.get('/events/{pk}/summary', response_model=int)
async def event_summary(
        pk: uuid.UUID,
        client: AsyncIOMotorClient = Depends(get_client)
):
    positive_count = await client.reactions.reactions.count_documents({
        'event': pk,
        'type': ReactionType.POSITIVE.value
    })
    negative_count = await client.reactions.reactions.count_documents({
        'event': pk,
        'type': ReactionType.NEGATIVE.value
    })
    return positive_count - negative_count


@app.post('/events/{pk}/toggle', response_model=int)
async def toggle_reaction(
        pk: uuid.UUID,
        data: ReactionCreate,
        user: User = Depends(get_user),
        client: AsyncIOMotorClient = Depends(get_client)
):
    positive_count = await client.reactions.reactions.count_documents({
        'event': pk,
        'type': ReactionType.POSITIVE
    })
    negative_count = await client.reactions.reactions.count_documents({
        'event': pk,
        'type': ReactionType.NEGATIVE
    })

    summary = positive_count - negative_count
    reaction_value = 1 if data.type == ReactionType.POSITIVE else -1
    reaction_db = await client.reactions.reactions.find_one({
        'event': pk,
        'user.id': user.id
    })

    if reaction_db is None:
        instance = Reaction(event=pk, type=data.type, user=user)
        await client.reactions.reactions.insert_one(instance.dict())
        return summary + reaction_value

    reaction = Reaction(**reaction_db)
    if reaction.type == data.type:
        await client.reactions.reactions.delete_one({'id': reaction.id})
        return summary + reaction_value * -1
    else:
        await client.reactions.reactions.update_one(
            {'id': reaction.id},
            {'$set': {
                'type': ReactionType.NEGATIVE if reaction.type == ReactionType.POSITIVE else ReactionType.POSITIVE,
                'changed': datetime.now()
            }}
        )
        return summary + reaction_value * 2
