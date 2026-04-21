from core.db import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from schema.flight_logs import FlightLogs


class User(Base):
    email = Column(String, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    nickname = Column(String)
    is_profile_public = Column(Boolean)

    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role", back_populates="users")

    user_profile_id = Column(Integer, ForeignKey("user_profile.id"))
    user_profile = relationship("UserProfile")

    # foreign key, inverse relationship
    flight_logs: FlightLogs = relationship("FlightLogs", back_populates="user")
