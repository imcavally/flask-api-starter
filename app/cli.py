"""Custom Flask CLI commands."""

import click
from flask import Flask
from sqlalchemy import select

from app.extensions import db
from app.models import Role, User


def register_cli(app: Flask) -> None:
    @app.cli.command("seed-admin")
    @click.option("--email", envvar="ADMIN_EMAIL", default="admin@example.com")
    @click.option("--password", envvar="ADMIN_PASSWORD", default="change-me-please")
    def seed_admin(email: str, password: str) -> None:
        """Create (or promote) an admin user.

        Reads --email/--password options or ADMIN_EMAIL/ADMIN_PASSWORD env vars.
        Idempotent: an existing user is promoted to admin instead of duplicated.
        """
        user = db.session.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, role=Role.ADMIN)
            user.set_password(password)
            db.session.add(user)
            action = "created"
        else:
            user.role = Role.ADMIN
            action = "promoted to admin"
        db.session.commit()
        click.echo(f"Admin user {email} {action}.")
