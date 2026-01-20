
from fastapi_utils.api_model import APIModel


class EmailRequestBody(APIModel):
    """For password resets"""

    subject: str
    message: bool
