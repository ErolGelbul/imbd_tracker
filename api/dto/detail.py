from pydantic import BaseModel


class DetailResponse(BaseModel):
    """
    DetailResponse represents a response associated with a detailed message.
    """

    message: str
