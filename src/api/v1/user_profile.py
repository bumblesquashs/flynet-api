from typing import Optional

from context.user_profile import UserProfileContext
from core.dependencies import get_db, get_user
from fastapi import Depends, HTTPException, Security, UploadFile, File
from fastapi_utils.inferring_router import InferringRouter
from fastapi.responses import Response

from model.responses import GeneralResponse
from model.user_profile import UserProfileModel, UserProfileUpdateModel
from model.security import UserTokenModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from schema.user import User

router = InferringRouter()

#
# @router.get("/profile_photo/{user_profile_id}")
# def profile_photo(
#         report_uuid: str,
#         qr_code: bool,
#         db: Session = Depends(get_db),
# ):
#     """Get the URL of a report for an appointment by report guid - for patients use"""
#     context = UserProfileContext(db)
#     byte_array = context.serve_profile(report_uuid, qr_code)
#
#     if byte_array is None:
#         raise HTTPException(status_code=404, detail="Appointment not found.")
#
#     return Response(content=byte_array, media_type="application/pdf")


@router.put("/profile_photo/{user_profile_id}")
def update_profile_photo(
        user_profile_id: int,
        image: UploadFile = File(...),
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> GeneralResponse:
    """Update an existing user profile photo, with the ID specified."""
    context = UserProfileContext(db)

    user = db.query(User).filter(User.id == current_user.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail=f"Could not find associated user model...")

    if not user.user_profile_id == user_profile_id:
        raise HTTPException(status_code=403, detail=f"Cannot update somebody else's profile photo!")

    try:
        result = context.set_profile_photo(user_profile_id, image)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e
    if result is None:
        raise HTTPException(status_code=400, detail=f"Profile with ID {user_profile_id} not found")
    elif result is False:
        raise HTTPException(status_code=400, detail="Failed to save or process the image. Please ensure you uploaded a valid image file (PNG, JPG)")
    else:
        return GeneralResponse(
            is_success=True,
            message="Profile image updated successfully"
        )


@router.put("/{user_profile_id}")
def update(
        user_profile_id: int,
        user_profile: UserProfileUpdateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> UserProfileModel:
    """Update an existing user profile, with the ID specified."""
    context = UserProfileContext(db)

    user = db.query(User).filter(User.id == current_user.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail=f"Could not find associated user model...")


    if not user.user_profile_id == user_profile_id:
        raise HTTPException(status_code=403, detail=f"Cannot update somebody else's profile!")

    try:
        updated_user_profile = context.update(user_profile_id, user_profile)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if updated_user_profile is None:
        raise HTTPException(status_code=400, detail=f"Could not update user profile...")

    return updated_user_profile
