import typing

from pydantic import BaseModel, validator


class CreateMovieBody(BaseModel):
    """
    CreateMovieBody is used as the body for the create movie endpoint.
    """

    title: str
    description: str
    release_year: int
    watched: bool = False

    @validator("title")
    def title_length_gt_three(cls, v):
        if len(v) < 4:
            raise ValueError("title's length must be greater than 3 characters.")
        return v

    @validator("description")
    def description_length_gt_three(cls, v):
        if len(v) < 4:
            raise ValueError("description's length must be greater than 3 characters.")
        return v

    @validator("release_year")
    def release_year_gt_1900(cls, v):
        if v < 1900:
            raise ValueError("release_year's must be greater than 1900.")
        return v


class MovieCreatedResponse(BaseModel):
    id: str


class MovieResponse(MovieCreatedResponse):
    title: str
    description: str
    release_year: int
    watched: bool


class MovieUpdateBody(BaseModel):
    title: typing.Optional[str] = None
    description: typing.Optional[str] = None
    release_year: typing.Optional[int] = None
    watched: typing.Optional[bool] = None
