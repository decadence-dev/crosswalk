import pickle
from datetime import datetime, timedelta

import graphene
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import Cookie, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from starlette import status
from starlette.graphql import GraphQLApp, AsyncioExecutor
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.websockets import WebSocket

from mutations import Mutation
from queries import Query
from settings import Settings


app = FastAPI()

security = HTTPBearer()

settings = Settings()


async def get_current_user_creadentials(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        data = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        if datetime.fromtimestamp(data["exp"]) <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired"
            )
        return {"id": data["id"], "username": data["username"]}
    except JWTError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))


async def get_db():
    client = AsyncIOMotorClient(
        settings.database_host, settings.database_port, uuidRepresentation="standard"
    )
    yield client[settings.database_name]
    client.close()


async def get_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.bootstrap_servers)
    await producer.start()
    yield producer
    await producer.stop()


async def get_consumer():
    consumer = AIOKafkaConsumer(settings.actions_topic, bootstrap_servers=settings.bootstrap_servers)
    await consumer.start()
    yield consumer
    await consumer.stop()


async def database_middleware(next, root, info, **args):
    if "db" not in info.context:
        info.context["db"] = info.context["request"].db
    return next(root, info, **args)


async def user_info_middleware(next, root, info, **args):
    if "credentials" not in info.context:
        info.context["credentials"] = info.context["request"].credentials
    if "timezone" not in info.context:
        info.context["timezone"] = info.context["request"].timezone
    return next(root, info, **args)


async def kafka_middleware(next, root, info, **args):
    if "producer" not in info.context:
        info.context["producer"] = info.context["request"].producer
    return next(root, info, **args)


class MiddlewareSchema(graphene.Schema):
    def __init__(self, middleware=(), *args, **kwargs):
        self._middleware = middleware
        super(MiddlewareSchema, self).__init__(*args, **kwargs)

    def execute(self, *args, **kwargs):
        kwargs.update(middleware=self._middleware)
        return super(MiddlewareSchema, self).execute(*args, **kwargs)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


schema = MiddlewareSchema(
    query=Query,
    mutation=Mutation,
    middleware=[database_middleware, user_info_middleware, kafka_middleware],
)


graphql_app = GraphQLApp(schema=schema, executor_class=AsyncioExecutor)


@app.post("/")
async def main(
    request: Request,
    timezone: str = Cookie("UTC"),
    credentials: dict = Depends(get_current_user_creadentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
    producer: AIOKafkaProducer = Depends(get_producer)
):
    request.db = db
    request.producer=producer
    request.timezone = timezone
    request.credentials = credentials
    return await graphql_app.handle_graphql(request)


@app.post("/token")
async def get_token():
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    payload = {
        "id": "00000000-0000-0000-0000-000000000000",
        "username": "mockuser",
        "exp": datetime.now() + timedelta(minutes=settings.auth_expiration_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


@app.websocket("/events-actions")
async def events_statuses_sender(websocket: WebSocket, consumer: AIOKafkaConsumer = Depends(get_consumer)):
    await websocket.accept()
    async for msg in consumer:
        await websocket.send_json(pickle.loads(msg.value))
