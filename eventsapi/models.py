import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Union

from pydantic import BaseModel, Field, HttpUrl, validator


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


class Position(BaseModel):
    address: str
    position_x: float
    position_y: float


class Event(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    position: Position
    type: EventType
    description: Optional[str]
    attrachemnts: Optional[List[HttpUrl]] = Field(default_factory=list)
    created_by: Optional[User]
    created: datetime = Field(default_factory=datetime.now)
    changed: datetime = Field(default_factory=datetime.now)


class EventCreate(BaseModel):
    name: str
    position: Position
    type: EventType
    description: Optional[str]
    attrachemnts: Optional[List[HttpUrl]] = Field(default_factory=list)


class EventUpdate(BaseModel):
    name: Optional[str]
    position: Optional[Position]
    type: Optional[EventType]
    description: Optional[str]
    attrachemnts: Optional[List[HttpUrl]] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        assert v is not None
        return v

    @validator('position')
    def validate_position(cls, v):
        assert v is not None
        return Position(**v)

    @validator('type')
    def validate_type(cls, v):
        assert v is not None
        return v
