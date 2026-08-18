"""Projects resource: CRUD with pagination, filtering and ownership rules.

Access rules:

* Any authenticated user can create projects and manage their own.
* Admins can see and modify every project.
* Deleting a project is admin-only (RBAC demo).
"""

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import select

from app.authz import current_user, role_required
from app.extensions import db
from app.models import Project, User
from app.schemas import (
    ProjectListSchema,
    ProjectQuerySchema,
    ProjectSchema,
    ProjectUpdateSchema,
)

blp = Blueprint(
    "projects", __name__, url_prefix="/api/v1/projects", description="Projects"
)


def _get_project_or_404(project_id: int, user: User) -> Project:
    """Fetch a project the user is allowed to access, or abort."""
    project = db.session.get(Project, project_id)
    if project is None:
        abort(404, message="Project not found.")
    if not user.is_admin and project.owner_id != user.id:
        # Hide other users' projects entirely rather than leaking existence.
        abort(404, message="Project not found.")
    return project


@blp.route("")
class ProjectList(MethodView):
    @jwt_required()
    @blp.arguments(ProjectQuerySchema, location="query")
    @blp.response(200, ProjectListSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    def get(self, args):
        """List projects (paginated, filterable by status and name)."""
        user = current_user()
        query = select(Project).order_by(Project.id.desc())
        if not user.is_admin:
            query = query.where(Project.owner_id == user.id)
        if "status" in args:
            query = query.where(Project.status == args["status"])
        if "q" in args:
            query = query.where(Project.name.ilike(f"%{args['q']}%"))

        page = db.paginate(
            query, page=args["page"], per_page=args["per_page"], error_out=False
        )
        return {
            "items": page.items,
            "meta": {
                "page": page.page,
                "per_page": page.per_page,
                "total": page.total,
                "pages": page.pages,
            },
        }

    @jwt_required()
    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    def post(self, data):
        """Create a project owned by the authenticated user."""
        user = current_user()
        project = Project(
            name=data["name"],
            description=data["description"],
            status=data["status"],
            owner_id=user.id,
        )
        db.session.add(project)
        db.session.commit()
        return project


@blp.route("/<int:project_id>")
class ProjectDetail(MethodView):
    @jwt_required()
    @blp.response(200, ProjectSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    def get(self, project_id):
        """Retrieve a single project."""
        return _get_project_or_404(project_id, current_user())

    @jwt_required()
    @blp.arguments(ProjectUpdateSchema)
    @blp.response(200, ProjectSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    def patch(self, data, project_id):
        """Partially update a project."""
        project = _get_project_or_404(project_id, current_user())
        for field in ("name", "description", "status"):
            if field in data:
                setattr(project, field, data[field])
        db.session.commit()
        return project

    @role_required("admin")
    @blp.response(204)
    @blp.doc(security=[{"bearerAuth": []}])
    def delete(self, project_id):
        """Delete a project (admin only)."""
        project = db.session.get(Project, project_id)
        if project is None:
            abort(404, message="Project not found.")
        db.session.delete(project)
        db.session.commit()
