import functools

import pytest

# noinspection PyUnresolvedReferences
from api._tests.fixture import test_client
from api.entities.movie import Movie
from api.handlers.movie_v1 import movie_repository
from api.repository.movie.memory import MemoryMovieRepository


def memory_repository_dependency(dependency):
    return dependency


@pytest.mark.asyncio()
async def test_create_movie(test_client):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    # Test
    result = test_client.post(
        "/api/v1/movies/",
        json={
            "title": "My Movie",
            "description": "string",
            "release_year": 2000,
            "watched": False,
        },
    )

    # Assertion
    movie_id = result.json().get("id")
    assert result.status_code == 201
    movie = await repo.get_by_id(movie_id=movie_id)
    assert movie is not None


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "movie_json",
    [
        (
            {
                "description": "string",
                "release_year": 2000,
                "watched": False,
            },
        ),
        (
            {
                "title": "My Movie",
                "release_year": 2000,
                "watched": False,
            }
        ),
        (
            {
                "title": "My Movie",
                "description": "string",
                "release_year": 0,
                "watched": False,
            }
        ),
        (
            {
                "title": "My Movie",
                "description": "string",
                "watched": False,
            }
        ),
    ],
)
async def test_create_movie_validation_error(test_client, movie_json):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    # Test
    result = test_client.post(
        "/api/v1/movies/",
        json=movie_json,
    )

    # Assertion
    assert result.status_code == 422


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "movie_seed,movie_id,expected_status_code,expected_result",
    [
        pytest.param(
            [],
            "random",
            404,
            {"message": "Movie with id random is not found."},
            id="not-found",
        ),
        pytest.param(
            [
                Movie(
                    movie_id="found",
                    title="My Movie",
                    description="Movie Description",
                    release_year=2000,
                )
            ],
            "found",
            200,
            {
                "description": "Movie Description",
                "id": "found",
                "release_year": 2000,
                "title": "My Movie",
                "watched": False,
            },
            id="found",
        ),
    ],
)
async def test_get_movie_by_id(
    test_client, movie_seed, movie_id, expected_status_code, expected_result
):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    for movie in movie_seed:
        await repo.create(movie)

    # Test
    result = test_client.get(f"/api/v1/movies/{movie_id}")

    # Assertion
    assert result.status_code == expected_status_code
    assert result.json() == expected_result


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "movie_seed,movie_title,skip, limit, expected_result",
    [
        pytest.param([], "movie_title", 0, 1000, [], id="empty-result"),
        pytest.param(
            [
                Movie(
                    movie_id="1",
                    title="movie title",
                    description="Movie Description",
                    release_year=2000,
                ),
                Movie(
                    movie_id="2",
                    title="movie title",
                    description="Movie Description",
                    release_year=2001,
                ),
                Movie(
                    movie_id="3",
                    title="movie title",
                    description="Movie Description",
                    release_year=2002,
                ),
                Movie(
                    movie_id="4",
                    title="movie title2",
                    description="Movie Description",
                    release_year=2002,
                ),
            ],
            "movie title",
            0,
            1000,
            [
                {
                    "description": "Movie Description",
                    "id": "1",
                    "release_year": 2000,
                    "title": "movie title",
                    "watched": False,
                },
                {
                    "description": "Movie Description",
                    "id": "2",
                    "release_year": 2001,
                    "title": "movie title",
                    "watched": False,
                },
                {
                    "description": "Movie Description",
                    "id": "3",
                    "release_year": 2002,
                    "title": "movie title",
                    "watched": False,
                },
            ],
            id="some-results",
        ),
        pytest.param(
            [
                Movie(
                    movie_id="1",
                    title="movie title",
                    description="Movie Description",
                    release_year=2000,
                ),
                Movie(
                    movie_id="2",
                    title="movie title",
                    description="Movie Description",
                    release_year=2001,
                ),
                Movie(
                    movie_id="3",
                    title="movie title",
                    description="Movie Description",
                    release_year=2002,
                ),
                Movie(
                    movie_id="4",
                    title="movie title2",
                    description="Movie Description",
                    release_year=2002,
                ),
            ],
            "movie title",
            1,
            1000,
            [
                {
                    "description": "Movie Description",
                    "id": "2",
                    "release_year": 2001,
                    "title": "movie title",
                    "watched": False,
                },
                {
                    "description": "Movie Description",
                    "id": "3",
                    "release_year": 2002,
                    "title": "movie title",
                    "watched": False,
                },
            ],
            id="some-results-pagination-1-1000",
        ),
        pytest.param(
            [
                Movie(
                    movie_id="1",
                    title="movie title",
                    description="Movie Description",
                    release_year=2000,
                ),
                Movie(
                    movie_id="2",
                    title="movie title",
                    description="Movie Description",
                    release_year=2001,
                ),
                Movie(
                    movie_id="3",
                    title="movie title",
                    description="Movie Description",
                    release_year=2002,
                ),
                Movie(
                    movie_id="4",
                    title="movie title2",
                    description="Movie Description",
                    release_year=2002,
                ),
            ],
            "movie title",
            1,
            1,
            [
                {
                    "description": "Movie Description",
                    "id": "2",
                    "release_year": 2001,
                    "title": "movie title",
                    "watched": False,
                },
            ],
            id="some-results-pagination-1-1",
        ),
    ],
)
async def test_get_movies_by_title(
    test_client, movie_seed, movie_title, skip, limit, expected_result
):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    for movie in movie_seed:
        await repo.create(movie)

    # Test
    result = test_client.get(
        f"/api/v1/movies/?title={movie_title}&skip={skip}&limit={limit}"
    )

    # Assertion
    assert result.status_code == 200
    for movie in result.json():
        assert movie in expected_result
    assert len(result.json()) == len(expected_result)


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "update_parameters, updated_movie",
    [
        (
            {"title": "My Title Update", "id": "test"},
            Movie(
                movie_id="top_movie",
                title="My Title Update",
                description="Needs Update",
                release_year=2000,
            ),
        ),
        (
            {"description": "My Desc Update", "random": "test"},
            Movie(
                movie_id="top_movie",
                title="Needs Update",
                description="My Desc Update",
                release_year=2000,
            ),
        ),
        (
            {"release_year": 3000},
            Movie(
                movie_id="top_movie",
                title="Needs Update",
                description="Needs Update",
                release_year=3000,
            ),
        ),
        (
            {"watched": True},
            Movie(
                movie_id="top_movie",
                title="Needs Update",
                description="Needs Update",
                release_year=2000,
                watched=True,
            ),
        ),
    ],
)
async def test_patch_update_movie(test_client, update_parameters, updated_movie):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    await repo.create(
        Movie(
            movie_id="top_movie",
            title="Needs Update",
            description="Needs Update",
            release_year=2000,
        )
    )

    # Test
    result = test_client.patch(f"/api/v1/movies/top_movie", json=update_parameters)

    # Assertion
    assert result.status_code == 200
    assert result.json() == {"message": "Movie updated."}
    if updated_movie is not None:
        assert await repo.get_by_id(movie_id="top_movie") == updated_movie


@pytest.mark.asyncio()
async def test_patch_update_movie_not_found(test_client):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    # Test
    result = test_client.patch(
        f"/api/v1/movies/top_movie", json={"title": "Title Update"}
    )

    # Assertion
    assert result.status_code == 400
    assert result.json() == {"message": "movie: top_movie not found"}


@pytest.mark.asyncio()
async def test_delete_movie(test_client):
    # Setup
    repo = MemoryMovieRepository()
    patched_dependency = functools.partial(memory_repository_dependency, repo)

    test_client.app.dependency_overrides[movie_repository] = patched_dependency
    await repo.create(
        Movie(
            movie_id="top_movie",
            title="Needs Update",
            description="Needs Update",
            release_year=2000,
        )
    )

    # Test
    result = test_client.delete(f"/api/v1/movies/top_movie")

    # Assertion
    assert result.status_code == 204
    assert await repo.get_by_id(movie_id="top_movie") is None
