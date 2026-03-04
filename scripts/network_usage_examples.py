"""
Practical usage examples for the pedestrian routing network
Demonstrates common spatial network analysis tasks

Author: Spatial Network Specialist
Date: 2025-12-22
"""
import pickle
import pandas as pd
import networkx as nx
import numpy as np

print("="*80)
print("PEDESTRIAN NETWORK - USAGE EXAMPLES")
print("="*80)

# ============================================================================
# Load network and data
# ============================================================================
print("\n1. LOADING NETWORK AND DATA")
print("-" * 80)

with open('pedestrian_network_graph_v2.pkl', 'rb') as f:
    G = pickle.load(f)

outlets = pd.read_csv('outlet_network_connections_v2.csv')

print(f"✓ Loaded network: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
print(f"✓ Loaded {len(outlets):,} connected outlets")

# ============================================================================
# Example 1: Find nearest outlets to a location
# ============================================================================
print("\n2. FIND NEAREST OUTLETS TO A LOCATION")
print("-" * 80)

# Pick a target location (e.g., Marina Bay area)
target_x, target_y = 30000, 29000
target_node = (round(target_x / 5) * 5, round(target_y / 5) * 5)  # Snap to grid

print(f"Target location: ({target_x}, {target_y})")

# Find nearest actual network node
min_dist = float('inf')
nearest_network_node = None
for node in G.nodes():
    dist = np.sqrt((node[0] - target_x)**2 + (node[1] - target_y)**2)
    if dist < min_dist:
        min_dist = dist
        nearest_network_node = node

print(f"Nearest network node: {nearest_network_node} ({min_dist:.1f}m away)")

# Compute distances to all outlets
outlet_distances = []
for idx, outlet in outlets.iterrows():
    outlet_node = (round(outlet['X'], 2), round(outlet['Y'], 2))

    if outlet_node in G:
        try:
            walk_time = nx.shortest_path_length(G, nearest_network_node, outlet_node, weight='weight')
            outlet_distances.append({
                'name': outlet['name'],
                'address': outlet['address'],
                'walk_time_min': walk_time,
                'outlet_id': outlet['outlet_id']
            })
        except nx.NetworkXNoPath:
            pass

# Sort by distance
outlet_distances.sort(key=lambda x: x['walk_time_min'])

# Show nearest 5
print(f"\nNearest 5 outlets:")
for i, outlet in enumerate(outlet_distances[:5], 1):
    print(f"  {i}. {outlet['name'][:40]:40s} - {outlet['walk_time_min']:.1f} min")

# ============================================================================
# Example 2: Compare accessibility of two outlet locations
# ============================================================================
print("\n3. COMPARE ACCESSIBILITY OF TWO OUTLETS")
print("-" * 80)

# Select two outlets
outlet1 = outlets.iloc[0]
outlet2 = outlets.iloc[50]

print(f"Outlet A: {outlet1['name']}")
print(f"Outlet B: {outlet2['name']}")

node1 = (round(outlet1['X'], 2), round(outlet1['Y'], 2))
node2 = (round(outlet2['X'], 2), round(outlet2['Y'], 2))

# Calculate how many outlets each can reach within time thresholds
time_thresholds = [10, 15, 20, 30]

print(f"\nOutlets reachable within walking time:")
print(f"{'Time':>6s}  {'Outlet A':>10s}  {'Outlet B':>10s}  {'Difference':>10s}")
print("-" * 45)

for threshold in time_thresholds:
    # Outlet A
    reachable_a = nx.single_source_dijkstra_path_length(G, node1, cutoff=threshold, weight='weight')
    count_a = sum(1 for _, o in outlets.iterrows()
                  if (round(o['X'], 2), round(o['Y'], 2)) in reachable_a)

    # Outlet B
    reachable_b = nx.single_source_dijkstra_path_length(G, node2, cutoff=threshold, weight='weight')
    count_b = sum(1 for _, o in outlets.iterrows()
                  if (round(o['X'], 2), round(o['Y'], 2)) in reachable_b)

    diff = count_a - count_b
    print(f"{threshold:>4d} min  {count_a:>10d}  {count_b:>10d}  {diff:>+10d}")

# ============================================================================
# Example 3: Identify most accessible outlets (highest betweenness)
# ============================================================================
print("\n4. IDENTIFY STRATEGIC HUB OUTLETS")
print("-" * 80)

# For computational efficiency, sample a subset
sample_nodes = list(outlets.head(100)['outlet_id'])
outlet_nodes = [(round(outlets[outlets['outlet_id']==oid].iloc[0]['X'], 2),
                 round(outlets[outlets['outlet_id']==oid].iloc[0]['Y'], 2))
                for oid in sample_nodes]
outlet_nodes = [n for n in outlet_nodes if n in G]

print(f"Computing betweenness centrality for {len(outlet_nodes)} outlet nodes...")
print("(This measures how often each outlet lies on shortest paths between other outlets)")

# Compute betweenness for subset
betweenness = nx.betweenness_centrality(G.subgraph(outlet_nodes), weight='weight')

# Get top 5 outlets by betweenness
top_outlets = sorted(betweenness.items(), key=lambda x: -x[1])[:5]

print(f"\nTop 5 'hub' outlets (high betweenness centrality):")
for i, (node, centrality) in enumerate(top_outlets, 1):
    # Find outlet name
    matching = outlets[(abs(outlets['X'] - node[0]) < 1) & (abs(outlets['Y'] - node[1]) < 1)]
    if len(matching) > 0:
        name = matching.iloc[0]['name']
        print(f"  {i}. {name[:40]:40s} - centrality: {centrality:.4f}")

# ============================================================================
# Example 4: Route quality analysis
# ============================================================================
print("\n5. ROUTE QUALITY ANALYSIS")
print("-" * 80)

# Pick two outlets and analyze the route
outlet_a = outlets.iloc[10]
outlet_b = outlets.iloc[20]

node_a = (round(outlet_a['X'], 2), round(outlet_a['Y'], 2))
node_b = (round(outlet_b['X'], 2), round(outlet_b['Y'], 2))

if node_a in G and node_b in G:
    print(f"Route from: {outlet_a['name']}")
    print(f"        to: {outlet_b['name']}")

    # Get path
    path = nx.shortest_path(G, node_a, node_b, weight='weight')
    walk_time = nx.shortest_path_length(G, node_a, node_b, weight='weight')

    # Analyze path segments
    segment_types = {}
    total_distance = 0

    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        edge_data = G[u][v]

        seg_type = edge_data.get('type', 'unknown')
        seg_length = edge_data.get('length_m', 0)

        segment_types[seg_type] = segment_types.get(seg_type, 0) + seg_length
        total_distance += seg_length

    print(f"\nRoute statistics:")
    print(f"  Total distance: {total_distance/1000:.2f} km")
    print(f"  Walking time: {walk_time:.1f} minutes")
    print(f"  Number of segments: {len(path)-1}")
    print(f"  Average speed implied: {(total_distance/1000)/(walk_time/60):.1f} km/h")

    print(f"\nRoute composition:")
    for seg_type, length in sorted(segment_types.items(), key=lambda x: -x[1]):
        pct = 100 * length / total_distance
        print(f"  {seg_type:20s}: {length/1000:6.2f} km ({pct:5.1f}%)")

# ============================================================================
# Example 5: Service area coverage analysis
# ============================================================================
print("\n6. SERVICE AREA COVERAGE ANALYSIS")
print("-" * 80)

# Divide Singapore into regions and analyze coverage
# Simple approach: divide by X coordinate (West-East)

# Define regions
regions = {
    'West': (0, 20000),
    'Central-West': (20000, 27000),
    'Central': (27000, 33000),
    'Central-East': (33000, 38000),
    'East': (38000, 50000)
}

print("Outlet distribution and average accessibility by region:")
print(f"{'Region':15s}  {'Outlets':>8s}  {'Avg 15-min reach':>16s}")
print("-" * 50)

for region_name, (x_min, x_max) in regions.items():
    # Get outlets in region
    region_outlets = outlets[(outlets['X'] >= x_min) & (outlets['X'] < x_max)]

    if len(region_outlets) == 0:
        continue

    # Calculate average accessibility
    accessibility_scores = []
    for idx, outlet in region_outlets.head(20).iterrows():  # Sample for efficiency
        node = (round(outlet['X'], 2), round(outlet['Y'], 2))
        if node in G:
            reachable = nx.single_source_dijkstra_path_length(G, node, cutoff=15, weight='weight')
            count = sum(1 for _, o in outlets.iterrows()
                       if (round(o['X'], 2), round(o['Y'], 2)) in reachable)
            accessibility_scores.append(count)

    if accessibility_scores:
        avg_reach = np.mean(accessibility_scores)
        print(f"{region_name:15s}  {len(region_outlets):8d}  {avg_reach:16.1f}")

# ============================================================================
# Example 6: Export results for GIS visualization
# ============================================================================
print("\n7. EXPORT RESULTS FOR VISUALIZATION")
print("-" * 80)

# Create example: outlets with accessibility score
outlet_accessibility = []

for idx, outlet in outlets.head(100).iterrows():  # Sample for demo
    node = (round(outlet['X'], 2), round(outlet['Y'], 2))

    if node in G:
        # Count outlets within 15 min
        reachable = nx.single_source_dijkstra_path_length(G, node, cutoff=15, weight='weight')
        count = sum(1 for _, o in outlets.iterrows()
                   if (round(o['X'], 2), round(o['Y'], 2)) in reachable)

        outlet_accessibility.append({
            'outlet_id': outlet['outlet_id'],
            'name': outlet['name'],
            'address': outlet['address'],
            'X': outlet['X'],
            'Y': outlet['Y'],
            'outlets_within_15min': count,
            'degree': G.degree(node)
        })

accessibility_df = pd.DataFrame(outlet_accessibility)
accessibility_df.to_csv('outlet_accessibility_analysis.csv', index=False)

print(f"✓ Saved accessibility analysis: outlet_accessibility_analysis.csv")
print(f"  Contains {len(accessibility_df)} outlets with accessibility metrics")
print(f"  Can be imported into QGIS/ArcGIS as CSV with X,Y coordinates")

print("\n" + "="*80)
print("EXAMPLES COMPLETE")
print("="*80)
print("\nThese examples demonstrate:")
print("  ✓ Nearest neighbor queries")
print("  ✓ Accessibility comparisons")
print("  ✓ Network centrality analysis")
print("  ✓ Route quality assessment")
print("  ✓ Regional coverage analysis")
print("  ✓ Data export for GIS")
print("\nRefer to NETWORK_DOCUMENTATION.md for more details and advanced usage.")
