# Pedestrian Routing Network

## 📁 Folder Structure

```
pedestrian_network/
├── core_files/              ⭐ START HERE
│   ├── pedestrian_network_graph_v2.pkl       # Main network graph
│   └── outlet_network_connections_v2.csv     # 5,430 connected outlets
│
├── documentation/           📚 READ THIS
│   ├── README_NETWORK.md                     # Complete file guide
│   ├── NETWORK_SUMMARY.md                    # Quick reference
│   ├── NETWORK_DOCUMENTATION.md              # Full technical docs
│   └── network_statistics_v2.txt             # Network stats
│
├── scripts/                 🐍 RUN THESE
│   ├── network_usage_examples.py             # Practical demos
│   ├── validate_network_routing.py           # Validation tests
│   ├── build_pedestrian_network_v2.py        # Network builder
│   └── explore_network_data.py               # Data exploration
│
├── analysis_outputs/        📊 RESULTS
│   ├── outlet_accessibility_analysis.csv     # Accessibility scores
│   ├── routing_validation_tests.csv          # Sample routes
│   └── example_route.csv                     # Detailed route
│
└── gis_files/              🗺️ FOR QGIS/ARCGIS
    └── pedestrian_network_edges_v2.shp       # Network shapefile
        (+ .dbf, .shx, .prj, .cpg)
```

## 🚀 Quick Start

### 1. Load Network (Python)

```python
import pickle
import pandas as pd
import networkx as nx

# Load from core_files/
with open('core_files/pedestrian_network_graph_v2.pkl', 'rb') as f:
    G = pickle.load(f)

outlets = pd.read_csv('core_files/outlet_network_connections_v2.csv')

print(f"Network: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
print(f"Outlets: {len(outlets):,}")
```

### 2. Find Shortest Path

```python
# Get two outlets
outlet_a = outlets.iloc[0]
outlet_b = outlets.iloc[100]

# Convert to network nodes
node_a = (round(outlet_a['X'], 2), round(outlet_a['Y'], 2))
node_b = (round(outlet_b['X'], 2), round(outlet_b['Y'], 2))

# Route
path = nx.shortest_path(G, node_a, node_b, weight='weight')
walk_time = nx.shortest_path_length(G, node_a, node_b, weight='weight')

print(f"Walking time: {walk_time:.1f} minutes")
```

### 3. Run Examples

```bash
cd scripts/
python network_usage_examples.py
```

## 📊 Network Statistics

- **Nodes**: 10,641
- **Edges**: 11,808
- **Total Length**: 2,107.9 km
- **Connected Outlets**: 5,430 (82.3%)
- **Fully Connected**: Yes ✓

## 📖 Documentation

Start with: `documentation/NETWORK_SUMMARY.md`

For details: `documentation/NETWORK_DOCUMENTATION.md`

## ⚡ Key Features

✅ Production-ready routing network
✅ 82.3% outlet coverage
✅ Validated with test cases
✅ Complete documentation
✅ Working examples included
✅ GIS-compatible shapefiles

## 🎯 Common Use Cases

1. **Shortest Path Routing** - Find optimal routes between outlets
2. **Accessibility Analysis** - Service areas, isochrones
3. **Location Optimization** - Identify strategic locations
4. **Coverage Analysis** - Regional accessibility scores
5. **Route Quality** - Analyze route composition

## 📞 Support

- Questions? → `documentation/README_NETWORK.md`
- Examples? → `scripts/network_usage_examples.py`
- Technical? → `documentation/NETWORK_DOCUMENTATION.md`

---

**Version**: 2.0 | **Status**: Production Ready ✅ | **Date**: Dec 22, 2025
