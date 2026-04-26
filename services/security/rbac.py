# =============================================================================
# Role-Based Access Control (RBAC)
# =============================================================================
from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Any, Callable


class Role(str, Enum):
    """System roles with hierarchical permissions."""
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    RESPONDER = "responder"
    OBSERVER = "observer"


class Permission(str, Enum):
    """Granular permissions for RBAC."""
    # Messaging
    SEND_MESSAGE = "send_message"
    READ_MESSAGE = "read_message"
    BROADCAST = "broadcast"
    MANAGE_CHANNELS = "manage_channels"

    # Events
    PUBLISH_EVENT = "publish_event"
    READ_EVENTS = "read_events"

    # Predictions
    VIEW_PREDICTIONS = "view_predictions"
    MANAGE_RULES = "manage_rules"

    # Protocols
    EXECUTE_PROTOCOL = "execute_protocol"
    MANAGE_PROTOCOLS = "manage_protocols"
    VIEW_PROTOCOL_AUDIT = "view_protocol_audit"

    # Admin
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SYSTEM = "manage_system"

    # Project Management
    VIEW_WBS = "view_wbs"
    MANAGE_WBS = "manage_wbs"
    VIEW_EVA = "view_eva"


# Role → Permission mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),  # All permissions
    Role.COORDINATOR: {
        Permission.SEND_MESSAGE,
        Permission.READ_MESSAGE,
        Permission.BROADCAST,
        Permission.MANAGE_CHANNELS,
        Permission.PUBLISH_EVENT,
        Permission.READ_EVENTS,
        Permission.VIEW_PREDICTIONS,
        Permission.MANAGE_RULES,
        Permission.EXECUTE_PROTOCOL,
        Permission.MANAGE_PROTOCOLS,
        Permission.VIEW_PROTOCOL_AUDIT,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_WBS,
        Permission.VIEW_EVA,
    },
    Role.RESPONDER: {
        Permission.SEND_MESSAGE,
        Permission.READ_MESSAGE,
        Permission.PUBLISH_EVENT,
        Permission.READ_EVENTS,
        Permission.VIEW_PREDICTIONS,
        Permission.EXECUTE_PROTOCOL,
        Permission.VIEW_PROTOCOL_AUDIT,
        Permission.VIEW_WBS,
        Permission.VIEW_EVA,
    },
    Role.OBSERVER: {
        Permission.READ_MESSAGE,
        Permission.READ_EVENTS,
        Permission.VIEW_PREDICTIONS,
        Permission.VIEW_PROTOCOL_AUDIT,
        Permission.VIEW_WBS,
        Permission.VIEW_EVA,
    },
}


class RBACManager:
    """Role-Based Access Control manager."""

    def has_permission(self, role: str | Role, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        if isinstance(role, str):
            try:
                role = Role(role)
            except ValueError:
                return False
        return permission in ROLE_PERMISSIONS.get(role, set())

    def get_permissions(self, role: str | Role) -> set[Permission]:
        """Get all permissions for a role."""
        if isinstance(role, str):
            try:
                role = Role(role)
            except ValueError:
                return set()
        return ROLE_PERMISSIONS.get(role, set())

    def require_permission(self, permission: Permission) -> Callable:
        """Decorator to require a specific permission on a route."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # The actual permission check happens in the FastAPI dependency
                # This decorator just annotates the required permission
                return await func(*args, **kwargs)
            wrapper._required_permission = permission  # type: ignore
            return wrapper
        return decorator


# Singleton instance
rbac = RBACManager()
