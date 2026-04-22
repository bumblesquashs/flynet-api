import csv

from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile
from pydantic import ValidationError

from model.security import UserTokenModel
from model.flight_logs import FlightLogImportModel
from model.responses import ImportResponse
from schema.flight_logs import FlightLogs
from schema.airports import Airport
from sqlalchemy.orm import Session
from context.airports import AirportContext

encodings = ["utf-8", "utf-16", "ansi", "ascii", "cp1252", "latin-1"]

def get_csv_reader(file) -> csv.DictReader:
    csv_bytes = file.file.read()  # This comes as a binary file
    for encoding in encodings:
        try:
            lines = csv_bytes.decode(encoding=encoding).splitlines()
            if lines is not None:
                return csv.DictReader(lines)
        except UnicodeDecodeError as e:
            continue
    return csv.DictReader([])


def two_digit_year_handler(date: datetime):
    # The formats with 2 digit years create ambiguity where 21 might be 1921 or 2021
    # The python strptime can assume 20xx, which is often wrong, so err on the case that nobody is over 100 years old...
    year_number = datetime.now().year % 100
    if date.year > 2000 and (date.year % 100) > year_number:
        # Dates like 01.01.58 will come in as 2058 so subtract 100 from the year for those
        return datetime(date.year - 100, date.month, date.day)
    return date


def strip_am_pm(date_cell) -> str:
    naughty_list = ['a.m.', 'p.m.', 'A.M.', 'P.M.', 'AM', 'PM', 'am', 'pm']
    for string in naughty_list:
        date_cell = date_cell.replace(string, "")

    return date_cell.rstrip()


def cell_to_datetime(date_cell) -> Optional[datetime]:
    if date_cell == "":
        return None

    date_cell = strip_am_pm(date_cell)

    # Attempt 1 - datetime cells with the following format 27.03.22 14:10
    try:
        date: datetime = datetime.strptime(date_cell, "%d.%m.%y %H:%M")
        return two_digit_year_handler(date)
    except ValueError:
        pass

    # Attempt 2 - that, but without the time part
    try:
        date: datetime = datetime.strptime(date_cell, "%d.%m.%y")
        return two_digit_year_handler(date)
    except ValueError:
        pass

    # Attempt 3 - Month day year 12/18/1996
    try:
        date: datetime = datetime.strptime(date_cell, "%m/%d/%Y")
        return date
    except ValueError:
        pass

    # Attempt 3.5 - Month day year 12/18/96
    try:
        date: datetime = datetime.strptime(date_cell, "%m/%d/%y")
        return two_digit_year_handler(date)
    except ValueError:
        pass

    # Attempt 4 - It might be in iso format. Split into parts on spaces
    date_parts = date_cell.split(" ")

    # Case where there is the date and the time but there is no timezone
    if len(date_parts) == 2:
        # No timezone case
        try:
            return datetime.fromisoformat(" ".join(date_parts))  # 2022-05-17 09:10
        except ValueError:
            return datetime.strptime(date_cell, "%Y-%m-%d %H:%M")  # 2022-05-17 9:10

    # Case where there is the timezone too
    if len(date_parts) > 2:
        # Dark magic to exclude the utc offset (some date strings are like "2021-12-30 05:00:00 -0800" in jane)
        return datetime.fromisoformat(" ".join(date_parts[:-1]))

    # Attempt 5: If none of those cases match, then the date should just be like "2021-12-30"
    try:
        return datetime.fromisoformat(date_cell)
    except ValueError:
        return None


def cell_to_time_string(time_cell):
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M:S %p", "%I:%M %p"):
        try:
            # TODO: should the db store the datetime instead?
            return datetime.strptime(time_cell, fmt).strftime("%H:%M")
        except ValueError:
            pass
    return None


def cell_to_boolean(possible_boolean) -> Optional[bool]:
    if possible_boolean == "":
        return None
    if possible_boolean.lower() in ("f", "false", "0"):
        return False
    if possible_boolean.lower() in ("t", "true", "1"):
        return True
    return None


# case insensitive, so spreadsheets with a col named "Airline" "airline" and "AIRLINE" all work
column_naming_table = {
    "date": ["Date"],
    "airline": ["Airline", "Carrier"],
    "flight_number": ["Flight", "Flight Number", "Number", "Flight No", "Flight No."],
    "departure_time": ["Departure Time", "Departure", "Departed"],
    "arrival_time": ["Arrival Time", "Arrival", "Arrived"],
    "plane_model": ["Plane Type", "Plane Model", "Type", "Model"],
    "plane_registration": ["Registration", "Tail", "Tail Number"],
    "note": ["Note", "Notes", "Remark", "Remarks"],
    "origin_airport": ["Origin Airport", "Origin", "Depart", "Start", "Leave", "From"],
    "destination_airport": ["Destination Airport", "Destination", "Arrive", "End", "To"]
}

def try_names(row_key, csv_row) -> str | None:
    names = column_naming_table[row_key]
    lowered_csv_row = {k.lower(): v for k, v in csv_row.items()}
    for name in names:
        if name.lower() in lowered_csv_row:
            return lowered_csv_row[name.lower()]
    return None


def format_validation_error(validation_error):
    return ' '.join(str(validation_error).split('\n')[1:])


class ImportContext:
    def __init__(self, db: Session):
        self.db = db

    def find_airport(self, imported_airport_string: str) -> int | None:
        '''
        :param imported_airport_string: the string from the users spreadsheet, we dont know what kind
        :return: Airport record id from db, or None if not found
        '''
        imported_airport_string = imported_airport_string.strip()
        to_all_caps: str = imported_airport_string.upper()
        matched_airport = None
        airport_context = AirportContext(self.db)

        # case one - its a IATA or ICAO code, so 3 letters
        if len(imported_airport_string) == 3 or len(imported_airport_string) == 4:
           matched_airport = airport_context.find_airport_by_code(to_all_caps)

        # case two, its an airport name of some sort
        elif len(imported_airport_string) > 4:
            matched_airports = airport_context.search(imported_airport_string, 1, 0)[0]
            if len(matched_airports) > 0:
                matched_airport = matched_airports[0]

        # failure!
        if matched_airport is None:
            return None

        return matched_airport.id


    def row_to_flight_log(self, csv_row: dict[str, str], user_id: int) -> FlightLogImportModel:
        date = try_names("date", csv_row)
        if date is not None:
            date = cell_to_datetime(date)

        departure_time = try_names("departure_time", csv_row)
        if departure_time is not None:
            departure_time = cell_to_datetime(departure_time)

        arrival_time = try_names("arrival_time", csv_row)
        if arrival_time is not None:
            arrival_time = cell_to_datetime(arrival_time)

        imported_origin_airport = try_names("origin_airport", csv_row)
        imported_destination_airport = try_names("origin_airport", csv_row)

        origin_airport_id = None
        destination_airport_id = None

        if imported_origin_airport is not None and imported_origin_airport != "":
            origin_airport_id = self.find_airport(imported_origin_airport)

        if imported_destination_airport is not None and imported_destination_airport != "":
            destination_airport_id = self.find_airport(imported_destination_airport)

        return FlightLogImportModel(
            date=date,
            airline=try_names("airline", csv_row),
            flight_number=try_names("flight_number", csv_row),
            departure_time=departure_time,
            arrival_time=arrival_time,
            plane_model=try_names("plane_model", csv_row),
            plane_registration=try_names("plane_registration", csv_row),
            note=try_names("note", csv_row),
            origin_airport_id=origin_airport_id,
            destination_airport_id=destination_airport_id,
            user_id=user_id,
        )

    def import_flight_log_csv(self, flight_log_file: UploadFile, current_user: UserTokenModel) -> ImportResponse:
        reader = get_csv_reader(flight_log_file)
        filename = flight_log_file.filename
        user_id = current_user.user_id

        num_created = 0
        num_updated = 0

        try:
            new_flight_logs: List[FlightLogImportModel] = [self.row_to_flight_log(row, user_id) for row in reader]
        except ValidationError as e:
            return ImportResponse(
                message=f"Error: {filename}: Validation error while importing flight logs: {format_validation_error(e)}",
                is_success=False,
                num_updated=0,
                num_created=0
            )
        except ValueError as e:
            return ImportResponse(
                message=f"Error: {filename}: Data format error while creating flight logs: {e.args[0]}",
                is_success=False,
                num_updated=0,
                num_created=0
            )


        # Second pass: write to db
        for new_flight_log in new_flight_logs:
            if new_flight_log is None:
                continue

            # We check to see if someone has already put this flight in
            existing_flight_log: FlightLogs = (
                self.db.query(FlightLogs)
                    .filter(FlightLogs.date == new_flight_log.date)
                    .filter(FlightLogs.flight_number == new_flight_log.flight_number)
                    .filter(FlightLogs.origin_airport_id == new_flight_log.origin_airport_id)
                    .filter(FlightLogs.destination_airport_id == new_flight_log.destination_airport_id)
                    .first()
            )

            if existing_flight_log is None:
                db_flight_log = FlightLogs(**new_flight_log.dict())
                self.db.add(db_flight_log)
                num_created += 1
            else:
                # Destructive import?
                new_flight_log_dict = vars(new_flight_log)
                for key in new_flight_log_dict:
                     if new_flight_log_dict[key] is not None:
                         setattr(existing_flight_log, key, new_flight_log_dict[key])
                num_updated += 1
        # Outside the loop:
        self.db.commit()

        return ImportResponse(
            message=f"Success: {filename}: Processed {num_created + num_updated} flight logs: created {num_created} and updated {num_updated}.",
            is_success=True,
            num_created=num_created,
            num_updated=num_updated,
        )
