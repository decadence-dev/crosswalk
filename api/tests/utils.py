from datetime import datetime, timedelta
from typing import Dict, Optional

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from jose import jwt

from main import settings, app


async def graphql(query: str, creadentials: Optional[Dict] = None, cookies: Optional[Dict] = None, **kwargs):
    headers = {}
    if creadentials is not None:
        payload = creadentials.copy()
        payload.update(
            {"exp": datetime.now() + timedelta(minutes=settings.auth_expiration_minutes)}
        )
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        headers = {"Authorization": f"bearer {token}"}
    async with AsyncClient(
        app=app,
        headers=headers,
        cookies=cookies,
        base_url="http://localhost:8000",
    ) as ac, LifespanManager(app):
        return await ac.post("/", json={"query": query, "variables": kwargs})
