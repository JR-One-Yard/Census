#!/bin/bash
# Run Comprehensive Spatial Econometric Analysis
# Australian Census 2021

echo "================================================================================"
echo "COMPREHENSIVE SPATIAL ECONOMETRIC ANALYSIS"
echo "Australian Census 2021"
echo "================================================================================"
echo ""
echo "This analysis will perform:"
echo "  • Spatial lag models for socioeconomic variables"
echo "  • Geographically Weighted Regression (GWR)"
echo "  • Moran's I and LISA statistics for thousands of variables"
echo "  • Spatial regimes modeling"
echo "  • Hot/cold spot detection"
echo ""
echo "WARNING: This is computationally intensive and may take several hours!"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds to begin..."
sleep 5

echo ""
echo "Starting analysis..."
echo ""

python3 /home/user/Census/spatial_econometric_analysis.py 2>&1 | tee /home/user/Census/spatial_analysis_log.txt

echo ""
echo "================================================================================"
echo "ANALYSIS COMPLETE!"
echo "================================================================================"
echo "Results saved to: /home/user/Census/spatial_analysis_results/"
echo "Log saved to: /home/user/Census/spatial_analysis_log.txt"
echo ""
