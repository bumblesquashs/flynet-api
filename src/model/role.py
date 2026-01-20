from typing import Optional

from fastapi_utils.api_model import APIModel


class RoleModel(APIModel):
    """Basic role definition."""

    id: Optional[int] = None
    slug: str
    name: str
