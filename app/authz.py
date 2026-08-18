"""Authorization helpers: current-user lookup and role-based access control."""

from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from flask_smorest import abort

from app.extensions import db
from app.models import User


def current_user() -> User:
    """Return the ``User`` for the verified JWT, or abort with 401."""
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        abort(401, message="User no longer exists.")
    return user


def role_required(*roles: str):
    """Protect a view: require a valid access token AND one of ``roles``.

    Usage::

        @role_required("admin")
        def delete(self, project_id): ...
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt().get("role") not in roles:
                abort(403, message="You do not have permission to perform this action.")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
