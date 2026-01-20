from core.db import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped

from schema.user import User


class Role(Base):
    __allow_unmapped__ = True
    slug: Mapped[str] = Column(String, nullable=False, unique=True)
    name: Mapped[str] = Column(String)

    # foreign key, inverse relationship
    users: User = relationship("User", back_populates="role")
