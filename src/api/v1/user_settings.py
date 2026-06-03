
from core.dependencies import get_db, get_user
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter

from model.user_settings import UserSettingsModel, UserSettingsUpdateModel
from context.user_settings import UserSettingsContext
from model.security import UserTokenModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from schema.user import User

router = InferringRouter()

@router.put("/{user_settings_id}")
def update(
        user_settings_id: int,
        user_settings: UserSettingsUpdateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> UserSettingsModel:
    """Update an existing user settings, with the ID specified."""
    context = UserSettingsContext(db)

    user = db.query(User).filter(User.id == current_user.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail=f"Could not find associated user model...")


    if not user.user_settings_id == user_settings_id:
        raise HTTPException(status_code=403, detail=f"Cannot update somebody else's settings!")

    try:
        updated_user_settings = context.update(user_settings_id, user_settings)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if updated_user_settings is None:
        raise HTTPException(status_code=400, detail=f"Could not update user settings...")

    return updated_user_settings
