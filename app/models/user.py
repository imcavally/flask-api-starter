"""User model with role-based access control."""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Role(enum.StrEnum):
    USER = "user"
    ADMIN = "admin"


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        Enum(Role, values_callable=lambda r: [e.value for e in r]),
        default=Role.USER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    projects: Mapped[list["Project"]] = relationship(  # noqa: F821
        back_populates="owner", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"
