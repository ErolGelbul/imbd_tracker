import secrets

import pytest

# noinspection PyUnresolvedReferences
from api._tests.fixture import mongo_movie_repo_fixture
from api.entities.movie import Movie
from api.repository.movie.abstractions import RepositoryException


@pytest.mark.asyncio
async def test_create(mongo_movie_repo_fixture):
    await mongo_movie_repo_fixture.create(
        movie=Movie(
            movie_id="first",
            title="My Movie",
            description="My Movie Description",
            release_year=2022,
            watched=True,
        )
    )
    movie: Movie = await mongo_movie_repo_fixture.get_by_id("first")
    assert movie == Movie(
        movie_id="first",
        title="My Movie",
        description="My Movie Description",
        release_year=2022,
        watched=True,
    )


@pytest.mark.parametrize(
    "initial_movies, movie_id, expected_result",
    [
        pytest.param([], "any", None, id="empty-case"),
        pytest.param(
            [
                Movie(
                    movie_id="first",
                    title="My Movie",
                    description="My Movie Description",
                    release_year=2022,
                    watched=True,
                ),
                Movie(
                    movie_id="second",
                    title="My Second Movie",
                    description="My Second Movie Description",
                    release_year=2023,
                    watched=False,
                ),
            ],
            "second",
            Movie(
                movie_id="second",
                title="My Second Movie",
                description="My Second Movie Description",
                release_year=2023,
                watched=False,
            ),
            id="movie-found",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_by_id(
    mongo_movie_repo_fixture, initial_movies, movie_id, expected_result
):
    for movie in initial_movies:
        await mongo_movie_repo_fixture.create(movie)
    movie: Movie = await mongo_movie_repo_fixture.get_by_id(movie_id)
    assert movie == expected_result


@pytest.mark.parametrize(
    "initial_movies,searched_title,expected_movies",
    [
        pytest.param([], "random title", [], id="empty-case"),
        pytest.param(
            [
                Movie(
                    movie_id="first",
                    title="My Movie",
                    description="My Movie Description",
                    release_year=2022,
                    watched=True,
                ),
                Movie(
                    movie_id="second",
                    title="My Second Movie",
                    description="My Second Movie Description",
                    release_year=2023,
                    watched=False,
                ),
                Movie(
                    movie_id="first_remake",
                    title="My Movie",
                    description="My Movie Description remake of the first movie from 2022",
                    release_year=2025,
                    watched=True,
                ),
            ],
            "My Movie",
            [
                Movie(
                    movie_id="first",
                    title="My Movie",
                    description="My Movie Description",
                    release_year=2022,
                    watched=True,
                ),
                Movie(
                    movie_id="first_remake",
                    title="My Movie",
                    description="My Movie Description remake of the first movie from 2022",
                    release_year=2025,
                    watched=True,
                ),
            ],
            id="found-movies",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_by_title(
    mongo_movie_repo_fixture, initial_movies, searched_title, expected_movies
):
    for movie in initial_movies:
        await mongo_movie_repo_fixture.create(movie)
    movies = await mongo_movie_repo_fixture.get_by_title(title=searched_title)
    assert movies == expected_movies


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "skip,limit,expected_results",
    [
        pytest.param(
            0,
            0,
            [
                Movie(
                    movie_id="my-id",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                ),
                Movie(
                    movie_id="my-id-2",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                ),
                Movie(
                    movie_id="my-id-3",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                ),
            ],
        ),
        pytest.param(
            0,
            1,
            [
                Movie(
                    movie_id="my-id",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                )
            ],
        ),
        pytest.param(
            1,
            1,
            [
                Movie(
                    movie_id="my-id-2",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                )
            ],
        ),
    ],
)
async def test_get_by_title_pagination(
    mongo_movie_repo_fixture, skip, limit, expected_results
):
    movie_seed = [
        Movie(
            movie_id="my-id",
            title="My Movie",
            description="My description",
            release_year=1990,
        ),
        Movie(
            movie_id="my-id-2",
            title="My Movie",
            description="My description",
            release_year=1990,
        ),
        Movie(
            movie_id="my-id-3",
            title="My Movie",
            description="My description",
            release_year=1990,
        ),
    ]
    for movie in movie_seed:
        await mongo_movie_repo_fixture.create(movie)
    results = await mongo_movie_repo_fixture.get_by_title(
        title="My Movie", skip=skip, limit=limit
    )
    assert results == expected_results


@pytest.mark.asyncio
async def test_update(mongo_movie_repo_fixture):
    initial_movie = Movie(
        movie_id="first",
        title="My Movie",
        description="My Movie Description",
        release_year=2022,
        watched=True,
    )
    await mongo_movie_repo_fixture.create(initial_movie)
    await mongo_movie_repo_fixture.update(
        movie_id="first", update_parameters={"title": "My M0vie"}
    )
    updated_movie = await mongo_movie_repo_fixture.get_by_id("first")
    assert updated_movie == Movie(
        movie_id="first",
        title="My M0vie",
        description="My Movie Description",
        release_year=2022,
        watched=True,
    )


@pytest.mark.asyncio
async def test_update_fail(mongo_movie_repo_fixture):
    initial_movie = Movie(
        movie_id="first",
        title="My Movie",
        description="My Movie Description",
        release_year=2022,
        watched=True,
    )
    await mongo_movie_repo_fixture.create(initial_movie)
    with pytest.raises(RepositoryException):
        await mongo_movie_repo_fixture.update(
            movie_id="first", update_parameters={"id": "second"}
        )


@pytest.mark.asyncio
async def test_delete(mongo_movie_repo_fixture):
    # Setup
    initial_movie = Movie(
        movie_id="first",
        title="My Movie",
        description="My Movie Description",
        release_year=2022,
        watched=True,
    )
    await mongo_movie_repo_fixture.create(initial_movie)
    # Test
    await mongo_movie_repo_fixture.delete(movie_id="first")
    await mongo_movie_repo_fixture.delete(movie_id=secrets.token_hex(10))
    # Assert
    assert await mongo_movie_repo_fixture.get_by_id(movie_id="first") is None
