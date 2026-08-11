from core.db import Base
from sqlalchemy import Column, String, Integer


class Aircraft(Base):
    primary_name = Column(String)
    icao_code = Column(String)
    iata_code = Column(String)
    manufacturer = Column(String)
    aircraft_class = Column(String)
    family = Column(String)
    year_introduced = Column(Integer)






