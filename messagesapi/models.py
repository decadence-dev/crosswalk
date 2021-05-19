import uuid
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    body: str
    event: uuid.UUID
    parent: Optional[uuid.UUID]
    user: Optional[uuid.UUID]
