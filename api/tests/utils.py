from datetime import datetime, timedelta
from typing import Dict, Optional

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from jose import jwt

from main import app, settings


def creadentials_to_token(creadentials: dict) -> str:
    payload = creadentials.copy()
    payload.update(
        {"exp": datetime.now() + timedelta(minutes=settings.auth_expiration_minutes)}
    )
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def dictseq(a: Dict, b: Dict) -> bool:
    """
    Compare two dicts.

    For particular cases we can't patch or mock testing objects,
    which prevents us to predict what exactly value will be retunred by logic.

    For example we can't mock any function we using in pydantinc.Field default_factory,
    because pydantic.BaseModel using metaclass, which collect model fields,
    and it's just imposible to mock any function in default_factory,
    because it was already imported and collected on module import step.
    """
    if a.keys() != b.keys():
        return False

    for val_a, val_b in zip(a.values(), b.values()):
        if val_a is Ellipsis or val_b is Ellipsis:
            continue
        elif type(val_a) != type(val_b):
            return False
        elif isinstance(val_a, dict):
            is_equal = dictseq(val_a, val_b)
            if not is_equal:
                return False
        elif val_a != val_b:
            return False

    return True


async def graphql(
    query: str,
    creadentials: Optional[Dict] = None,
    cookies: Optional[Dict] = None,
    **kwargs,
):
    headers = {}
    if creadentials is not None:
        token = creadentials_to_token(creadentials)
        headers = {"Authorization": f"bearer {token}"}
    async with AsyncClient(
        app=app,
        headers=headers,
        cookies=cookies,
        base_url="http://localhost:8000",
    ) as ac, LifespanManager(app):
        return await ac.post("/", json={"query": query, "variables": kwargs})
