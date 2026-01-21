from typing import List, Optional, Tuple

import requests
from jose import ExpiredSignatureError, jwt

from core.db import build_keyword_query, build_query_sort
from core.settings import settings
from model.requests import EmailRequestBody
from model.responses import GeneralResponse
from model.user import (
    UserCreateModel,
    UserCredentialsModel,
    UserModel,
    UserProfileUpdateModel,
    UserRegisterModel,
    UserUpdateModel,
)
from passlib.context import CryptContext
from schema.role import Role
from schema.user import User
from sqlalchemy.orm import Session


class UserContext:
    def __init__(self, db: Session, crypt_context: CryptContext):
        self.db = db
        self.crypt_context = crypt_context

    def create_hash(self, password: str):
        """Create a password hash using Bcrypt"""
        return self.crypt_context.hash(password)

    def validate_credentials(self, credentials: UserCredentialsModel) -> Optional[UserModel]:
        """Validate that the email and password matches what we have in the database."""
        user = self.db.query(User).filter(User.email == credentials.email).first()

        if not user:
            return None

        if self.crypt_context.verify(credentials.password, user.password):
            return UserModel.from_orm(user)

        return None

    def validate_token(self, token: str) -> Optional[UserModel]:
        """Validate that the token is valid and matches a user in the database"""
        options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}

        try:
            decoded = jwt.decode(token=token, key=settings.TOKEN_SECRET,
                                 algorithms=settings.TOKEN_ALGORITHM, options=options)

        except ExpiredSignatureError as error:
            print(f'Unable to decode the token, error: {error}')
            return None

        user = self.db.query(User).filter(User.id == decoded["sub"]).first()

        if not user:
            return None

        return UserModel.from_orm(user)

    def search(self, query: str, limit: int, offset: int, sort: str, sort_desc: bool) -> Tuple[List[UserModel], int]:
        columns = [User.first_name, User.last_name, User.email, Role.name]
        db_query = build_keyword_query(columns, query, self.db.query(User).join(Role))
        db_query = build_query_sort(columns, sort, sort_desc, db_query)

        user_count = db_query.count()

        users_model: List[UserModel] = []
        users = db_query.offset(offset).limit(limit).all()
        for user in users:
            users_model.append(UserModel.from_orm(user))

        return users_model, user_count

    def get(self, user_id: int) -> Optional[UserModel]:
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return None

        return UserModel.from_orm(user)

    def get_from_email(self, email: str) -> Optional[UserModel]:
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return None

        return UserModel.from_orm(user)

    def send_email(self, user_id: int, email_request: EmailRequestBody) -> GeneralResponse:
        existing_user: User = self.db.query(User).filter(User.id == user_id).first()

        if existing_user is None:
            return GeneralResponse(message="Email not found", is_success=False)

        api_key = settings.MAILGUN_API_KEY
        domain = settings.MAILGUN_DOMAIN

        email_body = {
            "from": "FlyNet <no-reply@flynet.placeholder>",
            "to": [f"{existing_user.first_name} {existing_user.last_name}", existing_user.email],
            "subject": email_request.subject,
            "template": "password-reset-flynet",
            "v:url": email_request.message,
        }

        post_result = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data=email_body
        )

        if post_result.status_code != 200:
            return GeneralResponse(message=f"Email send failure: {post_result.status_code} {post_result.text}",
                                   is_success=False)
        print(
            f'Email sent to {existing_user.email}\nSubject: {email_request.subject}\nEmail Message: {email_request.message}')

        return GeneralResponse(message="all good!", is_success=True)


    def create(self, user: UserCreateModel) -> Optional[UserModel]:
        user.password = self.create_hash(user.password)
        role: Role = self.db.query(Role).filter(Role.id == user.role_id).first()

        db_user = User(**user.dict())

        if role is not None:
            db_user.role = role

        self.db.add(db_user)
        self.db.commit()

        added_user: User = self.db.query(User).filter(User.email == user.email).first()

        if not added_user:
            return None

        return UserModel.from_orm(added_user)

    def register(self, user: UserRegisterModel) -> Optional[UserModel]:

        user.password = self.create_hash(user.password)

        db_user = User(**user.dict())
        db_user.role_id = 2

        self.db.add(db_user)
        self.db.commit()

        added_user: User = self.db.query(User).filter(User.id == db_user.id).first()

        if not added_user:
            return None

        return UserModel.from_orm(added_user)

    def update(self, user_id: int, user: UserUpdateModel) -> Optional[UserModel]:
        existing_user: User = self.db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            return None

        if user.password:
            user.password = self.create_hash(user.password)
            existing_user.password = user.password

        existing_user.first_name = user.first_name
        existing_user.last_name = user.last_name
        existing_user.email = user.email

        role: Role = self.db.query(Role).filter(Role.id == user.role_id).first()
        if role is not None:
            existing_user.role = role
            existing_user.role_id = role.id
        else:
            existing_user.role = None
            existing_user.role_id = None

        self.db.commit()

        updated_user: User = self.db.query(User).filter(User.id == user_id).first()

        if not updated_user:
            return None

        return UserModel.from_orm(updated_user)

    def update_profile(self, user_id: int, user: UserProfileUpdateModel) -> Optional[UserModel]:
        existing_user = self.db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            return None

        if user.password:
            user.password = self.create_hash(user.password)
            existing_user.password = user.password

        if user.first_name:
            existing_user.first_name = user.first_name

        if user.last_name:
            existing_user.last_name = user.last_name

        if user.email:
            existing_user.email = user.email

        self.db.commit()

        updated_user: User = self.db.query(User).filter(User.id == user_id).first()

        if not updated_user:
            return None

        return UserModel.from_orm(updated_user)

    def delete(self, user_id: int) -> Optional[UserModel]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        result = UserModel.from_orm(user)

        self.db.delete(user)
        self.db.commit()

        return result
