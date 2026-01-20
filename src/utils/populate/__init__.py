from schema import init_relationships
from sqlalchemy.orm import Session
from utils.database import init_test_db

from utils.populate.flight_logs import insert_logs
from utils.populate.user import insert_roles, insert_users


def all_data(drop_db: False):
    init_relationships()
    local_db: Session = init_test_db(drop_db)

    roles = insert_roles(local_db)
    users = insert_users(local_db, roles)  # noqa

    insert_logs(local_db)

    return local_db
