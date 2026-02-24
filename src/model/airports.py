from typing import Optional

from fastapi_utils.api_model import APIModel


class AirportCreateModel(APIModel):
    """Model used when creating logs"""

    icao_code: Optional[str] = None
    iata_code: Optional[str] = None
    local_code: Optional[str] = None
    airport_name: Optional[str] = None
    lat: Optional[str] = None
    lon: Optional[str] = None
    continent: Optional[str] = None
    iso_country: Optional[str] = None
    iso_region: Optional[str] = None
    airport_type: Optional[str] = None
    city: Optional[str] = None


class AirportModel(AirportCreateModel):
    """Model representing one flight log in the user's history"""
    id: int


class AirportUpdateModel(AirportCreateModel):
    pass


class AirportPopulateModel(AirportCreateModel):
    """Used with initial seed scripts; we need that ID."""
    id: int
