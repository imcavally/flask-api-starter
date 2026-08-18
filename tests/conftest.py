"""Shared pytest fixtures."""

import pytest

from app import create_app
from app.extensions import db
from app.models import Role, User


@pytest.fixture()
def app():
    """A fresh application + in-memory database per test."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    """A regular user with a known password."""
    user = User(email="user@example.com", role=Role.USER)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def admin(app):
    """An admin user with a known password."""
    admin = User(email="admin@example.com", role=Role.ADMIN)
    admin.set_password("password123")
    db.session.add(admin)
    db.session.commit()
    return admin


def login(client, email, password="password123"):
    """Log in and return the token pair."""
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.get_json()
    return res.get_json()


def auth_header(client, email, password="password123"):
    """Return an Authorization header for the given credentials."""
    tokens = login(client, email, password)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture()
def user_headers(client, user):
    return auth_header(client, user.email)


@pytest.fixture()
def admin_headers(client, admin):
    return auth_header(client, admin.email)
