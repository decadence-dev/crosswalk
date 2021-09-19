import uuid
from datetime import datetime

import graphene
from graphene import relay
from graphql_relay import from_global_id

from queries import Event, EventType


def get_event_from_document(doc):
    longitude, latitude = doc["location"]["coordinates"]
    return Event(
        **{field: value for field, value in doc.items() if field != "location"},
        longitude=longitude,
        latitude=latitude,
    )


class CreateEventMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        type = graphene.Enum.from_enum(EventType)(required=True)
        description = graphene.String()

        address = graphene.String(required=True)
        longitude = graphene.Float(required=True)
        latitude = graphene.Float(required=True)

    Output = Event

    @staticmethod
    async def mutate_and_get_payload(root, info, **input):
        current_date = datetime.now()
        credentials = info.context["credentials"]
        doc = {
            "id": uuid.uuid4(),
            "name": input["name"],
            "type": input["type"],
            "description": input.get("description"),
            "address": input["address"],
            "location": {
                "type": "Point",
                "coordinates": [input["longitude"], input["latitude"]],
            },
            "created_by": credentials,
            "created_date": current_date,
            "changed_date": current_date,
        }
        collection = info.context["db"].events
        await collection.insert_one(doc.copy())
        return get_event_from_document(doc)


class UpdateEventMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        type = graphene.Enum.from_enum(EventType)
        description = graphene.String()

        address = graphene.String()
        longitude = graphene.Float()
        latitude = graphene.Float()

    Output = Event

    @staticmethod
    async def mutate_and_get_payload(root, info, **input):
        type, _id = from_global_id(input["id"])
        collection = info.context["db"].events

        if doc := await collection.find_one({"id": uuid.UUID(_id)}, {"_id": 0}):
            doc.update(
                {
                    key: input[key]
                    for key in doc.keys()
                    if input.get(key) and key != "id"
                }
            )
            await collection.update_one({"id": uuid.UUID(_id)}, {"$set": doc.copy()})
            return get_event_from_document(doc)

        raise Exception(f"Event with id {_id} is not exist.")


class DeleteEventMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    Output = Event

    @staticmethod
    async def mutate_and_get_payload(root, info, **input):
        type, _id = from_global_id(input["id"])
        collection = info.context["db"].events

        if doc := await collection.find_one({"id": uuid.UUID(_id)}, {"_id": 0}):
            await collection.delete_one({"id": uuid.UUID(_id)})
            return get_event_from_document(doc)

        raise Exception(f"Event with id {_id} is not exist.")


class Mutation(graphene.ObjectType):
    create_event = CreateEventMutation.Field()
    update_event = UpdateEventMutation.Field()
    delete_event = DeleteEventMutation.Field()
