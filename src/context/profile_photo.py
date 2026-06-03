import os
import uuid
from typing import Optional

from fastapi import UploadFile
from openpyxl.drawing.image import PILImage

from sqlalchemy.orm import Session

from schema.user import User


profile_image_base_path = '../ProfileImages/'

# Supported image formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
ALLOWED_CONTENT_TYPES = {
    'image/png', 'image/jpeg', 'image/jpg', 'application/octet-stream'
}


def _is_valid_image(file: UploadFile) -> bool:
    """
    Check if the uploaded file is a valid image format
    """
    if not file.filename:
        print('validate profile photo debug:   no filename')
        return False

    # Check file extension
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in ALLOWED_EXTENSIONS:
        print('validate profile photo debug:   bad file extension')
        return False

    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        print('validate profile photo debug:   bad content type')
        return False

    return True


def _ensure_directory_exists():
    """
    Ensure the DatabasePhotos directory exists
    """
    if not os.path.exists(profile_image_base_path):
        os.makedirs(profile_image_base_path)


def _create_thumbnail(image_path: str, thumbnail_path: str, max_width: int = 250) -> bool:
    """
    Create a thumbnail version of the image with max width of 250px
    """
    try:
        with PILImage.open(image_path) as img:
            # Convert to RGB if it's in a different mode (like RGBA)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Calculate new dimensions maintaining aspect ratio
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)

            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False


def save_new_image(image: UploadFile) -> Optional[str]:
    """
    Generate UUID for file name, save image to disk, make thumbnail of image, save that too, return UUID
    Returns None if fail
    """
    try:
        # Validate image
        if not _is_valid_image(image):
            print(f"new profile photo debug: invalid image format: {image.filename}")
            return None

        # Ensure directory exists
        _ensure_directory_exists()

        # Generate UUID
        image_uuid = str(uuid.uuid4())

        # Get file extension
        file_ext = os.path.splitext(image.filename.lower())[1]
        if file_ext == '.jpeg':
            file_ext = '.jpg'  # Normalize jpeg to jpg

        # Define file paths
        image_filename = f"{image_uuid}{file_ext}"
        thumbnail_filename = f"{image_uuid}_thumbnail.jpg"

        image_path = os.path.join(profile_image_base_path, image_filename)
        thumbnail_path = os.path.join(profile_image_base_path, thumbnail_filename)

        # Save original image - TODO: re-use this if we support having full res flight photos
        contents = image.file.read()
        with open(image_path, "wb") as f:
            f.write(contents)

        # Create thumbnail
        if not _create_thumbnail(image_path, thumbnail_path):
            print('new profile photo debug: thumbnail creation failed, cleaning up')
            # If thumbnail creation fails, clean up and return None
            if os.path.exists(image_path):
                os.remove(image_path)
            return None

        # Reset file position for potential future reads
        image.file.seek(0)

        return image_uuid

    except Exception as e:
        print(f"new profile photo debug: error saving image: {e}")
        return None


def update_image(image: UploadFile, existing_image_uuid: str) -> bool:
    """
    Replace image at existing_image_uuid, and thumbnail
    Returns False if image cannot be found or error is hit
    """
    try:
        # Validate image
        if not _is_valid_image(image):
            print(f"update profile photo debug: invalid image format: {image.filename}")
            return False

        # Get file extension
        file_ext = os.path.splitext(image.filename.lower())[1]
        if file_ext == '.jpeg':
            file_ext = '.jpg'  # Normalize jpeg to jpg

        # Define file paths
        image_filename = f"{existing_image_uuid}{file_ext}"
        thumbnail_filename = f"{existing_image_uuid}_thumbnail.jpg"

        image_path = os.path.join(profile_image_base_path, image_filename)
        thumbnail_path = os.path.join(profile_image_base_path, thumbnail_filename)

        # Find existing image files (they might have different extensions)
        existing_image_path = None
        existing_thumbnail_path = None

        # Look for existing files with any supported extension
        for ext in ALLOWED_EXTENSIONS:
            potential_path = os.path.join(profile_image_base_path, f"{existing_image_uuid}{ext}")
            if os.path.exists(potential_path):
                existing_image_path = potential_path
                break

        # Look for existing thumbnail
        potential_thumbnail = os.path.join(profile_image_base_path, f"{existing_image_uuid}_thumbnail.jpg")
        if os.path.exists(potential_thumbnail):
            existing_thumbnail_path = potential_thumbnail

        if not existing_image_path:
            print(f"update profile photo debug: existing image not found for UUID: {existing_image_uuid}")
            return False

        # Remove old files
        if existing_image_path:
            os.remove(existing_image_path)
        if existing_thumbnail_path:
            os.remove(existing_thumbnail_path)

        # Save new image
        contents = image.file.read()
        with open(image_path, "wb") as f:
            f.write(contents)

        # Create new thumbnail
        if not _create_thumbnail(image_path, thumbnail_path):
            print(f"update profile photo debug: create thumbnail failed, cleaning up")
            if os.path.exists(image_path):
                os.remove(image_path)
            return False

        # Reset file position for potential future reads
        image.file.seek(0)

        return True

    except Exception as e:
        print(f"update profile photo debug: exception updating image: {e}")
        return False


class ProfilePhotoContext:
    def __init__(self, db: Session):
        self.db = db

    def set_profile_photo(self, user_id: int, image):
        '''
        Used to set the image on user profile create or user profile image update
        :param user_profile_id:
        :param user_id:
        :param image:
        :return:
        '''
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            print('profile photo debug:   no user object')
            return None

        if user.image_uuid:
            # already has a photo, so update, return bool
            result = update_image(image, user.image_uuid)
            if result:
                print('update profile photo debug:   done')
            return result

        # doesn't have one yet
        uuid_str = save_new_image(image)

        if uuid_str is None:
            print('create profile photo debug:   no uuid was returned from create, failing')
            return False  # Failure!

        user.image_uuid = uuid_str
        user.image_path = f'static/profile/thumbnails/{uuid_str}_thumbnail.jpg'

        self.db.commit()

        print('create profile photo debug:   done')
        return True




