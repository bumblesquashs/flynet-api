from typing import TypeVar

from core.db import Base
from pydantic import BaseModel
from sqlalchemy.orm import Session

SchemaType = TypeVar("SchemaType", bound=Base)
ModelType = TypeVar("ModelType", bound=BaseModel)


def update_model(model: BaseModel, identifier: int, schema_type: SchemaType, db: Session) -> SchemaType:
    if model is None or identifier <= 0 or schema_type is None or db is None:
        return None

    existing_item: schema_type = db.query(schema_type).filter(schema_type.id == identifier).first()

    if not existing_item:
        return None

    # Iterate over report object's fields to set the fields in the db object
    # This is less clean but much more concise than specifying all 50 fields again
    model_dict = vars(model)
    for key in model_dict:
        if model_dict[key] is not None:
            setattr(existing_item, key, model_dict[key])

    db.commit()

    updated_item: schema_type = db.query(schema_type).filter(schema_type.id == identifier).first()

    return updated_item
