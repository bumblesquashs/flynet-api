from typing import Any, Callable, List, Type

from core.db import Base
from core.settings import settings
from fastapi_utils.api_model import APIModel
from schema import init_relationships
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Global DB session reference
SessionLocal = None


def init_test_db(should_drop_db) -> Session:
    global SessionLocal
    init_relationships()

    if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite:///"):
        db_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
    else:
        db_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

    if should_drop_db:
        Base.metadata.drop_all(db_engine)  # all tables are deleted - for unit tests

    Base.metadata.create_all(bind=db_engine)
    SessionLocal = make_local_session(db_engine)  # global

    return SessionLocal()


def make_local_session(db_engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def get_test_db() -> Session:
    db = None
    try:
        db = SessionLocal()  # Pylint is apparently wrong about this here, that thing is indeed callable
        yield db
    finally:
        if db is not None:
            db.close()


def get_first(items: List[Any], condition: Callable[[Any], bool], default: Any = None):
    return next((item for item in items if condition(item)), default)


def insert_data(local_db: Session, model: Type, items: List[APIModel], return_model: Type[APIModel]):
    for item in items:
        orm_item = model(**item.dict(exclude_unset=True))
        existing = local_db.query(model).filter(model.id == item.id).first()
        if existing is not None:
            continue
        local_db.merge(orm_item)
        local_db.commit()

    db_items = local_db.query(model).all()

    return [return_model.from_orm(db_item) for db_item in db_items]
