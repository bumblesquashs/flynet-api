import uuid
from datetime import datetime
from typing import List

from model.flight_logs import FlightLogModel, FlightLogPopulateModel
from schema.flight_logs import FlightLogs
from sqlalchemy.orm import Session
from utils.database import insert_data


def insert_logs(db: Session) -> List[FlightLogModel]:

    flight_logs = [
     FlightLogPopulateModel(
         id=1,
         flight_number="AC123",
         date=datetime.now(),
         airline="Air Canada",
         origin_airport_id=1,
         destination_airport_id=2,
         plane_model="De Havilland Canada DHC-8 Dash 8",
         plane_registration="C-GGND",
         user_id=1,
         note="Flight successfully landed in fewer than 10 pieces"
        ),
    FlightLogPopulateModel(
        id=2,
        flight_number="BA67",
        date=datetime.now(),
        airline="Bowie Airlines",
        origin_airport_id=2,
        destination_airport_id=1,
        plane_model="Boeing 787-9",
        plane_registration="C-SUCK",
        user_id=2,
        note="Da best."
        )
    ]

    return insert_data(db, FlightLogs, flight_logs, FlightLogModel)