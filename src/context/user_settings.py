from typing import Optional


from model.user_settings import UserSettingsModel, UserSettingsUpdateModel
from sqlalchemy.orm import Session

from schema.user_settings import UserSettings


class UserSettingsContext:
    def __init__(self, db: Session):
        self.db = db


    def get(self, user_settings_id: int) -> Optional[UserSettingsModel]:
        user_settings = self.db.query(UserSettings).filter(UserSettings.id == user_settings_id).first()

        if not user_settings:
            return None

        return UserSettings.from_orm(user_settings)


    def update(self, user_settings_id: int, user_settings: UserSettingsUpdateModel) -> Optional[UserSettingsModel]:
        existing_user_settings: UserSettings = self.db.query(UserSettings).filter(UserSettings.id == user_settings_id).first()
        if not existing_user_settings:
            return None

        # Iterate over settings object's fields to set the fields in the db object
        # This is less clean but much more concise than specifying all fields again
        user_settings_dict = vars(user_settings)
        for key in user_settings_dict:
            if user_settings_dict[key] is not None:
                setattr(existing_user_settings, key, user_settings_dict[key])

        self.db.commit()

        updated_settings: UserSettings = self.db.query(UserSettings).filter(UserSettings.id == user_settings_id).first()

        if not updated_settings:
            return None

        return UserSettingsModel.from_orm(updated_settings)


