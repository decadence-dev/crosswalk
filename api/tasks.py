from models import EventAction, EventActionType
from settings import settings


async def send_event_created(producer, event):
    try:
        event_action = EventAction(
            id=event["id"], action_type=EventActionType.CREATE, data=event
        )
        await producer.send_and_wait(
            settings.actions_topic, event_action.json(by_alias=True).encode()
        )
    except Exception as err:
        print(err)


async def send_event_updated(producer, event):
    try:
        event_action = EventAction(
            id=event["id"], action_type=EventActionType.UPDATE, data=event
        )
        await producer.send_and_wait(
            settings.actions_topic, event_action.json(by_alias=True).encode()
        )
    except Exception as err:
        print(err)
