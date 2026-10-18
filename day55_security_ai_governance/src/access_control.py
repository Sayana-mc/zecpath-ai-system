from dataclasses import dataclass
from typing import Iterable
from .security_errors import AccessDenied


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str


class AccessController:
    """Small RBAC policy engine. Authentication must be provided by the host app."""

    def __init__(self, roles: dict[str, list[str]]):
        self.roles = roles

    def is_allowed(self, principal: Principal, permission: str) -> bool:
        if not principal.user_id or not principal.role:
            return False
        permissions = self.roles.get(principal.role, [])
        return "*" in permissions or permission in permissions

    def require(self, principal: Principal, permission: str) -> None:
        if not self.is_allowed(principal, permission):
            raise AccessDenied(
                f"User '{principal.user_id}' with role '{principal.role}' "
                f"cannot perform '{permission}'."
            )
