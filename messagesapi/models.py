import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    id: uuid.UUID
    name: str


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    body: str
    event: uuid.UUID

    user: User
    parent: Optional[uuid.UUID]

    created: datetime = Field(default_factory=datetime.now)
    changed: datetime = Field(default_factory=datetime.now)


class MessageCreate(BaseModel):
    body: str
    event: uuid.UUID
    parent: Optional[uuid.UUID]


class MessageUpdate(BaseModel):
    body: Optional[str]
