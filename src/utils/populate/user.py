from typing import List

from context.user import UserContext
from model.role import RoleModel
from model.user import UserModel, UserPopulateModel
from passlib.context import CryptContext

from model.user_profile import UserProfileModel, UserProfilePopulateModel
from schema.role import Role
from schema.user import User
from schema.user_profile import UserProfile
from sqlalchemy.orm import Session
from utils.database import get_first, insert_data


def insert_roles(db: Session) -> List[RoleModel]:
    roles = [
        RoleModel(id=1, slug="admin", name="Administrator"),
        RoleModel(id=2, slug="user", name="User")
    ]

    return insert_data(db, Role, roles, RoleModel)

def insert_profiles(db: Session) -> List[UserProfileModel]:
    profiles = [
        UserProfilePopulateModel(
            id=1,
            bio='james test bio',
            theme='',
            ui_mode='light',
            image_uuid=None,
            image_path=''
        ),
        UserProfilePopulateModel(
            id=2,
            bio='i dunno',
            theme='',
            ui_mode='dark',
            image_uuid = None,
            image_path = None,
        ),
        UserProfilePopulateModel(
            id=3,
            bio='um ummm im flyin',
            theme='',
            ui_mode='system',
            image_uuid='abbyfour', # real users will get a uuid here
            image_path="static/profile/thumbnails/abbyfour_thumbnail.png",
        ),
        UserProfilePopulateModel(
            id=4,
            bio="",
            theme='',
            ui_mode='system',
            image_uuid='victoria',  # real users will get a uuid here
            image_path="static/profile/thumbnails/victoria_thumbnail.png",
        ),
    ]

    return insert_data(db, UserProfile, profiles, UserProfileModel)

def insert_users(db: Session, roles) -> List[UserModel]:
    context = UserContext(db=db, crypt_context=CryptContext(schemes=["bcrypt"], deprecated="auto"))
    admin_role: RoleModel = get_first(roles, lambda r: r.slug == "admin")
    user_role: RoleModel = get_first(roles, lambda r: r.slug == "user")

    users = [
        UserPopulateModel(
            id=1,
            email="james@jmward.net",
            username="jmward",
            nickname="James",
            role_id=admin_role.id,
            password=context.create_hash("Testing11*"),
            is_profile_public=False,
            user_profile_id=1,
        ),
        UserPopulateModel(
            id=2,
            username="projectb",
            email="bowie@rheault.me",
            nickname=None,
            role_id=user_role.id,
            password=context.create_hash("Testing12*"),
            is_profile_public=True,
            user_profile_id=2,
        ),
        UserPopulateModel(
            id=3,
            username="abby",
            nickname="abby :3",
            email="ivison.abby@gmail.com",
            role_id=admin_role.id,
            password=context.create_hash("password"),
            is_profile_public=True,
            user_profile_id=3,
        ),
        UserPopulateModel(
            id=4,
            username="victoria",
            nickname="victoria!",
            email="emmabyron73@gmail.com",
            role_id=user_role.id,
            password=context.create_hash("K!V6R^&9k2&o7%8W"),
            is_profile_public=True,
            user_profile_id=4,
        ),
    ]

    return insert_data(db, User, users, UserModel)
