from datetime import datetime
from typing import List, Optional

from fastapi_utils.api_model import APIModel
from model.role import RoleModel


class UserModel(APIModel):
    """Basic user model for read operations."""

    id: Optional[int] = None
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    login_last_time: Optional[datetime] = None
    login_count: Optional[int] = None

    role_id: Optional[int] = None
    role: Optional[RoleModel] = None


class UserCreateModel(APIModel):
    """User model use for creating new users"""

    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None


class UserRegisterModel(APIModel):
    """User model use for reigstering new users"""

    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdateModel(APIModel):
    """User model used for updates, only specified fields are updated."""

    email: str
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None


class UserProfileUpdateModel(APIModel):
    """User Profile model used for updating current Users account details."""

    email: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserPopulateModel(UserCreateModel):
    """Used with initial seed scripts; we need that ID."""

    id: Optional[int]


class UserCredentialsModel(APIModel):
    """Used for authentication only."""

    email: str
    password: str
    scopes: Optional[List[str]]


class UserEmailModel(APIModel):
    """Used to search for user by email only."""

    email: str

class AccountManagementEmailModel(APIModel):
    """Used to send account management emails."""

    email: str
    name: str
    message: str
