from datetime import datetime

import graphene

from models import Event as EventModel
from queries import Event, SchemaEventType
from tasks import send_event_created, send_event_updated, send_event_deleted


def get_event_from_document(doc):
    longitude, latitude = doc["location"]["coordinates"]
    return Event(
        **{field: value for field, value in doc.items() if field != "location"},
        longitude=longitude,
        latitude=latitude,
    )


class CreateEventInput(graphene.InputObjectType):
    event_type = graphene.Field(type=SchemaEventType, required=True)
    description = graphene.String()

    address = graphene.String(required=True)
    longitude = graphene.Float(required=True)
    latitude = graphene.Float(required=True)


class CreateEventMutation(graphene.Mutation):
    class Arguments:
        data = CreateEventInput(required=True)

    Output = Event

    @staticmethod
    async def mutate(root, info, data):
        credentials = info.context["credentials"]
        event = EventModel(
            created_by=credentials,
            location={
                "coordinates": [data["longitude"], data["latitude"]],
            },
            **data,
        )

        collection = info.context["db"].events
        await collection.insert_one(event.dict())
        background = info.context["background"]
        background.add_task(
            send_event_created, info.context["producer"], event.dict(by_alias=True)
        )
        return event


class UpdateEventInput(graphene.InputObjectType):
    event_type = graphene.Field(type=SchemaEventType)
    description = graphene.String()

    address = graphene.String()
    longitude = graphene.Float()
    latitude = graphene.Float()


class UpdateEventMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        data = UpdateEventInput(required=True)

    Output = Event

    @staticmethod
    async def mutate(root, info, id, data):
        collection = info.context["db"].events
        if doc := await collection.find_one({"id": id}):
            doc.update(data)
            location = doc["location"]
            update_data = dict(
                doc,
                changed_date=datetime.now(),
                location={
                    "coordinates": [
                        data.get("longitude", location["coordinates"][0]),
                        data.get("latitude", location["coordinates"][1]),
                    ],
                },
            )
            updated_event = EventModel(**update_data)
            await collection.update_one({"id": id}, {"$set": updated_event.dict()})
            background = info.context["background"]
            background.add_task(
                send_event_updated,
                info.context["producer"],
                updated_event.dict(by_alias=True),
            )
            return updated_event

        raise Exception(f"Event with id {id} is not exist.")


class DeleteEventMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    Output = Event

    @staticmethod
    async def mutate(root, info, id):
        collection = info.context["db"].events

        if doc := await collection.find_one({"id": id}, {"_id": 0}):
            await collection.delete_one({"id": id})
            event = EventModel(**doc)
            background = info.context["background"]
            background.add_task(send_event_deleted, info.context["producer"], event.id)
            return event

        raise Exception(f"Event with id {id} is not exist.")


class Mutation(graphene.ObjectType):
    create_event = CreateEventMutation.Field()
    update_event = UpdateEventMutation.Field()
    delete_event = DeleteEventMutation.Field()
