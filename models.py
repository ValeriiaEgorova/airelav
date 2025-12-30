from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    tasks: list["GenerationTask"] = Relationship(back_populates="user")


class GenerationTask(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prompt: str
    file_format: str
    status: str = "pending"
    progress: int = 0
    status_message: str = "Ожидание"

    generated_code: str | None = None
    file_path: str | None = None
    error_log: str | None = None
    preview_data: list[dict[str, Any]] | None = Field(
        default=None, sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="tasks")
