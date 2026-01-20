from datetime import datetime
from typing import Optional

from fastapi_utils.api_model import APIModel
from model.user import UserModel

class FlightLogModel(APIModel):
    """Model representing one flight log in the user's history"""

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

    user_id: Optional[int] = None
    user: Optional[UserModel] = None


class FlightLogCreateModel(FlightLogModel):
    """Model used when creating logs"""
    pass


class FlightLogUpdateModel(FlightLogModel):
    id: Optional[int]


class FlightLogPopulateModel(FlightLogModel):
    """Used with initial seed scripts; we need that ID."""
    id: Optional[int]
