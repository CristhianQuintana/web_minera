from dataclasses import dataclass

from app.domain.entities import Actor
from app.domain.exceptions import ForbiddenError
from app.domain.value_objects import Permission, allows


@dataclass
class AuthContext:
    actor: Actor
    access_token: str

    def require(self, permission: Permission) -> None:
        if not allows(self.actor.role, permission):
            raise ForbiddenError("No tienes permisos para realizar esta acción.")

    def is_admin(self) -> bool:
        return self.actor.role.value == "admin"
