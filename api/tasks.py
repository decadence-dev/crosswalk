import pickle

from settings import Settings


settings = Settings()


async def send_event_created(producer, event):
    try:
        # TODO add all events data to body
        body = {
            'type': 'CREATE',
            'id': str(event['id']),
        }
        await producer.send_and_wait(settings.actions_topic, pickle.dumps(body))
    except Exception as err:
        print(err)
