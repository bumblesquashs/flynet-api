from core.db import Base
from sqlalchemy import Column, String


class UserSettings(Base):
    ui_mode = Column(String)
    theme = Column(String)



