"""Consistent JSON error handling.

Every error response -- including JWT failures and unhandled exceptions --
uses the same shape as flask-smorest's default::

    {"code": 404, "status": "Not Found", "message": "..."}

Validation errors additionally carry an ``errors`` object with per-field
details.
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.extensions import jwt


def _error_response(code: int, status: str, message: str, errors: dict | None = None):
    payload = {"code": code, "status": status, "message": message}
    if errors:
        payload["errors"] = errors
    return jsonify(payload), code


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        # flask-smorest's abort() attaches extra kwargs (custom message,
        # marshmallow validation messages) on ``error.data``.
        data = getattr(error, "data", None) or {}
        return _error_response(
            error.code,
            error.name,
            data.get("message", error.description),
            errors=data.get("messages"),
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        if isinstance(error, HTTPException):  # pragma: no cover - safety net
            return handle_http_exception(error)
        app.logger.exception("Unhandled exception")
        return _error_response(
            500, "Internal Server Error", "An unexpected error occurred."
        )

    # -- JWT errors -------------------------------------------------------
    @jwt.unauthorized_loader
    def handle_missing_token(reason: str):
        return _error_response(401, "Unauthorized", reason)

    @jwt.invalid_token_loader
    def handle_invalid_token(reason: str):
        return _error_response(401, "Unauthorized", reason)

    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header, _jwt_payload):
        return _error_response(401, "Unauthorized", "Token has expired.")

    @jwt.revoked_token_loader
    def handle_revoked_token(_jwt_header, _jwt_payload):
        return _error_response(401, "Unauthorized", "Token has been revoked.")
