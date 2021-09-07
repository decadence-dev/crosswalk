import uuid
from enum import Enum

import graphene
from graphene import relay

from pagination import SlicelessConnectionField, gen_slice_pipeline


class EventType(Enum):
    ROBBERY = 1
    FIGHT = 2
    DEATH = 3
    GUN = 4
    INADEQUATE = 5
    ACCEDENT = 6
    FIRE = 7
    POLICE = 8


class User(graphene.ObjectType):
    id = graphene.UUID(required=True)
    name = graphene.String(required=True)


class Event(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    name = graphene.String()
    type = graphene.Int()
    description = graphene.String()

    address = graphene.String()
    location = graphene.List(graphene.Float)

    created_by = graphene.Field(User)
    created_date = graphene.DateTime()
    changed_date = graphene.DateTime()

    @staticmethod
    async def get_node(info, id):
        collection = info.context["db"].events
        doc = await collection.find_one({"id": uuid.UUID(id)}, {"_id": 0})
        return doc


class EventConnection(relay.Connection):
    class Meta:
        node = Event


class EventTypeMap(graphene.ObjectType):
    name = graphene.String()
    value = graphene.Int()


class Query(graphene.ObjectType):
    event = relay.Node.Field(Event)
    events = SlicelessConnectionField(EventConnection)
    types = graphene.List(EventTypeMap)

    @staticmethod
    async def resolve_events(root, info, **kwargs):
        collection = info.context["db"].events
        cursor = collection.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "count": {"$sum": 1},
                        "docs": {"$push": "$$ROOT"},
                    }
                },
                *gen_slice_pipeline("docs", "count", **kwargs),
                {"$project": {"_id": 0, "docs._id": 0}},
            ]
        )
        return await cursor.next() if await cursor.fetch_next else None

    @staticmethod
    async def resolve_types(root, info, **kwargs):
        return EventType
