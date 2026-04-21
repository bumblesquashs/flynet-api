from typing import Optional

from fastapi_utils.api_model import APIModel


class UserProfileCreateModel(APIModel):
    """Model used when creating a user profile, which is done upon sign up and user create"""

    bio: Optional[str] = None
    theme: Optional[str] = None
    ui_mode: Optional[str] = None


class UserProfileModel(UserProfileCreateModel):
    """Full user profile model for reads"""
    id: int
    image_uuid: Optional[str] = None
    image_path: Optional[str] = None
 

class UserProfileUpdateModel(UserProfileCreateModel):
    pass


class UserProfilePopulateModel(UserProfileCreateModel):
    """Used with initial seed scripts; we need that ID, and ability to set profile pic"""
    id: int
    image_uuid: Optional[str] = None
    image_path: Optional[str] = None
