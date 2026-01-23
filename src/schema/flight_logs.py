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
    plane_model = Column(String) # TODO: fk to plane type table
    plane_registration = Column(String)
    note = Column(String)

    origin_airport_id = Column(Integer, ForeignKey("airport.id"))
    origin_airport = relationship("Airport", foreign_keys=[origin_airport_id])

    destination_airport_id = Column(Integer, ForeignKey("airport.id"))
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_id])

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="flight_logs")



