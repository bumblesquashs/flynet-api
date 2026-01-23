from typing import List

from model.airports import AirportModel, AirportPopulateModel
from schema.airports import Airport
from sqlalchemy.orm import Session
from utils.database import insert_data


def insert_airports(db: Session) -> List[AirportModel]:

    airports = [
     AirportPopulateModel(
         id=1,
         airport_name='Bumbleport Regional Aerodrome',
         iata_code='ZZZ',
         icao_code='CZZZ',
         airport_type='small_airport',
         lat="49.286257",
         lon="-123.146547",
         iso_country='CA',
         iso_region='CA-BC',
         continent='NA',
        ),
        AirportPopulateModel(
            id=2,
            airport_name='Rankin Inlet International',
            iata_code='HUD',
            icao_code='CHUD',
            airport_type='large_airport',
            lat="62.829253",
            lon="-92.142960",
            iso_country='CA',
            iso_region='CA-NU',
            continent='NA',
        ),
    ]

    return insert_data(db, Airport, airports, AirportModel)