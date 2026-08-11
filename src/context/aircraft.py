import csv

from typing import List, Optional, Tuple

from model.responses import GeneralResponse

from core.db import build_keyword_query
from model.aircraft import AircraftModel, AircraftCreateModel
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import ValidationError

from schema.aircraft import Aircraft


def load_aircraft_from_csv(path: str = "../aircraft.csv") -> List[AircraftCreateModel]:
    aircraft: List[AircraftCreateModel] = []
    skipped_rows = 0

    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_number, row in enumerate(reader, start=2): # the header row is row 1
            try:

                # 'aircraftum' is the singular of aircraft, trust
                aircraftum = AircraftCreateModel(
                    primary_name=row['model_name'],
                    icao_code=row['icao_code'],
                    iata_code=row['iata_code'],
                    family=row['family'],
                    manufacturer=row['manufacturer'],
                    aircraft_class=row['class'],
                    year_introduced=int(row['year_introduced'])
                )

                aircraft.append(aircraftum)

            except (KeyError, ValidationError, ValueError) as exc:
                skipped_rows += 1
                print(
                    f"Skipping row {row_number}: {exc}"
                )

    print(f"Imported {len(aircraft)} aircraft, skipped {skipped_rows} rows")
    return aircraft


class AircraftContext:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query_string: str, limit: int, offset: int) -> Tuple[List[AircraftModel], int]:

        base_query = self.db.query(Aircraft)

        # keyword search
        db_query = build_keyword_query(
            [Aircraft.primary_name, Aircraft.iata_code, Aircraft.icao_code, Aircraft.family, Aircraft.manufacturer],
            query_string,
            base_query,
        )

        if limit == -1:
            aircraft = db_query.order_by(desc(Aircraft.primary_name)).offset(offset).all()
        else:
            aircraft = db_query.order_by(desc(Aircraft.primary_name)).offset(offset).limit(limit).all()

        return [AircraftModel.from_orm(aircraftum) for aircraftum in aircraft], db_query.count()


    def get(self, airline_id: int) -> Optional[AircraftModel]:
        airline = self.db.query(Aircraft).filter(Aircraft.id == airline_id).first()

        if not airline:
            return None

        return AircraftModel.from_orm(airline)


    def find_aircraft_by_code(self, code: str):
        # Try IATA first
        possible_aircraft = self.db.query(Aircraft).filter(Aircraft.iata_code == code).first()

        if possible_aircraft:
            return possible_aircraft

        # Try ICAO second
        possible_aircraft = self.db.query(Aircraft).filter(Aircraft.icao_code == code).first()

        if possible_aircraft:
            return possible_aircraft

        return None


    def get_by_code(self, code: str) -> Optional[AircraftModel]:

        possible_aircraft = self.find_aircraft_by_code(code)

        if possible_aircraft is None:
            return None

        return AircraftModel.from_orm(possible_aircraft)


    def import_from_csv(self) -> Optional[GeneralResponse]:
        aircraft = load_aircraft_from_csv()
        for aircraftum in aircraft:
            db_aircraft = Aircraft(**aircraftum.dict())
            self.db.add(db_aircraft)

        self.db.commit()

        return GeneralResponse(message=f'{len(aircraft)} Rows imported.', is_success=True)
