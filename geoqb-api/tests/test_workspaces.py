"""Tests for workspace endpoints."""
import pytest
from fastapi import status


def test_create_workspace_success(client, auth_headers):
    """Test successful workspace creation."""
    response = client.post(
        "/api/v1/workspaces",
        headers=auth_headers,
        json={
            "name": "My Workspace",
            "description": "A test workspace"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "My Workspace"
    assert data["description"] == "A test workspace"
    assert data["tigergraph_graphname"] is not None
    assert data["layer_count"] == 0


def test_create_workspace_unauthorized(client):
    """Test workspace creation without auth fails."""
    response = client.post(
        "/api/v1/workspaces",
        json={"name": "Test Workspace"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_workspaces(client, auth_headers, test_workspace):
    """Test listing workspaces."""
    response = client.get("/api/v1/workspaces", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == test_workspace.name


def test_get_workspace(client, auth_headers, test_workspace):
    """Test getting workspace by ID."""
    response = client.get(
        f"/api/v1/workspaces/{test_workspace.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_workspace.id
    assert data["name"] == test_workspace.name


def test_get_nonexistent_workspace(client, auth_headers):
    """Test getting nonexistent workspace fails."""
    response = client.get(
        "/api/v1/workspaces/nonexistent-id",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_workspace(client, auth_headers, test_workspace):
    """Test updating workspace."""
    response = client.patch(
        f"/api/v1/workspaces/{test_workspace.id}",
        headers=auth_headers,
        json={
            "name": "Updated Workspace",
            "description": "Updated description"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Workspace"
    assert data["description"] == "Updated description"


def test_delete_workspace(client, auth_headers, test_workspace):
    """Test deleting workspace."""
    response = client.delete(
        f"/api/v1/workspaces/{test_workspace.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify workspace is deleted
    response = client.get(
        f"/api/v1/workspaces/{test_workspace.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
