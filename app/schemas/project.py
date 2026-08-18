"""Marshmallow schemas for the projects resource."""

from marshmallow import Schema, fields, validate

from app.models import ProjectStatus


class ProjectSchema(Schema):
    """Full project representation (create + read)."""

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default="")
    status = fields.Enum(ProjectStatus, by_value=True, load_default=ProjectStatus.DRAFT)
    owner_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProjectUpdateSchema(Schema):
    """Partial update -- every field optional."""

    name = fields.String(validate=validate.Length(min=1, max=120))
    description = fields.String()
    status = fields.Enum(ProjectStatus, by_value=True)


class ProjectQuerySchema(Schema):
    """Query-string arguments for listing projects."""

    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=10, validate=validate.Range(min=1, max=100))
    status = fields.Enum(ProjectStatus, by_value=True)
    q = fields.String(validate=validate.Length(min=1, max=120))


class PaginationMetaSchema(Schema):
    page = fields.Integer()
    per_page = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()


class ProjectListSchema(Schema):
    """Paginated list envelope."""

    items = fields.List(fields.Nested(ProjectSchema))
    meta = fields.Nested(PaginationMetaSchema)
