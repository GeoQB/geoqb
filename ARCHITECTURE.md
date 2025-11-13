# GeoQB Architecture Overview

## Executive Summary

GeoQB is a cloud-native, multi-layer graph management platform that enables systematic integration and analysis of geospatial data from diverse sources. Built on TigerGraph and inspired by Infrastructure-as-Code principles, it provides a declarative approach to managing complex spatial knowledge graphs.

**Key Capabilities:**
- Multi-layer graph management with H3 spatial indexing
- Integration of OpenStreetMap, Wikidata, and demographic data
- Graph-based ML analysis (Node2Vec, clustering, embeddings)
- Real-time data streaming via Kafka
- Decentralized data storage (SOLID pods, S3)
- CLI-driven workflow for data scientists

---

## Architecture Principles

### 1. Data-as-Code
Following Terraform's "Write, Plan, Apply" pattern, GeoQB treats data assets as declarative configurations:
- **Write**: Define layers via SPARQL/Overpass queries
- **Plan**: Stage and validate data transformations
- **Apply**: Execute ingestion and integration

### 2. Layer-Centric Design
Each layer represents a distinct knowledge domain:
- Amenities (restaurants, schools, hospitals)
- Transportation infrastructure
- Demographic data
- Environmental factors

Layers are independently queryable yet interconnected via spatial indices.

### 3. Cloud-Native Architecture
- **Stateless Processing**: All state in TigerGraph or object storage
- **API-Driven**: External services accessed via REST/GraphQL/SPARQL
- **Streaming-Ready**: Kafka integration for real-time updates
- **Scalable Storage**: S3-compatible storage for intermediate data

### 4. Standards-Based Integration
- **RDF/SPARQL**: Semantic web data (Sophox, Wikidata)
- **GeoJSON**: Spatial data interchange
- **H3**: Uber's hexagonal spatial indexing
- **Property Graphs**: TigerGraph native format

---

## System Architecture

### High-Level Component View

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  CLI Tools   │  │   Jupyter    │  │  Python API  │      │
│  │ gqws/gql/    │  │  Notebooks   │  │    Layer     │      │
│  │  gqblend     │  │              │  │   Library    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                   CORE PROCESSING LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Layer Management (geoqb_layers.py)           │   │
│  │  • Layer Definition    • Query Stack Management      │   │
│  │  • Metadata Tracking   • SPARQL Generation           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   H3 Spatial │  │  TigerGraph  │  │   Analytics  │      │
│  │   Indexing   │  │  Integration │  │   Engine     │      │
│  │              │  │              │  │              │      │
│  │ • Hex Grid   │  │ • Schema Mgmt│  │ • Node2Vec   │      │
│  │ • Neighbors  │  │ • Upserts    │  │ • Clustering │      │
│  │ • Resolution │  │ • Queries    │  │ • Embeddings │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                  DATA INTEGRATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     OSM      │  │    Kafka     │  │  Data4Good   │      │
│  │  Integration │  │  Streaming   │  │  Population  │      │
│  │              │  │              │  │  Data        │      │
│  │ • Overpass   │  │ • Topics     │  │              │      │
│  │ • Sophox     │  │ • Consumers  │  │ • CSV Import │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                   STORAGE & PERSISTENCE                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  TigerGraph  │  │  Workspace   │  │    Cloud     │      │
│  │  Cloud DB    │  │  File System │  │   Storage    │      │
│  │              │  │              │  │              │      │
│  │ • Vertices   │  │ • raw/       │  │ • S3 (Tebi)  │      │
│  │ • Edges      │  │ • stage/     │  │ • SOLID Pods │      │
│  │ • Layers     │  │ • md/        │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                      EXTERNAL SERVICES                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  OpenStreet  │  │   Wikidata   │  │  Confluent   │      │
│  │     Map      │  │   SPARQL     │  │    Cloud     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Layer Management System

**Module:** `geoqb_layers.py` (27KB, ~800 LOC)

**Responsibilities:**
- Define graph layers via declarative queries
- Manage query stacks for multi-source ingestion
- Generate SPARQL queries for Sophox endpoint
- Calculate bounding boxes for spatial queries
- Track layer metadata (name, type, resolution, timestamps)

**Key Classes:**
```python
class GeoQbLayers:
    - add_layer(): Register new layer definition
    - create_sophox_query(): Generate SPARQL from layer spec
    - get_query_stack(): Retrieve ordered query execution list
    - calculate_bbox(): Compute spatial bounds
```

**Layer Definition Example:**
```python
layer = {
    'name': 'hospitals',
    'type': 'amenity',
    'tags': {'amenity': 'hospital'},
    'resolution': 9,  # H3 resolution
    'bbox': [50.0, 8.0, 51.0, 9.0]  # [lat_min, lon_min, lat_max, lon_max]
}
```

### 2. Spatial Indexing with H3

**Module:** `geoqb_h3.py` (5KB, ~150 LOC)

**Purpose:** Convert lat/lon coordinates to Uber H3 hexagonal grid cells for efficient spatial operations.

**Key Functions:**
```python
# Coordinate to H3 conversion
h3_index = lat_lon_to_h3(lat, lon, resolution)

# Spatial relationships
neighbors = get_neighbors(h3_index)
parent = get_parent(h3_index, parent_resolution)
children = get_children(h3_index, child_resolution)

# Grid operations
ring = k_ring(h3_index, distance)
```

**H3 Resolution Strategy:**
- **Resolution 6**: City/region level (~36 km² per hex)
- **Resolution 9**: Neighborhood level (~0.1 km² per hex)
- **Resolution 12**: Building level (~0.0003 km² per hex)

**Benefits:**
- Consistent spatial aggregation
- Efficient nearest-neighbor queries
- Hierarchical spatial relationships
- No projection distortion

### 3. TigerGraph Integration

**Module:** `geoqb_tg.py` (10KB, ~300 LOC)

**Purpose:** Manage all interactions with TigerGraph Cloud database.

**Key Operations:**
```python
class GeoQbTG:
    # Connection management
    - connect(): Establish authenticated connection
    - test_connection(): Validate credentials

    # Schema operations
    - create_schema(): Initialize graph schema
    - drop_all(): Clean database

    # Data operations
    - upsert_vertices(): Bulk vertex insertion
    - upsert_edges(): Bulk edge creation
    - run_query(): Execute installed GSQL queries

    # Layer operations
    - extract_layer(): Export layer to local storage
    - stage_layer(): Prepare layer for analysis
```

**Graph Schema:**

**Vertex Types:**
- `osmtag` - OSM tag metadata (e.g., amenity=hospital)
- `h3place` - H3 grid cells at various resolutions
- `osmplace` - OpenStreetMap nodes/ways
- `fact` - Observation data (demographics, sensors, etc.)

**Edge Types:**
- `hasOSMTag` - Links places to their tags
- `h3_grid_link` - Connects adjacent H3 cells (spatial graph)
- `located_on_h3_cell` - Places to H3 cells
- `observed_at` - Facts observed at locations

### 4. OpenStreetMap Data Integration

**Modules:**
- `geoqb_osm_pandas.py` (11KB, ~350 LOC)
- `geoqb_sophox.py` (1.5KB, ~50 LOC)
- `osm_sparql_queries.py` (2.4KB, ~80 LOC)

**Data Sources:**

**A. Overpass API**
- Real-time OSM data queries
- Bounding box searches
- Tag-based filtering
- Node/way/relation retrieval

**B. Sophox SPARQL Endpoint**
- RDF representation of OSM data
- Semantic queries over OSM tags
- Wikidata integration
- Historical data access

**Query Example (SPARQL):**
```sparql
SELECT ?place ?placeLabel ?location WHERE {
    ?place osmm:tag:amenity "hospital" .
    ?place osmt:loc ?location .
    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en"
    }
    FILTER(geof:latitude(?location) > 50.0)
    FILTER(geof:latitude(?location) < 51.0)
}
```

### 5. Graph Analytics Engine

**Module:** `graph_analyser.py` (6KB, ~200 LOC)

**Algorithms:**

**A. Node2Vec**
- Graph embedding via random walks
- Learns low-dimensional representations
- Captures structural and community information
- Output: Dense vector per node (e.g., 128D)

**B. k-Means Clustering**
- Applied to Node2Vec embeddings
- Discovers communities in spatial graph
- Configurable cluster count
- Output: Cluster labels per node

**C. t-SNE Visualization**
- Dimensionality reduction (128D → 2D)
- Visual exploration of clusters
- Identifies mixed vs. separated communities

**D. Word Cloud Generation**
- Per-cluster tag frequency analysis
- Reveals semantic themes
- Community characterization

**Analysis Pipeline:**
```python
# 1. Extract graph layer
graph = extract_layer_as_networkx(layer_id)

# 2. Train Node2Vec model
model = Node2Vec(graph, dimensions=128, walk_length=30)
embeddings = model.wv

# 3. Cluster nodes
kmeans = KMeans(n_clusters=10)
labels = kmeans.fit_predict(embeddings)

# 4. Visualize
tsne = TSNE(n_components=2)
coords_2d = tsne.fit_transform(embeddings)
plot_clusters(coords_2d, labels)
```

### 6. Kafka Streaming Integration

**Module:** `geoqb_kafka.py` (5KB, ~150 LOC)

**Capabilities:**
- Connect to Confluent Cloud
- Create and manage topics
- Produce messages (JSON, Avro, Protobuf)
- Consume messages with offset management
- Schema registry integration

**Use Cases:**
- Real-time sensor data ingestion
- Event-driven layer updates
- Change data capture (CDC)
- Inter-system messaging

**Example Flow:**
```
IoT Sensors → Kafka Topic → GeoQB Consumer →
  H3 Indexing → TigerGraph Upsert → Updated Graph Layer
```

### 7. Data Enrichment Pipeline

**Module:** `gqblend.py` CLI + `data4good/` package

**Purpose:** Blend external datasets into existing graph layers.

**Supported Sources:**
- Facebook Data4Good population density maps
- Custom CSV datasets with lat/lon
- Kafka topic data streams

**Enrichment Process:**
```
1. Load external data (CSV, Kafka, API)
2. Extract coordinates or spatial reference
3. Convert to H3 indices at target resolution
4. Join with existing layer via H3 cells
5. Create 'fact' vertices with observed values
6. Link facts to h3place via 'observed_at' edges
7. Upsert to TigerGraph
```

**Result:** Multi-modal graph combining structure (OSM) and measurements (demographics, sensors).

### 8. Workspace Management

**Module:** `geoqb_workspace.py` (2.8KB, ~100 LOC)

**Directory Structure:**
```
$GEOQB_WORKSPACE/
├── raw/                    # Raw API responses
│   └── sophox/
│       └── {layer_name}.json
├── stage/                  # Processed data ready for ingestion
│   └── {layer_name}_h3_{resolution}.csv
├── md/                     # Metadata and layer definitions
│   └── layers.json
├── dumps/                  # Graph exports
│   └── {layer_name}_export.json
└── graph_layers/           # Extracted layer data
    └── {layer_name}_nodes.csv
    └── {layer_name}_edges.csv
```

**Operations:**
- `init()` - Create workspace structure
- `ls()` - List all assets with sizes
- `describe()` - Show asset metadata
- `clear()` - Remove processed data
- `delete()` - Remove specific assets

### 9. Visualization System

**Module:** `geoqb_plots.py` (8KB, ~250 LOC)

**Visualization Types:**

**A. Interactive Maps (Folium)**
- H3 hexagon overlays with color coding
- Popup information per hex
- Layer toggle controls
- Basemap options (OSM, Mapbox, etc.)

**B. Statistical Plots (Seaborn)**
- Tag frequency histograms
- Layer size comparisons
- Temporal trends

**C. 3D Visualizations (Plotly)**
- Multi-layer 3D graph
- Interactive rotation and zoom
- Node coloring by cluster

**D. Word Clouds**
- Per-cluster tag clouds
- Community characterization
- Semantic pattern discovery

---

## Data Flow Architecture

### Ingestion Pipeline

```
┌─────────────┐
│  External   │
│  Data       │
│  Sources    │
└──────┬──────┘
       │
       │ (1) Query/Fetch
       ▼
┌─────────────┐
│   Cache     │
│  raw/       │
└──────┬──────┘
       │
       │ (2) Parse & Transform
       ▼
┌─────────────┐
│  Staging    │
│  stage/     │
└──────┬──────┘
       │
       │ (3) H3 Indexing
       ▼
┌─────────────┐
│ H3-Indexed  │
│    Data     │
└──────┬──────┘
       │
       │ (4) Upsert
       ▼
┌─────────────┐
│ TigerGraph  │
│  Database   │
└─────────────┘
```

### Analysis Pipeline

```
┌─────────────┐
│ TigerGraph  │
│   Graph     │
└──────┬──────┘
       │
       │ (1) Extract Layer
       ▼
┌─────────────┐
│  NetworkX   │
│   Graph     │
└──────┬──────┘
       │
       │ (2) Node2Vec
       ▼
┌─────────────┐
│ Embeddings  │
│   (128D)    │
└──────┬──────┘
       │
       │ (3) ML Analysis
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Clusters   │────▶│ Visualize   │────▶│   Export    │
│   Labels    │     │   Results   │     │   Images    │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Deployment Architecture

### Current Deployment Model

**Type:** Developer-Centric, CLI-Driven

**Components:**
- **Compute**: Local Python execution (laptop, workstation, or VM)
- **Database**: TigerGraph Cloud (SaaS)
- **Storage**: Local filesystem + Optional cloud (S3, SOLID)
- **Streaming**: Confluent Cloud (SaaS)

**Deployment Flow:**
```bash
# 1. Setup environment
script/bootstrap.sh env1

# 2. Configure credentials
source env/env.sh env1

# 3. Initialize workspace
gqws init

# 4. Create and ingest layer
gql create hospitals --bbox 50.0,8.0,51.0,9.0
gql ingest hospitals

# 5. Run analysis
python examples/test_szenario_2_graph_analysis.py
```

### Proposed Cloud-Native Deployment

**Type:** Microservices on Kubernetes

```
┌────────────────────────────────────────────────────┐
│              Kubernetes Cluster                     │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │   API        │  │   Worker     │  │  Web    │ │
│  │  Gateway     │  │   Pods       │  │   UI    │ │
│  │ (FastAPI)    │  │  (Celery)    │  │ (React) │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │
│         │                 │                │      │
│         └─────────┬───────┴────────────────┘      │
│                   │                               │
│                   ▼                               │
│         ┌──────────────────┐                      │
│         │  Message Queue   │                      │
│         │   (RabbitMQ)     │                      │
│         └──────────────────┘                      │
└────────────────────────────────────────────────────┘
              │                      │
              ▼                      ▼
     ┌─────────────────┐   ┌─────────────────┐
     │  TigerGraph     │   │   Object Store  │
     │    Cloud        │   │      (S3)       │
     └─────────────────┘   └─────────────────┘
```

---

## Technology Stack Summary

### Core Technologies
- **Language**: Python 3.7+
- **Graph Database**: TigerGraph Cloud
- **Spatial Index**: Uber H3
- **Graph Analysis**: NetworkX, Node2Vec
- **ML Libraries**: scikit-learn, TensorFlow

### Data Sources
- **OpenStreetMap**: Overpass API, Sophox SPARQL
- **Demographics**: Facebook Data4Good
- **Semantic Web**: Wikidata, RDF triple stores
- **Streaming**: Apache Kafka (Confluent Cloud)

### Infrastructure
- **CLI Framework**: Click, plac
- **Data Processing**: Pandas, GeoPandas
- **Visualization**: Plotly, Folium, Seaborn
- **Cloud Storage**: S3-compatible (Tebi), SOLID pods
- **Version Control**: Git, Poetry

---

## Design Patterns

### 1. Repository Pattern
Workspace abstracts storage backend (local, S3, SOLID):
```python
workspace.save(layer_data, 'stage/')
data = workspace.load('raw/layer.json')
```

### 2. Factory Pattern
Layer definitions generate appropriate queries:
```python
layer_factory.create(layer_type='amenity', tags={'amenity': 'hospital'})
```

### 3. Strategy Pattern
Different data sources use pluggable adapters:
```python
data_source = select_adapter(source_type)  # Sophox, Overpass, Kafka
data_source.fetch(query)
```

### 4. Pipeline Pattern
Chained transformations in ingestion:
```python
pipeline = FetchPipeline() \
    .add(SophoxFetcher()) \
    .add(H3Indexer()) \
    .add(TigerGraphUpserter())
pipeline.execute(layer)
```

---

## Scalability Considerations

### Current Limitations
- **Single-threaded processing**: No parallelization of layer ingestion
- **In-memory graph analysis**: Limited by local RAM
- **Synchronous API calls**: Sequential fetching of external data
- **No caching layer**: Repeated queries hit external APIs

### Scaling Strategies

**Horizontal Scaling:**
- Deploy multiple worker processes for parallel layer processing
- Partition layers by spatial region
- Use Dask for distributed DataFrame operations

**Vertical Scaling:**
- TigerGraph Cloud already handles database scaling
- Use larger VM instances for Node2Vec on big graphs

**Caching:**
- Redis for API response caching
- CDN for static map tiles
- Materialized views in TigerGraph

**Batch Processing:**
- Apache Airflow for scheduled layer updates
- Bulk upserts instead of row-by-row

---

## Security Architecture

### Authentication & Authorization
- **TigerGraph**: Token-based authentication with secrets
- **Kafka**: SASL/SSL with username/password
- **S3**: Access key / secret key
- **SOLID**: OAuth with username/password

### Credential Management
- Environment variables in `env.sh` (not version controlled)
- Future: HashiCorp Vault, AWS Secrets Manager

### Network Security
- TLS/HTTPS for all external connections
- No open ingress ports (client-initiated connections only)
- VPC isolation in cloud deployments (future)

### Data Privacy
- SOLID pods for user data sovereignty
- Local-first processing option
- No PII stored in graph (only aggregated/indexed data)

---

## Monitoring & Observability

### Current State
- **Logging**: Python logging to console
- **Metrics**: None
- **Tracing**: None
- **Alerting**: None

### Future Additions
- **Prometheus**: Metrics collection (query rates, processing times)
- **Grafana**: Dashboards
- **Jaeger**: Distributed tracing
- **ELK Stack**: Centralized logging
- **PagerDuty**: Incident alerting

---

## Extension Points

### Adding New Data Sources
1. Create adapter class inheriting from `DataSource`
2. Implement `fetch()` and `parse()` methods
3. Register in `geoqb_layers.py`

### Adding New Analysis Algorithms
1. Add module in `geoqb/` directory
2. Implement `analyze()` function accepting NetworkX graph
3. Add CLI command in `examples/gql.py`

### Adding New Storage Backends
1. Implement `WorkspaceAdapter` interface
2. Add configuration in `env.sh`
3. Update `geoqb_workspace.py` to select adapter

### Adding New Visualization Types
1. Add function in `geoqb_plots.py`
2. Follow pattern: accept data + config, return figure
3. Support export to PNG/SVG/HTML

---

## Future Architecture Evolution

### Phase 1: API-First (6 months)
- REST API layer (FastAPI)
- Authentication & authorization
- Rate limiting
- API documentation (OpenAPI/Swagger)

### Phase 2: Web Dashboard (12 months)
- React frontend
- Interactive map viewer
- Layer management UI
- Analysis job scheduler

### Phase 3: Multi-Tenancy (18 months)
- User accounts and workspaces
- Data isolation
- Resource quotas
- Billing integration

### Phase 4: Marketplace (24 months)
- Public layer catalog
- User-contributed layers
- Licensing and payments
- Quality scoring

---

## References

- **TigerGraph Documentation**: https://docs.tigergraph.com/
- **H3 Specification**: https://h3geo.org/
- **OpenStreetMap Wiki**: https://wiki.openstreetmap.org/
- **Node2Vec Paper**: https://arxiv.org/abs/1607.00653
- **Sophox SPARQL Endpoint**: https://sophox.org/
- **Confluent Cloud**: https://docs.confluent.io/cloud/

---

**Document Version:** 1.0
**Last Updated:** 2024
**Maintained By:** GeoQB Development Team
