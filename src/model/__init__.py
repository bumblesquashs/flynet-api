from typing import Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class SearchQuery(BaseModel):
    """Basic search query properties."""

    query: Optional[str] = Query(None)
    limit: int = Query(50)
    offset: int = Query(0)
    sort: Optional[str] = Query(None)
    sort_desc: Optional[bool] = Query(False)


class SearchResponse(BaseModel, Generic[T]):
    """Basic generic class to return search results."""

    message: Optional[str] = None
    total: Optional[int] = None
    items: List[T]
