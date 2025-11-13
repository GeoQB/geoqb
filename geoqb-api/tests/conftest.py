"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, UserPlan, UserStatus
from app.auth import get_password_hash
import uuid

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        full_name="Test User",
        plan=UserPlan.FREE,
        status=UserStatus.ACTIVE,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_workspace(test_db, test_user):
    """Create a test workspace."""
    from app.models import Workspace
    workspace = Workspace(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Test Workspace",
        description="A test workspace",
        tigergraph_graphname="test_graph"
    )
    test_db.add(workspace)
    test_db.commit()
    test_db.refresh(workspace)
    return workspace


@pytest.fixture
def test_layer(test_db, test_workspace):
    """Create a test layer."""
    from app.models import Layer, LayerStatus
    layer = Layer(
        id=str(uuid.uuid4()),
        workspace_id=test_workspace.id,
        name="Test Layer",
        layer_type="amenity",
        tags={"amenity": "hospital"},
        bbox=[50.0, 8.0, 51.0, 9.0],
        resolution=9,
        status=LayerStatus.COMPLETED,
        feature_count=10
    )
    test_db.add(layer)
    test_db.commit()
    test_db.refresh(layer)
    return layer
