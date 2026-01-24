# Pedestrian Routing Network - Complete File Guide

## 📋 Project Overview

A production-ready pedestrian routing network for Singapore covering **5,430 halal-certified outlets** with **82.3% coverage**. Built from LTA transportation infrastructure data (April 2025) using a hybrid road-footpath approach.

---

## 🎯 Quick Start (3 Steps)

### 1. Load the Network

```python
import pickle
with open('pedestrian_network_graph_v2.pkl', 'rb') as f:
    G = pickle.load(f)
```

### 2. Load Outlets

```python
import pandas as pd
outlets = pd.read_csv('outlet_network_connections_v2.csv')
```

### 3. Find a Route

```python
import networkx as nx

# Get outlet nodes
outlet_a = outlets.iloc[0]
outlet_b = outlets.iloc[100]

node_a = (round(outlet_a['X'], 2), round(outlet_a['Y'], 2))
node_b = (round(outlet_b['X'], 2), round(outlet_b['Y'], 2))

# Compute shortest path
path = nx.shortest_path(G, node_a, node_b, weight='weight')
walk_time = nx.shortest_path_length(G, node_a, node_b, weight='weight')

print(f"Walking time: {walk_time:.1f} minutes")
```

---

## 📁 File Structure

### 🔴 Essential Files (Start Here)

| File | Size | Description |
|------|------|-------------|
| **`pedestrian_network_graph_v2.pkl`** | 1.1 MB | Main network graph (NetworkX) - USE THIS |
| **`outlet_network_connections_v2.csv`** | 798 KB | 5,430 connected outlets with coordinates |
| **`NETWORK_SUMMARY.md`** | 9.9 KB | Quick reference guide (read this first!) |

### 📘 Documentation

| File | Purpose |
|------|---------|
| **`NETWORK_DOCUMENTATION.md`** | Complete technical documentation (38 pages) |
| **`NETWORK_SUMMARY.md`** | Executive summary and quick reference |
| **`README_NETWORK.md`** | This file - file organization guide |
| `network_statistics_v2.txt` | Network metrics summary |

### 🐍 Python Scripts

| Script | Use Case |
|--------|----------|
| **`network_usage_examples.py`** | 6 practical examples (RUN THIS for demos) |
| **`validate_network_routing.py`** | Network validation and testing |
| `build_pedestrian_network_v2.py` | Network construction (reproducible) |
| `explore_network_data.py` | Data exploration (optional) |

### 📊 Analysis Outputs

| File | Content |
|------|---------|
| `outlet_accessibility_analysis.csv` | Accessibility scores for 100 sample outlets |
| `routing_validation_tests.csv` | 10 sample routes with distances/times |
| `example_route.csv` | Detailed route coordinates for visualization |

### 🗺️ GIS Files

| File | Format | Use |
|------|--------|-----|
| `pedestrian_network_edges_v2.shp` | Shapefile | Network visualization in QGIS/ArcGIS |
| (+ `.dbf`, `.shx`, `.prj`, `.cpg`) | Supporting | Shapefile components |

### 🗄️ Superseded Files (Version 1)

These files are from the initial build with lower coverage (54.5%). Use v2 files instead.

- ~~`pedestrian_network_graph.pkl`~~ → Use `pedestrian_network_graph_v2.pkl`
- ~~`outlet_network_connections.csv`~~ → Use `outlet_network_connections_v2.csv`
- ~~`build_pedestrian_network.py`~~ → Use `build_pedestrian_network_v2.py`

---

## 🚀 Usage Workflow

### For Analysts

1. **Read**: `NETWORK_SUMMARY.md` (5 min)
2. **Load**: Network + outlets (see Quick Start above)
3. **Run**: `network_usage_examples.py` to see what's possible
4. **Adapt**: Copy examples for your analysis
5. **Reference**: `NETWORK_DOCUMENTATION.md` for details

### For Developers

1. **Read**: `NETWORK_DOCUMENTATION.md` (technical specs)
2. **Understand**: `build_pedestrian_network_v2.py` (methodology)
3. **Test**: `validate_network_routing.py` (validation approach)
4. **Extend**: Modify scripts for custom requirements

### For GIS Users

1. **Import**: `pedestrian_network_edges_v2.shp` into QGIS/ArcGIS
2. **Import**: `outlet_network_connections_v2.csv` as point layer (X, Y fields)
3. **Visualize**: Network structure and outlet distribution
4. **Export**: Analysis results back to CSV for Python processing

---

## 📂 Directory Organization

```
web-scraping/
├── 📕 DOCUMENTATION
│   ├── NETWORK_SUMMARY.md              ← Start here!
│   ├── NETWORK_DOCUMENTATION.md        ← Complete reference
│   ├── README_NETWORK.md               ← This file
│   └── network_statistics_v2.txt       ← Quick stats
│
├── 🎯 CORE NETWORK FILES (Use these!)
│   ├── pedestrian_network_graph_v2.pkl       ← Main network
│   └── outlet_network_connections_v2.csv     ← Outlet data
│
├── 🐍 EXECUTABLE SCRIPTS
│   ├── network_usage_examples.py       ← Run this for demos!
│   ├── validate_network_routing.py     ← Validation tests
│   ├── build_pedestrian_network_v2.py  ← Network builder
│   └── explore_network_data.py         ← Data exploration
│
├── 📊 ANALYSIS OUTPUTS
│   ├── outlet_accessibility_analysis.csv
│   ├── routing_validation_tests.csv
│   └── example_route.csv
│
├── 🗺️ GIS FILES
│   ├── pedestrian_network_edges_v2.shp
│   ├── pedestrian_network_edges_v2.dbf
│   ├── pedestrian_network_edges_v2.shx
│   ├── pedestrian_network_edges_v2.prj
│   └── pedestrian_network_edges_v2.cpg
│
├── 📁 SOURCE DATA (LTA datasets)
│   ├── RoadSectionLine_Apr2025/
│   ├── Footpath_Apr2025/
│   ├── RoadCrossing_Apr2025/
│   └── PedestrainOverheadbridge_UnderPass_Apr2025/
│
└── 🗄️ VERSION 1 FILES (superseded)
    ├── pedestrian_network_graph.pkl
    └── outlet_network_connections.csv
```

---

## 🎓 Learning Path

### Beginner (No Coding)

1. Read `NETWORK_SUMMARY.md`
2. Open `pedestrian_network_edges_v2.shp` in QGIS
3. Visualize network and outlets
4. Understand spatial coverage

### Intermediate (Basic Python)

1. Read `NETWORK_SUMMARY.md`
2. Run `network_usage_examples.py`
3. Modify examples for your outlets
4. Export results to CSV

### Advanced (Spatial Analysis)

1. Read `NETWORK_DOCUMENTATION.md`
2. Study `build_pedestrian_network_v2.py`
3. Understand weighting methodology
4. Customize network construction
5. Implement advanced algorithms

---

## 📊 Network Statistics

```
🌐 NETWORK SIZE
   Nodes:              10,641
   Edges:              11,808
   Total Length:       2,107.9 km

📍 OUTLET COVERAGE
   Connected:          5,430 outlets
   Coverage Rate:      82.3%
   Avg Distance:       123.0 m to network

🔗 CONNECTIVITY
   Fully Connected:    Yes (single component)
   Avg Node Degree:    2.22

📏 VALIDATION
   Test Routes:        10/10 successful
   Avg Route:          18.5 km
   Network Quality:    Production ready ✅
```

---

## 🛠️ Common Tasks

### Task 1: Find Nearest Outlets

```python
# Find 10 nearest outlets to a location
target = (30000, 29000)  # X, Y coordinates

distances = []
for idx, outlet in outlets.iterrows():
    node = (round(outlet['X'], 2), round(outlet['Y'], 2))
    if node in G:
        try:
            dist = nx.shortest_path_length(G, target, node, weight='weight')
            distances.append((outlet['name'], dist))
        except:
            pass

distances.sort(key=lambda x: x[1])
for name, dist in distances[:10]:
    print(f"{name}: {dist:.1f} min")
```

### Task 2: Accessibility Score

```python
# How many outlets can each outlet reach in 15 minutes?
for idx, outlet in outlets.iterrows():
    node = (round(outlet['X'], 2), round(outlet['Y'], 2))
    if node in G:
        reachable = nx.single_source_dijkstra_path_length(
            G, node, cutoff=15, weight='weight'
        )
        score = len(reachable)
        print(f"{outlet['name']}: {score} reachable")
```

### Task 3: Route Analysis

```python
# Analyze route composition
path = nx.shortest_path(G, node_a, node_b, weight='weight')

route_types = {}
for i in range(len(path)-1):
    edge_type = G[path[i]][path[i+1]]['type']
    length = G[path[i]][path[i+1]]['length_m']
    route_types[edge_type] = route_types.get(edge_type, 0) + length

for edge_type, length in route_types.items():
    print(f"{edge_type}: {length/1000:.2f} km")
```

---

## ⚠️ Important Notes

### Version Control

- **Always use v2 files** (`*_v2.pkl`, `*_v2.csv`)
- Version 1 had 54.5% coverage (fragmented)
- Version 2 has 82.3% coverage (recommended)

### Coordinate System

- **Projection**: SVY21 (Singapore national CRS)
- **Units**: Meters
- **Format**: (X, Y) tuples
- **Precision**: 5-meter grid

### Node Lookup

Outlets are connected to network nodes. To find an outlet's node:

```python
outlet = outlets.iloc[0]
node = (round(outlet['X'], 2), round(outlet['Y'], 2))

# Verify node exists
if node in G:
    print("✓ Outlet connected to network")
else:
    print("✗ Outlet not in network")
```

### Performance

- Single route: <0.1 seconds
- 100 routes: ~5 seconds
- Accessibility (1 outlet): ~1 second
- Full betweenness: Hours (use sampling)

---

## 🐛 Troubleshooting

### "KeyError: node not in graph"

**Problem**: Outlet node doesn't exist in network
**Solution**:
1. Check if outlet in `outlet_network_connections_v2.csv`
2. Verify node with: `node in G`
3. Use only outlets from the connections file

### "NetworkXNoPath: No path between nodes"

**Problem**: Nodes in different components (shouldn't happen in v2)
**Solution**: Verify both nodes exist: `node_a in G and node_b in G`

### Slow Performance

**Problem**: Computing all-pairs distances
**Solution**:
1. Use `cutoff` parameter: `cutoff=15`
2. Sample outlets: `outlets.sample(100)`
3. Subset graph to region

### Wrong Coordinates

**Problem**: Using lat/lon instead of SVY21
**Solution**: All coordinates must be in SVY21 meters (X, Y format)

---

## 📞 Support Resources

| Question | Resource |
|----------|----------|
| "How do I...?" | `network_usage_examples.py` |
| "What does X mean?" | `NETWORK_DOCUMENTATION.md` |
| "Quick overview?" | `NETWORK_SUMMARY.md` |
| "What files do I need?" | This file (README_NETWORK.md) |
| "Is it working?" | `validate_network_routing.py` |

---

## 🎯 Success Checklist

Before starting your analysis, verify:

- ✅ Loaded `pedestrian_network_graph_v2.pkl` (not v1)
- ✅ Loaded `outlet_network_connections_v2.csv` (not v1)
- ✅ Read `NETWORK_SUMMARY.md` for methodology
- ✅ Ran `network_usage_examples.py` successfully
- ✅ Understood coordinate system (SVY21 meters)
- ✅ Verified node lookups: `node in G`

---

## 📈 Next Steps

### Immediate Actions

1. ✅ Read `NETWORK_SUMMARY.md` (5 min)
2. ✅ Run `network_usage_examples.py` (2 min)
3. ✅ Adapt examples for your use case
4. ✅ Consult `NETWORK_DOCUMENTATION.md` as needed

### Advanced Analysis

Consider implementing:
- Isochrone mapping (time-based service areas)
- Multi-destination routing (visiting multiple outlets)
- Optimization (facility location problems)
- Temporal analysis (peak hours, accessibility changes)

### Integration

Network can be integrated with:
- QGIS/ArcGIS (use shapefile)
- Web mapping (export to GeoJSON)
- Dashboards (accessibility metrics)
- Mobile apps (routing API)

---

**Network Version**: 2.0 ✅

**Status**: Production Ready

**Coverage**: 5,430 outlets (82.3%)

**Last Updated**: December 22, 2025

**Maintained By**: Spatial Network Specialist

---

For questions or issues, refer to the documentation files listed above. Happy routing! 🗺️🚶‍♂️
