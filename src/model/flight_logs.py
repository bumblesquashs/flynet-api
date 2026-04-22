from datetime import datetime
from typing import Optional

from fastapi_utils.api_model import APIModel
from model.user import UserModel
from model.airports import AirportModel

class FlightLogCreateModel(APIModel):
    """Model used when creating logs"""

    flight_number: Optional[str] = None
    airline: Optional[str] = None
    date: Optional[datetime] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    plane_model: Optional[str] = None
    plane_registration: Optional[str] = None
    note: Optional[str] = None

    origin_airport_id: Optional[int] = None
    destination_airport_id: Optional[int] = None


class FlightLogImportModel(FlightLogCreateModel):
    """Model used when importing logs"""
    user_id: int


class FlightLogModel(FlightLogCreateModel):
    """Model representing one flight log in the user's history"""
    user: Optional[UserModel] = None
    user_id: Optional[int] = None

    origin_airport_id: Optional[int] = None
    destination_airport_id: Optional[int] = None

    origin_airport: Optional[AirportModel] = None
    destination_airport: Optional[AirportModel] = None

    id: Optional[int]


class FlightLogUpdateModel(FlightLogCreateModel):
    pass


class FlightLogPopulateModel(FlightLogCreateModel):
    """Used with initial seed scripts; we set user here"""
    user: Optional[UserModel] = None
    user_id: Optional[int] = None

    origin_airport_id: Optional[int] = None
    destination_airport_id: Optional[int] = None

    id: Optional[int]
