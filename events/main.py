import os
from datetime import datetime, timedelta

import graphene
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from graphql.execution.executors.asyncio import AsyncioExecutor
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from starlette import status
from starlette.graphql import GraphQLApp
from starlette.requests import Request

from mutations import Mutation
from queries import Query

AUTH_EXPIRATION_MINUTES = os.getenv("AUTH_EXPIRATION_MINUTES", 60)
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", 27017)
DATABASE_NAME = os.getenv("DATABASE_NAME", "crosswalk")


app = FastAPI()

security = HTTPBearer()


async def get_current_user_creadentials(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        data = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        if datetime.fromtimestamp(data["exp"]) <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired"
            )
        return {"id": data["id"], "username": data["username"]}
    except JWTError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))


async def get_db():
    client = AsyncIOMotorClient(
        DATABASE_HOST, DATABASE_PORT, uuidRepresentation="standard"
    )
    yield client[DATABASE_NAME]
    client.close()


async def database_middleware(next, root, info, **args):
    if "db" not in info.context:
        info.context["db"] = info.context["request"].db
    return next(root, info, **args)


async def credentials_middleware(next, root, info, **args):
    if "credentials" not in info.context:
        info.context["credentials"] = info.context["request"].credentials
    return next(root, info, **args)


class MiddlewareSchema(graphene.Schema):
    def __init__(self, middleware=(), *args, **kwargs):
        self._middleware = middleware
        super(MiddlewareSchema, self).__init__(*args, **kwargs)

    def execute(self, *args, **kwargs):
        kwargs.update(middleware=self._middleware)
        return super(MiddlewareSchema, self).execute(*args, **kwargs)


schema = MiddlewareSchema(
    query=Query,
    mutation=Mutation,
    middleware=[database_middleware, credentials_middleware],
)


graphql_app = GraphQLApp(schema=schema, executor_class=AsyncioExecutor)


@app.post("/")
async def main(
    request: Request,
    credentials: dict = Depends(get_current_user_creadentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    request.db = db
    request.credentials = credentials
    return await graphql_app.handle_graphql(request)


@app.post("/token")
async def get_token():
    if not DEBUG:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    payload = {
        "id": "00000000-0000-0000-0000-000000000000",
        "username": "mockuser",
        "exp": datetime.now() + timedelta(minutes=AUTH_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
