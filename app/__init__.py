"""Application factory."""

import os

from dotenv import load_dotenv
from flask import Flask

from app.cli import register_cli
from app.config import CONFIGS
from app.errors import register_error_handlers

# Alias the Api extension: importing the ``app.api`` subpackage would otherwise
# shadow a bare ``api`` name in this package's namespace.
from app.extensions import api as rest_api
from app.extensions import db, jwt, migrate


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    ``config_name`` is one of ``development`` / ``testing`` / ``production``;
    it defaults to the ``FLASK_ENV`` environment variable, then ``development``.
    """
    load_dotenv()
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    rest_api.init_app(app)

    # Document the JWT bearer scheme in the OpenAPI spec (Swagger "Authorize").
    rest_api.spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )

    # Blueprints
    from app.api import auth_blp, health_blp, projects_blp

    rest_api.register_blueprint(health_blp)
    rest_api.register_blueprint(auth_blp)
    rest_api.register_blueprint(projects_blp)

    register_error_handlers(app)
    register_cli(app)

    return app
