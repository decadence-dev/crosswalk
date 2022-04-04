import pickle

from aiokafka import AIOKafkaProducer

from models import EventAction, EventActionStatus
from settings import settings


async def send_event_created(event_bytes):
    producer = AIOKafkaProducer(bootstrap_servers=settings.bootstrap_servers)
    await producer.start()
    try:
        event = pickle.loads(event_bytes)
        event_action = EventAction(
            id=event.id, status=EventActionStatus.CREATED, event=event
        )
        await producer.send(settings.actions_topic, pickle.dumps(event_action))
    except Exception as err:
        print(err)
    finally:
        await producer.stop()


async def send_event_updated(event_bytes):
    producer = AIOKafkaProducer(bootstrap_servers=settings.bootstrap_servers)
    await producer.start()
    try:
        event = pickle.loads(event_bytes)
        event_action = EventAction(
            id=event.id, status=EventActionStatus.UPDATED, event=event
        )
        await producer.send(settings.actions_topic, pickle.dumps(event_action))
    except Exception as err:
        print(err)
    finally:
        await producer.stop()


async def send_event_deleted(id):
    producer = AIOKafkaProducer(bootstrap_servers=settings.bootstrap_servers)
    await producer.start()
    try:
        event_action = EventAction(id=id, status=EventActionStatus.DELETED)
        await producer.send(
            settings.actions_topic,
            pickle.dumps(event_action),
        )
    except Exception as err:
        print(err)
    finally:
        await producer.stop()
