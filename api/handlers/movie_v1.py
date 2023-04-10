import dataclasses
import typing
import uuid
from collections import namedtuple
from functools import lru_cache

from fastapi import APIRouter, Body, Depends, Query, Path, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from jose import jwt, JWTError
from starlette import status
from starlette.responses import JSONResponse, Response

from api.dto.movie import (
    CreateMovieBody,
    MovieCreatedResponse,
    MovieResponse,
    MovieUpdateBody,
)
from api.entities.movie import Movie
from api.repository.movie.abstractions import MovieRepository, RepositoryException
from api.repository.movie.mongo import MongoMovieRepository
from api.dto.detail import DetailResponse
from api.settings import Settings, settings_instance

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


@lru_cache()
def movie_repository(settings: Settings = Depends(settings_instance)):
    """
    Movie repository instance to be used as a Fast API dependency.
    """
    return MongoMovieRepository(
        connection_string=settings.mongo_connection_string,
        database=settings.mongo_database_name,
    )


def pagination_params(
    skip: int = Query(0, title="Skip", description="The number of items to skip", ge=0),
    limit: int = Query(
        1000,
        title="Limit",
        description="The limit of the number of items returned",
        le=1000,
    ),
):
    Pagination = namedtuple("Pagination", ["skip", "limit"])
    return Pagination(skip=skip, limit=limit)


@router.post("/", status_code=201, response_model=MovieCreatedResponse)
async def post_create_movie(
    movie: CreateMovieBody = Body(..., title="Movie", description="The movie details"),
    repo: MovieRepository = Depends(movie_repository),
):
    """
    Creates a movie.
    """
    movie_id = str(uuid.uuid4())

    await repo.create(
        movie=Movie(
            movie_id=movie_id,
            title=movie.title,
            description=movie.description,
            release_year=movie.release_year,
            watched=movie.watched,
        )
    )
    return MovieCreatedResponse(id=movie_id)


@dataclasses.dataclass
class Token:
    name: str
    admin: bool


def authenticate_jwt(authorization: typing.Union[str, None] = Header(default=None)):
    token_secret = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCozMxH2Mo
4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0/IzW7yWR7QkrmBL7jTKEn5u
+qKhbwKfBstIs+bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyeh
kd3qqGElvW/VDL5AaWTg0nLVkjRo9z+40RQzuVaE8AkAFmxZzow3x+VJYKdjykkJ
0iT9wCS0DRTXu269V264Vf/3jvredZiKRkgwlL9xNAwxXFg0x/XFw005UWVRIkdg
cKWTjpBP2dPwVZ4WWC+9aGVd+Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbc
mwIDAQAB
-----END PUBLIC KEY-----"""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    token = authorization.split(" ")[1]
    try:
        token_payload = jwt.decode(token, token_secret, algorithms=["RS256"])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from e

    return Token(
        name=token_payload.get("name"), admin=token_payload.get("admin", False)
    )


@router.get(
    "/{movie_id}",
    responses={200: {"model": MovieResponse}, 404: {"model": DetailResponse}},
)
async def get_movie_by_id(
    movie_id: str, repo: MovieRepository = Depends(movie_repository)
):
    """
    Returns a Movie if found, None otherwise.
    """
    movie = await repo.get_by_id(movie_id=movie_id)
    if movie is None:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(
                DetailResponse(message=f"Movie with id {movie_id} is not found.")
            ),
        )
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        release_year=movie.release_year,
        watched=movie.watched,
    )


@router.get("/", response_model=typing.List[MovieResponse])
async def get_movies_by_title(
    title: str = Query(
        ..., title="Title", description="The title of the movie.", min_length=3
    ),
    pagination=Depends(pagination_params),
    repo: MovieRepository = Depends(movie_repository),
):
    """
    This handler returns movies by filtering their title.
    """
    movies = await repo.get_by_title(
        title, skip=pagination.skip, limit=pagination.limit
    )
    movies_return_value = []
    for movie in movies:
        movies_return_value.append(
            MovieResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                release_year=movie.release_year,
                watched=movie.watched,
            )
        )
    return movies_return_value


@router.patch(
    "/{movie_id}",
    responses={
        200: {"model": DetailResponse},
        400: {"model": DetailResponse},
    },
)
async def patch_update_movie(
    movie_id: str = Path(..., title="Movie ID", description="The id of the movie."),
    update_parameters: MovieUpdateBody = Body(
        ...,
        title="Update Body",
        description="The parameters of the movie to be updated.",
    ),
    repo: MovieRepository = Depends(movie_repository),
):
    """
    Updates a movie.
    """
    try:
        await repo.update(
            movie_id=movie_id,
            update_parameters=update_parameters.dict(
                exclude_unset=True, exclude_none=True
            ),
        )
        return DetailResponse(message="Movie updated.")
    except RepositoryException as e:
        return JSONResponse(
            status_code=400, content=jsonable_encoder(DetailResponse(message=str(e)))
        )


@router.delete("/{movie_id}", status_code=204)
async def delete_movie(
    movie_id: str = Path(..., title="Movie ID", description="The id of the movie."),
    repo: MovieRepository = Depends(movie_repository),
):
    await repo.delete(movie_id=movie_id)
    return Response(status_code=204)
