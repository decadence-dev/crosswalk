import uuid
from datetime import datetime

import pytest
from starlette import status

from models import EventType
from tests.utils import graphql


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
                "data": {
                    "updateEvent": {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "address": "40187 Angela Cliffs Apt. 378 North Heatherland, WY 07538",  # noqa: E501
                        "description": (
                            "Establish candidate cause although interest."
                            "Citizen face nor tough behavior. Need feeling happy within."  # noqa: E501
                            "Special serve stage pressure result where population."
                        ),
                        "longitude": -9.203746,
                        "latitude": -30.050664,
                        "createdDate": "1111-01-01T00:00:00+00:00",
                        "changedDate": "1234-05-06T00:00:00+00:00",
                        "createdBy": {
                            "id": "00000000-0000-0000-0000-000000000000",
                            "username": "mockuser",
                        },
                    }
                }
            },
        )
    ],
)
async def test_update(mocker, user, event, input, result):
    dt_patch = mocker.patch("mutations.datetime", mocker.Mock(wraps=datetime))
    dt_patch.now.return_value = datetime(1234, 5, 6)

    response = await graphql(
        """
        mutation updateEvent(
            $id: UUID!, $data: UpdateEventInput!
        ) {
            updateEvent (id: $id, data: $data) {
                id
                address
                description
                longitude
                latitude
                createdDate
                changedDate
                createdBy {
                    id
                    username
                }
            }
        }
        """,
        creadentials=user,
        id=str(event.id),
        data=input,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == result


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
@pytest.mark.parametrize(
    "input",
    [
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
        }
    ],
)
async def test_update_non_nonexistent_event(user, input):
    response = await graphql(
        """
        mutation updateEvent(
            $id: UUID!, $data: UpdateEventInput!
        ) {
            updateEvent (id: $id, data: $data) {
                id
                address
                description
                longitude
                latitude
                createdDate
                changedDate
                createdBy {
                    id
                    username
                }
            }
        }
        """,
        creadentials=user,
        id="12345678-1234-1234-1234-123456789012",
        data=input,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.usefixtures("mocker", "user", "event")
@pytest.mark.parametrize(
    "input,result",
    [
        (
            {
                "eventType": EventType.FIRE.name,
            },
            {
                "data": {
                    "updateEvent": {
                        "changedDate": "1234-05-06T00:00:00+00:00",
                    }
                }
            },
        )
    ],
)
async def test_update_changed_date_updated(mocker, user, event, input, result):
    dt_patch = mocker.patch("mutations.datetime", mocker.Mock(wraps=datetime))
    dt_patch.now.return_value = datetime(1234, 5, 6)
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
    assert response.json() == result


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
@pytest.mark.parametrize("address", [None, "89159 Patty Ways\nEast April, NM 44063"])
@pytest.mark.parametrize("latitude", [None, -153.540373])
@pytest.mark.parametrize("longitude", [None, 168.172962])
@pytest.mark.parametrize("event_type", [None, EventType.FIRE.name])
async def test_update_required_fieds(
    user, event, address, latitude, longitude, event_type
):
    if address and latitude and longitude and event_type:
        pytest.skip("One of required fields should be empty")

    input = {
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "evenType": event_type,
    }

    response = await graphql(
        """
        mutation updateEvent(
            $id: UUID!, $data: UpdateEventInput!
        ) {
            updateEvent (id: $id, data: $data) {
                id
            }
        }
        """,
        creadentials=user,
        id=str(event.id),
        data=input,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "mocker", "user", "event")
@pytest.mark.parametrize(
    "input,record",
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
                "id": uuid.UUID("00000000-0000-0000-0000-000000000000"),
                "description": (
                    "Establish candidate cause although interest."
                    "Citizen face nor tough behavior. Need feeling happy within."
                    "Special serve stage pressure result where population."
                ),
                "address": "40187 Angela Cliffs Apt. 378 North Heatherland, WY 07538",
                "event_type": 7,
                "location": {"type": "Point", "coordinates": [-9.203746, -30.050664]},
                "created_by": {
                    "id": uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    "username": "mockuser",
                },
                "created_date": datetime(1111, 1, 1),
                "changed_date": datetime(1234, 5, 6),
            },
        )
    ],
)
async def test_updated_event_record(db, mocker, user, event, input, record):
    dt_patch = mocker.patch("mutations.datetime", mocker.Mock(wraps=datetime))
    dt_patch.now.return_value = datetime(1234, 5, 6)
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
    event = await db.events.find_one(
        {"id": uuid.UUID("00000000-0000-0000-0000-000000000000")}, {"_id": 0}
    )
    assert event == record
