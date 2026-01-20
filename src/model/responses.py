from typing import Optional, List

from fastapi_utils.api_model import APIModel


class GeneralResponse(APIModel):
    """General response with success/fail and a message"""

    message: str
    is_success: bool
