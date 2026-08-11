from typing import List

from model.aircraft import AircraftModel, AircraftPopulateModel
from schema.aircraft import Aircraft
from sqlalchemy.orm import Session
from utils.database import insert_data


def insert_aircraft(db: Session) -> List[AircraftModel]:

    aircraft = [
     AircraftPopulateModel(
         id=1,
         primary_name="Airbus A380-800",
         icao_code="A388",
         iata_code="380",
         family="A380",
         manufacturer="Airbus",
         aircraft_class="widebody",
         year_introduced=2007
        ),
        AircraftPopulateModel(
            id=2,
            primary_name="Boeing 737-200",
            icao_code="B732",
            iata_code="732",
            family="B737",
            manufacturer="Airbus",
            aircraft_class="narrowbody",
            year_introduced=1968
        )
    ]

    return insert_data(db, Aircraft, aircraft, AircraftModel)