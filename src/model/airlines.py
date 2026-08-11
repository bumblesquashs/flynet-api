from typing import Optional

from fastapi_utils.api_model import APIModel


class AirlineCreateModel(APIModel):
    """Model used when importing airlines from csv"""

    primary_name: str = None
    icao_code: str = None
    iata_code: str = None
    alternate_names: Optional[str] = None
    is_active: bool = True


class AirlineModel(AirlineCreateModel):
    """Model representing one airline"""
    id: int


class AirlineUpdateModel(AirlineCreateModel):
    pass


class AirlinePopulateModel(AirlineCreateModel):
    """Used with initial seed scripts; we need that ID."""
    id: int
