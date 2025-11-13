"""Workspace management endpoints."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User, Workspace, Layer
from app.schemas import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new workspace.

    - **name**: Workspace name
    - **description**: Optional description
    """
    # Generate unique TigerGraph graphname
    tigergraph_graphname = f"geoqb_{current_user.id[:8]}_{uuid.uuid4().hex[:8]}"

    workspace = Workspace(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=workspace_data.name,
        description=workspace_data.description,
        tigergraph_graphname=tigergraph_graphname
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Add layer count
    response_data = WorkspaceResponse.model_validate(workspace)
    response_data.layer_count = 0

    return response_data


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all workspaces for the current user.
    """
    workspaces = db.query(Workspace).filter(
        Workspace.user_id == current_user.id
    ).all()

    # Add layer counts
    response_data = []
    for workspace in workspaces:
        ws_dict = WorkspaceResponse.model_validate(workspace)
        ws_dict.layer_count = db.query(Layer).filter(
            Layer.workspace_id == workspace.id
        ).count()
        response_data.append(ws_dict)

    return response_data


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get workspace by ID.
    """
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    response_data = WorkspaceResponse.model_validate(workspace)
    response_data.layer_count = db.query(Layer).filter(
        Layer.workspace_id == workspace.id
    ).count()

    return response_data


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update workspace details.
    """
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Update fields
    if workspace_data.name is not None:
        workspace.name = workspace_data.name
    if workspace_data.description is not None:
        workspace.description = workspace_data.description

    db.commit()
    db.refresh(workspace)

    response_data = WorkspaceResponse.model_validate(workspace)
    response_data.layer_count = db.query(Layer).filter(
        Layer.workspace_id == workspace.id
    ).count()

    return response_data


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a workspace and all its layers.
    """
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    db.delete(workspace)
    db.commit()

    return None
