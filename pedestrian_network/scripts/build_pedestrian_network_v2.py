"""
Build a pedestrian routing network with improved connectivity
Version 2: Better node snapping and component merging

Author: Spatial Network Specialist
Date: 2025-12-22
"""
import geopandas as gpd
import pandas as pd
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import snap, linemerge
import pickle
from tqdm import tqdm

print("="*80)
print("BUILDING PEDESTRIAN ROUTING NETWORK v2")
print("Improved connectivity with intelligent node snapping")
print("="*80)

# ============================================================================
# STEP 1: Load and prepare data
# ============================================================================
print("\n[STEP 1] Loading network datasets...")

roads = gpd.read_file('RoadSectionLine_Apr2025/RoadSectionLine.shp')
footpaths = gpd.read_file('Footpath_Apr2025/Footpath.shp')
crossings = gpd.read_file('RoadCrossing_Apr2025/RoadCrossing.shp')
bridges = gpd.read_file('PedestrainOverheadbridge_UnderPass_Apr2025/PedestrainOverheadbridge.shp')
outlets = pd.read_csv('deduplicated_outlets_geocoded.csv')
outlets = outlets[outlets['geocode_source'] != 'unmatched'].copy()

print(f"  ✓ Loaded all datasets")

# ============================================================================
# STEP 2: Prepare network components
# ============================================================================
print("\n[STEP 2] Preparing network components...")

# Filter roads: Exclude only Category 1 (expressways/highways)
# This includes Cat 2-5 AND "No Category" roads (which contain major central area roads)
pedestrian_roads = roads[roads['RD_CATG__1'] != 'Category 1'].copy()

# Process weights
pedestrian_roads['length_m'] = pedestrian_roads.geometry.length
pedestrian_roads['walk_time_min'] = pedestrian_roads['length_m'] / 83.3
category_factors = {
    'Category 2': 1.3,
    'Category 3': 1.15,
    'Category 4': 1.0,
    'Category 5': 0.9,
    'No Category': 1.1  # Treat similar to Category 3 (slightly higher impedance)
}
pedestrian_roads['impedance_factor'] = pedestrian_roads['RD_CATG__1'].map(category_factors)
pedestrian_roads['weight'] = pedestrian_roads['walk_time_min'] * pedestrian_roads['impedance_factor']
pedestrian_roads['type'] = 'road'

# Process footpaths
footpaths['length_m'] = footpaths.geometry.length
footpaths_clean = footpaths[footpaths['length_m'] >= 2.0].copy()
footpaths_clean['walk_time_min'] = footpaths_clean['length_m'] / 83.3
footpaths_clean['weight'] = footpaths_clean['walk_time_min'] * 0.8
footpaths_clean['type'] = 'footpath'

# Process crossings
crossings['length_m'] = crossings.geometry.length
crossings_clean = crossings[crossings['length_m'] >= 1.0].copy()
crossings_clean['walk_time_min'] = crossings_clean['length_m'] / 83.3 + 0.5
crossings_clean['weight'] = crossings_clean['walk_time_min'] * 1.2
crossings_clean['type'] = 'crossing'

print(f"  ✓ Prepared {len(pedestrian_roads):,} roads, {len(footpaths_clean):,} footpaths, {len(crossings_clean):,} crossings")

# ============================================================================
# STEP 3: Extract and snap nodes with tolerance
# ============================================================================
print("\n[STEP 3] Extracting nodes with intelligent snapping...")

SNAP_TOLERANCE = 5.0  # 5 meters - nodes within this distance will be merged

def extract_endpoints(gdf):
    """Extract start and end points from geometries"""
    points = []
    edge_data = []

    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue

        if isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
        else:
            lines = [geom]

        for line in lines:
            coords = list(line.coords)
            if len(coords) >= 2:
                start = coords[0]
                end = coords[-1]
                points.extend([start, end])
                edge_data.append({
                    'start': start,
                    'end': end,
                    'geometry': line,
                    'weight': row['weight'],
                    'length_m': row['length_m'],
                    'type': row['type']
                })

    return points, edge_data

# Extract all endpoints
all_points = []
all_edges = []

for gdf, name in [(pedestrian_roads, 'roads'),
                   (footpaths_clean, 'footpaths'),
                   (crossings_clean, 'crossings')]:
    points, edges = extract_endpoints(gdf)
    all_points.extend(points)
    all_edges.extend(edges)
    print(f"  • Extracted {len(edges):,} edges from {name}")

print(f"  ✓ Total: {len(all_edges):,} edges, {len(all_points):,} raw endpoints")

# ============================================================================
# STEP 4: Snap nearby nodes together
# ============================================================================
print("\n[STEP 4] Snapping nearby nodes...")

# Simple grid-based snapping for efficiency
points_array = np.array(all_points)
node_mapping = {}

# Snap to grid (round to nearest 5m)
for point in tqdm(all_points, desc="  Snapping nodes to grid"):
    snapped = (
        round(point[0] / SNAP_TOLERANCE) * SNAP_TOLERANCE,
        round(point[1] / SNAP_TOLERANCE) * SNAP_TOLERANCE
    )
    node_mapping[tuple(point)] = snapped

unique_nodes = len(set(node_mapping.values()))
print(f"  ✓ Snapped {len(all_points):,} endpoints to {unique_nodes:,} nodes")
print(f"    Merged {len(all_points) - unique_nodes:,} duplicate nodes")

# ============================================================================
# STEP 5: Build graph with snapped nodes
# ============================================================================
print("\n[STEP 5] Building graph with snapped nodes...")

G = nx.Graph()

for edge in tqdm(all_edges, desc="  Adding edges"):
    start_orig = tuple(edge['start'])
    end_orig = tuple(edge['end'])

    # Map to snapped nodes
    start = node_mapping.get(start_orig, (round(start_orig[0], 2), round(start_orig[1], 2)))
    end = node_mapping.get(end_orig, (round(end_orig[0], 2), round(end_orig[1], 2)))

    if start != end:
        # If edge exists, keep the one with lower weight
        if G.has_edge(start, end):
            existing_weight = G[start][end]['weight']
            if edge['weight'] < existing_weight:
                G[start][end]['weight'] = edge['weight']
                G[start][end]['length_m'] = edge['length_m']
                G[start][end]['type'] = edge['type']
        else:
            G.add_edge(start, end,
                      weight=edge['weight'],
                      length_m=edge['length_m'],
                      type=edge['type'])

print(f"  ✓ Graph built: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

# ============================================================================
# STEP 6: Analyze connectivity
# ============================================================================
print("\n[STEP 6] Analyzing connectivity...")

if nx.is_connected(G):
    print("  ✓ Graph is fully connected!")
else:
    components = list(nx.connected_components(G))
    print(f"  ⚠ Graph has {len(components)} components")
    component_sizes = sorted([len(c) for c in components], reverse=True)
    print(f"    Top 5 components: {component_sizes[:5]}")

    # Use largest component
    largest = max(components, key=len)
    G = G.subgraph(largest).copy()
    print(f"  → Using largest component: {G.number_of_nodes():,} nodes ({100*len(largest)/sum(component_sizes):.1f}%)")

# ============================================================================
# STEP 7: Connect outlets
# ============================================================================
print("\n[STEP 7] Connecting outlets to network...")

outlet_points = gpd.GeoDataFrame(
    outlets,
    geometry=gpd.points_from_xy(outlets.X, outlets.Y),
    crs=pedestrian_roads.crs
)

# Find nearest network node for each outlet (simple brute force for moderate size)
network_nodes_list = list(G.nodes())
network_nodes_array = np.array(network_nodes_list)

outlet_connections = []

for idx, outlet in tqdm(outlet_points.iterrows(), total=len(outlet_points), desc="  Connecting"):
    outlet_coord = np.array([outlet.X, outlet.Y])

    # Calculate distances to all network nodes
    distances = np.sqrt(((network_nodes_array - outlet_coord) ** 2).sum(axis=1))
    nearest_idx = distances.argmin()
    distance = distances[nearest_idx]

    # Connect if within 500m
    if distance <= 500:
        nearest_node = tuple(network_nodes_list[nearest_idx])
        outlet_node = (round(outlet.X, 2), round(outlet.Y, 2))

        G.add_node(outlet_node,
                   outlet_id=idx,
                   name=outlet['name'],
                   node_type='outlet')

        walk_time = distance / 83.3
        G.add_edge(outlet_node, nearest_node,
                   weight=walk_time,
                   length_m=distance,
                   type='outlet_connection')

        outlet_connections.append({
            'outlet_id': idx,
            'name': outlet['name'],
            'address': outlet['address'],
            'X': outlet.X,
            'Y': outlet.Y,
            'distance_to_network': distance,
            'network_node': nearest_node
        })

print(f"  ✓ Connected {len(outlet_connections):,} outlets")
print(f"    Coverage: {100*len(outlet_connections)/len(outlets):.1f}%")
print(f"    Avg distance: {np.mean([c['distance_to_network'] for c in outlet_connections]):.1f}m")
print(f"    Max distance: {np.max([c['distance_to_network'] for c in outlet_connections]):.1f}m")

# ============================================================================
# STEP 8: Save outputs
# ============================================================================
print("\n[STEP 8] Saving network files...")

# Save graph
with open('pedestrian_network_graph_v2.pkl', 'wb') as f:
    pickle.dump(G, f)
print(f"  ✓ Saved: pedestrian_network_graph_v2.pkl")

# Save outlet connections
outlets_df = pd.DataFrame(outlet_connections)
outlets_df.to_csv('outlet_network_connections_v2.csv', index=False)
print(f"  ✓ Saved: outlet_network_connections_v2.csv")

# Create GeoDataFrame of network edges for visualization
edges_for_viz = []
for u, v, data in G.edges(data=True):
    if 'outlet' not in data.get('type', ''):
        edges_for_viz.append({
            'geometry': LineString([u, v]),
            'weight': data['weight'],
            'length_m': data['length_m'],
            'type': data['type']
        })

edges_gdf = gpd.GeoDataFrame(edges_for_viz, crs=pedestrian_roads.crs)
edges_gdf.to_file('pedestrian_network_edges_v2.shp')
print(f"  ✓ Saved: pedestrian_network_edges_v2.shp")

# Save statistics
stats = {
    'total_nodes': G.number_of_nodes(),
    'total_edges': G.number_of_edges(),
    'network_nodes': G.number_of_nodes() - len(outlet_connections),
    'outlet_nodes': len(outlet_connections),
    'connected_outlets': len(outlet_connections),
    'total_outlets': len(outlets),
    'coverage_pct': 100 * len(outlet_connections) / len(outlets),
    'is_connected': nx.is_connected(G),
    'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
    'network_length_km': sum(d['length_m'] for _, _, d in G.edges(data=True)) / 1000
}

print(f"\n" + "="*80)
print("NETWORK V2 COMPLETE")
print("="*80)
print(f"\nKey Metrics:")
print(f"  • Total nodes: {stats['total_nodes']:,}")
print(f"  • Total edges: {stats['total_edges']:,}")
print(f"  • Connected outlets: {stats['connected_outlets']:,} / {stats['total_outlets']:,} ({stats['coverage_pct']:.1f}%)")
print(f"  • Network length: {stats['network_length_km']:.1f} km")
print(f"  • Fully connected: {stats['is_connected']}")
print(f"  • Avg node degree: {stats['avg_degree']:.2f}")

with open('network_statistics_v2.txt', 'w') as f:
    f.write("PEDESTRIAN NETWORK STATISTICS (v2)\n")
    f.write("="*70 + "\n\n")
    for key, value in stats.items():
        if isinstance(value, float):
            f.write(f"{key}: {value:.2f}\n")
        else:
            f.write(f"{key}: {value}\n")

print(f"\n  ✓ Saved: network_statistics_v2.txt")
print(f"\nNetwork ready for routing!")
