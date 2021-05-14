import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Union

from pydantic import BaseModel, Field, HttpUrl, validator, conlist


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
    id: uuid.UUID
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
    attrachemnts: Optional[List[HttpUrl]] = Field(default_factory=list)

    created_by: Optional[User]
    changed_by: Optional[User]
    created: datetime = Field(default_factory=datetime.now)
    changed: datetime = Field(default_factory=datetime.now)


class EventCreate(BaseModel):
    name: str
    type: EventType
    description: Optional[str]

    address: str
    location: conlist(float, min_items=2, max_items=2)
    attrachemnts: Optional[List[HttpUrl]] = Field(default_factory=list)

    @validator('location')
    def validate_location(cls, v):
        return Location(coordinates=v)


class EventUpdate(BaseModel):
    name: Optional[str]
    type: Optional[EventType]
    description: Optional[str]

    address: Optional[str]
    location: Optional[conlist(float, min_items=2, max_items=2)]
    attrachemnts: Optional[List[HttpUrl]] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        assert v is not None
        return v

    @validator('address')
    def validate_address(cls, v):
        assert v is not None
        return v

    @validator('location')
    def validate_location(cls, v):
        return Location(coordinates=v)

    @validator('type')
    def validate_type(cls, v):
        assert v is not None
        return v
