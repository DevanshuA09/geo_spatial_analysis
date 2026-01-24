#!/bin/bash
# Regenerate pedestrian network and create visualization
# Run this script to fix the central area gap issue

echo "=================================================================="
echo "PEDESTRIAN NETWORK REGENERATION"
echo "=================================================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "[1] Activating virtual environment..."
    source venv/bin/activate
fi

# Regenerate the network
echo ""
echo "[2] Regenerating pedestrian network with fix..."
echo "    (This will include 'No Category' roads to fix central area gap)"
cd pedestrian_network/scripts || exit 1
python build_pedestrian_network_v2.py
cd ../..

# Create before/after visualization
echo ""
echo "[3] Creating comparison visualization..."
python visualize_network_coverage.py

echo ""
echo "=================================================================="
echo "COMPLETE!"
echo "=================================================================="
echo ""
echo "Generated files:"
echo "  • pedestrian_network/gis_files/pedestrian_network_edges_v2.shp"
echo "  • pedestrian_network/core_files/outlet_network_connections_v2.csv"
echo "  • network_comparison_visualization.png"
echo ""
echo "Check network_comparison_visualization.png to see the fix!"
echo ""
