import asyncio

from aiokafka import AIOKafkaConsumer

from settings import settings


async def cunsume():
    consumer = AIOKafkaConsumer(
        settings.actions_topic,
        bootstrap_servers=settings.bootstrap_servers,
        # group_id="EventsActionsListeners",
        # auto_offset_reset="earliest",
        # enable_auto_commit=True
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(msg)
    finally:
        await consumer.stop()


asyncio.run(cunsume())
