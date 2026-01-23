import csv

from typing import List, Optional, Tuple

from model.responses import GeneralResponse

from core.db import build_keyword_query
from model.airports import AirportModel, AirportUpdateModel, AirportCreateModel
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import ValidationError

from schema.airports import Airport


def load_airports_from_csv(path: str = "airports.csv") -> List[AirportCreateModel]:
    airports: List[AirportCreateModel] = []
    skipped_rows = 0

    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_number, row in enumerate(reader, start=2): # the header row is row 1
            try:
                # to get icao code we check gps_code first, then fall back to ident
                icao_code = row.get("gps_code") or row.get("ident")
                icao_code = icao_code.strip() if icao_code else None

                iata_code = row.get("iata_code")
                iata_code = iata_code.strip() if iata_code else None

                # must have at least ICAO or IATA otherwise skippo
                if not icao_code and not iata_code:
                    raise ValueError("Missing both ICAO and IATA codes")

                airport = AirportCreateModel(
                    icao_code=icao_code,
                    iata_code=iata_code,
                    airport_name=row["name"].strip(),
                    lat=row["latitude_deg"].strip(),
                    lon=row["longitude_deg"].strip(),
                    continent=row["continent"].strip(),
                    iso_country=row["iso_country"].strip(),
                    iso_region=row.get("iso_region") or None,
                    airport_type=row["type"].strip(),
                )

                airports.append(airport)

            except (KeyError, ValidationError, ValueError) as exc:
                skipped_rows += 1
                print(
                    f"Skipping row {row_number}: {exc}"
                )

    print(f"Imported {len(airports)} airports, skipped {skipped_rows} rows")
    return airports


class AirportContext:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query_string: str, limit: int, offset: int) -> Tuple[List[AirportModel], int]:

        # loads of heliports out there that we don't need
        base_query = self.db.query(Airport).filter(Airport.airport_type != 'heliport')

        # keyword search
        db_query = build_keyword_query(
            [Airport.airport_name, Airport.iata_code, Airport.icao_code],
            query_string,
            base_query,
        )

        if limit == -1:
            airports = db_query.order_by(desc(Airport.airport_name)).offset(offset).all()
        else:
            airports = db_query.order_by(desc(Airport.airport_name)).offset(offset).limit(limit).all()

        return [AirportModel.from_orm(airport) for airport in airports], db_query.count()


    def get(self, airport_id: int) -> Optional[AirportModel]:
        airport = self.db.query(Airport).filter(Airport.id == airport_id).first()

        if not airport:
            return None

        return AirportModel.from_orm(airport)


    def import_from_csv(self) -> Optional[GeneralResponse]:
        airports = load_airports_from_csv()
        for airport in airports:
            db_airport = Airport(**airport.dict())
            self.db.add(db_airport)

        self.db.commit()

        return GeneralResponse(message=f'{len(airports)} Rows imported.', is_success=True)


    def update(self, airport_id: int, airport: AirportUpdateModel) -> Optional[AirportModel]:
        existing_airport: Airport = self.db.query(Airport).filter(Airport.id == airport_id).first()
        if not existing_airport:
            return None


        # Iterate over flight_log object's fields to set the fields in the db object
        # This is less clean but much more concise than specifying all fields again
        airport_dict = vars(airport)
        for key in airport_dict:
            if airport_dict[key] is not None:
                setattr(existing_airport, key, airport_dict[key])

        self.db.commit()

        updated_airport: Airport = self.db.query(Airport).filter(Airport.id == airport_id).first()

        if not updated_airport:
            return None

        return Airport.from_orm(updated_airport)