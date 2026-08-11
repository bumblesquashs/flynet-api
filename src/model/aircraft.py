from typing import Optional

from fastapi_utils.api_model import APIModel


class AircraftCreateModel(APIModel):
    """Model used when importing aircraft from csv"""

    primary_name: str = None
    icao_code: str = None
    iata_code: Optional[str] = None
    manufacturer: str = None
    aircraft_class: str = None
    family: Optional[str] = True
    year_introduced: int = None


class AircraftModel(AircraftCreateModel):
    """Model representing one model of aircraft"""
    id: int


class AircraftUpdateModel(AircraftCreateModel):
    pass


class AircraftPopulateModel(AircraftCreateModel):
    """Used with initial seed scripts; we need that ID."""
    id: int
