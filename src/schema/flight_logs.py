from sqlalchemy.orm import relationship

from core.db import Base
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey


class FlightLogs(Base):
    # For our purposes
    flight_number = Column(String)
    airline = Column(String) # TODO: consider making this a fk to a table?
    date = Column(DateTime)
    departure_time = Column(String)
    arrival_time = Column(String)
    departure_airport = Column(String) # TODO: fk to a table of airports?
    arrival_airport = Column(String)
    plane_model = Column(String) # TODO: fk to plane type table
    plane_registration = Column(String)
    note = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="flight_logs")



