#!/usr/bin/env python3
"""Check geographic description file for coordinate data"""
import pandas as pd

# Read the geographic description file
geo_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"

# Read main structures sheet
print("Reading ASGS Main Structures sheet...")
df = pd.read_excel(geo_file, sheet_name='2021_ASGS_MAIN_Structures')
print(f"Columns: {list(df.columns)}")
print(f"Rows: {len(df):,}")
print("\nFirst 20 rows:")
print(df.head(20))

# Check for SA1 data
print("\n\nFiltering for SA1 codes...")
if 'SA1_CODE_2021' in df.columns:
    df_sa1 = df[df['SA1_CODE_2021'].notna()]
    print(f"SA1 records: {len(df_sa1):,}")
    print(df_sa1.head(10))
else:
    # Check all columns
    print("Columns in dataframe:")
    for col in df.columns:
        print(f"  - {col}")
        if 'SA1' in str(col).upper():
            print(f"    Found SA1 column: {col}")
