"""Application configuration, loaded from environment variables.

Every setting has a sane development default so the API boots with zero
configuration (SQLite database, generated docs at /docs). Production
deployments override values via the environment -- see ``.env.example``.
"""

import os
from datetime import timedelta


def _database_url() -> str:
    """Return the SQLAlchemy database URL.

    Falls back to a local SQLite file. Heroku-style ``postgres://`` URLs are
    rewritten to the ``postgresql://`` scheme required by SQLAlchemy 2.
    """
    url = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class BaseConfig:
    """Shared configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Database
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_DAYS", "30"))
    )

    # OpenAPI / Swagger UI (flask-smorest)
    API_TITLE = "Flask API Starter"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # in-memory
    JWT_SECRET_KEY = "test-secret-key-only-for-the-test-suite"


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
