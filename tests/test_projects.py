"""Projects resource: CRUD, ownership, RBAC, pagination and filtering."""

import pytest

from app.extensions import db
from app.models import Project, ProjectStatus


def make_project(owner, name="Demo", status=ProjectStatus.DRAFT):
    project = Project(name=name, description="", status=status, owner_id=owner.id)
    db.session.add(project)
    db.session.commit()
    return project


class TestCrud:
    def test_create_project(self, client, user_headers):
        res = client.post(
            "/api/v1/projects",
            json={"name": "My API", "description": "A thing", "status": "active"},
            headers=user_headers,
        )
        assert res.status_code == 201
        body = res.get_json()
        assert body["name"] == "My API"
        assert body["status"] == "active"
        assert body["id"] > 0

    def test_create_requires_name(self, client, user_headers):
        res = client.post("/api/v1/projects", json={}, headers=user_headers)
        assert res.status_code == 422
        assert "name" in res.get_json()["errors"]["json"]

    def test_create_rejects_bad_status(self, client, user_headers):
        res = client.post(
            "/api/v1/projects",
            json={"name": "X", "status": "bogus"},
            headers=user_headers,
        )
        assert res.status_code == 422

    def test_get_project(self, client, user, user_headers):
        project = make_project(user, name="Readable")
        res = client.get(f"/api/v1/projects/{project.id}", headers=user_headers)
        assert res.status_code == 200
        assert res.get_json()["name"] == "Readable"

    def test_get_missing_project_is_404(self, client, user_headers):
        res = client.get("/api/v1/projects/9999", headers=user_headers)
        assert res.status_code == 404

    def test_patch_project(self, client, user, user_headers):
        project = make_project(user)
        res = client.patch(
            f"/api/v1/projects/{project.id}",
            json={"status": "archived"},
            headers=user_headers,
        )
        assert res.status_code == 200
        assert res.get_json()["status"] == "archived"

    def test_list_requires_auth(self, client):
        assert client.get("/api/v1/projects").status_code == 401


class TestOwnership:
    def test_user_cannot_see_others_project(self, client, user, admin, user_headers):
        other = make_project(admin, name="Admin's secret")
        res = client.get(f"/api/v1/projects/{other.id}", headers=user_headers)
        assert res.status_code == 404  # existence is not leaked

    def test_admin_sees_all_projects(self, client, user, admin, admin_headers):
        make_project(user, name="User project")
        make_project(admin, name="Admin project")
        res = client.get("/api/v1/projects", headers=admin_headers)
        assert res.get_json()["meta"]["total"] == 2


class TestRbac:
    def test_user_cannot_delete_project(self, client, user, user_headers):
        project = make_project(user)
        res = client.delete(f"/api/v1/projects/{project.id}", headers=user_headers)
        assert res.status_code == 403
        assert res.get_json()["code"] == 403
        assert db.session.get(Project, project.id) is not None

    def test_admin_can_delete_project(self, client, user, admin_headers):
        project = make_project(user)
        res = client.delete(f"/api/v1/projects/{project.id}", headers=admin_headers)
        assert res.status_code == 204
        assert db.session.get(Project, project.id) is None


class TestPaginationAndFiltering:
    @pytest.fixture()
    def many_projects(self, user):
        for i in range(1, 26):  # 25 projects
            status = ProjectStatus.ACTIVE if i % 2 else ProjectStatus.DRAFT
            make_project(user, name=f"Project {i:02d}", status=status)

    def test_default_page_size(self, client, user_headers, many_projects):
        res = client.get("/api/v1/projects", headers=user_headers)
        body = res.get_json()
        assert len(body["items"]) == 10
        assert body["meta"] == {"page": 1, "per_page": 10, "total": 25, "pages": 3}

    def test_second_page(self, client, user_headers, many_projects):
        res = client.get("/api/v1/projects?page=3&per_page=10", headers=user_headers)
        body = res.get_json()
        assert len(body["items"]) == 5
        assert body["meta"]["page"] == 3

    def test_per_page_capped_at_100(self, client, user_headers):
        res = client.get("/api/v1/projects?per_page=500", headers=user_headers)
        assert res.status_code == 422

    def test_filter_by_status(self, client, user_headers, many_projects):
        res = client.get("/api/v1/projects?status=active", headers=user_headers)
        body = res.get_json()
        assert body["meta"]["total"] == 13
        assert all(item["status"] == "active" for item in body["items"])

    def test_search_by_name(self, client, user_headers, many_projects):
        res = client.get("/api/v1/projects?q=project 07", headers=user_headers)
        body = res.get_json()
        assert body["meta"]["total"] == 1
        assert body["items"][0]["name"] == "Project 07"


class TestHealth:
    def test_health_is_public(self, client):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.get_json() == {"status": "ok"}
