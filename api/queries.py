import re
import uuid

import graphene
import pytz
from graphene import relay

from pagination import MotorConnectionField


def get_event_projection():
    return {
        "id": 1,
        "_id": 0,
        "name": 1,
        "event_type": 1,
        "description": 1,
        "address": 1,
        "created_by": 1,
        "created_date": 1,
        "changed_date": 1,
        "longitude": {"$arrayElemAt": ["$location.coordinates", 0]},
        "latitude": {"$arrayElemAt": ["$location.coordinates", -1]},
    }


class EventType(graphene.Enum):
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
    username = graphene.String(required=True)


class Event(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    event_type = graphene.Field(type=EventType)
    description = graphene.String()

    address = graphene.String()
    longitude = graphene.Float()
    latitude = graphene.Float()

    created_by = graphene.Field(User)
    created_date = graphene.DateTime()
    changed_date = graphene.DateTime()

    @staticmethod
    async def get_node(info, id):
        collection = info.context["db"].events
        doc = await collection.find_one({"id": uuid.UUID(id)}, get_event_projection())
        return Event(**doc)

    @staticmethod
    async def resolve_created_date(root, info, **kwargs):
        timezone = pytz.timezone(info.context["timezone"])
        return (
            root.created_date.astimezone(timezone)
            if root.created_date is not None
            else None
        )

    @staticmethod
    async def resolve_changed_date(root, info, **kwargs):
        timezone = pytz.timezone(info.context["timezone"])
        return (
            root["changed_date"].astimezone(timezone)
            if "changed_date" in root
            else None
        )


class EventConnection(relay.Connection):
    class Meta:
        node = Event


class Query(graphene.ObjectType):
    event = relay.Node.Field(Event)
    events = MotorConnectionField(EventConnection, search=graphene.String())

    @staticmethod
    async def resolve_events(root, info, **kwargs):
        filter = {}
        if value := kwargs.get("search"):
            # TODO replace filter with mongo text index
            pattern = re.compile(f".*{value}.*", re.IGNORECASE)
            filter.update({"address": pattern})

        collection = info.context["db"].events
        count = await collection.count_documents(filter)
        cursor = collection.find(filter, get_event_projection()).sort(
            [("created_date", -1)]
        )
        return cursor, count
