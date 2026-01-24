# Quick Start Guide

## ⚡ 3-Minute Setup

### Step 1: Navigate to folder

```bash
cd pedestrian_network
```

### Step 2: Load the network

```python
import pickle
import pandas as pd
import networkx as nx

# Load network
with open('core_files/pedestrian_network_graph_v2.pkl', 'rb') as f:
    G = pickle.load(f)

# Load outlets
outlets = pd.read_csv('core_files/outlet_network_connections_v2.csv')

print(f"✓ Network loaded: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
print(f"✓ Outlets loaded: {len(outlets):,}")
```

### Step 3: Find a route

```python
# Pick two outlets
outlet_a = outlets.iloc[0]
outlet_b = outlets.iloc[50]

# Get network nodes (rounded to match grid)
node_a = (round(outlet_a['X'], 2), round(outlet_a['Y'], 2))
node_b = (round(outlet_b['X'], 2), round(outlet_b['Y'], 2))

# Find shortest path
path = nx.shortest_path(G, node_a, node_b, weight='weight')
walk_time = nx.shortest_path_length(G, node_a, node_b, weight='weight')

# Calculate distance
distance_m = sum(G[path[i]][path[i+1]]['length_m'] for i in range(len(path)-1))

print(f"\nRoute from {outlet_a['name']} to {outlet_b['name']}")
print(f"  Distance: {distance_m/1000:.2f} km")
print(f"  Walk time: {walk_time:.1f} minutes")
print(f"  Segments: {len(path)-1}")
```

## 🎯 You're Ready!

That's it! You now have:
- ✅ A working pedestrian routing network
- ✅ 5,430 connected outlets
- ✅ Shortest path routing capability

## 📚 Next Steps

### See More Examples
```bash
cd scripts/
python network_usage_examples.py
```

This will show you:
1. Nearest outlet queries
2. Accessibility comparisons
3. Hub outlet identification
4. Route quality analysis
5. Regional coverage analysis
6. GIS export examples

### Read Documentation

- **Quick overview**: `documentation/NETWORK_SUMMARY.md`
- **File guide**: `documentation/README_NETWORK.md`
- **Full details**: `documentation/NETWORK_DOCUMENTATION.md`

## 🗺️ Visualize in GIS

1. Open QGIS or ArcGIS
2. Add layer: `gis_files/pedestrian_network_edges_v2.shp`
3. Add CSV layer: `core_files/outlet_network_connections_v2.csv`
   - X field: `X`
   - Y field: `Y`
   - CRS: SVY21

## 💡 Common Tasks

### Find Nearest 10 Outlets
```python
target_node = (30000, 29000)  # Your location

distances = []
for _, outlet in outlets.iterrows():
    node = (round(outlet['X'], 2), round(outlet['Y'], 2))
    if node in G:
        try:
            dist = nx.shortest_path_length(G, target_node, node, weight='weight')
            distances.append((outlet['name'], dist))
        except:
            pass

distances.sort(key=lambda x: x[1])
for name, dist in distances[:10]:
    print(f"{name}: {dist:.1f} min walk")
```

### Accessibility Score
```python
# How many outlets can this location reach in 15 min?
location = (round(outlets.iloc[0]['X'], 2), round(outlets.iloc[0]['Y'], 2))

reachable = nx.single_source_dijkstra_path_length(
    G, location, cutoff=15, weight='weight'
)

outlet_count = sum(1 for _, o in outlets.iterrows()
                   if (round(o['X'], 2), round(o['Y'], 2)) in reachable)

print(f"Outlets within 15 min: {outlet_count}")
```

## ⚠️ Important Notes

1. **Coordinates**: All coordinates are in SVY21 meters (X, Y)
2. **Node Format**: Always round to 2 decimals: `(round(X, 2), round(Y, 2))`
3. **Weight**: Use `weight='weight'` for time-based routing
4. **Files**: Always use `*_v2.*` files (latest version)

## 🆘 Troubleshooting

**"Node not in graph"**
→ Check outlet exists in `outlet_network_connections_v2.csv`

**"No path found"**
→ Verify both nodes exist: `node in G`

**Slow performance**
→ Use `cutoff` parameter: `cutoff=15`

---

**Questions?** Check `documentation/README_NETWORK.md` for complete file guide!
