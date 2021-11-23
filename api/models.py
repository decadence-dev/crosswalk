import uuid
from datetime import datetime
from enum import IntEnum
from typing import Optional, Tuple

import pydantic
from graphene.utils.str_converters import to_camel_case


class CamelCasedModel(pydantic.BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class EventType(IntEnum):
    ROBBERY = 1
    FIGHT = 2
    DEATH = 3
    GUN = 4
    INADEQUATE = 5
    ACCEDENT = 6
    FIRE = 7
    POLICE = 8


class User(pydantic.BaseModel):
    id: uuid.UUID = pydantic.Field(...)
    username: str = pydantic.Field(...)


class Location(pydantic.BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float] = pydantic.Field(...)


class Event(CamelCasedModel):
    id: Optional[uuid.UUID] = pydantic.Field(default_factory=uuid.uuid4)
    description: Optional[str] = ""
    address: str = pydantic.Field(...)
    event_type: EventType = pydantic.Field(...)
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


class EventActionType(IntEnum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3


class EventAction(CamelCasedModel):
    id: uuid.UUID
    action_type: EventActionType
    data: Optional[Event]
