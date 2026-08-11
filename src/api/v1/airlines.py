from typing import Optional

from context.airlines import AirlineContext
from core.dependencies import get_db, get_user
from fastapi import Depends, HTTPException, Security
from fastapi_utils.inferring_router import InferringRouter
from model import SearchResponse
from model.airlines import AirlineModel
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
) -> SearchResponse[AirlineModel]:
    """Perform an airline search, allows basic keyword search by name, iata/icao code, etc"""
    context = AirlineContext(db)

    airlines, total = context.search(query, limit, offset)

    return SearchResponse(items=airlines, total=total)


@router.get("/code/{code}")
def by_code(
        code: str,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AirlineModel:
    """Get the details of a airline with the specified IATA or ICAO code."""
    context = AirlineContext(db)
    airline = context.get_by_code(code)

    if airline is None:
        raise HTTPException(status_code=404, detail="Airline not found.")

    return airline


@router.get("/{airline_id}")
def details(
        airline_id: int,
        db: Session = Depends(get_db),
        # pylint: disable=unused-argument
        current_user: UserTokenModel = Security(get_user, scopes=["user"]),
) -> AirlineModel:
    """Get the details of a airline with the specified ID."""
    context = AirlineContext(db)
    airline = context.get(airline_id)

    if airline is None:
        raise HTTPException(status_code=404, detail="Airline not found.")

    return airline
