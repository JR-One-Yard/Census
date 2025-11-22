#!/usr/bin/env python3
"""Quick test to verify spatial analysis setup"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import glob
import os

# Test imports
print("Testing spatial analysis packages...")
print("✓ pandas")
print("✓ numpy")
print("✓ geopandas")

import libpysal as lps
print("✓ libpysal")

from esda.moran import Moran
print("✓ esda (Moran's I)")

from spreg import OLS, ML_Lag
print("✓ spreg (spatial regression)")

from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW
print("✓ mgwr (Geographically Weighted Regression)")

print("\n✓ All packages imported successfully!")

# Test data loading
print("\nTesting data access...")
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS"

# Test SA2
sa2_dir = os.path.join(DATA_DIR, "SA2/AUS")
sa2_files = glob.glob(os.path.join(sa2_dir, "*.csv"))
print(f"✓ Found {len(sa2_files)} SA2 data files")

# Load one file as test
if sa2_files:
    test_file = sa2_files[0]
    df = pd.read_csv(test_file)
    print(f"✓ Successfully loaded test file: {os.path.basename(test_file)}")
    print(f"  - Rows: {len(df)}")
    print(f"  - Columns: {len(df.columns)}")

# Test creating simple geodataframe
print("\nTesting geodataframe creation...")
points = [Point(i, i) for i in range(10)]
gdf = gpd.GeoDataFrame({'id': range(10), 'value': np.random.rand(10)}, geometry=points)
print(f"✓ Created test geodataframe: {len(gdf)} points")

# Test spatial weights
print("\nTesting spatial weights creation...")
from libpysal.weights import KNN
coords = np.array([[i, i] for i in range(10)])
w = KNN.from_array(coords, k=3)
print(f"✓ Created KNN spatial weights: {w.n} observations, {w.mean_neighbors} neighbors")

# Test Moran's I
print("\nTesting Moran's I calculation...")
values = np.random.rand(10)
moran = Moran(values, w)
print(f"✓ Calculated Moran's I = {moran.I:.4f}, p-value = {moran.p_sim:.4f}")

print("\n" + "="*80)
print("ALL TESTS PASSED!")
print("="*80)
print("\nThe spatial analysis environment is ready.")
print("You can now run the full analysis with:")
print("  python3 /home/user/Census/spatial_econometric_analysis.py")
print("or:")
print("  ./run_spatial_analysis.sh")
