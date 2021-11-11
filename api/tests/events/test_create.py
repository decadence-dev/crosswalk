import faker
import pytest

from models import EventType
from tests.utils import graphql

fake = faker.Faker()


@pytest.fixture
@pytest.mark.usefixtures("faker")
async def input(faker):
    return {
        "address": faker.address(),
        "eventType": faker.random_element(EventType),
        "description": faker.text(),
        "longitude": faker.coordinate(),
        "latitude": faker.coordinate(),
    }


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
                            "Word painting social expect. Well who where a open could day."
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
async def test_create(db, user, input, result):
    response = await graphql(
        """
        mutation createEvent(
            $eventType: EventType!,
            $address: String!,
            $description: String!,
            $longitude: Float!,
            $latitude: Float!
        ) {
            createEvent (
                input: {
                    eventType: $eventType,
                    address: $address,
                    description: $description,
                    longitude: $longitude
                    latitude: $latitude
                }
            ) {
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
        **input,
    )

    assert response.status_code == 200
    assert response.json() == result


@pytest.mark.asyncio
@pytest.mark.usefixtures("user")
@pytest.mark.parametrize("address", [None, fake.address()])
@pytest.mark.parametrize("latitude", [None, float(fake.coordinate())])
@pytest.mark.parametrize("longitude", [None, float(fake.coordinate())])
@pytest.mark.parametrize("event_type", [None, EventType.ROBBERY.name])
async def test_create_with_required_fields_empty(
    user, address, latitude, longitude, event_type
):
    if address and latitude and longitude and event_type:
        pytest.skip("One of required fields should be empty")

    response = await graphql(
        """
        mutation createEvent(
            $eventType: EventType!,
            $address: String!,
            $description: String!,
            $longitude: Float!,
            $latitude: Float!
        ) {
            createEvent (
                input: {
                    eventType: $eventType,
                    address: $address,
                    description: $description,
                    longitude: $longitude
                    latitude: $latitude
                }
            ) {
                id
            }
        }
        """,
        creadentials=user,
        address=address,
        eventType=event_type,
        longitude=longitude,
        latitude=latitude,
        description=fake.text(),
    )

    assert response.status_code == 400
