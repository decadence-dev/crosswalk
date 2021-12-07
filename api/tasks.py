import pickle

from models import EventAction, EventActionStatus
from settings import settings


async def send_event_created(producer, event_bytes):
    try:
        event = pickle.loads(event_bytes)
        event_action = EventAction(
            id=event.id, status=EventActionStatus.CREATED, event=event
        )
        await producer.send_and_wait(settings.actions_topic, pickle.dumps(event_action))
    except Exception as err:
        print(err)


async def send_event_updated(producer, event_bytes):
    try:
        event = pickle.loads(event_bytes)
        event_action = EventAction(
            id=event.id, status=EventActionStatus.UPDATED, event=event
        )
        await producer.send_and_wait(
            settings.actions_topic, pickle.dumps(event_action)
        )
    except Exception as err:
        print(err)


async def send_event_deleted(producer, id):
    try:
        event_action = EventAction(id=id, status=EventActionStatus.DELETED)
        await producer.send_and_wait(
            settings.actions_topic, pickle.dumps(event_action),
        )
    except Exception as err:
        print(err)
