from core.db import Base
from sqlalchemy import Column, String, Boolean


class Airline(Base):
    primary_name = Column(String)
    icao_code = Column(String)
    iata_code = Column(String)
    alternate_names = Column(String)
    is_active = Column(Boolean)




