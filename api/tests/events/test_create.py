import uuid
from datetime import datetime

import pytest
from starlette import status

from models import EventType
from tests.utils import graphql


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "eventType": EventType.ROBBERY.name,
                "address": "2530 Daniel Islands Apt. 802 Port Angelaton, NV 21553",
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
                        "address": "2530 Daniel Islands Apt. 802 Port Angelaton, NV 21553",  # noqa: E501
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
@pytest.mark.usefixtures("db", "faker", "user")
@pytest.mark.parametrize(
    "address", [None, "59427 Hernandez Square Suite 835\nWest Nicoleville, HI 29447"]
)
@pytest.mark.parametrize("latitude", [None, -138.437396])
@pytest.mark.parametrize("longitude", [None, 90.675089])
@pytest.mark.parametrize("event_type", [None, EventType.ROBBERY.name])
async def test_create_with_required_fields_empty(
    faker, user, address, latitude, longitude, event_type
):
    if address and latitude and longitude and event_type:
        pytest.skip("One of required fields should be empty")

    input = {
        "creadentials": user,
        "address": address,
        "eventType": event_type,
        "longitude": longitude,
        "latitude": latitude,
        "description": faker.text(),
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
@pytest.mark.usefixtures("db", "mocker", "event_mock", "user")
@pytest.mark.parametrize(
    "input,record",
    [
        (
            {
                "eventType": EventType.ROBBERY.name,
                "address": "2530 Daniel Islands Apt. 802 Port Angelaton, NV 21553",
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
                "address": "2530 Daniel Islands Apt. 802 Port Angelaton, NV 21553",
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
async def test_created_event_record(db, mocker, user, event_mock, input, record):
    mocker.patch("mutations.EventModel", mocker.Mock(wraps=event_mock))

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
