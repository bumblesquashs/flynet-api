from typing import List

from model.role import RoleModel
from schema.role import Role
from sqlalchemy.orm import Session


class RoleContext:
    def __init__(self, db: Session):
        self.db = db

    def get_scopes(self, slug: str) -> List[str]:
        """Get the list of scopes for a given role; this is really simple right now."""
        role = self.db.query(Role).filter(Role.slug == slug).first()

        if not role:
            return []

        if role.slug.lower() == "admin":
            return ["me", "user", "admin"]

        return ["me", "user"]

    def get_roles(self) -> List[RoleModel]:
        query = self.db.query(Role)
        return query.all()
