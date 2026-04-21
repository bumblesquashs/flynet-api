from context.role import RoleContext
from context.user import UserContext
from core.dependencies import get_crypt_context, get_db
from core.security import create_access_token
from core.settings import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.inferring_router import InferringRouter
from model.security import SecurityModel, TokenResponse
from model.user import UserCredentialsModel, UserLoginModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

router = InferringRouter()


@router.get("/status", tags=["Status"])
def status() -> dict:
    """
    Performs a basic health check and returns a response indicating API health.
    """
    return {"status": "Healthy"}


@router.post("/token", tags=["Token"])
def authenticate(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    crypt_context: CryptContext = Depends(get_crypt_context),
) -> TokenResponse:
    """
    Authenticate a user and create a JWT access to utilize for the API.
    """
    context = UserContext(db=db, crypt_context=crypt_context)
    auth_credentials = UserCredentialsModel(
        username=credentials.username, password=credentials.password, scopes=credentials.scopes
    )

    user = context.validate_credentials(auth_credentials)

    if user is None:
        return TokenResponse(access_token='fail', role='fail')
    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials specified.")

    role_context = RoleContext(db=db)
    scopes = role_context.get_scopes(user.role.slug)

    security_model = SecurityModel(settings=settings, client_id=credentials.client_id, scopes=scopes)

    return TokenResponse(access_token=create_access_token(user, security_model), role=user.role.slug)


@router.post("/auth/login", tags=["Auth"])
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserLoginModel:
    """
    Authenticate a user and create a JWT access to utilize for the API.
    """
    context = UserContext(db=db, crypt_context=crypt_context)
    auth_credentials = UserCredentialsModel(
        username=credentials.username, password=credentials.password, scopes=credentials.scopes
    )

    user = context.validate_credentials(auth_credentials)

    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials specified.")

    role_context = RoleContext(db=db)
    scopes = role_context.get_scopes(user.role.slug)

    security_model = SecurityModel(settings=settings, client_id=credentials.client_id, scopes=scopes)

    access_token = create_access_token(user, security_model)

    return UserLoginModel(
        id=user.id,
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        is_profile_public=user.is_profile_public,
        token=access_token,
        role=user.role.slug,
        role_id=user.role.id,
        user_profile=user.user_profile,
        user_profile_id=user.user_profile_id
    )