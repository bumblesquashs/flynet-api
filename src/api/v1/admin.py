
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from context.user import UserContext
from core.dependencies import get_crypt_context, get_db, get_user
from model import SearchQuery, SearchResponse
from model.security import UserTokenModel
from model.user import UserCreateModelAdmin, UserModel, UserUpdateModelAdmin

router = InferringRouter()


@router.get("/users")
def search(
        q: SearchQuery = Depends(),
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),  # noqa
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> SearchResponse[UserModel]:
    """Perform a user search, allows basic keyword search by first and last name, and email."""

    context = UserContext(db, crypt_context=crypt_context)
    users, user_count = context.admin_search(q.query, q.limit, q.offset, q.sort, q.sort_desc)

    return SearchResponse(items=users, total=user_count)


@router.get("/user/{user_id}")
def details(
        user_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),
        crypt_context: CryptContext = Depends(get_crypt_context),
) -> UserModel:
    """Get the details of a user with the specified ID."""
    context = UserContext(db, crypt_context=crypt_context)
    user = context.get(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


@router.post("/user")
def create(
        user: UserCreateModelAdmin,
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


@router.put("/user/{user_id}")
def update(
        user_id: int,
        user: UserUpdateModelAdmin,
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


@router.delete("/user/{user_id}")
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
