"""API blueprints."""

from app.api.auth import blp as auth_blp
from app.api.health import blp as health_blp
from app.api.projects import blp as projects_blp

__all__ = ["auth_blp", "health_blp", "projects_blp"]
