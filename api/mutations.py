import uuid
from datetime import datetime

import graphene
from graphene import relay
from graphql_relay import from_global_id

from queries import Event, SchemaEventType
from tasks import send_event_created


def get_event_from_document(doc):
    longitude, latitude = doc["location"]["coordinates"]
    return Event(
        **{field: value for field, value in doc.items() if field != "location"},
        longitude=longitude,
        latitude=latitude,
    )


class CreateEventMutation(relay.ClientIDMutation):
    class Input:
        event_type = graphene.Field(type=SchemaEventType, required=True)
        description = graphene.String()

        address = graphene.String(required=True)
        longitude = graphene.Float(required=True)
        latitude = graphene.Float(required=True)

    Output = Event

    @staticmethod
    async def mutate_and_get_payload(root, info, **input):
        current_date = datetime.now()
        credentials = info.context["credentials"]
        if not input["address"]:
            raise Exception("Address value cannot be empty string")
        doc = {
            "id": uuid.uuid4(),
            "event_type": input["event_type"],
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
        background = info.context["background"]
        background.add_task(send_event_created, info.context["producer"], doc)
        return get_event_from_document(doc)


class UpdateEventMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        event_type = graphene.Field(type=SchemaEventType)
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
            updated_document = dict(
                doc,
                **{
                    key: input[key]
                    for key in doc.keys()
                    if input.get(key) and key != "id"
                },
                changed_date=datetime.now(),
            )
            await collection.update_one(
                {"id": uuid.UUID(_id)}, {"$set": updated_document.copy()}
            )
            return get_event_from_document(updated_document)

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
