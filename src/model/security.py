from datetime import datetime, timedelta
from typing import Any, List, Optional, Union

from core.settings import Settings
from fastapi_utils.api_model import APIModel
from pydantic import BaseModel


class UserTokenModel(APIModel):
    """A model that represent the JWT access token we're using, OAuth2 compliant-ish."""

    iss: str
    sub: str
    aud: Union[str, List[str]]
    azp: Optional[str] = None
    exp: int
    iat: int
    scopes: str

    @property
    def user_id(self):
        return self.sub


class SecurityModel(APIModel):
    """Convenience class that lets us map some common things we need to create a token."""

    audience: str
    issuer: str
    client_id: Optional[str] = None
    expiration: int
    scopes: Optional[str] = None

    def __init__(self, settings: Settings, client_id: Optional[str], scopes: Optional[List], **data: Any):
        data["audience"] = f"{settings.SERVER_SCHEME}://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
        data["issuer"] = f"{settings.SERVER_SCHEME}://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
        data["client_id"] = client_id
        data["scopes"] = " ".join(scopes)

        timestamp = (datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRES_MINUTES)).timestamp()
        data["expiration"] = int(timestamp)

        super().__init__(**data)


class SecurityPasswordResetModel(APIModel):
    """Class that lets us create a token that expires in an hour and can only be used once."""

    audience: str
    issuer: str
    client_id: Optional[str] = None
    expiration: int
    scopes: Optional[str] = None

    def __init__(self, settings: Settings, client_id: Optional[str], scopes: Optional[List], **data: Any):
        data["audience"] = f"{settings.SERVER_SCHEME}://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
        data["issuer"] = f"{settings.SERVER_SCHEME}://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
        data["client_id"] = client_id
        data["scopes"] = " ".join(scopes)

        timestamp = (datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRES_MINUTES_PASS_RESET)).timestamp()
        data["expiration"] = int(timestamp)

        super().__init__(**data)


class TokenResponse(BaseModel):
    """Response expected by OAuth2 compliant clients with the token."""

    access_token: str
    token_type: str = "bearer"
    role: str
