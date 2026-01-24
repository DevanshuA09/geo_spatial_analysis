"""
Explore the network datasets to understand their structure and attributes
"""
import geopandas as gpd
import pandas as pd

print("="*70)
print("EXPLORING NETWORK DATA STRUCTURE")
print("="*70)

# Load all network datasets
print("\n1. Loading Road Section Lines...")
roads = gpd.read_file('RoadSectionLine_Apr2025/RoadSectionLine.shp')
print(f"   Rows: {len(roads):,}")
print(f"   Columns: {list(roads.columns)}")
print(f"   CRS: {roads.crs}")
print("\n   Sample data:")
print(roads.head(3))
print(f"\n   Road categories (RD_CATG__1):")
print(roads['RD_CATG__1'].value_counts().sort_index())

print("\n" + "-"*70)
print("2. Loading Footpaths...")
footpaths = gpd.read_file('Footpath_Apr2025/Footpath.shp')
print(f"   Rows: {len(footpaths):,}")
print(f"   Columns: {list(footpaths.columns)}")
print(f"   CRS: {footpaths.crs}")
print("\n   Sample data:")
print(footpaths.head(3))

print("\n" + "-"*70)
print("3. Loading Road Crossings...")
crossings = gpd.read_file('RoadCrossing_Apr2025/RoadCrossing.shp')
print(f"   Rows: {len(crossings):,}")
print(f"   Columns: {list(crossings.columns)}")
print(f"   CRS: {crossings.crs}")
print("\n   Sample data:")
print(crossings.head(3))

print("\n" + "-"*70)
print("4. Loading Pedestrian Overhead Bridges/Underpasses...")
bridges = gpd.read_file('PedestrainOverheadbridge_UnderPass_Apr2025/PedestrainOverheadbridge.shp')
print(f"   Rows: {len(bridges):,}")
print(f"   Columns: {list(bridges.columns)}")
print(f"   CRS: {bridges.crs}")
print("\n   Sample data:")
print(bridges.head(3))

print("\n" + "-"*70)
print("5. Loading Outlets...")
outlets = pd.read_csv('deduplicated_outlets_geocoded.csv')
outlets_geocoded = outlets[outlets['geocode_source'] != 'unmatched']
print(f"   Total outlets: {len(outlets):,}")
print(f"   Geocoded outlets: {len(outlets_geocoded):,}")
print(f"   X range: {outlets_geocoded['X'].min():.2f} to {outlets_geocoded['X'].max():.2f}")
print(f"   Y range: {outlets_geocoded['Y'].min():.2f} to {outlets_geocoded['Y'].max():.2f}")

print("\n" + "="*70)
print("EXPLORATION COMPLETE")
print("="*70)
