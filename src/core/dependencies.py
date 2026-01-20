from functools import lru_cache
from typing import Any, Iterator, Optional

from core.settings import settings
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi_utils.session import FastAPISessionMaker
from jose import jwt
from model.security import SecurityModel, UserTokenModel
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

oauth2_auth = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "me": "Get own data.",
        "admin": "Manage static data and user info global to the site.",
        "user": "For all usual user business.",
    },
)


def get_db() -> Iterator[Session]:
    yield from _get_api_session_maker().get_db()


@lru_cache()
def _get_api_session_maker() -> FastAPISessionMaker:
    return FastAPISessionMaker(settings.SQLALCHEMY_DATABASE_URI)


@lru_cache()
def get_crypt_context() -> CryptContext:
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_auth)) -> Any:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.TOKEN_SECRET,
            algorithms=[settings.TOKEN_ALGORITHM],
            audience=settings.AUDIENCE,
            issuer=settings.ISSUER,
        )

        user_token = UserTokenModel(**payload)
        user_scopes = user_token.scopes.split() if user_token.scopes is not None else []

        for required_scope in security_scopes.scopes:
            if required_scope not in user_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=f"Don't have required permission: {required_scope}"
                )

    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials") from e

    return user_token
