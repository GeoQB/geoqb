"""Layer management endpoints."""
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User, Workspace, Layer, LayerStatus, UsageEvent
from app.schemas import LayerCreate, LayerUpdate, LayerResponse, UsageEventCreate
from app.services.quota import check_layer_quota
from app.services.ingestion import ingest_layer_task

router = APIRouter(prefix="/layers", tags=["layers"])


@router.post("/{workspace_id}/layers", response_model=LayerResponse, status_code=status.HTTP_201_CREATED)
async def create_layer(
    workspace_id: str,
    layer_data: LayerCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new layer in a workspace.

    This will start a background ingestion process to fetch and load OSM data.

    - **name**: Layer name
    - **layer_type**: Type (amenity, building, highway, etc.)
    - **tags**: OSM tags to filter (e.g., {"amenity": "hospital"})
    - **bbox**: Bounding box [lat_min, lon_min, lat_max, lon_max]
    - **resolution**: H3 resolution (6-15, default 9)
    """
    # Check if workspace exists and belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check quota
    quota_ok, error_msg = check_layer_quota(db, current_user)
    if not quota_ok:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_msg
        )

    # Create layer
    layer = Layer(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        name=layer_data.name,
        layer_type=layer_data.layer_type,
        tags=layer_data.tags,
        bbox=layer_data.bbox,
        resolution=layer_data.resolution,
        status=LayerStatus.PENDING
    )

    db.add(layer)

    # Track usage
    usage_event = UsageEvent(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        event_type="layer_created",
        resource_id=layer.id,
        quantity=1
    )
    db.add(usage_event)

    db.commit()
    db.refresh(layer)

    # Start background ingestion
    background_tasks.add_task(ingest_layer_task, layer.id, db)

    return layer


@router.get("/{workspace_id}/layers", response_model=List[LayerResponse])
async def list_layers(
    workspace_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all layers in a workspace.
    """
    # Check workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    layers = db.query(Layer).filter(
        Layer.workspace_id == workspace_id
    ).all()

    return layers


@router.get("/{workspace_id}/layers/{layer_id}", response_model=LayerResponse)
async def get_layer(
    workspace_id: str,
    layer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get layer details by ID.
    """
    # Check workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    layer = db.query(Layer).filter(
        Layer.id == layer_id,
        Layer.workspace_id == workspace_id
    ).first()

    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )

    return layer


@router.patch("/{workspace_id}/layers/{layer_id}", response_model=LayerResponse)
async def update_layer(
    workspace_id: str,
    layer_id: str,
    layer_data: LayerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update layer details.

    Note: Changing tags, bbox, or resolution will NOT re-ingest data.
    Delete and recreate the layer to re-ingest with new parameters.
    """
    # Check workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    layer = db.query(Layer).filter(
        Layer.id == layer_id,
        Layer.workspace_id == workspace_id
    ).first()

    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )

    # Update fields
    if layer_data.name is not None:
        layer.name = layer_data.name
    if layer_data.tags is not None:
        layer.tags = layer_data.tags
    if layer_data.bbox is not None:
        layer.bbox = layer_data.bbox
    if layer_data.resolution is not None:
        layer.resolution = layer_data.resolution

    db.commit()
    db.refresh(layer)

    return layer


@router.delete("/{workspace_id}/layers/{layer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_layer(
    workspace_id: str,
    layer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a layer.

    This will remove the layer from the database and TigerGraph.
    """
    # Check workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    layer = db.query(Layer).filter(
        Layer.id == layer_id,
        Layer.workspace_id == workspace_id
    ).first()

    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )

    # TODO: Delete from TigerGraph

    db.delete(layer)
    db.commit()

    return None


@router.post("/{workspace_id}/layers/{layer_id}/reingest", response_model=LayerResponse)
async def reingest_layer(
    workspace_id: str,
    layer_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trigger re-ingestion of layer data.

    This will re-fetch OSM data and reload into TigerGraph.
    """
    # Check workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    layer = db.query(Layer).filter(
        Layer.id == layer_id,
        Layer.workspace_id == workspace_id
    ).first()

    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )

    # Reset layer status
    layer.status = LayerStatus.PENDING
    layer.error_message = None
    layer.feature_count = 0
    layer.ingestion_started_at = None
    layer.ingestion_completed_at = None

    db.commit()
    db.refresh(layer)

    # Start background ingestion
    background_tasks.add_task(ingest_layer_task, layer.id, db)

    return layer
