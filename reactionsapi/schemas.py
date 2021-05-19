import uuid
from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel


class User(BaseModel):
    id: uuid.UUID
    name: str


class ReactionType(str, Enum):
    POSITIVE = 'POSITIVE'
    NEGATIVE = 'NEGATIVE'


class Reaction(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    type: ReactionType = ReactionType.POSITIVE
    event: uuid.UUID
    user: User

    created: datetime = Field(default_factory=datetime.now)
    changed: datetime = Field(default_factory=datetime.now)


class ReactionCreate(BaseModel):
    type: ReactionType = ReactionType.POSITIVE
