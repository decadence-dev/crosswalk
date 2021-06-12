import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, validator, conlist, constr


class EventType(str, Enum):
    ROBBERY = 'ROBBERY'
    FIGHT = 'FIGHT'
    DEATH = 'DEATH'
    GUN = 'GUN'
    INADEQUATE = 'INADEQUATE'
    ACCEDENT = 'ACCEDENT'
    FIRE = 'FIRE'
    POLICE = 'POLICE'


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str


class Location(BaseModel):
    type = 'Point'
    coordinates: List = []


class Event(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    type: EventType
    description: Optional[str]

    address: str
    location: Location
    attachments: Optional[List[HttpUrl]] = Field(default_factory=list)

    created_by: Optional[User]
    changed_by: Optional[User]
    created: datetime = Field(default_factory=datetime.now)
    changed: datetime = Field(default_factory=datetime.now)


class EventCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    type: EventType
    description: Optional[constr(strip_whitespace=True, min_length=1)]

    address: constr(strip_whitespace=True, min_length=1)
    location: conlist(float, min_items=2, max_items=2)

    @validator('location')
    def validate_location(cls, v):
        return Location(coordinates=v)


class EventUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)]
    type: Optional[EventType]
    description: Optional[constr(strip_whitespace=True, min_length=1)]

    address: Optional[constr(strip_whitespace=True, min_length=1)]
    location: Optional[conlist(float, min_items=2, max_items=2)]
    attachments: Optional[List[HttpUrl]] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        assert v is not None
        return v

    @validator('type')
    def validate_type(cls, v):
        assert v is not None
        return v

    @validator('address')
    def validate_address(cls, v):
        assert v is not None
        return v

    @validator('location')
    def validate_location(cls, v):
        return Location(coordinates=v)
