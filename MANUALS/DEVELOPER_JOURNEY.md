# GeoQB Developer Journey

**From Beginner to Production: Building Spatial Knowledge Graph Applications**

Master GeoQB development from basic scripts to production-ready applications.

---

## 🎯 Learning Path Overview

```
Level 1: Foundations (2-4 hours)
├─ Setup development environment
├─ Understand the architecture
├─ Work with layers and queries
└─ Basic data ingestion

Level 2: Intermediate (4-8 hours)
├─ Multi-layer analysis
├─ Custom data integration
├─ Graph querying with GSQL
└─ Visualization techniques

Level 3: Advanced (8-16 hours)
├─ Real-time streaming with Kafka
├─ Graph machine learning
├─ Custom algorithms
└─ Performance optimization

Level 4: Production (16+ hours)
├─ API development
├─ Docker deployment
├─ Monitoring and logging
└─ Security best practices
```

**Total Time:** 30-50 hours for complete mastery
**Prerequisites:** Python, Git, basic SQL, Docker (for Level 4)

---

## Level 1: Foundations

### Module 1.1: Development Environment Setup

#### Professional Development Setup

```bash
# Clone and setup
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB

# Create development environment
python3 -m venv venv-dev
source venv-dev/bin/activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Install development tools
pip install \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython \
    jupyter \
    pylint

# Setup pre-commit hooks (recommended)
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Format code
black geoanalysis/

# Lint
flake8 geoanalysis/ --max-line-length=100

# Type check
mypy geoanalysis/ --ignore-missing-imports
EOF

chmod +x .git/hooks/pre-commit
```

#### IDE Configuration

**VS Code** (`settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "python.analysis.typeCheckingMode": "basic"
}
```

**PyCharm**: File → Settings → Tools → External Tools → Add Black, Flake8

#### Exercise 1.1: Verify Setup

Create `test_setup.py`:

```python
#!/usr/bin/env python3
"""Verify development environment"""

def test_imports():
    """Test all major imports work"""
    try:
        from geoanalysis.geoqb import (
            GeoQbLayers,
            GeoQbTG,
            lat_lon_to_h3,
            fetch_osm_data_overpass
        )
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tigergraph_connection():
    """Test TigerGraph connection"""
    import os
    from geoanalysis.geoqb.geoqb_tg import GeoQbTG

    tg = GeoQbTG(
        host=os.getenv('TG_URL'),
        username=os.getenv('TG_USERNAME'),
        password=os.getenv('TG_PASSWORD')
    )

    if tg.test_connection():
        print("✅ TigerGraph connected!")
        return True
    else:
        print("❌ TigerGraph connection failed!")
        return False

if __name__ == '__main__':
    import sys
    success = test_imports() and test_tigergraph_connection()
    sys.exit(0 if success else 1)
```

Run:
```bash
python test_setup.py
```

---

### Module 1.2: Understanding the Architecture

#### Component Interaction

```python
"""
Understanding the GeoQB architecture through code
"""

from geoanalysis.geoqb import GeoQbLayers, GeoQbTG
from geoanalysis.geoqb.geoqb_h3 import lat_lon_to_h3, get_h3_neighbors
import os

# 1. LAYER MANAGER - Defines what data to fetch
layers = GeoQbLayers(workspace_path=os.getenv('GEOQB_WORKSPACE'))

# 2. SPATIAL INDEXER - Converts coordinates to H3
lat, lon = 50.1109, 8.6821  # Frankfurt
h3_index = lat_lon_to_h3(lat, lon, resolution=9)
neighbors = get_h3_neighbors(h3_index)

print(f"H3 Index: {h3_index}")
print(f"Neighbors: {len(neighbors)}")

# 3. GRAPH DATABASE - Stores and queries data
tg = GeoQbTG(
    host=os.getenv('TG_URL'),
    username=os.getenv('TG_USERNAME'),
    password=os.getenv('TG_PASSWORD')
)

# 4. DATA FLOW
# OSM API → Layer Manager → H3 Indexer → TigerGraph → Analysis
```

#### Exercise 1.2: Trace Data Flow

Write code that:
1. Fetches hospitals from OSM
2. Converts coordinates to H3 (resolution 9)
3. Loads into TigerGraph
4. Queries back from TigerGraph
5. Prints comparison

**Solution template:**
```python
# Your code here
# Step 1: Fetch from OSM
data_osm = fetch_osm_data_overpass(bbox, tags)

# Step 2: Add H3
data_h3 = data_osm.copy()
data_h3['h3'] = data_h3.apply(lambda r: lat_lon_to_h3(r['lat'], r['lon'], 9), axis=1)

# Step 3: Load to TG
# ... your implementation

# Step 4: Query back
# ... your implementation

# Step 5: Compare
print(f"OSM records: {len(data_osm)}")
print(f"TG records: {result_count}")
```

---

### Module 1.3: Working with Layers

#### Layer Definition Best Practices

```python
"""
Professional layer definition and management
"""

from geoanalysis.geoqb import GeoQbLayers
from typing import Dict, List, Tuple
import json

class LayerFactory:
    """Factory for creating well-structured layer definitions"""

    @staticmethod
    def create_amenity_layer(
        name: str,
        amenity_type: str,
        bbox: Tuple[float, float, float, float],
        resolution: int = 9,
        description: str = ""
    ) -> Dict:
        """
        Create a standardized amenity layer.

        Args:
            name: Unique layer name (e.g., 'frankfurt_hospitals')
            amenity_type: OSM amenity tag value
            bbox: (lat_min, lon_min, lat_max, lon_max)
            resolution: H3 resolution (6, 9, or 12)
            description: Human-readable description

        Returns:
            Layer definition dictionary
        """
        return {
            'name': name,
            'type': 'amenity',
            'tags': {'amenity': amenity_type},
            'bbox': list(bbox),
            'resolution': resolution,
            'description': description or f"{amenity_type} locations",
            'created_at': pd.Timestamp.now().isoformat(),
            'version': '1.0'
        }

    @staticmethod
    def create_composite_layer(
        name: str,
        layers: List[str],
        operation: str = 'union',
        description: str = ""
    ) -> Dict:
        """Create a layer that combines multiple other layers"""
        return {
            'name': name,
            'type': 'composite',
            'source_layers': layers,
            'operation': operation,  # union, intersection, difference
            'description': description,
            'created_at': pd.Timestamp.now().isoformat(),
            'version': '1.0'
        }

# Usage
factory = LayerFactory()

hospitals = factory.create_amenity_layer(
    name='hospitals',
    amenity_type='hospital',
    bbox=(50.0, 8.5, 50.2, 8.8),
    description="All hospitals in Frankfurt"
)

pharmacies = factory.create_amenity_layer(
    name='pharmacies',
    amenity_type='pharmacy',
    bbox=(50.0, 8.5, 50.2, 8.8),
    description="All pharmacies in Frankfurt"
)

healthcare = factory.create_composite_layer(
    name='healthcare',
    layers=['hospitals', 'pharmacies'],
    operation='union',
    description="Combined healthcare facilities"
)
```

#### Exercise 1.3: Layer Manager

Build a command-line layer manager:

```python
#!/usr/bin/env python3
"""
Layer Management CLI

Usage:
    python layer_manager.py list
    python layer_manager.py create hospitals --amenity hospital --bbox 50,8,51,9
    python layer_manager.py delete hospitals
    python layer_manager.py export hospitals
"""

import click
import json
from pathlib import Path

@click.group()
def cli():
    """GeoQB Layer Manager"""
    pass

@cli.command()
def list():
    """List all layers"""
    # Your implementation
    pass

@cli.command()
@click.argument('name')
@click.option('--amenity', required=True)
@click.option('--bbox', required=True, help='lat_min,lon_min,lat_max,lon_max')
@click.option('--resolution', default=9, type=int)
def create(name, amenity, bbox, resolution):
    """Create a new layer"""
    # Your implementation
    pass

@cli.command()
@click.argument('name')
def delete(name):
    """Delete a layer"""
    # Your implementation
    pass

@cli.command()
@click.argument('name')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json')
def export(name, format):
    """Export layer definition"""
    # Your implementation
    pass

if __name__ == '__main__':
    cli()
```

**Challenge:** Add validation, error handling, and tests!

---

### Module 1.4: Data Ingestion Pipeline

#### Production-Ready Ingestion

```python
"""
Robust data ingestion pipeline with error handling
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IngestionStatus(Enum):
    """Ingestion pipeline statuses"""
    PENDING = "pending"
    FETCHING = "fetching"
    PROCESSING = "processing"
    LOADING = "loading"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class IngestionResult:
    """Result of an ingestion operation"""
    layer_name: str
    status: IngestionStatus
    records_fetched: int
    records_processed: int
    records_loaded: int
    errors: List[str]
    duration_seconds: float

class IngestionPipeline:
    """
    Production-ready data ingestion pipeline

    Features:
    - Retry logic
    - Error handling
    - Progress tracking
    - Validation
    - Logging
    """

    def __init__(self, tg_client, workspace_path: str):
        self.tg = tg_client
        self.workspace = workspace_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def ingest_layer(
        self,
        layer_def: Dict,
        retry_count: int = 3,
        validate: bool = True
    ) -> IngestionResult:
        """
        Ingest a layer with full error handling

        Args:
            layer_def: Layer definition dictionary
            retry_count: Number of retries on failure
            validate: Whether to validate data before loading

        Returns:
            IngestionResult with details
        """
        start_time = time.time()
        errors = []

        try:
            # Step 1: Fetch
            self.logger.info(f"Fetching layer: {layer_def['name']}")
            data = self._fetch_with_retry(layer_def, retry_count)

            # Step 2: Process
            self.logger.info(f"Processing {len(data)} records")
            processed = self._process_data(data, layer_def)

            # Step 3: Validate (optional)
            if validate:
                self.logger.info("Validating data")
                validation_errors = self._validate_data(processed)
                if validation_errors:
                    errors.extend(validation_errors)
                    if len(validation_errors) > len(processed) * 0.1:  # >10% errors
                        raise ValueError(f"Validation failed: {len(validation_errors)} errors")

            # Step 4: Load
            self.logger.info("Loading to TigerGraph")
            loaded_count = self._load_to_tigergraph(processed, layer_def)

            duration = time.time() - start_time
            return IngestionResult(
                layer_name=layer_def['name'],
                status=IngestionStatus.COMPLETED,
                records_fetched=len(data),
                records_processed=len(processed),
                records_loaded=loaded_count,
                errors=errors,
                duration_seconds=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Ingestion failed: {e}", exc_info=True)
            return IngestionResult(
                layer_name=layer_def['name'],
                status=IngestionStatus.FAILED,
                records_fetched=0,
                records_processed=0,
                records_loaded=0,
                errors=[str(e)] + errors,
                duration_seconds=duration
            )

    def _fetch_with_retry(self, layer_def: Dict, retry_count: int):
        """Fetch data with exponential backoff retry"""
        for attempt in range(retry_count):
            try:
                return fetch_osm_data_overpass(
                    bbox=layer_def['bbox'],
                    tags=layer_def['tags'],
                    timeout=180
                )
            except Exception as e:
                if attempt == retry_count - 1:
                    raise
                wait_time = 2 ** attempt  # Exponential backoff
                self.logger.warning(f"Fetch failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                time.sleep(wait_time)

    def _process_data(self, data, layer_def: Dict):
        """Process raw data (add H3, clean, etc.)"""
        # Add H3 indices
        data['h3_index'] = data.apply(
            lambda r: lat_lon_to_h3(r['lat'], r['lon'], layer_def['resolution']),
            axis=1
        )
        return data

    def _validate_data(self, data) -> List[str]:
        """Validate processed data"""
        errors = []

        # Check for nulls
        null_counts = data.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                errors.append(f"Column {col} has {count} null values")

        # Check H3 indices are valid
        invalid_h3 = data[~data['h3_index'].str.match(r'^[0-9a-f]{15}$')]
        if len(invalid_h3) > 0:
            errors.append(f"{len(invalid_h3)} invalid H3 indices")

        return errors

    def _load_to_tigergraph(self, data, layer_def: Dict) -> int:
        """Load data to TigerGraph"""
        # Prepare vertices
        vertices = data.to_dict('records')

        # Upsert
        result = self.tg.upsert_vertices('h3place', vertices)
        return len(vertices)

# Usage
pipeline = IngestionPipeline(tg_client, workspace_path)
result = pipeline.ingest_layer(layer_def, retry_count=3, validate=True)

print(f"Status: {result.status}")
print(f"Loaded: {result.records_loaded} records")
print(f"Duration: {result.duration_seconds:.2f}s")
if result.errors:
    print(f"Errors: {result.errors}")
```

#### Exercise 1.4: Build Your Pipeline

Create a complete ingestion pipeline that:
1. Reads layer definition from JSON file
2. Fetches data with retry logic
3. Validates data quality
4. Loads to TigerGraph
5. Generates a summary report

**Bonus:** Add progress bars using `tqdm`!

---

## Level 2: Intermediate

### Module 2.1: Multi-Layer Analysis

#### Layer Combination Strategies

```python
"""
Advanced multi-layer analysis techniques
"""

from typing import List, Dict
import pandas as pd
import numpy as np

class MultiLayerAnalyzer:
    """Analyze relationships across multiple layers"""

    def __init__(self, tg_client):
        self.tg = tg_client

    def calculate_accessibility_score(
        self,
        h3_index: str,
        layers: List[str],
        weights: Dict[str, float],
        distance_threshold: int = 5  # H3 k-ring distance
    ) -> float:
        """
        Calculate accessibility score for a location.

        Score = Σ (weight_i * count_i) / total_weight

        Args:
            h3_index: H3 cell to score
            layers: List of layer names to consider
            weights: Dict of layer_name -> weight
            distance_threshold: Max distance in H3 cells

        Returns:
            Accessibility score (0-1)
        """
        # Get nearby cells
        from geoanalysis.geoqb.geoqb_h3 import k_ring
        nearby_cells = k_ring(h3_index, distance_threshold)

        # Count amenities per layer
        layer_counts = {}
        for layer in layers:
            count = self._count_amenities_in_cells(layer, nearby_cells)
            layer_counts[layer] = count

        # Calculate weighted score
        total_weight = sum(weights.values())
        score = sum(
            weights.get(layer, 0) * count
            for layer, count in layer_counts.items()
        ) / total_weight if total_weight > 0 else 0

        # Normalize to 0-1
        return min(score / 10.0, 1.0)  # Assume 10+ is maximum

    def _count_amenities_in_cells(
        self,
        layer_name: str,
        h3_cells: List[str]
    ) -> int:
        """Count amenities in specified H3 cells"""
        # Query TigerGraph
        query = f"""
        SELECT COUNT(*) as count
        FROM h3place
        WHERE h3place.id IN ({','.join(f"'{c}'" for c in h3_cells)})
          AND h3place.layer_id = '{layer_name}'
        """
        result = self.tg.run_query(query)
        return result[0]['count'] if result else 0

    def find_optimal_locations(
        self,
        bbox: Tuple[float, float, float, float],
        resolution: int,
        layers: List[str],
        weights: Dict[str, float],
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Find top N locations with best accessibility.

        Args:
            bbox: Bounding box to search
            resolution: H3 resolution
            layers: Layers to consider
            weights: Layer weights
            top_n: Number of results

        Returns:
            DataFrame with top locations and scores
        """
        # Generate H3 grid for bbox
        from geoanalysis.geoqb.geoqb_h3 import bbox_to_h3_cells
        h3_cells = bbox_to_h3_cells(bbox, resolution)

        # Score each cell
        scores = []
        for h3_index in h3_cells:
            score = self.calculate_accessibility_score(
                h3_index, layers, weights
            )
            lat, lon = h3_to_lat_lon(h3_index)
            scores.append({
                'h3_index': h3_index,
                'lat': lat,
                'lon': lon,
                'score': score
            })

        # Convert to DataFrame and sort
        df = pd.DataFrame(scores)
        df = df.nlargest(top_n, 'score')
        return df

# Usage
analyzer = MultiLayerAnalyzer(tg_client)

# Define weights for different amenities
weights = {
    'hospitals': 0.25,
    'schools': 0.20,
    'public_transport': 0.30,
    'parks': 0.15,
    'grocery_stores': 0.10
}

# Find best locations in Frankfurt
best_locations = analyzer.find_optimal_locations(
    bbox=(50.0, 8.5, 50.2, 8.8),
    resolution=9,
    layers=list(weights.keys()),
    weights=weights,
    top_n=10
)

print("Top 10 most accessible locations:")
print(best_locations)
```

#### Exercise 2.1: Sustainability Scorer

Build a complete sustainability scoring system:

**Requirements:**
1. Support at least 5 layers (transport, healthcare, education, parks, shops)
2. Customizable weights
3. Cache results for performance
4. Generate visual heatmap
5. Export to CSV/JSON

**Deliverable:** Working application with tests

---

### Module 2.2: Custom Data Integration

#### Integrating External Data Sources

```python
"""
Integrate custom CSV data into GeoQB
"""

import pandas as pd
from typing import Optional
from geoanalysis.geoqb.geoqb_h3 import lat_lon_to_h3

class CustomDataIntegrator:
    """Integrate custom datasets into GeoQB"""

    def __init__(self, tg_client):
        self.tg = tg_client

    def load_csv_with_coordinates(
        self,
        csv_path: str,
        lat_column: str,
        lon_column: str,
        layer_name: str,
        resolution: int = 9,
        additional_columns: Optional[List[str]] = None
    ) -> int:
        """
        Load CSV with lat/lon coordinates.

        Args:
            csv_path: Path to CSV file
            lat_column: Name of latitude column
            lon_column: Name of longitude column
            layer_name: Layer name to create
            resolution: H3 resolution
            additional_columns: Extra columns to include

        Returns:
            Number of records loaded
        """
        # Load CSV
        df = pd.read_csv(csv_path)

        # Validate columns exist
        required = [lat_column, lon_column]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Add H3 index
        df['h3_index'] = df.apply(
            lambda r: lat_lon_to_h3(r[lat_column], r[lon_column], resolution),
            axis=1
        )

        # Prepare vertices
        columns_to_include = additional_columns or []
        vertices = []

        for _, row in df.iterrows():
            vertex = {
                'id': row['h3_index'],
                'resolution': resolution,
                'layer_id': layer_name,
                'lat': row[lat_column],
                'lon': row[lon_column]
            }

            # Add additional attributes
            for col in columns_to_include:
                if col in df.columns:
                    vertex[col] = row[col]

            vertices.append(vertex)

        # Upsert to TigerGraph
        self.tg.upsert_vertices('h3place', vertices)
        return len(vertices)

    def load_geojson(
        self,
        geojson_path: str,
        layer_name: str,
        resolution: int = 9
    ) -> int:
        """Load GeoJSON file"""
        import geopandas as gpd

        # Load GeoJSON
        gdf = gpd.read_file(geojson_path)

        # Extract centroids
        gdf['centroid'] = gdf.geometry.centroid
        gdf['lat'] = gdf.centroid.y
        gdf['lon'] = gdf.centroid.x

        # Add H3
        gdf['h3_index'] = gdf.apply(
            lambda r: lat_lon_to_h3(r['lat'], r['lon'], resolution),
            axis=1
        )

        # Convert to regular DataFrame and load
        df = pd.DataFrame(gdf.drop(columns='geometry'))
        # ... (similar to CSV loading)

        return len(gdf)

# Example: Load custom POI data
integrator = CustomDataIntegrator(tg_client)

# Load from CSV
count = integrator.load_csv_with_coordinates(
    csv_path='custom_pois.csv',
    lat_column='latitude',
    lon_column='longitude',
    layer_name='custom_pois',
    resolution=9,
    additional_columns=['name', 'type', 'rating']
)

print(f"Loaded {count} custom POIs")
```

#### Exercise 2.2: Data Connector Library

Build connectors for:
1. Google Sheets
2. PostgreSQL/PostGIS
3. REST API endpoints
4. Parquet files

**Template:**
```python
class DataConnector:
    """Base class for data connectors"""

    def fetch(self) -> pd.DataFrame:
        """Fetch data from source"""
        raise NotImplementedError

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate fetched data"""
        raise NotImplementedError

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform to GeoQB format"""
        raise NotImplementedError

class GoogleSheetsConnector(DataConnector):
    # Your implementation
    pass

class PostgreSQLConnector(DataConnector):
    # Your implementation
    pass
```

---

### Module 2.3: Graph Querying with GSQL

#### Writing Custom GSQL Queries

```gsql
/*
 * Find hot spots: H3 cells with multiple amenities
 *
 * This query identifies locations with high amenity density
 */

CREATE QUERY find_hotspots(
    /* Input parameters */
    SET<STRING> amenity_types,
    INT min_count = 5,
    INT max_results = 100
) FOR GRAPH OSMGraph {

    /* Type definitions */
    SumAccum<INT> @@count;
    MapAccum<STRING, INT> @amenity_counts;

    /* Start from H3 cells */
    Cells = SELECT c
            FROM h3place:c
            WHERE c.layer_id IN amenity_types
            ACCUM c.@amenity_counts += (c.layer_id -> 1);

    /* Filter cells with multiple amenities */
    Hotspots = SELECT c
               FROM Cells:c
               WHERE c.@amenity_counts.size() >= min_count
               ORDER BY c.@amenity_counts.size() DESC
               LIMIT max_results;

    PRINT Hotspots;
}
```

**Install and run:**
```python
from geoanalysis.geoqb import GeoQbTG

tg = GeoQbTG(host, username, password)

# Install query
with open('find_hotspots.gsql', 'r') as f:
    query_text = f.read()
    tg.install_query(query_text)

# Run query
results = tg.run_installed_query(
    'find_hotspots',
    params={
        'amenity_types': ['hospitals', 'schools', 'parks'],
        'min_count': 3,
        'max_results': 50
    }
)

print(f"Found {len(results)} hotspots")
```

#### Exercise 2.3: Query Library

Build a library of useful GSQL queries:

1. **Shortest Path**: Find shortest path between two locations
2. **Community Detection**: Find communities in spatial network
3. **Influence Spreading**: Simulate influence propagation
4. **Anomaly Detection**: Find unusual spatial patterns
5. **Time-Series Analysis**: Analyze temporal changes

**Deliverable:** GSQL files + Python wrappers + tests

---

## Level 3: Advanced

### Module 3.1: Real-Time Streaming with Kafka

#### Building a Streaming Pipeline

```python
"""
Real-time spatial data streaming with Kafka
"""

from confluent_kafka import Producer, Consumer
from geoanalysis.geoqb.geoqb_kafka import KafkaManager
from geoanalysis.geoqb.geoqb_h3 import lat_lon_to_h3
import json

class SpatialStreamProcessor:
    """Process spatial events in real-time"""

    def __init__(self, kafka_config, tg_client):
        self.kafka = KafkaManager(**kafka_config)
        self.tg = tg_client

    def start_processing(
        self,
        input_topic: str,
        layer_name: str,
        resolution: int = 9,
        batch_size: int = 100
    ):
        """
        Start processing spatial events from Kafka.

        Args:
            input_topic: Kafka topic to consume from
            layer_name: Layer name for processed data
            resolution: H3 resolution
            batch_size: Batch size for TigerGraph upserts
        """
        def process_message(msg):
            """Process a single message"""
            try:
                # Parse JSON
                event = json.loads(msg.value().decode('utf-8'))

                # Extract coordinates
                lat = event['latitude']
                lon = event['longitude']

                # Add H3 index
                h3_index = lat_lon_to_h3(lat, lon, resolution)

                # Prepare vertex
                vertex = {
                    'id': h3_index,
                    'resolution': resolution,
                    'layer_id': layer_name,
                    'timestamp': event.get('timestamp'),
                    'event_type': event.get('type')
                }

                # Buffer for batch processing
                self.buffer.append(vertex)

                # Flush batch
                if len(self.buffer) >= batch_size:
                    self.flush_buffer()

            except Exception as e:
                print(f"Error processing message: {e}")

        # Start consuming
        self.buffer = []
        self.kafka.consume_messages(
            topic=input_topic,
            consumer_group='geoqb_processor',
            callback=process_message
        )

    def flush_buffer(self):
        """Flush buffered vertices to TigerGraph"""
        if self.buffer:
            self.tg.upsert_vertices('h3place', self.buffer)
            print(f"Flushed {len(self.buffer)} vertices")
            self.buffer = []

# Usage
processor = SpatialStreamProcessor(kafka_config, tg_client)

processor.start_processing(
    input_topic='sensor_events',
    layer_name='realtime_sensors',
    resolution=9,
    batch_size=100
)
```

#### Exercise 3.1: IoT Sensor Network

Build a complete IoT sensor monitoring system:

**Components:**
1. **Sensor Simulator**: Generate fake sensor data
2. **Kafka Producer**: Send to Kafka topic
3. **Stream Processor**: Process and load to TigerGraph
4. **Real-Time Dashboard**: Visualize live data
5. **Alerting**: Detect anomalies and send alerts

**Bonus:** Add Apache Flink for complex event processing!

---

### Module 3.2: Graph Machine Learning

#### Node2Vec for Spatial Embeddings

```python
"""
Advanced graph machine learning with Node2Vec
"""

from geoanalysis.geoqb.graph_analyser import (
    extract_layer_as_networkx,
    train_node2vec,
    cluster_nodes
)
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

class SpatialGraphML:
    """Graph ML for spatial analysis"""

    def __init__(self, tg_client):
        self.tg = tg_client

    def analyze_spatial_communities(
        self,
        layer_name: str,
        n_clusters: int = 10,
        dimensions: int = 128,
        walk_length: int = 30,
        num_walks: int = 200
    ):
        """
        Discover spatial communities using Node2Vec.

        Returns:
            dict with graph, embeddings, clusters, visualization
        """
        # Extract as NetworkX graph
        print("Extracting graph...")
        graph = extract_layer_as_networkx(self.tg, layer_name)
        print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

        # Train Node2Vec
        print("Training Node2Vec...")
        model = train_node2vec(
            graph,
            dimensions=dimensions,
            walk_length=walk_length,
            num_walks=num_walks,
            workers=4
        )

        # Get embeddings
        node_list = list(graph.nodes())
        embeddings = model.wv[node_list]

        # Cluster
        print(f"Clustering into {n_clusters} communities...")
        labels = cluster_nodes(embeddings, n_clusters)

        # Visualize with t-SNE
        print("Creating visualization...")
        tsne = TSNE(n_components=2, random_state=42)
        coords_2d = tsne.fit_transform(embeddings)

        # Plot
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(
            coords_2d[:, 0],
            coords_2d[:, 1],
            c=labels,
            cmap='tab10',
            alpha=0.6
        )
        plt.colorbar(scatter)
        plt.title(f"Spatial Communities: {layer_name}")
        plt.xlabel("t-SNE Dimension 1")
        plt.ylabel("t-SNE Dimension 2")

        return {
            'graph': graph,
            'embeddings': embeddings,
            'clusters': labels,
            'coords_2d': coords_2d,
            'model': model
        }

    def find_similar_locations(
        self,
        h3_index: str,
        model,
        top_n: int = 10
    ):
        """Find locations similar to given H3 cell"""
        similar = model.wv.most_similar(h3_index, topn=top_n)
        return similar

# Usage
ml = SpatialGraphML(tg_client)

results = ml.analyze_spatial_communities(
    layer_name='restaurants',
    n_clusters=5
)

# Find similar locations
similar = ml.find_similar_locations(
    h3_index='891f1d4a9ffffff',
    model=results['model'],
    top_n=10
)

print("Similar locations:")
for location, similarity in similar:
    print(f"  {location}: {similarity:.3f}")
```

#### Exercise 3.2: Build a Recommendation Engine

Create a location recommendation system:

**Features:**
1. User profile with preferences
2. Content-based filtering (layer similarities)
3. Collaborative filtering (user similarities)
4. Hybrid approach
5. Real-time updates

**Deliverable:** Working recommendation API

---

## Level 4: Production

### Module 4.1: Building Production APIs

#### FastAPI Application

```python
"""
Production GeoQB API with FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="GeoQB API",
    description="Spatial Knowledge Graph API",
    version="1.0.0"
)

# Models
class LayerCreate(BaseModel):
    name: str
    amenity_type: str
    bbox: List[float]  # [lat_min, lon_min, lat_max, lon_max]
    resolution: int = 9

class Location(BaseModel):
    h3_index: str
    lat: float
    lon: float
    score: Optional[float] = None

# Dependency: Get TigerGraph client
def get_tg_client():
    # Your implementation
    pass

# Endpoints
@app.post("/api/v1/layers", status_code=201)
async def create_layer(
    layer: LayerCreate,
    tg=Depends(get_tg_client)
):
    """Create and ingest a new layer"""
    try:
        # Create layer definition
        # Fetch data
        # Load to TigerGraph
        return {"status": "success", "layer_name": layer.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/layers")
async def list_layers(tg=Depends(get_tg_client)):
    """List all layers"""
    # Your implementation
    pass

@app.get("/api/v1/locations/search")
async def search_locations(
    bbox: str,  # "lat_min,lon_min,lat_max,lon_max"
    layers: str,  # Comma-separated layer names
    top_n: int = 10,
    tg=Depends(get_tg_client)
) -> List[Location]:
    """Search for best locations"""
    # Your implementation
    pass

@app.get("/api/v1/locations/{h3_index}/score")
async def score_location(
    h3_index: str,
    layers: str,
    tg=Depends(get_tg_client)
):
    """Get accessibility score for location"""
    # Your implementation
    pass

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run:
```bash
pip install fastapi uvicorn
python api.py

# Test
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

#### Exercise 4.1: Complete the API

Implement:
1. Authentication (JWT tokens)
2. Rate limiting
3. Caching (Redis)
4. API documentation
5. Tests (pytest + httpx)
6. Deployment (Docker + K8s)

---

### Module 4.2: Testing Strategies

```python
"""
Comprehensive testing for GeoQB applications
"""

import pytest
from unittest.mock import Mock, patch
from geoanalysis.geoqb import GeoQbLayers, GeoQbTG

# Unit tests
def test_layer_creation():
    """Test layer can be created"""
    layers = GeoQbLayers(workspace_path='/tmp/test')
    layers.add_layer(
        name='test_layer',
        layer_type='amenity',
        tags={'amenity': 'hospital'},
        bbox=[50, 8, 51, 9],
        resolution=9
    )
    assert 'test_layer' in layers.layers
    assert layers.layers['test_layer']['resolution'] == 9

# Integration tests
@pytest.fixture
def tg_client():
    """Fixture providing TigerGraph client"""
    # Use test instance or mock
    return Mock(spec=GeoQbTG)

def test_data_ingestion(tg_client):
    """Test data can be ingested"""
    # Your test
    pass

# End-to-end tests
def test_full_pipeline():
    """Test complete workflow"""
    # 1. Create layer
    # 2. Fetch data
    # 3. Load to TG
    # 4. Query back
    # 5. Verify
    pass
```

#### Exercise 4.2: Test Suite

Build comprehensive test suite covering:
1. Unit tests (90%+ coverage)
2. Integration tests
3. Performance tests
4. Security tests
5. Load tests

---

## Final Project: Production Application

Build a complete production application:

**Requirements:**
1. REST API (FastAPI)
2. Real-time streaming (Kafka)
3. Graph ML (Node2Vec)
4. Docker deployment
5. Kubernetes manifests
6. Monitoring (Prometheus)
7. Documentation (Swagger)
8. Tests (90%+ coverage)
9. CI/CD (GitHub Actions)
10. Security hardening

**Deliverables:**
- Source code (GitHub repo)
- Documentation
- Deployment guide
- Demo video

---

## Resources

- [Architecture Overview](../ARCHITECTURE.md)
- [Module Reference](../MODULES.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Security Guide](../SECURITY.md)

---

**Last Updated:** 2024
**Difficulty:** Intermediate to Advanced
**Estimated Time:** 30-50 hours
**Next:** [Theory & Algorithms](THEORY_AND_ALGORITHMS.md)
