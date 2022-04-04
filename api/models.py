import uuid
from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Tuple

import pydantic
from graphene.utils.str_converters import to_camel_case


class User(pydantic.BaseModel):
    id: uuid.UUID = pydantic.Field(...)
    username: str = pydantic.Field(...)


class Location(pydantic.BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float] = pydantic.Field(...)


class Event(pydantic.BaseModel):
    id: Optional[uuid.UUID] = pydantic.Field(default_factory=uuid.uuid4)
    event_type: List[str] = pydantic.Field(...)
    description: Optional[str] = ""

    address: str = pydantic.Field(...)
    location: Location = pydantic.Field(...)

    created_by: User = pydantic.Field(...)
    created_date: datetime = pydantic.Field(default_factory=datetime.now)
    changed_date: datetime = pydantic.Field(default_factory=datetime.now)

    @property
    def longitude(self):
        return self.location.coordinates[0]

    @property
    def latitude(self):
        return self.location.coordinates[1]

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class EventActionStatus(IntEnum):
    CREATED = 1
    UPDATED = 2
    DELETED = 3
    UNAUTHORIZED = 4
    ERROR = 5


class EventAction(pydantic.BaseModel):
    status: EventActionStatus = pydantic.Field(...)
    event: Optional[Event]
