from core.db import Base
from sqlalchemy import Column, String


class Airport(Base):
    icao_code = Column(String)
    iata_code = Column(String)
    local_code = Column(String)
    airport_name = Column(String)
    lat: Column = Column(String)
    lon: Column = Column(String)
    continent = Column(String)
    iso_country = Column(String)
    iso_region = Column(String)
    # TODO: enum of these values
    # TODO: large_airport, small_airport, medium_airport, heliport, seaplane_base, closed
    airport_type = Column(String)
    city = Column(String)




