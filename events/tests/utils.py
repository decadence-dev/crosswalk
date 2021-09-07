from datetime import datetime, timedelta
from typing import Dict, Optional

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from jose import jwt

from main import AUTH_EXPIRATION_MINUTES, SECRET_KEY, app


async def graphql(query: str, creadentials: Optional[Dict] = None, **kwargs):
    headers = {}
    if creadentials is not None:
        payload = creadentials.copy()
        payload.update(
            {"exp": datetime.now() + timedelta(minutes=AUTH_EXPIRATION_MINUTES)}
        )
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        headers = {"Authorization": f"bearer {token}"}
    async with AsyncClient(
        app=app,
        headers=headers,
        base_url="http://localhost:8000",
    ) as ac, LifespanManager(app):
        return await ac.post("/", json={"query": query, "variables": kwargs})
