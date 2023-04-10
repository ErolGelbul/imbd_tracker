import abc
import typing

from api.entities.movie import Movie


class RepositoryException(Exception):
    pass


class MovieRepository(abc.ABC):
    async def create(self, movie: Movie):
        """
        Inserts a movie into the database.

        Raises RepositoryException of failure.
        """
        raise NotImplementedError

    async def get_by_id(self, movie_id: str) -> typing.Optional[Movie]:
        """
        Retrieves a Movie by it's ID and if the movie is not found it will return None.
        """
        raise NotImplementedError

    async def get_by_title(
        self, title: str, skip: int = 0, limit: int = 1000
    ) -> typing.List[Movie]:
        """
        Returns a list of movies which share the same title.
        """
        raise NotImplementedError

    async def update(self, movie_id: str, update_parameters: dict):
        """
        Update a movie by it's id.
        """
        raise NotImplementedError

    async def delete(self, movie_id: str):
        """
        Deletes a movie by it's id.

        Raises RepositoryException of failure.
        """
        raise NotImplementedError
