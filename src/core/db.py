""" Set up the Base Database model

Init the minimum required fields for the schema; effectively we're using this to create the metadata entity set
for Alembic to manage migrations for us. `Base` will be passed into the target_metadata in the `env.py` file inside our
`migrations` directory.
"""
import re
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, cast, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Query, Mapped
from sqlalchemy.sql import asc, desc
from sqlalchemy.sql.elements import and_, or_


def camel2snake(camel_case_str):
    # Insert an underscore before each uppercase letter and convert to lowercase
    snake_case_str = re.sub(r'([a-z])([A-Z])', r'\1_\2', camel_case_str).lower()
    return snake_case_str


@as_declarative()
class Base:
    __allow_unmapped__ = True
    __name__: str
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[DateTime] = Column(DateTime, name="created_at", nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime, name="updated_at", nullable=False, server_default=func.now())

    def __init__(self, *args, **kwargs):
        pass

    @declared_attr
    def __tablename__(cls) -> str:  # noqa pylint: disable=no-self-argument
        """Generate table names automatically."""
        return camel2snake(cls.__name__)


def build_keyword_query(columns: List[Column], search_query: str, db_query: Query):
    """
    Build a keyword search query for the supplied base query, and the search_query supplied, given the columns
    specified.

    This will tokenize the search_query based on spaced, and for each keyword will try to locate it in the specified
    columns, each keyword must be present in the columns specified.

    :param columns: The set of SQL Alchemy Columns from the schema.
    :param search_query: A string of keywords to search.
    :param db_query: The base SQL Alchemy query to use.

    :return: A SQL Alchemy query object that can be further manipulated; if columns are missing, or if the search
    string is empty, the original db_query is returned.
    """
    if db_query is None:
        return None

    if columns is None or len(columns) == 0:
        return db_query

    if search_query is None or len(search_query) == 0:
        return db_query

    keywords = search_query.split(" ")
    filter_list = []
    for keyword in keywords:
        keyword_filter = [cast(column, String).ilike(f"%{keyword}%") for column in columns]
        filter_list.append(or_(*keyword_filter))

    return db_query.filter(and_(*filter_list))


def build_query_sort(columns: List[Column], column_name: str, sort_desc: bool, db_query: Query):
    if db_query is None:
        return None

    if columns is None or len(columns) == 0:
        return db_query

    if column_name is None or len(column_name) == 0:
        return db_query

    # This is to avoid a circular import; maybe get_first() needs to be extracted from where
    # it currently lives.
    import utils.database

    column_name = camel2snake(column_name)
    sort_column = utils.database.get_first(columns, lambda c: c.name == column_name, columns[0])
    sort_function = desc(sort_column) if sort_desc else asc(sort_column)

    return db_query.order_by(sort_function)
