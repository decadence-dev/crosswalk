import re

import graphene

from models import Event as EventModel
from models import EventType
from settings import settings
from utils import astimezone

SchemaEventType = graphene.Enum.from_enum(EventType)


class User(graphene.ObjectType):
    id = graphene.UUID(required=True)
    username = graphene.String(required=True)


class Event(graphene.ObjectType):
    id = graphene.UUID()
    event_type = graphene.Field(type=SchemaEventType)
    description = graphene.String()

    address = graphene.String()
    longitude = graphene.Float()
    latitude = graphene.Float()

    created_by = graphene.Field(User)
    created_date = graphene.DateTime()
    changed_date = graphene.DateTime()

    @staticmethod
    async def resolve_created_date(parent, info, **kwargs):
        return astimezone(parent.created_date, info.context["timezone"])

    @staticmethod
    async def resolve_changed_date(parent, info, **kwargs):
        return astimezone(parent.changed_date, info.context["timezone"])


class EventsCollection(graphene.ObjectType):
    count = graphene.Int(default_value=0)
    has_next = graphene.Boolean(default_value=False)
    items = graphene.List(Event, default_value=[])


class Query(graphene.ObjectType):
    event = graphene.Field(Event, id=graphene.UUID(required=True))
    events = graphene.Field(
        EventsCollection,
        limit=graphene.Int(default_value=settings.global_limit),
        offset=graphene.Int(default_value=0),
        search=graphene.String(),
    )

    @staticmethod
    async def resolve_event(parent, info, id):
        collection = info.context["db"].events
        doc = await collection.find_one({"id": id})
        return EventModel(**doc)

    @staticmethod
    async def resolve_events(parent, info, **kwargs):
        # Creating filter for documents counting
        query = {}
        if search := kwargs.get("search"):
            # TODO replace filter with mongo text index
            pattern = re.compile(f".*{search}.*", re.IGNORECASE)
            query.update({"address": pattern})

        # Creating pipelines from query for documents filtering
        pipelines = [{"$match": {key: value}} for key, value in query.items()]

        # Updating pipelines with limit, offset and sort aggregations
        pipelines.append({"$sort": {"changed_date": -1}})
        if offset := kwargs.get("offset"):
            if offset < 0:
                raise ValueError("Offset cannot be negative")
            pipelines.append({"$skip": offset})
        if limit := kwargs.get("limit"):
            # TODO to limit maximum "limit" with global value
            if limit < 0:
                raise ValueError("Limit cannot be negative")
            pipelines.append({"$limit": limit})

        collection = info.context["db"].events
        count = await collection.count_documents(query)
        cursor = collection.aggregate(pipelines)

        return EventsCollection(
            count=count,
            has_next=offset + limit < count and limit != 0,
            items=[EventModel(**doc) async for doc in cursor],
        )
