from typing import List, Optional, Union

from fastapi import Depends, HTTPException, Security, UploadFile, File
from fastapi_utils.inferring_router import InferringRouter
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from context.profile_photo import ProfilePhotoContext
from context.role import RoleContext
from context.user import UserContext
from core.dependencies import get_crypt_context, get_db, get_user
from core.security import create_pass_reset_token
from core.settings import settings
from model import SearchResponse
from model.requests import EmailRequestBody
from model.responses import GeneralResponse
from model.role import RoleModel
from model.security import TokenResponse, UserTokenModel, SecurityPasswordResetModel
from model.user import UserRegisterModel, UserUpdateModel, \
    UserEmailModel, AccountManagementEmailModel, UserModelPrivate, UserModelPublic
from schema.user import User

router = InferringRouter()


@router.get("/me")
def own_profile(
        db: Session = Depends(get_db),
        current_user: UserTokenModel = Security(get_user, scopes=["me"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModelPrivate:
    """Get the user details of the currently logged-in user."""

    context = UserContext(db, crypt_context=crypt_context)
    user = context.get_self(int(current_user.sub))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user



@router.put("/me")
def update_self(
        user: UserUpdateModel,
        current_user: UserTokenModel = Security(get_user, scopes=["me"]),
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
        # pylint: disable=unused-argument
) -> UserModelPrivate:
    """
    Update current user entity. Gets user id from token.
    Can send any combination of fields including email and password and username...
    """
    context = UserContext(db, crypt_context=crypt_context)

    try:
        updated_user = context.update_self(int(current_user.sub), user)

    except IntegrityError as error:
        raise HTTPException(status_code=400, detail="Username and email must be unique.") from error

    if updated_user is None:
        raise HTTPException(status_code=400, detail="Could not update user.")

    return updated_user


@router.get("/role")
def get_roles(
        db: Session = Depends(get_db),
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),  # noqa
) -> List[RoleModel]:
    """Get list of roles in the system for user management"""
    context = RoleContext(db)

    return context.get_roles()



@router.get("/search/{query}")
def search_profiles(
        query: str,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> SearchResponse[UserModelPublic]:
    """Search public profiles by username."""
    context = UserContext(db, crypt_context=crypt_context)
    # TODO: we can use the pagination here if we want later
    users, count = context.public_search(query, limit=20, offset=0, sort="username", sort_desc=False)

    return SearchResponse(items=users, total=count)



@router.get("/user_id/{user_id}")
def get_profile_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModelPublic:
    """Get the public profile of a user with the specified ID."""
    context = UserContext(db, crypt_context=crypt_context)
    user = context.get_by_id_public(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


@router.get("/username/{username}")
def get_profile_by_username(
        username: str,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModelPublic:
    """Get the public profile of a user with the specified ID."""
    context = UserContext(db, crypt_context=crypt_context)
    user = context.get_by_username_public(username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


@router.put("/profile_photo")
def update_profile_photo(
        image: UploadFile = File(...),
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> GeneralResponse:
    """Update an existing user profile photo, with the ID specified."""

    profile_photo_context = ProfilePhotoContext(db)
    user_id = current_user.user_id

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail=f"Could not find associated user...")

    try:
        result = profile_photo_context.set_profile_photo(user_id, image)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e
    if result is None:
        raise HTTPException(status_code=400, detail=f"User with ID {user_id} not found")
    elif result is False:
        raise HTTPException(status_code=400, detail="Failed to save or process the image. Please ensure you uploaded a valid image file (PNG, JPG)")
    else:
        return GeneralResponse(
            is_success=True,
            message="Profile image updated successfully"
        )


# ====================================
#  Account Management Endpoints - Currently unused in UI
# ====================================

@router.post("/register")
def register(
        user: UserRegisterModel,
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModelPrivate:
    """Create a new user entity, and assign a role."""
    context = UserContext(db, crypt_context=crypt_context)
    try:
        created_user = context.register(user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if created_user is None:
        raise HTTPException(status_code=400, detail="Could not create user.")

    return created_user


@router.delete("/delete_self/")
def delete_self(
        db: Session = Depends(get_db),
        current_user: UserTokenModel = Security(get_user, scopes=["me"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModelPrivate:
    """Deletes the current user entity."""
    context = UserContext(db, crypt_context=crypt_context)
    user = context.delete(int(current_user.sub))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


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
        user: UserUpdateModel,
        db: Session = Depends(get_db),
        crypt_context: CryptContext = Depends(get_crypt_context),
        token: Optional[str] = None,
) -> UserModelPrivate:
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
