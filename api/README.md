# Events API service

## Tests

In case, the tested logic doesn't required any data fixtures, but creating new data in database, like create mutation does,
we need to mark its test as `@pytest.usefixtures.db`.

```python
import pytest
from tests.utils import graphql
from starlette import status

@pytest.mark.asyncio
@pytest.mark.usefixtures("db", "user")
@pytest.mark.parametrize(
    ...
)
async def test_create(user, input, result):
    response = await graphql(
        ...
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == result
```

In our tests we don't have any explicit teardown functions definition, basically because we don't need it.
`pytest` provides flexible interface of yield fixtures, which makes our fixtures works as context managers,
so all teardown logic for particular collection is stores in the same fixture after yield call.

```python
import pytest

@pytest.fixture
@pytest.mark.usefixtures("db", "faker", "user")
async def events(db, faker, user):
    collection = db.events
    result = await collection.insert_many(
        ...
    )
    yield result.inserted_ids
    await collection.delete_many({"id": {"$in": result.inserted_ids}})
```

Fixture `db` are also contains teardown logic, but more global than just specific test data records deletion — it's drops whole `test` database.

```python
import pytest
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture
async def db():
    client = AsyncIOMotorClient(
        ...
    )
    yield client[...]
    client.drop_database("test")
```

Simple use of this fixture in tests is allows us to clear database between separated tests module runs, 
if fixtures doesnt have teardown logic or module doesnt have any appropriate fixtures at all.
