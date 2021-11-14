import uuid
from datetime import datetime

import faker
import pytest
from fastapi.testclient import TestClient
from starlette import status

from main import app
from models import Event, EventActionType, EventType
from tests.utils import graphql

fake = faker.Faker()


class PreparedEvent(Event):
    """
    Event mock objects

    For id, created_date, changed_date fields event we have set default_factory,
    which makes for us imposible patch of datetime and uuid modules,
    because of default_factory works on metaclass layer
    and at the moment we are using Event model in mutation,
    model patch just will not have any effect for already defined fields values.

    To resolve this issue we've created PreparedEvent model,
    which allow us to set values of id, created_date and changed_date explicitly.
    """

    def __init__(self, **kwargs):
        super().__init__(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            created_date=datetime(1234, 5, 6),
            changed_date=datetime(1234, 5, 6),
            **kwargs
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "eventType": EventType.ROBBERY.name,
                "address": "2530 Daniel Islands Apt. 802\nPort Angelaton, NV 21553",
                "description": (
                    "True situation song friend act economic fire. "
                    "Direction notice film happy open month recent."
                    "Word painting social expect. Well who where a open could day."
                ),
                "longitude": -150.644803,
                "latitude": -15.707780,
            },
            {
                "data": {
                    "createEvent": {
                        "eventType": "ROBBERY",
                        "address": "2530 Daniel Islands Apt. 802\nPort Angelaton, NV 21553",  # noqa: E501
                        "description": (
                            "True situation song friend act economic fire. "
                            "Direction notice film happy open month recent."
                            "Word painting social expect. Well who where a open could day."  # noqa: E501
                        ),
                        "createdBy": {"username": "mockuser"},
                        "longitude": -150.644803,
                        "latitude": -15.707780,
                    }
                }
            },
        )
    ],
)
async def test_create(user, input, result):
    response = await graphql(
        """
        mutation createEvent(
            $data: CreateEventInput!,
        ) {
            createEvent (data: $data) {
                eventType
                address
                description
                createdBy {
                    username
                }
                longitude
                latitude
            }
        }
        """,
        creadentials=user,
        data=input,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == result


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize("address", [None, fake.address()])
@pytest.mark.parametrize("latitude", [None, float(fake.coordinate())])
@pytest.mark.parametrize("longitude", [None, float(fake.coordinate())])
@pytest.mark.parametrize("event_type", [None, EventType.ROBBERY.name])
async def test_create_with_required_fields_empty(
    user, address, latitude, longitude, event_type
):
    if address and latitude and longitude and event_type:
        pytest.skip("One of required fields should be empty")

    input = {
        "creadentials": user,
        "address": address,
        "eventType": event_type,
        "longitude": longitude,
        "latitude": latitude,
        "description": fake.text(),
    }

    response = await graphql(
        """
        mutation createEvent(
            $data: CreateEventInput!
        ) {
            createEvent (data: $data) {
                id
            }
        }
        """,
        creadentials=user,
        data=input,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "mocker", "user")
@pytest.mark.parametrize(
    "input,record",
    [
        (
            {
                "eventType": EventType.ROBBERY.name,
                "address": "2530 Daniel Islands Apt. 802\nPort Angelaton, NV 21553",
                "description": (
                    "True situation song friend act economic fire. "
                    "Direction notice film happy open month recent."
                    "Word painting social expect. Well who where a open could day."
                ),
                "longitude": -150.644803,
                "latitude": -15.707780,
            },
            {
                "id": uuid.UUID("00000000-0000-0000-0000-000000000000"),
                "description": (
                    "True situation song friend act economic fire. "
                    "Direction notice film happy open month recent."
                    "Word painting social expect. Well who where a open could day."
                ),
                "address": "2530 Daniel Islands Apt. 802\nPort Angelaton, NV 21553",
                "event_type": 1,
                "location": {"type": "Point", "coordinates": [-150.644803, -15.707780]},
                "created_by": {
                    "id": uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    "username": "mockuser",
                },
                "created_date": datetime(1234, 5, 6),
                "changed_date": datetime(1234, 5, 6),
            },
        )
    ],
)
async def test_created_event_record(db, mocker, user, input, record):
    mocker.patch("mutations.EventModel", mocker.Mock(wraps=PreparedEvent))

    response = await graphql(
        """
        mutation createEvent(
            $data: CreateEventInput!
        ) {
            createEvent (data: $data) {
                id
            }
        }
        """,
        creadentials=user,
        data=input,
    )

    assert response.status_code == status.HTTP_200_OK
    event = await db.events.find_one(
        {"id": uuid.UUID("00000000-0000-0000-0000-000000000000")}, {"_id": 0}
    )

    assert event == record


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "mocker", "user")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "eventType": EventType.ROBBERY.name,
                "address": "2530 Daniel Islands Apt. 802\nPort Angelaton, NV 21553",
                "description": (
                    "True situation song friend act economic fire. "
                    "Direction notice film happy open month recent."
                    "Word painting social expect. Well who where a open could day."
                ),
                "longitude": -150.644803,
                "latitude": -15.707780,
            },
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "actionType": EventActionType.CREATE.value,
                "data": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "description": (
                        "True situation song friend act economic fire. "
                        "Direction notice film happy open month recent."
                        "Word painting social expect. Well who where a open could day."  # noqa: E501
                    ),
                    "address": "2530 Daniel Islands Apt. 802\nPort Angelaton, NV 21553",  # noqa: E501
                    "eventType": EventType.ROBBERY.value,
                    "location": {
                        "type": "Point",
                        "coordinates": [-150.644803, -15.707780],
                    },
                    "createdBy": {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "username": "mockuser",
                    },
                    "createdDate": "1234-05-06T00:00:00",
                    "changedDate": "1234-05-06T00:00:00",
                },
            },
        )
    ],
)
async def test_receive_create_action(mocker, user, input, result):
    client = TestClient(app)
    mocker.patch("mutations.EventModel", mocker.Mock(wraps=PreparedEvent))
    with client.websocket_connect("/events-actions") as websocket:
        response = await graphql(
            """
            mutation createEvent(
                $data: CreateEventInput!
            ) {
                createEvent (data: $data) {
                    eventType
                    address
                    description
                    createdBy {
                        username
                    }
                    longitude
                    latitude
                }
            }
            """,
            creadentials=user,
            data=input,
        )

        assert response.status_code == status.HTTP_200_OK
        message = websocket.receive_json()
        assert message == result
