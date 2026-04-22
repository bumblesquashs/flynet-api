from typing import Optional, List

from fastapi_utils.api_model import APIModel


class GeneralResponse(APIModel):
    """General response with success/fail and a message"""

    message: str
    is_success: bool


class ImportResponse(APIModel):
    """For flight log upload responses"""

    message: str
    is_success: bool
    num_created: Optional[int]
    num_updated: Optional[int]