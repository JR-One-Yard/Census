#!/usr/bin/env python3
"""
Add Geographic Names to Multi-Gen Analysis Results
"""

import pandas as pd
from pathlib import Path

print("Loading geographic descriptor...")
try:
    # Load the geographic descriptor
    geo_desc = pd.read_excel(
        "./2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx",
        sheet_name="2021_ASGS_MAIN_Structures"
    )
    # Filter to SA2 only
    geo_desc = geo_desc[geo_desc['ASGS_Structure'] == 'SA2']
    print(f"  ✓ Loaded {len(geo_desc)} SA2 area names")
    print(f"  Columns: {geo_desc.columns.tolist()}")

    # Clean up the geographic data
    geo_lookup = geo_desc[['Census_Code_2021', 'Census_Name_2021']].copy()
    geo_lookup.columns = ['SA2_CODE', 'SA2_Name']

    # Convert SA2_CODE to string to ensure proper matching
    geo_lookup['SA2_CODE'] = geo_lookup['SA2_CODE'].astype(str)

    # Process each result file
    result_dir = Path("./results/multigen_housing")
    result_files = list(result_dir.glob("*.csv"))

    print(f"\nProcessing {len(result_files)} result files...")

    for result_file in result_files:
        print(f"  Processing {result_file.name}...")

        # Load the result file
        df = pd.read_csv(result_file)

        # Convert SA2_CODE to string for proper matching
        df['SA2_CODE'] = df['SA2_CODE'].astype(str)

        # Remove old SA2_Name column if exists
        if 'SA2_Name' in df.columns:
            df = df.drop('SA2_Name', axis=1)

        # Merge with geographic names
        df = df.merge(geo_lookup, on='SA2_CODE', how='left')

        # Reorder columns to put SA2_Name after SA2_CODE
        cols = df.columns.tolist()
        if 'SA2_Name' in cols:
            cols.remove('SA2_Name')
            sa2_code_idx = cols.index('SA2_CODE')
            cols.insert(sa2_code_idx + 1, 'SA2_Name')
            df = df[cols]

        # Save back
        df.to_csv(result_file, index=False, float_format='%.2f')
        print(f"    ✓ Updated with geographic names")

    print("\n✓ All files updated successfully!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
