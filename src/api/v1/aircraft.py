from typing import Optional

from context.aircraft import AircraftContext
from core.dependencies import get_db, get_user
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter
from model import SearchResponse
from model.aircraft import AircraftModel
from model.security import UserTokenModel
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
) -> SearchResponse[AircraftModel]:
    """Perform an aircraft search, allows basic keyword search by name, iata/icao code, family, manufacturer"""
    context = AircraftContext(db)

    aircraft, total = context.search(query, limit, offset)

    return SearchResponse(items=aircraft, total=total)


@router.get("/code/{code}")
def by_code(
        code: str,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AircraftModel:
    """Get the details of an aircraft with the specified IATA or ICAO code."""
    context = AircraftContext(db)
    airline = context.get_by_code(code)

    if airline is None:
        raise HTTPException(status_code=404, detail="Aircraft not found.")

    return airline


@router.get("/{aircraft_id}")
def details(
        aircraft_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AircraftModel:
    """Get the details of a airline with the specified ID."""
    context = AircraftContext(db)
    airline = context.get(aircraft_id)

    if airline is None:
        raise HTTPException(status_code=404, detail="Aircraft not found.")

    return airline
