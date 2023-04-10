from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # General Settings
    enable_metrics: bool = Field(
        True,
        title="Enable metrics",
        description="Expose prometheus metrics if set to True. Default: True",
        env="ENABLE_METRICS"
    )
    # MongoDB Settings
    mongo_connection_string: str = Field(
        "mongodb://localhost:27017",
        title="MongoDB Movies Connection string",
        description="The connection string for the MongoDB database.",
        env="MONGODB_CONNECTION_STRING",
    )
    mongo_database_name: str = Field(
        "movie_track_db",
        title="MongoDB Movies Database name",
        description="The database name for the MongoDB Movies database.",
        env="MONGODB_DATABASE_NAME",
    )

    def __hash__(self) -> int:
        return 1


@lru_cache()
def settings_instance():
    """
    Settings instance to used as a Fast API dependency.
    """
    return Settings()
