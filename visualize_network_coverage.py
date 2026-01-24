"""
Visualize pedestrian network coverage
Shows: Original LTA roads vs Current/Fixed pedestrian network
Author: Network Diagnostics
Date: 2026-01-06
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import sys
import os

print("="*80)
print("PEDESTRIAN NETWORK VISUALIZATION")
print("="*80)

# ============================================================================
# Load data
# ============================================================================
print("\n[1] Loading data...")

# Load original LTA road network
roads_lta = gpd.read_file('RoadSectionLine_Apr2025/RoadSectionLine.shp')
print(f"  ✓ LTA roads: {len(roads_lta):,}")

# Load current pedestrian network (if exists)
ped_network_path = 'pedestrian_network/gis_files/pedestrian_network_edges_v2.shp'
if os.path.exists(ped_network_path):
    ped_network = gpd.read_file(ped_network_path)
    print(f"  ✓ Current pedestrian network: {len(ped_network):,} edges")
    has_current = True
else:
    print(f"  ⚠ No current pedestrian network found")
    has_current = False

# Load outlets
outlets_path = 'pedestrian_network/core_files/outlet_network_connections_v2.csv'
if os.path.exists(outlets_path):
    import pandas as pd
    outlets_df = pd.read_csv(outlets_path)
    outlets = gpd.GeoDataFrame(
        outlets_df,
        geometry=gpd.points_from_xy(outlets_df.X, outlets_df.Y),
        crs=roads_lta.crs
    )
    print(f"  ✓ Connected outlets: {len(outlets):,}")
    has_outlets = True
else:
    print(f"  ⚠ No outlet connections found")
    has_outlets = False

# Prepare road categories for comparison
roads_cat1 = roads_lta[roads_lta['RD_CATG__1'] == 'Category 1']
roads_cat2_5 = roads_lta[roads_lta['RD_CATG__1'].isin(['Category 2', 'Category 3', 'Category 4', 'Category 5'])]
roads_no_cat = roads_lta[roads_lta['RD_CATG__1'] == 'No Category']
roads_all_ped = roads_lta[roads_lta['RD_CATG__1'] != 'Category 1']  # Fixed version

print(f"  • Category 1 (Expressways): {len(roads_cat1):,}")
print(f"  • Category 2-5: {len(roads_cat2_5):,}")
print(f"  • No Category: {len(roads_no_cat):,}")
print(f"  • All pedestrian (Cat 2-5 + No Cat): {len(roads_all_ped):,}")

# ============================================================================
# Create visualizations
# ============================================================================
print("\n[2] Creating visualizations...")

# Define central area bounds for reference
central_x = [28000, 32000]
central_y = [28000, 32000]

# Create figure with subplots
if has_current:
    fig, axes = plt.subplots(1, 3, figsize=(24, 10))
else:
    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    axes = [axes[0], axes[1], None]

# ============================================================================
# Plot 1: Original LTA Roads (all categories)
# ============================================================================
ax1 = axes[0]
roads_lta.plot(ax=ax1, color='red', linewidth=0.3, alpha=0.4, label='All LTA roads')
roads_no_cat.plot(ax=ax1, color='darkred', linewidth=0.8, alpha=0.8, label='No Category (excluded in old version)')

# Highlight central area
ax1.axvline(central_x[0], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax1.axvline(central_x[1], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax1.axhline(central_y[0], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax1.axhline(central_y[1], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax1.text(30000, 31500, 'Central\nArea', ha='center', va='center',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5), fontsize=10)

ax1.set_title('Original LTA Road Network\n(Red = All roads, Dark Red = "No Category")', fontsize=12, fontweight='bold')
ax1.set_xlabel('X (SVY21)')
ax1.set_ylabel('Y (SVY21)')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)

# ============================================================================
# Plot 2: Current/Old Pedestrian Network (if exists)
# ============================================================================
if has_current:
    ax2 = axes[1]
    roads_lta.plot(ax=ax2, color='red', linewidth=0.3, alpha=0.3, label='Original LTA roads')
    ped_network.plot(ax=ax2, color='black', linewidth=0.6, alpha=0.8, label='Pedestrian network (OLD)')

    if has_outlets:
        outlets.plot(ax=ax2, color='green', markersize=5, alpha=0.5, label=f'Outlets ({len(outlets):,})')

    # Highlight central area
    ax2.axvline(central_x[0], color='blue', linestyle='--', alpha=0.3, linewidth=1)
    ax2.axvline(central_x[1], color='blue', linestyle='--', alpha=0.3, linewidth=1)
    ax2.axhline(central_y[0], color='blue', linestyle='--', alpha=0.3, linewidth=1)
    ax2.axhline(central_y[1], color='blue', linestyle='--', alpha=0.3, linewidth=1)
    ax2.text(30000, 31500, 'Central\nArea\n(MISSING)', ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7), fontsize=10, fontweight='bold')

    ax2.set_title('OLD Pedestrian Network (Dec 23)\n(Black = Current network, Red = Original roads)',
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('X (SVY21)')
    ax2.set_ylabel('Y (SVY21)')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

# ============================================================================
# Plot 3: Expected Fixed Network
# ============================================================================
ax3 = axes[2] if has_current else axes[1]
roads_lta.plot(ax=ax3, color='red', linewidth=0.3, alpha=0.2, label='Original LTA roads (all)')
roads_all_ped.plot(ax=ax3, color='darkgreen', linewidth=0.6, alpha=0.7,
                   label=f'FIXED network ({len(roads_all_ped):,} roads)')
roads_no_cat.plot(ax=ax3, color='lime', linewidth=0.8, alpha=0.9,
                  label=f'Newly included "No Category" ({len(roads_no_cat):,})')

# Highlight central area
ax3.axvline(central_x[0], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax3.axvline(central_x[1], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax3.axhline(central_y[0], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax3.axhline(central_y[1], color='blue', linestyle='--', alpha=0.3, linewidth=1)
ax3.text(30000, 31500, 'Central\nArea\n(COVERED)', ha='center', va='center',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7), fontsize=10, fontweight='bold')

ax3.set_title('FIXED Pedestrian Network (After Regeneration)\n(Green = Fixed network, Lime = Newly added roads)',
              fontsize=12, fontweight='bold')
ax3.set_xlabel('X (SVY21)')
ax3.set_ylabel('Y (SVY21)')
ax3.legend(loc='upper right')
ax3.grid(True, alpha=0.3)

# ============================================================================
# Save figure
# ============================================================================
plt.tight_layout()
output_file = 'network_comparison_visualization.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✓ Saved: {output_file}")

# ============================================================================
# Statistics
# ============================================================================
print("\n" + "="*80)
print("NETWORK STATISTICS")
print("="*80)
print(f"\nOriginal LTA Roads:")
print(f"  • Total: {len(roads_lta):,}")
print(f"  • Category 1 (Expressways): {len(roads_cat1):,}")
print(f"  • Category 2-5: {len(roads_cat2_5):,}")
print(f"  • No Category: {len(roads_no_cat):,}")

if has_current:
    print(f"\nOLD Pedestrian Network (Cat 2-5 only):")
    print(f"  • Edges in shapefile: {len(ped_network):,}")
    print(f"  • Source roads: ~{len(roads_cat2_5):,}")

if has_outlets:
    print(f"\nOLD Outlet Connections:")
    print(f"  • Connected outlets: {len(outlets):,}")

print(f"\nFIXED Pedestrian Network (Cat 2-5 + No Category):")
print(f"  • Expected source roads: {len(roads_all_ped):,}")
print(f"  • Additional roads: +{len(roads_no_cat):,} ({100*len(roads_no_cat)/len(roads_cat2_5):.1f}% increase)")

# Central area analysis
central_no_cat = roads_no_cat.cx[central_x[0]:central_x[1], central_y[0]:central_y[1]]
print(f"\nCentral Area Impact:")
print(f"  • 'No Category' roads in central area: {len(central_no_cat):,}")
print(f"  • This explains the gap in the old network!")

print("\n" + "="*80)
print("TO FIX THE NETWORK:")
print("  Run: cd pedestrian_network/scripts && python build_pedestrian_network_v2.py")
print("="*80)
print(f"\nVisualization complete! Check: {output_file}")
