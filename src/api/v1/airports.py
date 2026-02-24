from typing import Optional

from context.airports import AirportContext
from core.dependencies import get_db, get_user
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter
from model import SearchResponse
from model.airports import AirportModel, AirportUpdateModel
from model.responses import GeneralResponse
from model.security import UserTokenModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = InferringRouter()


@router.get("/")
def search(
    query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    # pylint: disable=unused-argument
    current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> SearchResponse[AirportModel]:
    """Perform a flight log search, allows basic keyword search by airline, flight number, more later."""
    context = AirportContext(db)

    airports, total = context.search(query, limit, offset)

    return SearchResponse(items=airports, total=total)


@router.get("/import_csv")
def import_csv(
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),
) -> GeneralResponse:
    """Get the details of a flight_log with the specified ID."""
    context = AirportContext(db)
    return context.import_from_csv()



@router.get("/code/{code}")
def by_code(
        code: str,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AirportModel:
    """Get the details of a flight_log with the specified IATA or ICAO code."""
    context = AirportContext(db)
    airport = context.get_by_code(code)

    if airport is None:
        raise HTTPException(status_code=404, detail="Airport not found.")

    return airport

@router.put("/update_city/{code}/{city_name}")
def update_city(
        code: str,
        city_name: str,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AirportModel:
    """Update an airports city on the fly."""
    context = AirportContext(db)
    airport = context.rename_city(code, city_name)

    if airport is None:
        raise HTTPException(status_code=404, detail="Airport not found.")

    return airport


@router.get("/{flight_log_id}")
def details(
        airport_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AirportModel:
    """Get the details of a flight_log with the specified ID."""
    context = AirportContext(db)
    airport = context.get(airport_id)

    if airport is None:
        raise HTTPException(status_code=404, detail="Airport not found.")

    return airport


@router.put("/{airport_id}")
def update(
        airport_id: int,
        airport: AirportUpdateModel,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["admin"]),
) -> AirportModel:
    """Update an existing airport entity, with the ID specified. Admin only."""
    context = AirportContext(db)
    try:
        updated_airport = context.update(airport_id, airport)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity error: {''.join(e.orig.args)}") from e

    if updated_airport is None:
        raise HTTPException(status_code=400, detail=f"Could not update airport...")

    return updated_airport
