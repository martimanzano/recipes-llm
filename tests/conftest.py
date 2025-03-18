# conftest.py
import pytest
from app.database.database import async_engine

@pytest.fixture(scope="session", autouse=True)
async def close_db_engine():
    # Do nothing before the tests run
    yield
    # Dispose of the engine to close all connections.
    await async_engine.dispose()
