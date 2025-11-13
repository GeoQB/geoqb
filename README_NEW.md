# GeoQB - Graph-Based Multi-Layer Geospatial Analysis Platform

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![TigerGraph](https://img.shields.io/badge/TigerGraph-Cloud-orange.svg)](https://www.tigergraph.com/)

> **Data-as-Code for Geospatial Analysis**
> What [Terraform](https://www.terraform.io/) is for infrastructure management, GeoQB is for multi-layer geospatial knowledge graphs.

![GeoQB Logo](pyGeoQB/docs/images/temp_logo.png)

---

## 🌟 What is GeoQB?

GeoQB is a cloud-native platform for managing, analyzing, and deriving insights from multi-layer spatial knowledge graphs. It enables researchers, data scientists, and analysts to:

- **Integrate** geospatial data from OpenStreetMap, Wikidata, demographics, and custom sources
- **Analyze** using graph machine learning (Node2Vec, clustering, embeddings)
- **Scale** with TigerGraph Cloud and H3 spatial indexing
- **Collaborate** using declarative, version-controlled layer definitions
- **Visualize** with interactive maps, clusters, and custom dashboards

**Created during the [Graph FOR All Hackathon](https://devpost.com/software/geoqb)** and presented at Knowledge Graph Conference (KGC2022).

---

## 🎯 Key Use Cases

### 🏠 Sustainability Scoring
Automatically assess the sustainability of any location based on public transportation access, nearby amenities, services, and environmental factors.

```python
# Score a location's sustainability
score = calculate_impact_score(
    location=(50.1109, 8.6821),  # Frankfurt, Germany
    layers=['public_transport', 'healthcare', 'education', 'green_spaces'],
    weights={'public_transport': 0.3, 'healthcare': 0.3, 'education': 0.2, 'green_spaces': 0.2}
)
# Returns: 0.85 (highly sustainable)
```

### 🏙️ Urban Planning
Combine infrastructure, demographics, and service layers to understand urban structure and identify underserved areas.

### 📊 ESG Analysis
Assess environmental, social, and governance factors for corporate real estate and investment decisions.

### 🛍️ Retail Site Selection
Analyze competitor proximity, demographic fit, and accessibility for optimal retail location selection.

---

## ✨ Key Features

### 🗺️ Multi-Layer Graph Management
- Define layers via declarative SPARQL or Overpass queries
- Version control layer definitions
- Merge data from multiple sources into unified graph
- Systematic data integration and update workflows

### 📐 H3 Spatial Indexing
- Uber's hexagonal hierarchical spatial index
- Consistent spatial aggregation at multiple resolutions
- Efficient neighbor and proximity queries
- Seamless integration with graph structure

### 🔬 Graph Machine Learning
- **Node2Vec**: Learn node embeddings via random walks
- **Community Detection**: Discover spatial clusters
- **t-SNE Visualization**: 2D visualization of high-dimensional embeddings
- **Word Clouds**: Semantic characterization of communities

### 🌊 Real-Time Streaming
- Apache Kafka integration (Confluent Cloud)
- Ingest sensor data and events in real-time
- Update graph layers with streaming data
- Schema registry support (Avro, JSON, Protobuf)

### 🎨 Interactive Visualizations
- Folium/Mapbox interactive maps
- H3 hexagon overlays with custom coloring
- 3D graph visualizations (Plotly)
- Statistical plots (Seaborn)
- Export to PNG, HTML, SVG

### ☁️ Cloud-Native Architecture
- TigerGraph Cloud for scalable graph database
- S3-compatible storage for workspace data
- Kafka for streaming data integration
- SOLID pods for decentralized data management

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- TigerGraph Cloud account ([free tier](https://tgcloud.io/))
- 8GB+ RAM recommended

### Installation

```bash
# Clone repository
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB

# Setup environment
./script/bootstrap.sh env1

# Configure credentials (see docs/QUICKSTART.md)
cp env/env.sh.template env/env.sh
# Edit env/env.sh with your credentials

# Activate environment
source env/env.sh env1

# Initialize CLI tools
source script/set_aliases.sh env1
```

### First Steps

```bash
# 1. Initialize workspace
gqws init

# 2. Create your first layer
gql create hospitals \
    --tags amenity=hospital \
    --bbox 50.0,8.0,51.0,9.0 \
    --resolution 9

# 3. Ingest data
gql ingest hospitals

# 4. Analyze
python examples/test_szenario_2_graph_analysis.py

# 5. Visualize results
open $GEOQB_WORKSPACE/graph_layers/clusters.html
```

---

## 📚 Documentation

### Getting Started
- **[Quickstart Guide](pyGeoQB/docs/QUICKSTART.md)** - Get up and running in 10 minutes
- **[Tutorial Notebooks](pyGeoQB/notebooks/)** - Interactive Jupyter notebooks
- **[Example Scripts](pyGeoQB/examples/)** - Complete workflow examples

### Technical Documentation
- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[Module Reference](MODULES.md)** - Complete API documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment strategies
- **[Security Guide](SECURITY.md)** - OWASP security analysis and best practices

### Business Documentation
- **[Monetization Strategy](MONETIZATION.md)** - Business model and revenue opportunities

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     User Interfaces                      │
│         CLI Tools  |  Jupyter  |  Python API             │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                   Core Processing                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Layer     │  │  TigerGraph │  │  Analytics  │     │
│  │  Management │  │ Integration │  │   Engine    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└───────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                Data Integration                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │     OSM     │  │    Kafka    │  │  Data4Good  │     │
│  │ (Overpass,  │  │  Streaming  │  │ Population  │     │
│  │   Sophox)   │  │             │  │    Data     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└───────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│            Storage & External Services                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ TigerGraph  │  │  Workspace  │  │    Cloud    │     │
│  │   Cloud     │  │   Storage   │  │  Services   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└───────────────────────────────────────────────────────────┘
```

**Key Technologies:**
- **Graph Database**: TigerGraph Cloud
- **Spatial Index**: Uber H3
- **Data Sources**: OpenStreetMap (Overpass, Sophox), Wikidata, Data4Good
- **ML/Analytics**: NetworkX, Node2Vec, scikit-learn, TensorFlow
- **Streaming**: Apache Kafka (Confluent Cloud)
- **Visualization**: Folium, Plotly, Mapbox, Seaborn

[See full architecture documentation →](ARCHITECTURE.md)

---

## 🛠️ Core Modules

| Module | Purpose | Key Features |
|--------|---------|--------------|
| **geoqb_layers** | Layer management | Layer definitions, query generation, SPARQL |
| **geoqb_tg** | TigerGraph integration | Connection, schema, upserts, queries |
| **geoqb_h3** | H3 spatial indexing | Coordinate conversion, neighbors, hierarchies |
| **geoqb_osm_pandas** | OSM data integration | Overpass API, Sophox SPARQL, tag processing |
| **graph_analyser** | ML analysis | Node2Vec, k-means, t-SNE, community detection |
| **geoqb_kafka** | Streaming | Kafka producer/consumer, topic management |
| **geoqb_plots** | Visualization | Maps, charts, word clouds, 3D graphs |

[Complete module documentation →](MODULES.md)

---

## 📋 CLI Tools

GeoQB provides three main CLI tools for managing your geospatial knowledge graphs:

### `gqws` - Workspace Manager
```bash
gqws init              # Initialize workspace
gqws ls                # List all assets
gqws describe <asset>  # Show asset details
gqws clear             # Clear staging area
```

### `gql` - Layer Manager
```bash
gql ls                           # List all layers
gql create <name> [options]      # Create new layer
gql ingest <name>                # Ingest layer data
gql extract <name>               # Extract layer from graph
gql clusters <name>              # Run cluster analysis
gql calc-impact-score [options]  # Calculate impact scores
```

### `gqblend` - Data Blender
```bash
gqblend asset add <file>         # Add data asset
gqblend topic add <topic>        # Add Kafka topic
gqblend init --layer <name>      # Initialize blending
```

---

## 💡 Examples

### Example 1: Sustainability Analysis

```python
from geoanalysis.geoqb import (
    GeoQbLayers,
    GeoQbTG,
    fetch_osm_data_overpass,
    calculate_impact_score
)

# Define layers for sustainability analysis
layers = GeoQbLayers(workspace_path='~/geoqb-workspace')

# Public transportation
layers.add_layer('public_transport', 'amenity',
                 {'public_transport': 'stop_position'},
                 bbox=[50.0, 8.5, 50.2, 8.8], resolution=9)

# Healthcare facilities
layers.add_layer('healthcare', 'amenity',
                 {'amenity': 'hospital'},
                 bbox=[50.0, 8.5, 50.2, 8.8], resolution=9)

# Education
layers.add_layer('education', 'amenity',
                 {'amenity': 'school'},
                 bbox=[50.0, 8.5, 50.2, 8.8], resolution=9)

# Ingest all layers
tg = GeoQbTG(host=TG_URL, username=TG_USER, password=TG_PASS)
for layer_name in ['public_transport', 'healthcare', 'education']:
    data = fetch_osm_data_overpass(
        bbox=layers.layers[layer_name]['bbox'],
        tags=layers.layers[layer_name]['tags']
    )
    # Process and upsert to TigerGraph
    # ... (see full example in examples/)

# Calculate sustainability score
score = calculate_impact_score(
    h3_index='891f1d4a9ffffff',
    layers=['public_transport', 'healthcare', 'education'],
    weights={'public_transport': 0.4, 'healthcare': 0.3, 'education': 0.3},
    tg_conn=tg
)
print(f"Sustainability Score: {score:.2f}")
```

### Example 2: Community Detection

```python
from geoanalysis.geoqb import (
    extract_layer_as_networkx,
    train_node2vec,
    cluster_nodes,
    reduce_dimensions_tsne,
    plot_clusters_2d
)

# Extract layer as graph
graph = extract_layer_as_networkx(tg, 'restaurants')
print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

# Train Node2Vec embeddings
model = train_node2vec(graph, dimensions=128, walk_length=30, num_walks=200)
embeddings = model.wv[list(graph.nodes())]

# Cluster
labels = cluster_nodes(embeddings, n_clusters=10)

# Visualize
coords_2d = reduce_dimensions_tsne(embeddings)
plot_clusters_2d(coords_2d, labels, 'restaurant_clusters.png')
```

[More examples →](pyGeoQB/examples/)

---

## 🔒 Security

GeoQB follows security best practices and has undergone an OWASP Top 10 security audit.

**Key Security Features:**
- Input validation and sanitization
- Parameterized queries (SPARQL injection protection)
- Path traversal protection
- TLS for all external connections
- Secrets management support (Vault, AWS Secrets Manager)

**For Production Use:**
- Use secrets manager (not env.sh)
- Enable encryption at rest
- Implement audit logging
- Configure rate limiting
- Regular security updates

[Full security documentation →](SECURITY.md)

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build image
docker build -t geoqb:latest .

# Run with docker-compose
docker-compose up -d
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Cloud Platforms

- **AWS**: ECS/Fargate with RDS and S3
- **Azure**: Container Instances with Azure Files
- **GCP**: Cloud Run with Cloud Storage

[Complete deployment guide →](DEPLOYMENT.md)

---

## 🤝 Contributing

We welcome contributions! GeoQB is open source (Apache 2.0 license).

### Ways to Contribute

- **Code**: Submit pull requests for bug fixes or features
- **Documentation**: Improve docs, add examples, write tutorials
- **Data Layers**: Create and share reusable layer definitions
- **Testing**: Report bugs, suggest improvements
- **Community**: Answer questions, help other users

### Development Setup

```bash
# Clone and setup
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest

# Format code
black geoanalysis/

# Lint
flake8 geoanalysis/
```

---

## 🗺️ Roadmap

### ✅ Completed (v0.1)
- CLI tools for layer management
- TigerGraph integration
- H3 spatial indexing
- OSM data integration (Overpass, Sophox)
- Node2Vec graph analysis
- Basic visualizations
- Kafka streaming support

### 🚧 In Progress (v0.2)
- REST API layer
- Web dashboard
- Docker deployment
- Enhanced security
- Comprehensive documentation

### 🔮 Planned (v0.3+)
- Multi-user authentication
- Data marketplace
- Mobile apps
- Real-time collaboration
- AI-powered insights
- Industry solution packs

---

## 📊 Project Stats

- **Lines of Code**: ~3,700+ (core modules)
- **Dependencies**: 47 Python packages
- **Data Sources**: OpenStreetMap, Wikidata, Data4Good, Custom
- **Graph Database**: TigerGraph Cloud
- **License**: Apache 2.0
- **Started**: 2022 (Graph FOR All Hackathon)

---

## 🌍 Community & Support

### Resources

- **GitHub**: [https://github.com/GeoQB/geoqb](https://github.com/GeoQB/geoqb)
- **Devpost**: [https://devpost.com/software/geoqb](https://devpost.com/software/geoqb)
- **Playground**: [https://github.com/GeoQB/geoqb-playground](https://github.com/GeoQB/geoqb-playground)
- **KGC2022 Presentation**: [Link to presentation]

### Getting Help

- **Documentation**: Start with [QUICKSTART.md](pyGeoQB/docs/QUICKSTART.md)
- **Issues**: [GitHub Issues](https://github.com/GeoQB/geoqb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/GeoQB/geoqb/discussions)

---

## 📜 License

Copyright 2024 GeoQB Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## 🙏 Acknowledgments

### Inspiration

**Google Data Commons**: The [Data Commons Sustainability Initiative](https://blog.google/outreach-initiatives/sustainability/data-commons-sustainability/) addresses similar challenges. GeoQB can wrap layers around the Data Commons Knowledge Graph for fast integration into TigerGraph.

**Terraform**: The "Write, Plan, Apply" workflow inspired our data-as-code approach to managing multi-layer graphs.

### Built With

- **[TigerGraph](https://www.tigergraph.com/)** - Scalable graph database
- **[H3](https://h3geo.org/)** - Uber's hexagonal spatial indexing
- **[OpenStreetMap](https://www.openstreetmap.org/)** - Open geospatial data
- **[Wikidata](https://www.wikidata.org/)** - Linked open data
- **[Facebook Data4Good](https://dataforgood.facebook.com/)** - Population density data
- **[Confluent](https://www.confluent.io/)** - Kafka streaming platform

### Team

Created by Mirko Kämpf and contributors

### Recognition

- **Graph FOR All Hackathon** submission
- **Knowledge Graph Conference (KGC2022)** presentation

---

## 🚀 Get Started

Ready to build spatial knowledge graphs?

```bash
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB
./script/bootstrap.sh env1
```

Read the [Quickstart Guide](pyGeoQB/docs/QUICKSTART.md) and start analyzing!

---

**Star ⭐ this repository if you find it useful!**

[🏠 Home](https://github.com/GeoQB/geoqb) | [📖 Docs](ARCHITECTURE.md) | [💡 Examples](pyGeoQB/examples/) | [🤝 Contribute](CONTRIBUTING.md) | [📄 License](LICENSE)
