# noinspection PyPackageRequirements
import pytest

# noinspection PyUnresolvedReferences
from api._tests.fixture import memory_movie_repo_fixture
from api.entities.movie import Movie
from api.repository.movie.abstractions import RepositoryException


@pytest.mark.asyncio
async def test_create(memory_movie_repo_fixture):
    movie = Movie(
        movie_id="test",
        title="My Movie",
        description="My description",
        release_year=1990,
    )
    await memory_movie_repo_fixture.create(movie)
    assert await memory_movie_repo_fixture.get_by_id("test") is movie


@pytest.mark.parametrize(
    "movies_seed,movie_id,expected_result",
    [
        pytest.param([], "my-id", None, id="empty"),
        pytest.param(
            [
                Movie(
                    movie_id="my-id",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                )
            ],
            "my-id",
            Movie(
                movie_id="my-id",
                title="My Movie",
                description="My description",
                release_year=1990,
            ),
            id="actual-movie",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_by_id(
    memory_movie_repo_fixture, movies_seed, movie_id, expected_result
):
    for movie in movies_seed:
        await memory_movie_repo_fixture.create(movie)
    # noinspection PyTypeChecker
    movie = await memory_movie_repo_fixture.get_by_id(movie_id=movie_id)
    assert movie == expected_result


@pytest.mark.parametrize(
    "movies_seed,movie_title,expected_results",
    [
        pytest.param([], "some-title", [], id="empty-results"),
        pytest.param(
            [
                Movie(
                    movie_id="my-id",
                    title="My Movie",
                    description="My description",
                    release_year=1990,
                )
            ],
            "some-title",
            [],
            id="empty-results-2",
        ),
        pytest.param(
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
            ],
            "My Movie",
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
            ],
            id="results",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_by_title(
    memory_movie_repo_fixture, movies_seed, movie_title, expected_results
):
    for movie in movies_seed:
        await memory_movie_repo_fixture.create(movie)
    # noinspection PyTypeChecker
    result = await memory_movie_repo_fixture.get_by_title(title=movie_title)
    assert result == expected_results


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
    memory_movie_repo_fixture, skip, limit, expected_results
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
        await memory_movie_repo_fixture.create(movie)
    results = await memory_movie_repo_fixture.get_by_title(
        title="My Movie", skip=skip, limit=limit
    )
    assert results == expected_results


@pytest.mark.asyncio
async def test_update(memory_movie_repo_fixture):
    await memory_movie_repo_fixture.create(
        Movie(
            movie_id="my-id-2",
            title="My Movie",
            description="My description",
            release_year=1990,
        )
    )
    await memory_movie_repo_fixture.update(
        movie_id="my-id-2",
        update_parameters={
            "title": "My updated Movie",
            "description": "My updated description",
            "release_year": 2010,
            "watched": True,
        },
    )
    movie = await memory_movie_repo_fixture.get_by_id("my-id-2")
    assert movie == Movie(
        movie_id="my-id-2",
        title="My updated Movie",
        description="My updated description",
        release_year=2010,
        watched=True,
    )


@pytest.mark.asyncio
async def test_update_fail(memory_movie_repo_fixture):
    await memory_movie_repo_fixture.create(
        Movie(
            movie_id="my-id-2",
            title="My Movie",
            description="My description",
            release_year=1990,
        )
    )
    with pytest.raises(RepositoryException):
        await memory_movie_repo_fixture.update(
            movie_id="my-id-2", update_parameters={"id": "fail"}
        )


@pytest.mark.asyncio
async def test_delete(memory_movie_repo_fixture):
    await memory_movie_repo_fixture.create(
        Movie(
            movie_id="my-id-2",
            title="My Movie",
            description="My description",
            release_year=1990,
        )
    )
    await memory_movie_repo_fixture.delete("my-id-2")
    assert await memory_movie_repo_fixture.get_by_id("my-id-2") is None
