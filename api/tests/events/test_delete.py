import uuid

import pytest
from starlette import status

from tests.utils import graphql


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
@pytest.mark.parametrize(
    "result",
    [
        {
            "data": {
                "deleteEvent": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "address": "7607 Jennifer Canyon Foleyville, MN 60927",  # noqa: E501
                    "description": (
                        "City point during. Maybe movement few record baby."
                        "Interesting use throughout responsibility."
                        "Team almost by continue run professional."
                    ),
                    "longitude": -159.243865,
                    "latitude": 168.469047,
                    "createdDate": "1111-01-01T00:00:00+00:00",
                    "changedDate": "1111-01-01T00:00:00+00:00",
                    "createdBy": {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "username": "mockuser",
                    },
                }
            }
        },
    ],
)
async def test_delete(user, event, result):
    response = await graphql(
        """
        mutation deleteEvent($id: UUID!) {
            deleteEvent (id: $id) {
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
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == result


@pytest.mark.asyncio
@pytest.mark.usefixtures("user", "event")
async def test_delete_non_nonexistent_event(user):
    response = await graphql(
        """
        mutation deleteEvent($id: UUID!) {
            deleteEvent (id: $id) {
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
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user", "event")
async def test_delete_record(db, user, event):
    await graphql(
        """
        mutation deleteEvent($id: UUID!) {
            deleteEvent (id: $id) {
                id
            }
        }
        """,
        creadentials=user,
        id=str(event.id),
    )

    event = await db.events.find_one(
        {"id": uuid.UUID("00000000-0000-0000-0000-000000000000")}, {"_id": 0}
    )

    assert event is None