from typing import List

from model.airlines import AirlineModel, AirlinePopulateModel
from schema.airlines import Airline
from sqlalchemy.orm import Session
from utils.database import insert_data


def insert_airlines(db: Session) -> List[AirlineModel]:

    airports = [
     AirlinePopulateModel(
         id=1,
         primary_name="Air Canada",
         icao_code="ACA",
         iata_code="AC",
         alternate_names=None,
         is_active=True,
    ),
    AirlinePopulateModel(
        id=1,
        primary_name="Scandinavian Airlines",
        icao_code="SAS",
        iata_code="SK",
        alternate_names="SAS",
        is_active=True,
        )
    ]

    return insert_data(db, Airline, airports, AirlineModel)