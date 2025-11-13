"""Tests for layer endpoints."""
import pytest
from fastapi import status


def test_create_layer_success(client, auth_headers, test_workspace):
    """Test successful layer creation."""
    response = client.post(
        f"/api/v1/workspaces/{test_workspace.id}/layers",
        headers=auth_headers,
        json={
            "name": "Hospitals",
            "layer_type": "amenity",
            "tags": {"amenity": "hospital"},
            "bbox": [50.0, 8.0, 51.0, 9.0],
            "resolution": 9
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Hospitals"
    assert data["layer_type"] == "amenity"
    assert data["tags"] == {"amenity": "hospital"}
    assert data["status"] == "pending"


def test_create_layer_invalid_bbox(client, auth_headers, test_workspace):
    """Test layer creation with invalid bbox fails."""
    response = client.post(
        f"/api/v1/workspaces/{test_workspace.id}/layers",
        headers=auth_headers,
        json={
            "name": "Test Layer",
            "layer_type": "amenity",
            "tags": {"amenity": "hospital"},
            "bbox": [50.0, 8.0, 45.0, 9.0],  # Invalid: lat_min > lat_max
            "resolution": 9
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_layers(client, auth_headers, test_workspace, test_layer):
    """Test listing layers in workspace."""
    response = client.get(
        f"/api/v1/workspaces/{test_workspace.id}/layers",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == test_layer.name


def test_get_layer(client, auth_headers, test_workspace, test_layer):
    """Test getting layer by ID."""
    response = client.get(
        f"/api/v1/workspaces/{test_workspace.id}/layers/{test_layer.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_layer.id
    assert data["name"] == test_layer.name


def test_update_layer(client, auth_headers, test_workspace, test_layer):
    """Test updating layer."""
    response = client.patch(
        f"/api/v1/workspaces/{test_workspace.id}/layers/{test_layer.id}",
        headers=auth_headers,
        json={"name": "Updated Layer"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Layer"


def test_delete_layer(client, auth_headers, test_workspace, test_layer):
    """Test deleting layer."""
    response = client.delete(
        f"/api/v1/workspaces/{test_workspace.id}/layers/{test_layer.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify layer is deleted
    response = client.get(
        f"/api/v1/workspaces/{test_workspace.id}/layers/{test_layer.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_reingest_layer(client, auth_headers, test_workspace, test_layer):
    """Test re-ingesting layer."""
    response = client.post(
        f"/api/v1/workspaces/{test_workspace.id}/layers/{test_layer.id}/reingest",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "pending"
    assert data["feature_count"] == 0
