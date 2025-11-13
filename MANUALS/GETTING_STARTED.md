# GeoQB: Getting Started Guide

**Your First Steps into Spatial Knowledge Graphs**

Welcome to GeoQB! This guide will take you from zero to your first geospatial graph analysis in under 30 minutes.

---

## 📚 Table of Contents

1. [What You'll Learn](#what-youll-learn)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Core Concepts](#core-concepts)
5. [Your First Project](#your-first-project)
6. [Next Steps](#next-steps)

---

## What You'll Learn

By the end of this guide, you will:

✅ Understand what GeoQB does and why it's useful
✅ Set up your development environment
✅ Create your first layer
✅ Ingest real geospatial data
✅ Run basic analyses
✅ Visualize results on a map

**Time Required:** 30 minutes
**Difficulty:** Beginner
**Prerequisites:** Basic Python knowledge

---

## Prerequisites

### Required Knowledge

- **Python Basics**: Variables, functions, imports
- **Command Line**: Basic terminal navigation
- **Optional**: Basic understanding of geospatial concepts (helpful but not required)

### System Requirements

- **Operating System**: macOS, Linux, or Windows WSL
- **Python**: 3.7 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free space
- **Network**: Internet connection for cloud services

### Required Accounts

1. **TigerGraph Cloud** (Free tier)
   - Sign up at: https://tgcloud.io/
   - Create a new graph instance
   - Note your credentials

2. **Optional but Recommended:**
   - GitHub account (for version control)
   - Jupyter (for interactive development)

---

## Installation

### Step 1: Clone the Repository

```bash
# Clone GeoQB
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB

# Check you're in the right directory
ls
# You should see: examples/, geoanalysis/, script/, etc.
```

### Step 2: Setup Environment

GeoQB provides a bootstrap script that sets up everything for you:

```bash
# Run bootstrap script
./script/bootstrap.sh env1

# This will:
# 1. Create a Python virtual environment
# 2. Install all dependencies
# 3. Setup CLI tools
```

**What's happening?**
- A virtual environment `env1` is created
- All required Python packages are installed
- This takes 2-5 minutes depending on your connection

### Step 3: Configure Credentials

Create your configuration file:

```bash
# Create env directory
mkdir -p env

# Copy template
cat > env/env.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source $1/bin/activate

### WORKSPACE
export GEOQB_WORKSPACE="$HOME/geoqb-workspace/"

### OpenStreetMap Data Sources
export overpass_endpoint="https://overpass.kumi.systems/api/interpreter"
export sophox_endpoint="https://sophox.org:443/sparql"

### TigerGraph Cloud (REQUIRED - Update with your credentials)
export TG_URL="https://YOUR_INSTANCE.i.tgcloud.io/"
export TG_SECRET="YOUR_SECRET"
export TG_PASSWORD="YOUR_PASSWORD"
export TG_USERNAME="YOUR_USERNAME"
EOF

# Make executable
chmod +x env/env.sh
```

**Important:** Edit `env/env.sh` with your actual TigerGraph credentials!

```bash
# Edit with your favorite editor
nano env/env.sh
# or
vim env/env.sh
```

### Step 4: Activate Environment

```bash
# Activate GeoQB environment
source env/env.sh env1

# Setup CLI aliases
source script/set_aliases.sh env1

# Test it works
python -c "from geoanalysis.geoqb import GeoQbLayers; print('✅ GeoQB imported successfully!')"
```

If you see "✅ GeoQB imported successfully!" you're ready to go!

---

## Core Concepts

Before diving into code, let's understand the key concepts.

### 1. Layers

A **layer** is a collection of geospatial data about a specific topic.

**Examples:**
- Hospitals layer (all hospitals in an area)
- Transit stops layer (public transportation)
- Restaurants layer (dining locations)

**Think of it like:** Layers in Photoshop or GIS, but stored in a graph database

### 2. H3 Spatial Index

GeoQB uses **H3** - Uber's hexagonal spatial index.

**Why hexagons?**
- ✅ Uniform coverage (no distortion)
- ✅ Consistent neighbors (always 6)
- ✅ Multiple resolutions (zoom levels)
- ✅ Efficient computation

**Visual:**
```
    / \     / \     / \
   /   \   /   \   /   \
  |  H  | |  E  | |  X  |
   \   /   \   /   \   /
    \ /     \ /     \ /
```

**Resolutions we commonly use:**
- **Resolution 6**: ~36 km² per hex (city/region level)
- **Resolution 9**: ~0.1 km² per hex (neighborhood level)
- **Resolution 12**: ~0.0003 km² per hex (building level)

### 3. Graph Database

GeoQB stores data in **TigerGraph** - a graph database.

**What's a graph?**
- **Nodes** (vertices): Things (places, tags, facts)
- **Edges**: Relationships between things

**Example:**
```
(Hospital) --[hasOSMTag]--> (amenity=hospital)
(Hospital) --[located_on_h3_cell]--> (H3_Index)
(H3_Index) --[h3_grid_link]--> (Neighboring_H3_Index)
```

**Why graphs?**
- Natural for geospatial relationships
- Powerful queries (shortest path, community detection)
- Scalable to millions of nodes

### 4. Data-as-Code

GeoQB treats data like infrastructure-as-code.

**Traditional GIS:** Click, export, lose track of what you did
**GeoQB:** Define layers in code, version control, reproduce exactly

**Example Layer Definition:**
```python
layer = {
    'name': 'hospitals',
    'type': 'amenity',
    'tags': {'amenity': 'hospital'},
    'bbox': [50.0, 8.0, 51.0, 9.0],  # Frankfurt area
    'resolution': 9  # Neighborhood level
}
```

This is versioned in Git, shareable, reproducible!

---

## Your First Project

Let's build something real: **Analyze hospital accessibility in Frankfurt, Germany**

### Project 1: Hospital Accessibility Map

**Goal:** Create an interactive map showing hospital distribution

**What you'll learn:**
- Create a workspace
- Define a layer
- Fetch OpenStreetMap data
- Load into graph database
- Visualize on a map

#### Step 1: Initialize Workspace

```bash
# Make sure environment is activated
source env/env.sh env1
source script/set_aliases.sh env1

# Create workspace
gqws init

# Check it worked
gqws ls
```

**What happened?**
A workspace directory was created with:
```
~/geoqb-workspace/
├── raw/          # Raw data from APIs
├── stage/        # Processed data
├── md/           # Metadata
├── dumps/        # Graph exports
└── graph_layers/ # Extracted layers
```

#### Step 2: Setup Database Schema

First time only - create the graph structure:

```bash
# Navigate to examples
cd examples

# Run schema setup
python test_szenario_0.py
```

**Expected Output:**
```
🎨 GeoQB ASCII Art
Connecting to TigerGraph...
✅ Connected successfully!
Creating schema...
✅ Schema created!
Vertices: osmtag, h3place, osmplace, fact
Edges: hasOSMTag, h3_grid_link, located_on_h3_cell, observed_at
```

#### Step 3: Define Your First Layer

Create a new Python file: `my_first_layer.py`

```python
#!/usr/bin/env python3
"""
My First GeoQB Layer
Goal: Analyze hospitals in Frankfurt, Germany
"""

import os
from geoanalysis.geoqb.geoqb_layers import GeoQbLayers
from geoanalysis.geoqb.geoqb_tg import GeoQbTG

# Initialize layer manager
workspace = os.getenv('GEOQB_WORKSPACE')
layers = GeoQbLayers(workspace_path=workspace)

# Define Frankfurt bounding box
# Format: [lat_min, lon_min, lat_max, lon_max]
frankfurt_bbox = [
    50.015,  # South latitude
    8.550,   # West longitude
    50.200,  # North latitude
    8.800    # East longitude
]

# Create hospital layer
print("📋 Creating hospitals layer...")
layers.add_layer(
    name='frankfurt_hospitals',
    layer_type='amenity',
    tags={'amenity': 'hospital'},
    bbox=frankfurt_bbox,
    resolution=9  # Neighborhood level
)

# Save layer definition
layers.save_layers()
print("✅ Layer definition saved!")
print(f"📍 Bounding box: {frankfurt_bbox}")
print(f"🔍 Resolution: 9 (neighborhood level)")
```

Run it:

```bash
python my_first_layer.py
```

**Expected Output:**
```
📋 Creating hospitals layer...
✅ Layer definition saved!
📍 Bounding box: [50.015, 8.55, 50.2, 8.8]
🔍 Resolution: 9 (neighborhood level)
```

#### Step 4: Fetch Data from OpenStreetMap

Now let's get real hospital data:

```python
#!/usr/bin/env python3
"""
Fetch hospital data from OpenStreetMap
"""

import os
from geoanalysis.geoqb.geoqb_layers import GeoQbLayers
from geoanalysis.geoqb.geoqb_osm_pandas import fetch_osm_data_overpass

# Load layer definition
workspace = os.getenv('GEOQB_WORKSPACE')
layers = GeoQbLayers(workspace_path=workspace)
layers.load_layers()

# Get our hospital layer
hospital_layer = layers.layers['frankfurt_hospitals']

print("🌍 Fetching data from OpenStreetMap...")
print(f"   Bounding box: {hospital_layer['bbox']}")
print(f"   Looking for: {hospital_layer['tags']}")

# Fetch from Overpass API
data = fetch_osm_data_overpass(
    bbox=hospital_layer['bbox'],
    tags=hospital_layer['tags'],
    timeout=180
)

print(f"✅ Found {len(data)} hospitals!")
print("\n📊 Sample data:")
print(data.head())

# Save to workspace
import pandas as pd
output_path = os.path.join(workspace, 'raw', 'frankfurt_hospitals.csv')
data.to_csv(output_path, index=False)
print(f"\n💾 Saved to: {output_path}")
```

**Expected Output:**
```
🌍 Fetching data from OpenStreetMap...
   Bounding box: [50.015, 8.55, 50.2, 8.8]
   Looking for: {'amenity': 'hospital'}
✅ Found 12 hospitals!

📊 Sample data:
   id            name              lat       lon
0  123  Universitätsklinikum  50.0965   8.6709
1  456  St. Katharinen        50.1123   8.6543
...
```

#### Step 5: Process with H3 Indexing

Add H3 spatial indices:

```python
#!/usr/bin/env python3
"""
Add H3 spatial indices to hospital data
"""

import os
import pandas as pd
from geoanalysis.geoqb.geoqb_h3 import lat_lon_to_h3

# Load data
workspace = os.getenv('GEOQB_WORKSPACE')
data_path = os.path.join(workspace, 'raw', 'frankfurt_hospitals.csv')
data = pd.read_csv(data_path)

print(f"📊 Loaded {len(data)} hospitals")

# Add H3 index
print("🔷 Adding H3 spatial indices...")
data['h3_index'] = data.apply(
    lambda row: lat_lon_to_h3(row['lat'], row['lon'], resolution=9),
    axis=1
)

print("✅ H3 indices added!")
print("\n🔍 Sample with H3:")
print(data[['name', 'lat', 'lon', 'h3_index']].head())

# Save processed data
stage_path = os.path.join(workspace, 'stage', 'frankfurt_hospitals_h3.csv')
data.to_csv(stage_path, index=False)
print(f"\n💾 Saved to: {stage_path}")
```

**Expected Output:**
```
📊 Loaded 12 hospitals
🔷 Adding H3 spatial indices...
✅ H3 indices added!

🔍 Sample with H3:
            name      lat      lon         h3_index
0  Universitätskl...  50.0965  8.6709  891e204a9ffffff
1  St. Katharinen     50.1123  8.6543  891e204b1ffffff
```

#### Step 6: Load into TigerGraph

Now load into the graph database:

```python
#!/usr/bin/env python3
"""
Load hospital data into TigerGraph
"""

import os
import pandas as pd
from geoanalysis.geoqb.geoqb_tg import GeoQbTG

# Connect to TigerGraph
print("🔌 Connecting to TigerGraph...")
tg = GeoQbTG(
    host=os.getenv('TG_URL'),
    username=os.getenv('TG_USERNAME'),
    password=os.getenv('TG_PASSWORD')
)

if tg.test_connection():
    print("✅ Connected!")
else:
    print("❌ Connection failed!")
    exit(1)

# Load processed data
workspace = os.getenv('GEOQB_WORKSPACE')
data_path = os.path.join(workspace, 'stage', 'frankfurt_hospitals_h3.csv')
data = pd.read_csv(data_path)

print(f"\n📤 Uploading {len(data)} hospitals...")

# Prepare vertices
h3_vertices = []
osm_vertices = []
tag_vertices = [{'id': 'amenity_hospital'}]

for _, row in data.iterrows():
    # H3 cell vertex
    h3_vertices.append({
        'id': row['h3_index'],
        'resolution': 9,
        'layer_id': 'frankfurt_hospitals'
    })

    # OSM place vertex
    osm_vertices.append({
        'id': f"osm_{row['id']}",
        'name': row.get('name', 'Unknown'),
        'lat': row['lat'],
        'lon': row['lon']
    })

# Upsert vertices
print("   Upserting H3 cells...")
tg.upsert_vertices('h3place', h3_vertices)

print("   Upserting OSM places...")
tg.upsert_vertices('osmplace', osm_vertices)

print("   Upserting tags...")
tg.upsert_vertices('osmtag', tag_vertices)

# Prepare edges
edges = []
for _, row in data.iterrows():
    edges.append({
        'from': f"osm_{row['id']}",
        'to': row['h3_index']
    })

print("   Creating edges...")
tg.upsert_edges('located_on_h3_cell', 'osmplace', 'h3place', edges)

print("✅ Upload complete!")
print(f"   {len(h3_vertices)} H3 cells")
print(f"   {len(osm_vertices)} OSM places")
print(f"   {len(edges)} edges")
```

#### Step 7: Visualize on Map

Finally, create an interactive map:

```python
#!/usr/bin/env python3
"""
Visualize hospitals on interactive map
"""

import os
import pandas as pd
import folium
from geoanalysis.geoqb.geoqb_h3 import h3_to_lat_lon

# Load data
workspace = os.getenv('GEOQB_WORKSPACE')
data_path = os.path.join(workspace, 'stage', 'frankfurt_hospitals_h3.csv')
data = pd.read_csv(data_path)

print("🗺️  Creating interactive map...")

# Create map centered on Frankfurt
frankfurt_center = [50.1109, 8.6821]
m = folium.Map(
    location=frankfurt_center,
    zoom_start=12,
    tiles='OpenStreetMap'
)

# Add hospital markers
for _, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"<b>{row.get('name', 'Hospital')}</b><br>H3: {row['h3_index']}",
        icon=folium.Icon(color='red', icon='plus', prefix='fa')
    ).add_to(m)

# Add H3 hexagons
import h3
for _, row in data.iterrows():
    # Get hexagon boundary
    h3_boundary = h3.h3_to_geo_boundary(row['h3_index'], geo_json=True)

    # Add polygon
    folium.Polygon(
        locations=[(lat, lon) for lon, lat in h3_boundary],
        color='blue',
        fill=True,
        fillColor='blue',
        fillOpacity=0.2,
        popup=f"H3 Cell: {row['h3_index']}"
    ).add_to(m)

# Save map
output_path = os.path.join(workspace, 'graph_layers', 'frankfurt_hospitals_map.html')
m.save(output_path)

print(f"✅ Map created!")
print(f"📂 Open this file in your browser:")
print(f"   {output_path}")
```

**Open the HTML file in your browser and you'll see:**
- Interactive map of Frankfurt
- Red markers for each hospital
- Blue hexagons showing H3 cells
- Click on markers for details!

---

## Exercises

### Exercise 1: Expand Your Analysis

Modify the code to analyze a different city. Try:
- **Berlin**: `[52.40, 13.20, 52.60, 13.55]`
- **London**: `[51.40, -0.30, 51.65, 0.10]`
- **New York**: `[40.60, -74.10, 40.85, -73.85]`

**Challenge:** Find which city has the highest hospital density!

### Exercise 2: Add More Layers

Add layers for:
- **Pharmacies**: `{'amenity': 'pharmacy'}`
- **Schools**: `{'amenity': 'school'}`
- **Parks**: `{'leisure': 'park'}`

Create a multi-layer map showing all of them!

### Exercise 3: Calculate Accessibility

For each H3 cell, count how many hospitals are within 2km.

**Hint:**
```python
from geoanalysis.geoqb.geoqb_h3 import k_ring

# Get cells within distance
nearby_cells = k_ring(h3_index, k=5)  # Approximately 2km at resolution 9
```

---

## Quiz: Test Your Understanding

### Question 1
**What is H3 resolution 9 used for?**
- A) Global analysis
- B) Neighborhood-level analysis ✅
- C) Building-level analysis
- D) Street-level analysis

### Question 2
**In GeoQB's graph model, what does an edge represent?**
- A) A place on the map
- B) A relationship between entities ✅
- C) A data table
- D) A file on disk

### Question 3
**What format is a bounding box in GeoQB?**
- A) [north, south, east, west]
- B) [lat_min, lon_min, lat_max, lon_max] ✅
- C) [lon, lat, lon, lat]
- D) [x1, y1, x2, y2]

### Question 4
**Why use H3 hexagons instead of squares?**
- A) They look cooler
- B) Uniform coverage with no distortion ✅
- C) Easier to compute
- D) Traditional GIS uses them

### Question 5
**What does "data-as-code" mean in GeoQB?**
- A) Data is stored in source code files
- B) Layer definitions are code that can be versioned ✅
- C) You must write code to access data
- D) Data is compiled like software

**Answers:** 1-B, 2-B, 3-B, 4-B, 5-B

---

## Troubleshooting

### Problem: "Module not found" error

**Solution:**
```bash
# Make sure environment is activated
source env/env.sh env1

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: TigerGraph connection fails

**Solution:**
1. Check your credentials in `env/env.sh`
2. Verify TigerGraph instance is running (check cloud dashboard)
3. Test connection:
```python
from geoanalysis.geoqb.geoqb_tg import GeoQbTG
import os

tg = GeoQbTG(
    host=os.getenv('TG_URL'),
    username=os.getenv('TG_USERNAME'),
    password=os.getenv('TG_PASSWORD')
)
print(tg.test_connection())
```

### Problem: No data returned from Overpass API

**Solution:**
1. Check bounding box is valid (lat/lon ranges)
2. Try smaller bounding box
3. Check OSM tag exists: https://taginfo.openstreetmap.org/
4. Increase timeout parameter

### Problem: Map doesn't display

**Solution:**
1. Check HTML file path is correct
2. Ensure folium is installed: `pip install folium`
3. Try opening in different browser

---

## Next Steps

Congratulations! You've completed your first GeoQB project! 🎉

**Where to go from here:**

### For Developers
👉 [Developer Journey](DEVELOPER_JOURNEY.md) - Build production applications

### For Researchers
👉 [Researcher Journey](RESEARCHER_JOURNEY.md) - Advanced spatial analysis

### For Business Users
👉 [Business Journey](BUSINESS_JOURNEY.md) - Create business insights

### Advanced Topics
👉 [Theory & Algorithms](THEORY_AND_ALGORITHMS.md) - Deep dive into the science
👉 [Advanced Topics](ADVANCED_TOPICS.md) - Streaming, ML, production deployment

---

## Additional Resources

### Documentation
- [Architecture Overview](../ARCHITECTURE.md)
- [Module Reference](../MODULES.md)
- [Security Guide](../SECURITY.md)
- [Deployment Guide](../DEPLOYMENT.md)

### Community
- GitHub: https://github.com/GeoQB/geoqb
- Discussions: https://github.com/GeoQB/geoqb/discussions
- Issues: https://github.com/GeoQB/geoqb/issues

### External Resources
- H3 Documentation: https://h3geo.org/
- TigerGraph Docs: https://docs.tigergraph.com/
- OpenStreetMap Wiki: https://wiki.openstreetmap.org/

---

## Feedback

We'd love to hear from you!

- ⭐ Star the repo if you found this helpful
- 💬 Join the discussion
- 🐛 Report issues
- 📝 Contribute improvements

---

**Last Updated:** 2024
**Difficulty:** Beginner
**Estimated Time:** 30 minutes
**Next:** [Developer Journey](DEVELOPER_JOURNEY.md) or [Researcher Journey](RESEARCHER_JOURNEY.md)
