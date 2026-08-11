from schema import init_relationships
from sqlalchemy.orm import Session
from utils.database import init_test_db

from utils.populate.flight_logs import insert_logs
from utils.populate.user import insert_roles, insert_users, insert_settings
from utils.populate.airports import insert_airports
from utils.populate.aircraft import insert_aircraft
from utils.populate.airlines import insert_airlines



def all_data(drop_db: False):
    init_relationships()
    local_db: Session = init_test_db(drop_db)

    insert_settings(local_db)
    roles = insert_roles(local_db)
    users = insert_users(local_db, roles)  # noqa

    insert_airports(local_db)
    insert_aircraft(local_db)
    insert_airlines(local_db)

    insert_logs(local_db)

    return local_db
