"""Marshmallow schemas for authentication endpoints."""

from marshmallow import Schema, fields, validate

from app.models import Role


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=128),
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class TokenPairSchema(Schema):
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)


class AccessTokenSchema(Schema):
    access_token = fields.String(dump_only=True)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.Enum(Role, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
