# GeoQB Module Documentation

Complete reference for all modules in the pyGeoQB package.

---

## Table of Contents

1. [Core Modules](#core-modules)
2. [Data Integration Modules](#data-integration-modules)
3. [Analysis Modules](#analysis-modules)
4. [Utility Modules](#utility-modules)
5. [CLI Tools](#cli-tools)
6. [Experimental Modules](#experimental-modules)

---

## Core Modules

### geoqb_layers.py

**Purpose:** Multi-layer graph management and layer definition handling.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_layers.py`

**Size:** ~27KB, ~800 lines of code

**Key Classes:**

#### `GeoQbLayers`

Main class for managing layer definitions and query generation.

**Attributes:**
- `layers` (dict): Collection of layer definitions
- `query_stack` (list): Ordered list of queries to execute
- `workspace_path` (str): Path to data workspace

**Key Methods:**

```python
def add_layer(self, name, layer_type, tags, bbox, resolution=9):
    """
    Register a new layer definition.

    Args:
        name (str): Unique layer identifier
        layer_type (str): Type of layer (amenity, building, highway, etc.)
        tags (dict): OSM tags to filter (e.g., {'amenity': 'hospital'})
        bbox (list): Bounding box [lat_min, lon_min, lat_max, lon_max]
        resolution (int): H3 resolution level (6, 9, or 12)

    Returns:
        dict: Layer definition
    """

def create_sophox_query(self, layer):
    """
    Generate SPARQL query for Sophox endpoint based on layer definition.

    Args:
        layer (dict): Layer definition

    Returns:
        str: SPARQL query string
    """

def get_query_stack(self):
    """
    Get ordered list of queries to execute for all layers.

    Returns:
        list: Query definitions with metadata
    """

def save_layers(self):
    """
    Persist layer definitions to workspace metadata directory.
    """

def load_layers(self):
    """
    Load layer definitions from workspace.

    Returns:
        dict: Layer definitions
    """

def calculate_bbox(self, center_lat, center_lon, radius_km):
    """
    Calculate bounding box from center point and radius.

    Args:
        center_lat (float): Center latitude
        center_lon (float): Center longitude
        radius_km (float): Radius in kilometers

    Returns:
        list: [lat_min, lon_min, lat_max, lon_max]
    """
```

**Usage Example:**

```python
from geoanalysis.geoqb import GeoQbLayers

# Initialize layer manager
layers = GeoQbLayers(workspace_path='/path/to/workspace')

# Define a layer
layers.add_layer(
    name='hospitals',
    layer_type='amenity',
    tags={'amenity': 'hospital'},
    bbox=[50.0, 8.0, 51.0, 9.0],
    resolution=9
)

# Generate SPARQL query
query = layers.create_sophox_query(layers.layers['hospitals'])

# Save definitions
layers.save_layers()
```

---

### geoqb_tg.py

**Purpose:** TigerGraph database integration and management.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_tg.py`

**Size:** ~10KB, ~300 lines of code

**Key Classes:**

#### `GeoQbTG`

Manages all TigerGraph operations.

**Attributes:**
- `conn`: pyTigerGraph connection object
- `graph_name` (str): Name of the graph in TigerGraph
- `host` (str): TigerGraph host URL
- `token` (str): Authentication token

**Key Methods:**

```python
def __init__(self, host, username, password, graph_name='OSMGraph'):
    """
    Initialize TigerGraph connection.

    Args:
        host (str): TigerGraph host URL
        username (str): Username
        password (str): Password
        graph_name (str): Graph name (default: 'OSMGraph')
    """

def test_connection(self):
    """
    Test database connection.

    Returns:
        bool: True if connection successful
    """

def create_schema(self):
    """
    Create graph schema with vertex and edge types.
    Defines: osmtag, h3place, osmplace, fact vertices
    Defines: hasOSMTag, h3_grid_link, located_on_h3_cell, observed_at edges
    """

def drop_all(self):
    """
    Drop all data and schema. WARNING: Destructive operation.
    """

def upsert_vertices(self, vertex_type, vertices):
    """
    Bulk upsert vertices.

    Args:
        vertex_type (str): Vertex type name
        vertices (list): List of vertex dictionaries

    Returns:
        dict: Upsert statistics
    """

def upsert_edges(self, edge_type, source_vertex_type, target_vertex_type, edges):
    """
    Bulk upsert edges.

    Args:
        edge_type (str): Edge type name
        source_vertex_type (str): Source vertex type
        target_vertex_type (str): Target vertex type
        edges (list): List of edge dictionaries

    Returns:
        dict: Upsert statistics
    """

def run_installed_query(self, query_name, params=None):
    """
    Execute an installed GSQL query.

    Args:
        query_name (str): Query name
        params (dict): Query parameters

    Returns:
        list: Query results
    """

def extract_layer(self, layer_id, output_path):
    """
    Extract layer data to file.

    Args:
        layer_id (str): Layer identifier
        output_path (str): Output file path
    """
```

**Usage Example:**

```python
from geoanalysis.geoqb import GeoQbTG
import os

# Initialize connection
tg = GeoQbTG(
    host=os.getenv('TG_URL'),
    username=os.getenv('TG_USERNAME'),
    password=os.getenv('TG_PASSWORD')
)

# Test connection
if tg.test_connection():
    print("Connected successfully")

# Create schema (first time only)
tg.create_schema()

# Upsert vertices
vertices = [
    {'id': 'h3_891f1d4a9ffffff', 'resolution': 9, 'layer_id': 'hospitals'},
    {'id': 'h3_891f1d4b1ffffff', 'resolution': 9, 'layer_id': 'hospitals'}
]
tg.upsert_vertices('h3place', vertices)

# Query data
results = tg.run_installed_query('osm_tag_histogram', {'layer_id': 'hospitals'})
```

---

### geoqb_h3.py

**Purpose:** H3 hexagonal spatial indexing operations.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_h3.py`

**Size:** ~5KB, ~150 lines of code

**Key Functions:**

```python
def lat_lon_to_h3(lat, lon, resolution):
    """
    Convert latitude/longitude to H3 index.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        resolution (int): H3 resolution (0-15)

    Returns:
        str: H3 index (hex string)

    Example:
        >>> lat_lon_to_h3(50.1109, 8.6821, 9)
        '891f1d4a9ffffff'
    """

def h3_to_lat_lon(h3_index):
    """
    Convert H3 index to latitude/longitude.

    Args:
        h3_index (str): H3 index

    Returns:
        tuple: (latitude, longitude)
    """

def get_h3_neighbors(h3_index):
    """
    Get adjacent H3 cells.

    Args:
        h3_index (str): H3 index

    Returns:
        set: Set of neighbor H3 indices
    """

def h3_to_parent(h3_index, parent_resolution):
    """
    Get parent H3 cell at coarser resolution.

    Args:
        h3_index (str): Child H3 index
        parent_resolution (int): Parent resolution (must be < child resolution)

    Returns:
        str: Parent H3 index
    """

def h3_to_children(h3_index, child_resolution):
    """
    Get children H3 cells at finer resolution.

    Args:
        h3_index (str): Parent H3 index
        child_resolution (int): Child resolution (must be > parent resolution)

    Returns:
        set: Set of child H3 indices
    """

def k_ring(h3_index, k):
    """
    Get all H3 cells within k distance.

    Args:
        h3_index (str): Center H3 index
        k (int): Distance (number of steps)

    Returns:
        set: Set of H3 indices within k distance (includes center)
    """

def create_h3_grid_links(h3_cells):
    """
    Create adjacency links between H3 cells for graph construction.

    Args:
        h3_cells (list): List of H3 indices

    Returns:
        list: Edge definitions for TigerGraph upsert
    """
```

**Resolution Guide:**

| Resolution | Avg. Hex Area | Use Case |
|------------|---------------|----------|
| 0 | 4,250,547 km² | Global |
| 3 | 12,393 km² | Country |
| 6 | 36.1 km² | City/Region |
| 9 | 0.105 km² | Neighborhood |
| 12 | 0.0003 km² | Building |
| 15 | 0.0000009 km² | Precise location |

**Usage Example:**

```python
from geoanalysis.geoqb import lat_lon_to_h3, get_h3_neighbors, k_ring

# Convert coordinate to H3
lat, lon = 50.1109, 8.6821  # Frankfurt, Germany
h3_index = lat_lon_to_h3(lat, lon, resolution=9)
print(f"H3 index: {h3_index}")

# Get neighbors
neighbors = get_h3_neighbors(h3_index)
print(f"Found {len(neighbors)} neighbors")

# Get 2-ring neighborhood
neighborhood = k_ring(h3_index, k=2)
print(f"2-ring contains {len(neighborhood)} cells")
```

---

### geoqb_workspace.py

**Purpose:** Local workspace and file management.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_workspace.py`

**Size:** ~2.8KB, ~100 lines of code

**Key Classes:**

#### `Workspace`

Manages local filesystem structure for data assets.

**Methods:**

```python
def __init__(self, base_path):
    """
    Initialize workspace.

    Args:
        base_path (str): Root workspace directory path
    """

def init(self):
    """
    Create workspace directory structure.
    Creates: raw/, stage/, md/, dumps/, graph_layers/
    """

def list_assets(self):
    """
    List all data assets in workspace.

    Returns:
        dict: Assets by category with sizes
    """

def describe(self, asset_name):
    """
    Get metadata about a specific asset.

    Args:
        asset_name (str): Asset identifier

    Returns:
        dict: Asset metadata
    """

def clear(self, category='stage'):
    """
    Remove all files in a category.

    Args:
        category (str): Category to clear (raw, stage, dumps, etc.)
    """

def delete_asset(self, asset_path):
    """
    Delete a specific asset file.

    Args:
        asset_path (str): Relative path to asset
    """

def get_size(self, path):
    """
    Calculate size of file or directory.

    Args:
        path (str): File or directory path

    Returns:
        int: Size in bytes
    """
```

**Directory Structure:**

```
$GEOQB_WORKSPACE/
├── raw/                    # Raw API responses (cached)
│   ├── sophox/             # SPARQL query results
│   │   └── hospitals.json
│   └── overpass/           # Overpass API results
│       └── highways.json
├── stage/                  # Processed, ready-to-load data
│   ├── hospitals_h3_9.csv
│   └── highways_h3_9.csv
├── md/                     # Metadata and layer definitions
│   ├── layers.json
│   └── queries.json
├── dumps/                  # Full graph exports
│   └── full_export_20240101.json
└── graph_layers/           # Extracted layer data
    ├── hospitals_nodes.csv
    ├── hospitals_edges.csv
    └── hospitals_metadata.json
```

---

## Data Integration Modules

### geoqb_osm_pandas.py

**Purpose:** OpenStreetMap data extraction and processing.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_osm_pandas.py`

**Size:** ~11KB, ~350 lines of code

**Key Functions:**

```python
def fetch_osm_data_overpass(bbox, tags, timeout=180):
    """
    Fetch OSM data from Overpass API.

    Args:
        bbox (list): [lat_min, lon_min, lat_max, lon_max]
        tags (dict): OSM tags to filter (e.g., {'amenity': 'hospital'})
        timeout (int): Query timeout in seconds

    Returns:
        pandas.DataFrame: OSM elements with geometry and tags
    """

def fetch_osm_data_sophox(sparql_query):
    """
    Fetch OSM data from Sophox SPARQL endpoint.

    Args:
        sparql_query (str): SPARQL query string

    Returns:
        pandas.DataFrame: Query results
    """

def parse_osm_tags(osm_element):
    """
    Parse OSM tags from element.

    Args:
        osm_element (dict): OSM element from API

    Returns:
        dict: Normalized tags
    """

def convert_to_h3(df, resolution=9):
    """
    Add H3 indices to DataFrame based on lat/lon columns.

    Args:
        df (pandas.DataFrame): DataFrame with 'lat' and 'lon' columns
        resolution (int): H3 resolution

    Returns:
        pandas.DataFrame: DataFrame with added 'h3_index' column
    """

def prepare_for_tigergraph(df, layer_id):
    """
    Transform DataFrame to TigerGraph upsert format.

    Args:
        df (pandas.DataFrame): Processed OSM data
        layer_id (str): Layer identifier

    Returns:
        tuple: (vertices, edges) ready for upsert
    """
```

**Usage Example:**

```python
from geoanalysis.geoqb import fetch_osm_data_overpass, convert_to_h3

# Fetch hospitals in Frankfurt
bbox = [50.0, 8.5, 50.2, 8.8]
tags = {'amenity': 'hospital'}

df = fetch_osm_data_overpass(bbox, tags)
print(f"Found {len(df)} hospitals")

# Add H3 indices
df = convert_to_h3(df, resolution=9)

# Prepare for loading
vertices, edges = prepare_for_tigergraph(df, layer_id='hospitals')
```

---

### geoqb_sophox.py

**Purpose:** Sophox SPARQL endpoint integration.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_sophox.py`

**Size:** ~1.5KB, ~50 lines of code

**Key Functions:**

```python
def execute_sparql_query(endpoint_url, query):
    """
    Execute SPARQL query against Sophox.

    Args:
        endpoint_url (str): SPARQL endpoint URL
        query (str): SPARQL query string

    Returns:
        dict: Query results in JSON format
    """

def parse_sparql_results(results):
    """
    Parse SPARQL JSON results to pandas DataFrame.

    Args:
        results (dict): SPARQL JSON results

    Returns:
        pandas.DataFrame: Parsed results
    """
```

---

### geoqb_kafka.py

**Purpose:** Apache Kafka streaming integration.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_kafka.py`

**Size:** ~5KB, ~150 lines of code

**Key Classes:**

#### `KafkaManager`

Manages Kafka producers and consumers.

**Methods:**

```python
def __init__(self, bootstrap_servers, security_config):
    """
    Initialize Kafka connection.

    Args:
        bootstrap_servers (str): Kafka broker addresses
        security_config (dict): SASL/SSL configuration
    """

def create_topic(self, topic_name, num_partitions=1, replication_factor=3):
    """
    Create a new Kafka topic.

    Args:
        topic_name (str): Topic name
        num_partitions (int): Number of partitions
        replication_factor (int): Replication factor
    """

def produce_message(self, topic, key, value, value_schema=None):
    """
    Produce message to topic.

    Args:
        topic (str): Topic name
        key (str): Message key
        value (dict): Message value
        value_schema (dict): Avro schema (optional)
    """

def consume_messages(self, topic, consumer_group, callback):
    """
    Consume messages from topic.

    Args:
        topic (str): Topic name
        consumer_group (str): Consumer group ID
        callback (function): Function to process each message
    """

def list_topics(self):
    """
    List all available topics.

    Returns:
        list: Topic names
    """
```

**Usage Example:**

```python
from geoanalysis.geoqb import KafkaManager

# Initialize
kafka = KafkaManager(
    bootstrap_servers=os.getenv('bootstrap_servers'),
    security_config={
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': os.getenv('sasl_username'),
        'sasl.password': os.getenv('sasl_password')
    }
)

# Produce message
kafka.produce_message(
    topic='geo_events',
    key='location_001',
    value={'lat': 50.1109, 'lon': 8.6821, 'type': 'hospital'}
)

# Consume messages
def process_message(msg):
    print(f"Received: {msg.value()}")

kafka.consume_messages('geo_events', 'geoqb_consumer', process_message)
```

---

### data4good/HighResolutionPopulationDensityMapsAndDemographicEstimates.py

**Purpose:** Facebook Data4Good demographic data integration.

**Location:** `pyGeoQB/geoanalysis/geoqb/data4good/`

**Key Functions:**

```python
def load_population_data(csv_path):
    """
    Load Data4Good population density CSV.

    Args:
        csv_path (str): Path to CSV file

    Returns:
        pandas.DataFrame: Population data with lat/lon
    """

def enrich_with_population(h3_cells, population_df):
    """
    Join H3 cells with population data.

    Args:
        h3_cells (list): H3 indices
        population_df (pandas.DataFrame): Population data

    Returns:
        pandas.DataFrame: Enriched data
    """
```

---

## Analysis Modules

### graph_analyser.py

**Purpose:** Graph machine learning and analysis.

**Location:** `pyGeoQB/geoanalysis/geoqb/graph_analyser.py`

**Size:** ~6KB, ~200 lines of code

**Key Functions:**

```python
def extract_layer_as_networkx(tg_conn, layer_id):
    """
    Extract layer from TigerGraph as NetworkX graph.

    Args:
        tg_conn: TigerGraph connection
        layer_id (str): Layer identifier

    Returns:
        networkx.Graph: Layer as NetworkX graph
    """

def train_node2vec(graph, dimensions=128, walk_length=30, num_walks=200, workers=4):
    """
    Train Node2Vec model on graph.

    Args:
        graph (networkx.Graph): Input graph
        dimensions (int): Embedding dimensions
        walk_length (int): Length of random walks
        num_walks (int): Number of walks per node
        workers (int): Parallel workers

    Returns:
        gensim.models.Word2Vec: Trained model with embeddings
    """

def cluster_nodes(embeddings, n_clusters=10):
    """
    Cluster nodes using k-means.

    Args:
        embeddings (numpy.ndarray): Node embeddings
        n_clusters (int): Number of clusters

    Returns:
        numpy.ndarray: Cluster labels
    """

def reduce_dimensions_tsne(embeddings, n_components=2):
    """
    Reduce embedding dimensions with t-SNE.

    Args:
        embeddings (numpy.ndarray): High-dimensional embeddings
        n_components (int): Target dimensions

    Returns:
        numpy.ndarray: Reduced embeddings
    """

def generate_cluster_wordcloud(graph, cluster_labels, cluster_id):
    """
    Generate word cloud for a cluster.

    Args:
        graph (networkx.Graph): Graph with node attributes
        cluster_labels (numpy.ndarray): Cluster assignments
        cluster_id (int): Cluster to analyze

    Returns:
        wordcloud.WordCloud: Word cloud object
    """

def plot_clusters_2d(coords_2d, labels, output_path):
    """
    Plot 2D cluster visualization.

    Args:
        coords_2d (numpy.ndarray): 2D coordinates
        labels (numpy.ndarray): Cluster labels
        output_path (str): Output image path
    """
```

**Analysis Pipeline Example:**

```python
from geoanalysis.geoqb import (
    extract_layer_as_networkx,
    train_node2vec,
    cluster_nodes,
    reduce_dimensions_tsne,
    plot_clusters_2d
)

# Extract layer
graph = extract_layer_as_networkx(tg, 'hospitals')

# Train Node2Vec
model = train_node2vec(graph, dimensions=128)
embeddings = model.wv[list(graph.nodes())]

# Cluster
labels = cluster_nodes(embeddings, n_clusters=10)

# Visualize
coords_2d = reduce_dimensions_tsne(embeddings)
plot_clusters_2d(coords_2d, labels, 'clusters.png')
```

---

### calc_impact_score.py

**Purpose:** Calculate impact scores for locations.

**Location:** `pyGeoQB/geoanalysis/geoqb/calc_impact_score.py`

**Size:** ~4KB, ~120 lines of code

**Key Functions:**

```python
def calculate_impact_score(h3_index, layers, weights, tg_conn):
    """
    Calculate weighted impact score for a location.

    Args:
        h3_index (str): H3 cell to score
        layers (list): Layer identifiers to include
        weights (dict): Weight per layer (e.g., {'hospitals': 0.3, 'schools': 0.2})
        tg_conn: TigerGraph connection

    Returns:
        float: Impact score (0-1)
    """

def get_layer_value(h3_index, layer_id, tg_conn):
    """
    Get layer-specific value for H3 cell.

    Args:
        h3_index (str): H3 cell
        layer_id (str): Layer identifier
        tg_conn: TigerGraph connection

    Returns:
        float: Layer value (normalized)
    """

def create_impact_heatmap(bbox, layers, weights, resolution, tg_conn):
    """
    Create impact score heatmap for region.

    Args:
        bbox (list): [lat_min, lon_min, lat_max, lon_max]
        layers (list): Layers to include
        weights (dict): Layer weights
        resolution (int): H3 resolution
        tg_conn: TigerGraph connection

    Returns:
        pandas.DataFrame: H3 cells with impact scores
    """
```

---

### geoqb_plots.py

**Purpose:** Visualization functions.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_plots.py`

**Size:** ~8KB, ~250 lines of code

**Key Functions:**

```python
def plot_h3_layer_on_map(h3_data, layer_column, output_html):
    """
    Create interactive Folium map with H3 hexagons.

    Args:
        h3_data (pandas.DataFrame): Data with 'h3_index' column
        layer_column (str): Column to color by
        output_html (str): Output HTML file path
    """

def plot_tag_histogram(tag_counts, output_path):
    """
    Create bar chart of tag frequencies.

    Args:
        tag_counts (dict): Tag -> count mapping
        output_path (str): Output image path
    """

def plot_layer_comparison(layer_stats, output_path):
    """
    Compare statistics across layers.

    Args:
        layer_stats (pandas.DataFrame): Layer statistics
        output_path (str): Output image path
    """

def create_3d_graph_plot(graph, node_positions, node_colors):
    """
    Create 3D interactive graph visualization.

    Args:
        graph (networkx.Graph): Graph to plot
        node_positions (dict): Node -> (x, y, z) positions
        node_colors (dict): Node -> color mapping

    Returns:
        plotly.graph_objects.Figure: Interactive 3D plot
    """
```

---

## Utility Modules

### geoqb_profiles.py

**Purpose:** User profile and SOLID pod management.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_profiles.py`

**Size:** ~6KB, ~200 lines of code

**Key Classes:**

#### `UserProfile`

Manages user preferences and impact profiles.

**Methods:**

```python
def __init__(self, username, solid_pod_url=None):
    """
    Initialize user profile.

    Args:
        username (str): Username
        solid_pod_url (str): SOLID pod URL (optional)
    """

def set_preferences(self, preferences):
    """
    Set user preferences.

    Args:
        preferences (dict): Preference weights (e.g., {'hospitals': 0.3})
    """

def save_to_solid_pod(self):
    """
    Save profile to SOLID pod.
    """

def load_from_solid_pod(self):
    """
    Load profile from SOLID pod.

    Returns:
        dict: User preferences
    """
```

---

### geoqb_zipcodes.py

**Purpose:** ZIP code utilities.

**Location:** `pyGeoQB/geoanalysis/geoqb/geoqb_zipcodes.py`

**Key Functions:**

```python
def zipcode_to_bbox(zipcode, country='DE'):
    """
    Convert ZIP code to bounding box.

    Args:
        zipcode (str): ZIP code
        country (str): Country code

    Returns:
        list: [lat_min, lon_min, lat_max, lon_max]
    """
```

---

### reverse_geo_coding.py

**Purpose:** Reverse geocoding utilities.

**Location:** `pyGeoQB/geoanalysis/geoqb/reverse_geo_coding.py`

**Key Functions:**

```python
def reverse_geocode(lat, lon, provider='nominatim'):
    """
    Get address from coordinates.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        provider (str): Geocoding provider

    Returns:
        dict: Address components
    """
```

---

## CLI Tools

### gqws (Workspace Manager)

**Location:** `pyGeoQB/examples/gqws.py`

**Purpose:** Manage workspace and data assets.

**Commands:**

```bash
# Initialize workspace
gqws init

# List all assets
gqws ls

# Describe asset
gqws describe hospitals_h3_9.csv

# Clear staging area
gqws clear --category stage

# Delete specific asset
gqws delete raw/sophox/hospitals.json
```

---

### gql (Layer Manager)

**Location:** `pyGeoQB/examples/gql.py`

**Purpose:** Manage graph layers.

**Commands:**

```bash
# List layers
gql ls

# Create layer
gql create hospitals --tags amenity=hospital --bbox 50.0,8.0,51.0,9.0

# Ingest layer
gql ingest hospitals

# Extract layer
gql extract hospitals --output graph_layers/

# Extract all layers
gql extract-all

# Calculate impact scores
gql calc-impact-score --layers hospitals,schools --weights 0.5,0.5

# Run clustering analysis
gql clusters hospitals --n-clusters 10
```

---

### gqblend (Data Blender)

**Location:** `pyGeoQB/examples/gqblend.py`

**Purpose:** Blend external data sources.

**Commands:**

```bash
# List blend operations
gqblend ls

# Add data asset
gqblend asset add population_data.csv --type csv

# Add Kafka topic
gqblend topic add sensor_data --schema sensor.avsc

# Initialize blend
gqblend init --layer hospitals --asset population_data.csv

# Clear blends
gqblend clear
```

---

## Experimental Modules

### mtf/potential_layer_calculations.py

**Purpose:** Multi-temporal functions for time-series analysis.

**Status:** Experimental

**Location:** `pyGeoQB/geoanalysis/geoqb/mtf/`

---

### tebiS3Store/uploadReport.py

**Purpose:** S3 storage integration (Tebi).

**Status:** In development

**Location:** `pyGeoQB/geoanalysis/geoqb/tebiS3Store/`

---

## Module Dependency Graph

```
┌──────────────────┐
│   CLI Tools      │
│ gqws, gql,       │
│ gqblend          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  geoqb_layers    │────▶│  geoqb_tg        │
│  (Layer Mgmt)    │     │  (TigerGraph)    │
└────────┬─────────┘     └──────────────────┘
         │
         ├────────────────────┐
         │                    │
         ▼                    ▼
┌──────────────────┐   ┌──────────────────┐
│  geoqb_osm       │   │  geoqb_h3        │
│  (OSM Data)      │   │  (H3 Index)      │
└──────────────────┘   └──────────────────┘
         │                    │
         └─────────┬──────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ graph_analyser   │
         │ (ML Analysis)    │
         └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  geoqb_plots     │
         │  (Visualization) │
         └──────────────────┘
```

---

## Common Usage Patterns

### Pattern 1: Create and Analyze Layer

```python
from geoanalysis.geoqb import (
    GeoQbLayers,
    GeoQbTG,
    fetch_osm_data_overpass,
    convert_to_h3,
    prepare_for_tigergraph,
    train_node2vec,
    cluster_nodes
)

# 1. Define layer
layers = GeoQbLayers(workspace_path='/path/to/workspace')
layers.add_layer('hospitals', 'amenity', {'amenity': 'hospital'},
                 bbox=[50.0, 8.0, 51.0, 9.0], resolution=9)

# 2. Fetch data
df = fetch_osm_data_overpass(bbox=[50.0, 8.0, 51.0, 9.0],
                              tags={'amenity': 'hospital'})

# 3. Convert to H3
df = convert_to_h3(df, resolution=9)

# 4. Load to TigerGraph
tg = GeoQbTG(host=TG_URL, username=TG_USER, password=TG_PASS)
vertices, edges = prepare_for_tigergraph(df, 'hospitals')
tg.upsert_vertices('h3place', vertices)
tg.upsert_edges('hasOSMTag', 'h3place', 'osmtag', edges)

# 5. Analyze
graph = extract_layer_as_networkx(tg, 'hospitals')
model = train_node2vec(graph)
clusters = cluster_nodes(model.wv, n_clusters=5)
```

### Pattern 2: Stream Data to Graph

```python
from geoanalysis.geoqb import KafkaManager, GeoQbTG, lat_lon_to_h3

# Setup
kafka = KafkaManager(bootstrap_servers=KAFKA_SERVERS, security_config=CONFIG)
tg = GeoQbTG(host=TG_URL, username=TG_USER, password=TG_PASS)

# Process messages
def process_sensor_data(msg):
    data = msg.value()
    h3_index = lat_lon_to_h3(data['lat'], data['lon'], resolution=9)

    # Upsert to TigerGraph
    vertex = {'id': h3_index, 'layer_id': 'sensors'}
    fact = {'id': f"fact_{data['timestamp']}", 'value': data['value']}
    edge = {'from': h3_index, 'to': fact['id']}

    tg.upsert_vertices('h3place', [vertex])
    tg.upsert_vertices('fact', [fact])
    tg.upsert_edges('observed_at', 'h3place', 'fact', [edge])

kafka.consume_messages('sensor_topic', 'geoqb_consumer', process_sensor_data)
```

---

## Error Handling

All modules follow consistent error handling:

```python
from geoanalysis.geoqb import GeoQbError, TigerGraphConnectionError

try:
    tg = GeoQbTG(host=TG_URL, username=TG_USER, password=TG_PASS)
    tg.test_connection()
except TigerGraphConnectionError as e:
    print(f"Connection failed: {e}")
except GeoQbError as e:
    print(f"GeoQB error: {e}")
```

---

## Configuration

Modules read configuration from environment variables:

```bash
# TigerGraph
export TG_URL="https://your-instance.tgcloud.io/"
export TG_USERNAME="your_username"
export TG_PASSWORD="your_password"

# OSM Data
export overpass_endpoint="https://overpass.kumi.systems/api/interpreter"
export sophox_endpoint="https://sophox.org:443/sparql"

# Kafka
export bootstrap_servers="your-kafka-broker:9092"
export sasl_username="your_kafka_user"
export sasl_password="your_kafka_password"

# Workspace
export GEOQB_WORKSPACE="/path/to/workspace/"
```

---

## Testing

Each module should have corresponding tests:

```python
# test/test_geoqb_h3.py
from geoanalysis.geoqb import lat_lon_to_h3, get_h3_neighbors

def test_lat_lon_to_h3():
    h3_index = lat_lon_to_h3(50.0, 8.0, resolution=9)
    assert len(h3_index) == 15
    assert h3_index.startswith('89')

def test_neighbors():
    h3_index = lat_lon_to_h3(50.0, 8.0, resolution=9)
    neighbors = get_h3_neighbors(h3_index)
    assert len(neighbors) == 6  # Hexagons have 6 neighbors
```

---

**Document Version:** 1.0
**Last Updated:** 2024
**Maintained By:** GeoQB Development Team
