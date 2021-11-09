import re

import graphene
import pytz
from graphene import relay

from models import EventType, Event as EventModel

from settings import settings


SchemaEventType = graphene.Enum.from_enum(EventType)


class User(graphene.ObjectType):
    id = graphene.UUID(required=True)
    username = graphene.String(required=True)


class Event(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    event_type = graphene.Field(type=SchemaEventType)
    description = graphene.String()

    address = graphene.String()
    longitude = graphene.Float()
    latitude = graphene.Float()

    created_by = graphene.Field(User)
    created_date = graphene.DateTime()
    changed_date = graphene.DateTime()

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
            root.changed_date.astimezone(timezone)
            if root.changed_date is not None
            else None
        )


class EventsCollection(graphene.ObjectType):
    count = graphene.Int(default_value=0)
    has_next = graphene.Boolean(default_value=False)
    items = graphene.List(Event, default_value=[])


class Query(graphene.ObjectType):
    event = graphene.Field(Event, id=graphene.UUID(required=True))
    events = graphene.Field(
        EventsCollection, limit=graphene.Int(default_value=settings.global_limit), offset=graphene.Int(default_value=0), search=graphene.String()
    )

    @staticmethod
    async def resolve_event(root, info, id):
        collection = info.context["db"].events
        doc = await collection.find_one({"id": id})
        return EventModel(**doc)

    @staticmethod
    async def resolve_events(root, info, **kwargs):
        # Creating filter for documents counting
        query = {}
        if search := kwargs.get("search"):
            # TODO replace filter with mongo text index
            pattern = re.compile(f".*{search}.*", re.IGNORECASE)
            query.update({'address': pattern})

        # Creating pipelines from query for documents filtering
        pipelines = [{'$match': {key: value}} for key, value in query.items()]

        # Updating pipelines with limit, offset and sort aggregations
        if offset := kwargs.get('offset'):
            if offset < 0:
                raise ValueError('Offset cannot be negative')
            pipelines.append({'$skip': offset})
        if limit := kwargs.get('limit'):
            if limit < 0:
                raise ValueError('Limit cannot be negative')
            pipelines.append({'$limit': limit})
        pipelines.append({'$sort': {'changed_date': -1}})

        collection = info.context["db"].events
        count = await collection.count_documents(query)
        cursor = collection.aggregate(pipelines)

        return EventsCollection(
            count=count,
            has_next=offset + limit < count and limit != 0,
            items=[EventModel(**doc) async for doc in cursor]
        )
