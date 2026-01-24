# Pedestrian Network - CBD Area Gap Fix

## Issue Identified

The pedestrian network was missing roads in Singapore's CBD (Central Business District) including Raffles Place, Marina Bay, and downtown areas.

**Key Visualization:** See **[cbd_area_analysis.png](cbd_area_analysis.png)** - Shows CBD area before/after fix with 76.5% coverage achieved.

**TL;DR:** The CBD is 94% "No Category" roads which were being excluded. Fix applied and network regenerated. CBD coverage improved from ~62 edges to 869 edges (14x improvement).

## Root Cause

The network building script (`pedestrian_network/scripts/build_pedestrian_network_v2.py`) was filtering roads to include only **Category 2-5** roads, which excluded:

1. **Category 1 roads** (312 roads) - Expressways/highways *(correctly excluded)*
2. **"No Category" roads** (2,506 roads) - **This was the problem**

### Impact

The "No Category" classification contains approximately **1,045 road segments in the central area**, including major roads such as:
- Orchard Road (18 segments)
- North Bridge Road (19 segments)
- River Valley Road (18 segments)
- Victoria Street (14 segments)
- Beach Road (12 segments)
- New Bridge Road (14 segments)

By excluding these roads, the network had a significant gap in Singapore's CBD.

## Solution

Modified the filtering logic to exclude only Category 1 expressways/highways, rather than whitelisting specific categories:

**Previous code:**
```python
pedestrian_roads = roads[roads['RD_CATG__1'].isin([
    'Category 2', 'Category 3', 'Category 4', 'Category 5'
])].copy()
```

**Updated code:**
```python
# Exclude only Category 1 (expressways/highways)
pedestrian_roads = roads[roads['RD_CATG__1'] != 'Category 1'].copy()
```

Also added an impedance factor for "No Category" roads (1.1) in the routing weights.

## Results

### Overall Network
- **Roads used:** 12,508 → 15,014 (+2,506 roads, +20%)
- **Network edges:** 10,270 → 12,072 (+1,802 edges, +17.5%)
- **Outlet coverage:** 78.6% → 95.6%

### CBD Area Specifically
- **CBD roads:** 1,136 total (94% are "No Category")
- **Old max possible:** ~62 edges (Cat 2-5 only)
- **New coverage:** 869 edges (76.5%)
- **Improvement:** 14x more coverage in CBD!

## Files Modified

- `pedestrian_network/scripts/build_pedestrian_network_v2.py` (lines 41-54)

## Visualizations

- **[cbd_area_analysis.png](cbd_area_analysis.png)** - CBD-specific analysis (RECOMMENDED)
- **[network_before_after.png](network_before_after.png)** - Full Singapore comparison

See **[CBD_FIX_SUMMARY.md](CBD_FIX_SUMMARY.md)** for detailed CBD analysis.

## Regenerating the Network

To regenerate the corrected network files:

```bash
cd pedestrian_network/scripts
python build_pedestrian_network_v2.py
```

This will create updated versions of:
- `pedestrian_network_graph_v2.pkl`
- `pedestrian_network_edges_v2.shp`
- `outlet_network_connections_v2.csv`
- `network_statistics_v2.txt`
