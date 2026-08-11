import csv

from typing import List, Optional, Tuple

from model.responses import GeneralResponse

from core.db import build_keyword_query
from model.airlines import AirlineModel, AirlineCreateModel
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import ValidationError

from schema.airlines import Airline


def load_airlines_from_csv(path: str = "../airlines.csv") -> List[AirlineCreateModel]:
    airlines: List[AirlineCreateModel] = []
    skipped_rows = 0

    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_number, row in enumerate(reader, start=2): # the header row is row 1
            try:

                type_label = row['typeLabel']
                is_active = False if 'former' in type_label else True

                airline = AirlineCreateModel(
                    primary_name=row['airlineLabel'],
                    alternate_names=row['otherNames'],
                    icao_code=row['icao'],
                    iata_code=row['iata'],
                    is_active=is_active,
                )
                airlines.append(airline)

            except (KeyError, ValidationError, ValueError) as exc:
                skipped_rows += 1
                print(
                    f"Skipping row {row_number}: {exc}"
                )

    print(f"Imported {len(airlines)} airlines, skipped {skipped_rows} rows")
    return airlines


class AirlineContext:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query_string: str, limit: int, offset: int) -> Tuple[List[AirlineModel], int]:

        base_query = self.db.query(Airline)

        # keyword search
        db_query = build_keyword_query(
            [Airline.primary_name, Airline.alternate_names, Airline.iata_code, Airline.icao_code],
            query_string,
            base_query,
        )

        if limit == -1:
            airlines = db_query.order_by(desc(Airline.primary_name)).offset(offset).all()
        else:
            airlines = db_query.order_by(desc(Airline.primary_name)).offset(offset).limit(limit).all()

        return [AirlineModel.from_orm(airline) for airline in airlines], db_query.count()


    def get(self, airline_id: int) -> Optional[AirlineModel]:
        airline = self.db.query(Airline).filter(Airline.id == airline_id).first()

        if not airline:
            return None

        return AirlineModel.from_orm(airline)


    def find_airline_by_code(self, code: str):
        # Try IATA first
        possible_airline = self.db.query(Airline).filter(Airline.iata_code == code).first()

        if possible_airline:
            return possible_airline

        # Try ICAO second
        possible_airline = self.db.query(Airline).filter(Airline.icao_code == code).first()

        if possible_airline:
            return possible_airline

        return None


    def get_by_code(self, code: str) -> Optional[AirlineModel]:

        possible_airline = self.find_airline_by_code(code)

        if possible_airline is None:
            return None

        return AirlineModel.from_orm(possible_airline)


    def import_from_csv(self) -> Optional[GeneralResponse]:
        airlines = load_airlines_from_csv()
        for airline in airlines:
            db_airline = Airline(**airline.dict())
            self.db.add(db_airline)

        self.db.commit()

        return GeneralResponse(message=f'{len(airlines)} Rows imported.', is_success=True)
