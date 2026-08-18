"""Liveness endpoint (no auth) -- handy for load balancers and smoke tests."""

from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields

blp = Blueprint("health", __name__, url_prefix="/api/v1", description="Health")


class HealthSchema(Schema):
    status = fields.String(dump_only=True)


@blp.route("/health")
class Health(MethodView):
    @blp.response(200, HealthSchema)
    def get(self):
        """Report service liveness."""
        return {"status": "ok"}
