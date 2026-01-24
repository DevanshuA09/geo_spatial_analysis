# 📍 Pedestrian Network - Complete Index

## 🎯 Start Here

**New to this network?** → Read [QUICK_START.md](QUICK_START.md) (3 minutes)

**Need overview?** → Read [documentation/NETWORK_SUMMARY.md](documentation/NETWORK_SUMMARY.md) (10 minutes)

**Want to code?** → Run [scripts/network_usage_examples.py](scripts/network_usage_examples.py)

---

## 📂 Folder Guide

### 🔴 core_files/ - Essential Network Data

**Use these files in your analysis:**

| File | Size | Description |
|------|------|-------------|
| `pedestrian_network_graph_v2.pkl` | 1.1 MB | ⭐ Main routing network (NetworkX graph) |
| `outlet_network_connections_v2.csv` | 798 KB | ⭐ 5,430 connected outlets with coordinates |

**Load in Python:**
```python
import pickle, pandas as pd
G = pickle.load(open('core_files/pedestrian_network_graph_v2.pkl', 'rb'))
outlets = pd.read_csv('core_files/outlet_network_connections_v2.csv')
```

---

### 📚 documentation/ - Read These

| File | Pages | Read If... |
|------|-------|-----------|
| `NETWORK_SUMMARY.md` | 10 | You want a quick overview |
| `README_NETWORK.md` | 11 | You need to find a specific file |
| `NETWORK_DOCUMENTATION.md` | 38 | You need technical details |
| `network_statistics_v2.txt` | 1 | You just want the numbers |

**Reading order:**
1. Start: `NETWORK_SUMMARY.md`
2. Reference: `README_NETWORK.md`
3. Deep dive: `NETWORK_DOCUMENTATION.md`

---

### 🐍 scripts/ - Run These

| Script | Purpose | Run Time |
|--------|---------|----------|
| `network_usage_examples.py` | ⭐ 6 practical demos | 2 min |
| `validate_network_routing.py` | Network validation tests | 1 min |
| `build_pedestrian_network_v2.py` | Rebuild network from scratch | 5 min |
| `explore_network_data.py` | Explore source data | 30 sec |

**To run:**
```bash
cd scripts/
python network_usage_examples.py
```

**What you'll learn:**
1. Nearest outlet queries
2. Accessibility comparisons
3. Hub identification
4. Route quality analysis
5. Regional coverage
6. GIS export

---

### 📊 analysis_outputs/ - Results

Example outputs from the network:

| File | Rows | Description |
|------|------|-------------|
| `outlet_accessibility_analysis.csv` | 100 | Sample accessibility scores |
| `routing_validation_tests.csv` | 10 | Test route results |
| `example_route.csv` | 64 | Detailed route coordinates |

**Use for:**
- Understanding output format
- Validating your own results
- Importing into GIS

---

### 🗺️ gis_files/ - For QGIS/ArcGIS

**Shapefile:** `pedestrian_network_edges_v2.shp` (+ .dbf, .shx, .prj, .cpg)

**Size:** 2.3 MB total

**To visualize:**
1. Open QGIS/ArcGIS
2. Add layer → `pedestrian_network_edges_v2.shp`
3. Add CSV layer → `core_files/outlet_network_connections_v2.csv`
   - X field: `X`
   - Y field: `Y`
   - CRS: SVY21

---

## 🎓 Learning Paths

### Path 1: Analyst (No Coding)
```
1. Read: NETWORK_SUMMARY.md
2. Open: gis_files/pedestrian_network_edges_v2.shp in QGIS
3. Visualize: Network and outlet distribution
4. Understand: Spatial coverage
```

### Path 2: Python User
```
1. Read: QUICK_START.md
2. Run: scripts/network_usage_examples.py
3. Modify: Examples for your needs
4. Reference: NETWORK_DOCUMENTATION.md
```

### Path 3: Advanced Developer
```
1. Read: NETWORK_DOCUMENTATION.md
2. Study: scripts/build_pedestrian_network_v2.py
3. Understand: Methodology and weighting
4. Extend: Custom network analysis
```

---

## 📊 Network Overview

```
📍 NETWORK STATISTICS
   Nodes:              10,641
   Edges:              11,808
   Total Length:       2,107.9 km
   Coverage:           82.3% (5,430/6,595 outlets)

🏗️ COMPONENTS
   Roads (Cat 2-5):    83.7%
   Footpaths:          3.1%
   Crossings:          0.2%
   Outlet Links:       13.0%

✅ QUALITY
   Fully Connected:    Yes
   Validated:          10/10 test routes successful
   Performance:        <0.1s per route
   Status:             Production Ready
```

---

## ⚡ Quick Reference

### Load Network
```python
import pickle, pandas as pd, networkx as nx

G = pickle.load(open('core_files/pedestrian_network_graph_v2.pkl', 'rb'))
outlets = pd.read_csv('core_files/outlet_network_connections_v2.csv')
```

### Find Route
```python
outlet_a = outlets.iloc[0]
outlet_b = outlets.iloc[50]

node_a = (round(outlet_a['X'], 2), round(outlet_a['Y'], 2))
node_b = (round(outlet_b['X'], 2), round(outlet_b['Y'], 2))

path = nx.shortest_path(G, node_a, node_b, weight='weight')
time = nx.shortest_path_length(G, node_a, node_b, weight='weight')
```

### Accessibility
```python
reachable = nx.single_source_dijkstra_path_length(
    G, source_node, cutoff=15, weight='weight'
)
print(f"Reachable nodes: {len(reachable)}")
```

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| "Node not in graph" | Check outlet in `outlet_network_connections_v2.csv` |
| "No path found" | Verify: `node_a in G and node_b in G` |
| Slow performance | Use `cutoff` parameter in routing |
| Wrong coordinates | Ensure SVY21 meters, not lat/lon |

---

## 📞 Where to Find Answers

| Question | File |
|----------|------|
| How do I use this? | `QUICK_START.md` |
| What's the methodology? | `documentation/NETWORK_SUMMARY.md` |
| Where's file X? | `documentation/README_NETWORK.md` |
| Technical details? | `documentation/NETWORK_DOCUMENTATION.md` |
| Example code? | `scripts/network_usage_examples.py` |
| Is it working? | `scripts/validate_network_routing.py` |

---

## 🎯 Use Cases

### ✅ What This Network Can Do

- ✓ Shortest path routing between outlets
- ✓ Walking time/distance calculations
- ✓ Accessibility analysis (isochrones)
- ✓ Service area mapping
- ✓ Location optimization
- ✓ Coverage analysis by region
- ✓ Route quality assessment
- ✓ Network centrality analysis

### ⚠️ What It Cannot Do

- ✗ Turn-by-turn navigation (insufficient detail)
- ✗ Real-time traffic/congestion
- ✗ Elevation/slope routing (no terrain data)
- ✗ Multi-modal transit (MRT/bus not integrated)
- ✗ Indoor routing (mall corridors, etc.)

---

## 📦 File Sizes

```
Total Network Package: ~4.5 MB

Breakdown:
  core_files/          1.9 MB  (Network + outlets)
  gis_files/           2.3 MB  (Shapefiles)
  documentation/       34 KB   (Docs)
  scripts/             32 KB   (Python)
  analysis_outputs/    13 KB   (Results)
```

---

## 🔄 Version Info

**Current Version:** 2.0

**Version History:**
- v2.0 (Current): Grid snapping, 82.3% coverage, fully connected
- v1.0 (Deprecated): Point matching, 54.5% coverage, fragmented

**Always use v2 files** (marked with `_v2`)

---

## ✅ Checklist Before Starting

- [ ] Read `QUICK_START.md` or `NETWORK_SUMMARY.md`
- [ ] Located `core_files/` folder
- [ ] Understand SVY21 coordinate system
- [ ] Know how to load: `pickle.load()` and `pd.read_csv()`
- [ ] Verified NetworkX installed: `import networkx as nx`
- [ ] Ready to use `_v2` files (not v1)

---

**Created:** December 22, 2025
**Version:** 2.0
**Status:** Production Ready ✅
**Coverage:** 5,430 outlets (82.3%)
**Maintained By:** Spatial Network Specialist
