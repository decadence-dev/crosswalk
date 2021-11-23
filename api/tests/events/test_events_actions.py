from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from starlette import status

from main import app
from models import EventActionType, EventType
from tests.utils import graphql


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "mocker", "event_mock", "user")
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
                "id": "00000000-0000-0000-0000-000000000000",
                "actionType": EventActionType.CREATE.value,
                "data": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "description": (
                        "True situation song friend act economic fire. "
                        "Direction notice film happy open month recent."
                        "Word painting social expect. Well who where a open could day."  # noqa: E501
                    ),
                    "address": "2530 Daniel Islands Apt. 802 Port Angelaton, NV 21553",  # noqa: E501
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
async def test_receive_create_action(mocker, event_mock, user, input, result):
    client = TestClient(app)
    mocker.patch("mutations.EventModel", mocker.Mock(wraps=event_mock))
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


@pytest.mark.asyncio
@pytest.mark.usefixtures("mocker", "user", "event")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "eventType": EventType.FIRE.name,
                "address": "40187 Angela Cliffs Apt. 378 North Heatherland, WY 07538",
                "description": (
                    "Establish candidate cause although interest."
                    "Citizen face nor tough behavior. Need feeling happy within."
                    "Special serve stage pressure result where population."
                ),
                "longitude": -9.203746,
                "latitude": -30.050664,
            },
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "actionType": EventActionType.UPDATE.value,
                "data": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "description": (
                        "Establish candidate cause although interest."
                        "Citizen face nor tough behavior. Need feeling happy within."
                        "Special serve stage pressure result where population."
                    ),
                    "address": "40187 Angela Cliffs Apt. 378 North Heatherland, WY 07538",  # noqa: E501
                    "eventType": EventType.FIRE.value,
                    "location": {
                        "type": "Point",
                        "coordinates": [-9.203746, -30.050664],
                    },
                    "createdBy": {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "username": "mockuser",
                    },
                    "createdDate": "1111-01-01T00:00:00",
                    "changedDate": "1234-05-06T00:00:00",
                },
            },
        )
    ],
)
async def test_receive_update_action(mocker, user, event, input, result):
    client = TestClient(app)
    dt_patch = mocker.patch("mutations.datetime", mocker.Mock(wraps=datetime))
    dt_patch.now.return_value = datetime(1234, 5, 6)
    with client.websocket_connect("/events-actions") as websocket:
        response = await graphql(
            """
            mutation updateEvent(
                $id: UUID!, $data: UpdateEventInput!
            ) {
                updateEvent (id: $id, data: $data) {
                    changedDate
                }
            }
            """,
            creadentials=user,
            id=str(event.id),
            data=input,
        )

        assert response.status_code == status.HTTP_200_OK
        message = websocket.receive_json()
        assert message == result


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
@pytest.mark.parametrize(
    "result",
    [
        {
            "id": "00000000-0000-0000-0000-000000000000",
            "actionType": EventActionType.DELETE.value,
        }
    ],
)
async def test_receive_delete_action(user, event, result):
    client = TestClient(app)
    with client.websocket_connect("/events-actions") as websocket:
        response = await graphql(
            """
            mutation deleteEvent($id: UUID!) {
                deleteEvent (id: $id) {
                    changedDate
                }
            }
            """,
            creadentials=user,
            id=str(event.id),
        )

        assert response.status_code == status.HTTP_200_OK
        message = websocket.receive_json()
        assert message == result
