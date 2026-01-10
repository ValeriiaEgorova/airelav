import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from database import get_session
from main import app

sqlite_file_name = "database.db"
sqlite_url = "sqlite:///:memory:"

engine = create_engine(
    sqlite_url, connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """
    Полностью отключает RateLimiter.
    """

    # 1. Функция без аргументов.
    # FastAPI увидит её, поймет, что ей ничего не нужно, и просто вызовет.
    async def mock_call():
        return None

    # 2. Патчим __call__.
    # Важно: используем side_effect, чтобы подменить логику вызова.
    with patch("fastapi_limiter.depends.RateLimiter.__call__", side_effect=mock_call):
        # 3. Патчим init, чтобы не требовал Redis
        with patch("fastapi_limiter.FastAPILimiter.init", new=AsyncMock()):
            yield
