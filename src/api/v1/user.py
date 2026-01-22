from typing import List, Optional, Union

from model.responses import GeneralResponse

from context.role import RoleContext
from context.user import UserContext
from core.dependencies import get_crypt_context, get_db, get_user
from core.security import create_access_token, create_pass_reset_token
from core.settings import settings
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter
from model import SearchQuery, SearchResponse
from model.requests import EmailRequestBody
from model.role import RoleModel
from model.responses import GeneralResponse
from model.security import SecurityModel, TokenResponse, UserTokenModel, SecurityPasswordResetModel
from model.user import UserCreateModel, UserModel, UserProfileUpdateModel, UserRegisterModel, UserUpdateModel, \
    UserEmailModel, AccountManagementEmailModel
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

router = InferringRouter()


@router.get("/")
def search(
        q: SearchQuery = Depends(),
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),  # noqa
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> SearchResponse[UserModel]:
    """Perform a user search, allows basic keyword search by first and last name, and email."""

    context = UserContext(db, crypt_context=crypt_context)
    users, user_count = context.search(q.query, q.limit, q.offset, q.sort, q.sort_desc)

    return SearchResponse(items=users, total=user_count)


@router.post("/password")
def email(
        user: UserEmailModel,
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> Union[GeneralResponse, TokenResponse]:
    """
    Search for user by email, if found create a JWT to send to user to reset their password.
    """

    context = UserContext(db=db, crypt_context=crypt_context)
    user = context.get_from_email(user.email)

    if user is None:
        return GeneralResponse(message=f'No user found with associated email {user.email}', is_success=False)
    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials specified.")

    role_context = RoleContext(db=db)
    scopes = role_context.get_scopes(user.role.slug)

    security_model = SecurityPasswordResetModel(settings=settings, client_id=None, scopes=scopes)
    token_response = TokenResponse(access_token=create_pass_reset_token(user, security_model), role=user.role.slug)
    access_token = token_response.access_token

    url = f'{settings.BACKEND_CORS_ORIGINS[0]}''/reset?token='f'{access_token}'

    request_body = EmailRequestBody(message=url, subject='Password Reset for FlyNet')
    context.send_email(user_id=user.id, email_request=request_body)

    return token_response

@router.post("/account_management_email")
def account_management_email(
        email_content: AccountManagementEmailModel,
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> GeneralResponse:
    """
    Sends account management email.
    """

    context = UserContext(db=db, crypt_context=crypt_context)
    user = context.get_from_email(email_content.email)

    if user is None:
        return GeneralResponse(message="No account with this email was found.", is_success=False)
    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials specified.")

    request_body = EmailRequestBody(
                                    message=f'{email_content.message} \n\nPlease make the requested changes to the account with the email {email_content.email}. ',
                                    subject=f'{email_content.name} has requested a change to their account'
                                )
    context.send_account_management_email(user_id=user.id, email_request=request_body)

    return GeneralResponse(message="Your email has been sent.", is_success=True)


@router.put("/password")
def reset(
        user: UserProfileUpdateModel,
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
        token: Optional[str] = None,
) -> UserModel:
    """Reset user password if token is valid."""
    context = UserContext(db, crypt_context)
    existing_user = context.validate_token(token)

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found or token invalid.")

    try:
        updated_user = context.update_profile(existing_user.id, user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email must be unique.") from e

    if updated_user is None:
        raise HTTPException(status_code=400, detail="Could not update user.")

    return updated_user


@router.get("/me")
def own_profile(
        db: Session = Depends(get_db),
        current_user: UserTokenModel = Security(get_user, scopes=["me"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Get the user details of the currently logged-in user."""

    context = UserContext(db, crypt_context=crypt_context)
    user = context.get(int(current_user.sub))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


# Note: this must be located above the endpoint with the variable GET route, so that this matches first
@router.get("/role")
def get_roles(
        db: Session = Depends(get_db),
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),  # noqa
) -> List[RoleModel]:
    """Get list of roles in the system for user management"""
    context = RoleContext(db)

    return context.get_roles()


@router.get("/{user_id}")
def details(
        user_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Get the details of a user with the specified ID."""
    context = UserContext(db, crypt_context=crypt_context)
    user = context.get(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


@router.post("/")
def create(
        user: UserCreateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Create a new user entity, and assign a role."""
    context = UserContext(db, crypt_context=crypt_context)
    try:
        created_user = context.create(user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Username must be unique. Email, if provided, must also be unique.") from e

    if created_user is None:
        raise HTTPException(status_code=400, detail="Could not create user.")

    return created_user


@router.post("/register")
def register(
        user: UserRegisterModel,
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Create a new user entity, and assign a role."""
    context = UserContext(db, crypt_context=crypt_context)
    try:
        created_user = context.register(user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if created_user is None:
        raise HTTPException(status_code=400, detail="Could not create user.")

    return created_user


@router.put("/{user_id}")
def update(
        user_id: int,
        user: UserUpdateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Update an existing user entity, with the ID specified."""
    context = UserContext(db, crypt_context=crypt_context)
    try:
        updated_user = context.update(user_id, user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Username and email must be unique") from e

    if updated_user is None:
        raise HTTPException(status_code=400, detail="Could not update user.")

    return updated_user


@router.delete("/{user_id}")
def delete(
        user_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Delete the user with the specified ID."""
    context = UserContext(db, crypt_context)
    user = context.delete(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


@router.put("/profile/")
def profile(
        user: UserProfileUpdateModel,
        current_user: UserTokenModel = Security(get_user, scopes=["me"]),
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
        # pylint: disable=unused-argument
) -> UserModel:
    """Update current user entity."""
    context = UserContext(db, crypt_context=crypt_context)

    try:
        updated_user = context.update_profile(int(current_user.sub), user)

    except IntegrityError as error:
        raise HTTPException(status_code=400, detail="Username and email must be unique.") from error

    if updated_user is None:
        raise HTTPException(status_code=400, detail="Could not update user.")

    return updated_user


@router.delete("/delete_profile/")
def delete_profile(
        db: Session = Depends(get_db),
        current_user: UserTokenModel = Security(get_user, scopes=["me"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Deletes the current user entity."""
    context = UserContext(db, crypt_context=crypt_context)
    user = context.delete(int(current_user.sub))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user
