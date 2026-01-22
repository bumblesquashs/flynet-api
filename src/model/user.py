from datetime import datetime
from typing import List, Optional

from fastapi_utils.api_model import APIModel
from model.role import RoleModel


class UserModel(APIModel):
    """Basic user model for read operations."""

    id: Optional[int] = None
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    is_profile_public: Optional[bool] = False

    role_id: Optional[int] = None
    role: Optional[RoleModel] = None


class UserLoginModel(UserModel):
    """Used for the login method, that does the token oauth and also returns user fields"""
    token: str
    role: str


class UserCreateModel(APIModel):
    """User model use for creating new users"""

    username: str
    password: str
    email: Optional[str]
    nickname: Optional[str]
    is_profile_public: bool = False

    role_id: Optional[int] = None


class UserRegisterModel(APIModel):
    """User model use for registering new users"""

    username: str
    password: str
    email: Optional[str]
    nickname: str
    is_profile_public: bool


class UserUpdateModel(APIModel):
    """User model used for updates, only specified fields are updated."""

    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_profile_public: bool


class UserProfileUpdateModel(APIModel):
    """User Profile model used for updating current Users account details."""

    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
    is_profile_public: bool


class UserPopulateModel(UserCreateModel):
    """Used with initial seed scripts; we need that ID."""

    id: Optional[int]


class UserCredentialsModel(APIModel):
    """Used for authentication only."""

    username: str
    password: str
    scopes: Optional[List[str]]


class UserEmailModel(APIModel):
    """Used to search for user by email only."""

    email: str

class UserUsernameModel(APIModel):
    """Used to search for user by username only."""

    username: str

class AccountManagementEmailModel(APIModel):
    """Used to send account management emails."""

    email: str
    username: str
    message: str
