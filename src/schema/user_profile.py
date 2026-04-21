from core.db import Base
from sqlalchemy import Column, String, Integer


class UserProfile(Base):
    bio = Column(String)
    image_uuid = Column(String)
    image_path = Column(String)
    ui_mode = Column(String)
    theme = Column(String)



