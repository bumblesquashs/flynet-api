from typing import Optional

from context.flight_logs import FlightLogsContext
from starlette.responses import StreamingResponse

from context.flight_logs import FlightLogsContext
from core.dependencies import get_db, get_user
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter
from model import SearchResponse
from model.flight_logs import FlightLogCreateModel, FlightLogModel, FlightLogUpdateModel
from model.responses import GeneralResponse
from model.security import UserTokenModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = InferringRouter()


@router.get("/")
def search(
    query: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    airline: Optional[str] = None,
    flight_number: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    # pylint: disable=unused-argument
    current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> SearchResponse[FlightLogModel]:
    """Perform a flight log search, allows basic keyword search by airline, flight number, more later."""
    context = FlightLogsContext(db)

    flight_logs, total = context.search(query, start_date, end_date, flight_number, airline,
                                    limit, offset, current_user)

    return SearchResponse(items=flight_logs, total=total)


@router.get("/{flight_log_id}")
def details(
        flight_log_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> FlightLogModel:
    """Get the details of a flight_log with the specified ID."""
    context = FlightLogsContext(db)
    flight_log = context.get(flight_log_id)

    if flight_log is None:
        raise HTTPException(status_code=404, detail="FlightLog not found.")

    return flight_log


@router.post("/")
def create(
        flight_log: FlightLogCreateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> FlightLogModel:
    """Create a new flight_log entity"""
    context = FlightLogsContext(db)
    try:
        created_flight_log = context.create(flight_log, current_user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if created_flight_log is None:
        raise HTTPException(status_code=400, detail="Could not create flight_log.")

    return created_flight_log


@router.put("/{flight_log_id}")
def update(
        flight_log_id: int,
        flight_log: FlightLogUpdateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> FlightLogModel:
    """Update an existing flight_log entity, with the ID specified."""
    context = FlightLogsContext(db)
    try:
        updated_flight_log = context.update(flight_log_id, flight_log, current_user)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if updated_flight_log is None:
        raise HTTPException(status_code=400, detail=f"Could not update log: log not found for user {current_user.user_id}.")

    return updated_flight_log


@router.delete("/{flight_log_id}")
def delete(
        flight_log_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> FlightLogModel:
    """Delete the report with the specified ID."""
    context = FlightLogsContext(db)
    flight_log = context.delete(flight_log_id, current_user)

    if flight_log is None:
        raise HTTPException(status_code=404, detail=f"Could not delete log: Log not found for user {current_user.user_id}.")

    return flight_log