from typing import Optional

from fastapi_utils.api_model import APIModel


class UserSettingsCreateModel(APIModel):
    """Model used when creating user settings, which is done upon sign up and user create"""

    theme: Optional[str] = None
    ui_mode: Optional[str] = None


class UserSettingsModel(UserSettingsCreateModel):
    """Full user settings model for reads"""
    id: int
 

class UserSettingsUpdateModel(UserSettingsCreateModel):
    pass


class UserSettingsPopulateModel(UserSettingsCreateModel):
    """Used with initial seed scripts; we need that ID, and ability to set profile pic"""
    id: int
