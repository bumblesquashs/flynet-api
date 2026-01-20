from core.db import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from schema.flight_logs import FlightLogs


class User(Base):
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    login_last_time = Column(DateTime(timezone=True))
    login_count = Column(Integer, nullable=False, default=0)

    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role", back_populates="users")

    # foreign key, inverse relationship
    flight_logs: FlightLogs = relationship("FlightLogs", back_populates="user")
