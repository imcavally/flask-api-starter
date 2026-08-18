"""Flask extension instances.

Instantiated here (unbound) and initialised against the app in the
application factory, so they can be imported anywhere without circular
imports.
"""

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all models (SQLAlchemy 2 style)."""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
api = Api()
