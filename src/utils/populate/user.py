from typing import List

from context.user import UserContext
from model.role import RoleModel
from model.user import UserModel, UserPopulateModel
from passlib.context import CryptContext
from schema.role import Role
from schema.user import User
from sqlalchemy.orm import Session
from utils.database import get_first, insert_data


def insert_roles(db: Session) -> List[RoleModel]:
    roles = [
        RoleModel(id=1, slug="admin", name="Administrator"),
        RoleModel(id=2, slug="user", name="User")
    ]

    return insert_data(db, Role, roles, RoleModel)


def insert_users(db: Session, roles) -> List[UserModel]:
    context = UserContext(db=db, crypt_context=CryptContext(schemes=["bcrypt"], deprecated="auto"))
    admin_role: RoleModel = get_first(roles, lambda r: r.slug == "admin")
    user_role: RoleModel = get_first(roles, lambda r: r.slug == "user")

    users = [
        UserPopulateModel(
            id=1,
            email="james@jmward.net",
            role_id=admin_role.id,
            first_name="James",
            last_name="Ward",
            password=context.create_hash("Testing11*"),
        ),
        UserPopulateModel(
            id=2,
            email="bowie@bowie.bowie",
            role_id=user_role.id,
            first_name="Bowie Test",
            last_name="User",
            password=context.create_hash("Testing12*"),
        ),
    ]

    return insert_data(db, User, users, UserModel)
