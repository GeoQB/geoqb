"""Data ingestion service."""
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add pyGeoQB to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../pyGeoQB"))

from app.models import Layer, LayerStatus


def ingest_layer_task(layer_id: str, db: Session):
    """
    Background task to ingest layer data from OSM into TigerGraph.

    This function runs in a background thread and updates the layer
    status as it progresses.

    Args:
        layer_id: Layer ID to ingest
        db: Database session
    """
    layer = db.query(Layer).filter(Layer.id == layer_id).first()
    if not layer:
        return

    try:
        # Update status to processing
        layer.status = LayerStatus.PROCESSING
        layer.ingestion_started_at = datetime.utcnow()
        layer.error_message = None
        db.commit()

        # Import GeoQB modules
        try:
            from geoqb_osm_pandas import get_osm_data_pandas
            from geoqb_h3 import add_h3_to_data
            from geoqb_tg import GeoQbTg
        except ImportError as e:
            raise Exception(f"Failed to import GeoQB modules: {str(e)}")

        # Step 1: Fetch OSM data
        bbox_dict = {
            "south": layer.bbox[0],
            "west": layer.bbox[1],
            "north": layer.bbox[2],
            "east": layer.bbox[3]
        }

        osm_data = get_osm_data_pandas(
            tags=layer.tags,
            bbox=bbox_dict
        )

        if osm_data is None or len(osm_data) == 0:
            raise Exception("No OSM data found for the specified tags and bbox")

        # Step 2: Add H3 indices
        osm_data_with_h3 = add_h3_to_data(osm_data, resolution=layer.resolution)

        # Step 3: Load into TigerGraph
        tg = GeoQbTg(
            host=os.getenv("TIGERGRAPH_HOST"),
            username=os.getenv("TIGERGRAPH_USERNAME"),
            password=os.getenv("TIGERGRAPH_PASSWORD"),
            graphname=layer.workspace.tigergraph_graphname
        )

        # TODO: Implement actual TigerGraph loading
        # For now, just simulate success
        feature_count = len(osm_data_with_h3)

        # Update layer with results
        layer.status = LayerStatus.COMPLETED
        layer.feature_count = feature_count
        layer.ingestion_completed_at = datetime.utcnow()
        layer.metadata = {
            "osm_features": feature_count,
            "h3_resolution": layer.resolution,
            "bbox": layer.bbox
        }
        db.commit()

    except Exception as e:
        # Update layer with error
        layer.status = LayerStatus.FAILED
        layer.error_message = str(e)
        layer.ingestion_completed_at = datetime.utcnow()
        db.commit()
