import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from model.security import UserTokenModel

from core.db import build_keyword_query
from model.flight_logs import FlightLogModel, FlightLogUpdateModel, FlightLogCreateModel
from sqlalchemy import desc, or_, and_
from sqlalchemy.orm import Session

from schema.flight_logs import FlightLogs


class FlightLogsContext:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query_string: str, start_date: Optional[str], end_date: Optional[str],
               flight_number, airline, limit: int, offset: int, current_user: UserTokenModel) \
            -> Tuple[List[FlightLogModel], int]:

        # only get logs for current user
        base_query = self.db.query(FlightLogs).filter(FlightLogs.user_id == current_user.user_id)

        # keyword search
        db_query = build_keyword_query(
            [FlightLogs.flight_number, FlightLogs.airline],
            query_string,
            base_query,
        )


        # time ranges
        if start_date is not None and end_date is not None:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            db_query = db_query.filter(or_(
                and_(FlightLogs.date >= start_date, FlightLogs.date <= end_date),
                # and_(FlightLog.date >= start_date, FlightLog.date <= end_date)
            ))


        if limit == -1:
            flight_logs = db_query.order_by(desc(FlightLogs.date)).offset(offset).all()
        else:
            flight_logs = db_query.order_by(desc(FlightLogs.date)).offset(offset).limit(limit).all()

        return [FlightLogModel.from_orm(flight_log) for flight_log in flight_logs], db_query.count()

    def get(self, flight_log_id: int) -> Optional[FlightLogModel]:
        flight_log = self.db.query(FlightLogs).filter(FlightLogs.id == flight_log_id).first()

        if not flight_log:
            return None

        return FlightLogModel.from_orm(flight_log)

    def delete(self, flight_log_id: int, current_user: UserTokenModel) -> Optional[FlightLogModel]:
        flight_log = self.db.query(FlightLogs).filter(FlightLogs.id == flight_log_id).first()
        if not flight_log:
            return None

        if flight_log.user_id != int(current_user.user_id):
            return None

        result = FlightLogModel.from_orm(flight_log)

        self.db.delete(flight_log)
        self.db.commit()

        return result

    def create(self, flight_log: FlightLogCreateModel, current_user: Optional[UserTokenModel]) -> Optional[FlightLogModel]:

        db_flight_log = FlightLogs(**flight_log.dict())
        if current_user is not None:
            db_flight_log.user_id = int(current_user.user_id)

        self.db.add(db_flight_log)
        self.db.commit()

        created_id = db_flight_log.id

        added_flight_log: FlightLogs = self.db.query(FlightLogs).filter(FlightLogs.id == created_id).first()

        if not added_flight_log:
            return None

        return FlightLogModel.from_orm(added_flight_log)

    def update(self, flight_log_id: int, flight_log: FlightLogUpdateModel, current_user: UserTokenModel) -> Optional[FlightLogModel]:
        existing_flight_log: FlightLogs = self.db.query(FlightLogs).filter(FlightLogs.id == flight_log_id).first()
        if not existing_flight_log:
            return None

        if existing_flight_log.user_id != int(current_user.user_id):
            return None

        # Iterate over flight_log object's fields to set the fields in the db object
        # This is less clean but much more concise than specifying all fields again
        flight_log_dict = vars(flight_log)
        for key in flight_log_dict:
            if flight_log_dict[key] is not None:
                setattr(existing_flight_log, key, flight_log_dict[key])

        self.db.commit()

        updated_flight_log: FlightLogs = self.db.query(FlightLogs).filter(FlightLogs.id == flight_log_id).first()

        if not updated_flight_log:
            return None

        return FlightLogModel.from_orm(updated_flight_log)