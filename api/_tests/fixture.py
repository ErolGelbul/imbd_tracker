import asyncio
import secrets

import pytest

from starlette.testclient import TestClient

from api.api import create_app
from api.repository.movie.memory import MemoryMovieRepository
from api.repository.movie.mongo import MongoMovieRepository
from api.settings import Settings, settings_instance


@pytest.fixture()
def test_client():
    settings: Settings = settings_instance()
    settings.enable_metrics = False
    return TestClient(app=create_app())


@pytest.fixture()
def memory_movie_repo_fixture():
    return MemoryMovieRepository()


@pytest.fixture()
def mongo_movie_repo_fixture():
    random_database_name = secrets.token_hex(5)
    repo = MongoMovieRepository(
        connection_string="mongodb://localhost:27017", database=random_database_name
    )
    yield repo
    # noinspection PyProtectedMember
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(repo._client.drop_database(random_database_name))
