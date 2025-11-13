"""Integration tests for typical user flows."""
import pytest
from fastapi import status


def test_complete_user_journey(client):
    """
    Test complete user journey:
    1. Sign up
    2. Create workspace
    3. Create layer
    4. Query layer
    5. Delete resources
    """
    # Step 1: Sign up
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "journey@example.com",
            "password": "securepass123",
            "full_name": "Journey User"
        }
    )
    assert signup_response.status_code == status.HTTP_201_CREATED

    # Step 2: Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "journey@example.com",
            "password": "securepass123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 3: Create workspace
    workspace_response = client.post(
        "/api/v1/workspaces",
        headers=headers,
        json={
            "name": "Journey Workspace",
            "description": "Testing complete flow"
        }
    )
    assert workspace_response.status_code == status.HTTP_201_CREATED
    workspace_id = workspace_response.json()["id"]

    # Step 4: Create layer
    layer_response = client.post(
        f"/api/v1/workspaces/{workspace_id}/layers",
        headers=headers,
        json={
            "name": "Test Hospitals",
            "layer_type": "amenity",
            "tags": {"amenity": "hospital"},
            "bbox": [50.0, 8.0, 51.0, 9.0],
            "resolution": 9
        }
    )
    assert layer_response.status_code == status.HTTP_201_CREATED
    layer_id = layer_response.json()["id"]

    # Step 5: List layers
    layers_response = client.get(
        f"/api/v1/workspaces/{workspace_id}/layers",
        headers=headers
    )
    assert layers_response.status_code == status.HTTP_200_OK
    assert len(layers_response.json()) == 1

    # Step 6: Delete layer
    delete_layer_response = client.delete(
        f"/api/v1/workspaces/{workspace_id}/layers/{layer_id}",
        headers=headers
    )
    assert delete_layer_response.status_code == status.HTTP_204_NO_CONTENT

    # Step 7: Delete workspace
    delete_workspace_response = client.delete(
        f"/api/v1/workspaces/{workspace_id}",
        headers=headers
    )
    assert delete_workspace_response.status_code == status.HTTP_204_NO_CONTENT


def test_free_tier_quota_enforcement(client, auth_headers, test_workspace, test_db):
    """Test that free tier quota limits are enforced."""
    from app.models import Layer, LayerStatus
    import uuid

    # Create layers up to free tier limit (5)
    for i in range(5):
        layer = Layer(
            id=str(uuid.uuid4()),
            workspace_id=test_workspace.id,
            name=f"Layer {i}",
            layer_type="amenity",
            tags={"amenity": "test"},
            bbox=[50.0, 8.0, 51.0, 9.0],
            resolution=9,
            status=LayerStatus.COMPLETED
        )
        test_db.add(layer)
    test_db.commit()

    # Attempt to create 6th layer (should fail)
    response = client.post(
        f"/api/v1/workspaces/{test_workspace.id}/layers",
        headers=auth_headers,
        json={
            "name": "Quota Exceeded",
            "layer_type": "amenity",
            "tags": {"amenity": "test"},
            "bbox": [50.0, 8.0, 51.0, 9.0],
            "resolution": 9
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "limit" in response.json()["detail"].lower()


def test_unauthorized_access_to_other_user_resources(client, test_db):
    """Test that users cannot access other users' resources."""
    from app.models import User, Workspace, UserPlan, UserStatus
    from app.auth import get_password_hash
    import uuid

    # Create two users
    user1 = User(
        id=str(uuid.uuid4()),
        email="user1@example.com",
        password_hash=get_password_hash("pass123"),
        full_name="User 1",
        plan=UserPlan.FREE,
        status=UserStatus.ACTIVE
    )
    user2 = User(
        id=str(uuid.uuid4()),
        email="user2@example.com",
        password_hash=get_password_hash("pass123"),
        full_name="User 2",
        plan=UserPlan.FREE,
        status=UserStatus.ACTIVE
    )
    test_db.add_all([user1, user2])
    test_db.commit()

    # User 1 creates workspace
    workspace = Workspace(
        id=str(uuid.uuid4()),
        user_id=user1.id,
        name="User 1 Workspace",
        tigergraph_graphname="graph1"
    )
    test_db.add(workspace)
    test_db.commit()

    # User 2 logs in
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user2@example.com", "password": "pass123"}
    )
    user2_token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 tries to access User 1's workspace (should fail)
    response = client.get(
        f"/api/v1/workspaces/{workspace.id}",
        headers=user2_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
