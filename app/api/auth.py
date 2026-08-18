"""Authentication endpoints: register, login, refresh, current user."""

from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_smorest import Blueprint, abort
from sqlalchemy import select

from app.authz import current_user
from app.extensions import db
from app.models import User
from app.schemas import (
    AccessTokenSchema,
    LoginSchema,
    RegisterSchema,
    TokenPairSchema,
    UserSchema,
)

blp = Blueprint(
    "auth", __name__, url_prefix="/api/v1/auth", description="Authentication"
)


def _token_pair(user: User) -> dict:
    claims = {"role": user.role.value}
    return {
        "access_token": create_access_token(str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(str(user.id), additional_claims=claims),
    }


@blp.route("/register")
class Register(MethodView):
    @blp.arguments(RegisterSchema)
    @blp.response(201, UserSchema)
    def post(self, data):
        """Create a new user account."""
        exists = db.session.scalar(select(User).where(User.email == data["email"]))
        if exists:
            abort(409, message="A user with this email already exists.")
        user = User(email=data["email"])
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(200, TokenPairSchema)
    def post(self, data):
        """Exchange credentials for an access + refresh token pair."""
        user = db.session.scalar(select(User).where(User.email == data["email"]))
        if user is None or not user.check_password(data["password"]):
            abort(401, message="Invalid email or password.")
        return _token_pair(user)


@blp.route("/refresh")
class Refresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, AccessTokenSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    def post(self):
        """Issue a fresh access token from a refresh token."""
        user = db.session.get(User, int(get_jwt_identity()))
        if user is None:
            abort(401, message="User no longer exists.")
        return {
            "access_token": create_access_token(
                str(user.id), additional_claims={"role": user.role.value}
            )
        }


@blp.route("/me")
class Me(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    def get(self):
        """Return the authenticated user's profile."""
        return current_user()
