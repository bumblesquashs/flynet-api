from datetime import datetime

from core.settings import settings
from jose import jwt
from model.security import SecurityModel, UserTokenModel, SecurityPasswordResetModel
from model.user import UserModel


def create_access_token(user: UserModel, security_model: SecurityModel) -> str:
    token = UserTokenModel(
        iss=security_model.issuer,
        sub=str(user.id),
        iat=int(datetime.now().timestamp()),
        exp=security_model.expiration,
        aud=security_model.audience,
        azp=security_model.client_id,
        scopes=security_model.scopes,
    )

    encoded_jwt = jwt.encode(token.dict(), settings.TOKEN_SECRET, algorithm=settings.TOKEN_ALGORITHM)
    return encoded_jwt


def create_pass_reset_token(user: UserModel, security_model: SecurityPasswordResetModel) -> str:
    token = UserTokenModel(
        iss=security_model.issuer,
        sub=str(user.id),
        iat=int(datetime.utcnow().timestamp()),
        exp=security_model.expiration,
        aud=security_model.audience,
        azp=security_model.client_id,
        scopes=security_model.scopes,
    )

    encoded_jwt = jwt.encode(token.dict(), settings.TOKEN_SECRET, algorithm=settings.TOKEN_ALGORITHM)
    return encoded_jwt
