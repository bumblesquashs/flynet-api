from datetime import datetime
from typing import Optional

from fastapi_utils.api_model import APIModel
from model.user import UserModel

class FlightLogCreateModel(APIModel):
    """Model used when creating logs"""

    flight_number: Optional[str] = None
    airline: Optional[str] = None
    date: Optional[datetime] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    plane_model: Optional[str] = None
    plane_registration: Optional[str] = None
    note: Optional[str] = None

class FlightLogModel(FlightLogCreateModel):
    """Model representing one flight log in the user's history"""
    user: Optional[UserModel] = None
    user_id: Optional[int] = None
    id: Optional[int]


class FlightLogUpdateModel(FlightLogCreateModel):
    pass


class FlightLogPopulateModel(FlightLogModel):
    """Used with initial seed scripts; we need that ID."""
    user: Optional[UserModel] = None
    user_id: Optional[int] = None
    id: Optional[int]
