#!/usr/bin/env python3
"""
Explore Census tables to identify relevant data for TOD analysis
"""

import pandas as pd
import os

# Read metadata
metadata_path = "2021_GCP_all_for_AUS_short-header/Metadata/Metadata_2021_GCP_DataPack_R1_R2.xlsx"

print("=" * 80)
print("EXPLORING CENSUS DATA TABLES FOR TOD ANALYSIS")
print("=" * 80)

# Read all sheet names
xl_file = pd.ExcelFile(metadata_path)
print(f"\nAvailable sheets: {xl_file.sheet_names}\n")

# Read the main metadata sheet (usually first one or named something like "Table_List" or "DataPack_Tables")
try:
    # Try reading the first sheet
    df_meta = pd.read_excel(metadata_path, sheet_name=0)
    print(f"First sheet columns: {df_meta.columns.tolist()}\n")
    print(df_meta.head(20))
except Exception as e:
    print(f"Error reading metadata: {e}")

# Also check the sequential template
template_path = "2021_GCP_all_for_AUS_short-header/Metadata/2021_GCP_Sequential_Template_R2.xlsx"
print("\n" + "=" * 80)
print("CHECKING SEQUENTIAL TEMPLATE")
print("=" * 80)

xl_template = pd.ExcelFile(template_path)
print(f"\nTemplate sheets: {xl_template.sheet_names}\n")

# Search for keywords related to transportation and employment
keywords = ['travel', 'transport', 'method', 'work', 'employment', 'occupation', 'journey',
            'commute', 'motor', 'car', 'train', 'bus', 'public', 'transit']

print("\n" + "=" * 80)
print("SEARCHING FOR TRANSPORTATION/EMPLOYMENT RELATED TABLES")
print("=" * 80)

# Read table descriptions if available
for sheet in xl_file.sheet_names[:5]:  # Check first 5 sheets
    try:
        df = pd.read_excel(metadata_path, sheet_name=sheet)
        print(f"\n--- Sheet: {sheet} ---")
        print(f"Columns: {df.columns.tolist()}")

        # Search in all text columns
        for col in df.columns:
            if df[col].dtype == 'object':  # Text columns
                for keyword in keywords:
                    matches = df[df[col].astype(str).str.contains(keyword, case=False, na=False)]
                    if not matches.empty:
                        print(f"\n  Keyword '{keyword}' found in column '{col}':")
                        print(f"  {matches[[col]].head()}")

    except Exception as e:
        print(f"  Error reading sheet {sheet}: {e}")

print("\n" + "=" * 80)
print("SAMPLING SPECIFIC TABLES")
print("=" * 80)

# Sample some likely tables
sa1_path = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SA1/AUS/"

# Tables to check
tables_to_check = {
    'G43': 'Labour Force Status',
    'G51A': 'Occupation',
    'G54A': 'Industry of Employment',
    'G58A': 'Income by Employment Status',
    'G59A': 'Unknown - checking columns',
    'G60A': 'Unknown - checking columns',
    'G61A': 'Unknown - checking columns',
    'G62': 'Unknown - checking columns'
}

for table, desc in tables_to_check.items():
    filepath = f"{sa1_path}2021Census_{table}_AUST_SA1.csv"
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, nrows=2)
        print(f"\n{table} - {desc}")
        print(f"  Columns (first 15): {df.columns.tolist()[:15]}")
        print(f"  Total columns: {len(df.columns)}")

        # Check if it has transport-related columns
        transport_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['car', 'train', 'bus', 'walk', 'bicycle', 'ferry', 'tram', 'motor', 'public', 'transport', 'method'])]
        if transport_cols:
            print(f"  *** TRANSPORTATION COLUMNS FOUND: {transport_cols}")
    else:
        print(f"\n{table} - File not found")

print("\n" + "=" * 80)
print("CHECKING SA2 and SA3 DATA AVAILABILITY")
print("=" * 80)

for geo_level in ['SA2', 'SA3']:
    geo_path = f"2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/{geo_level}/AUS/"
    if os.path.exists(geo_path):
        files = os.listdir(geo_path)
        print(f"\n{geo_level}: {len(files)} files")
        print(f"  Sample files: {files[:5]}")
    else:
        print(f"\n{geo_level}: Directory not found")

print("\n" + "=" * 80)
print("Done!")
print("=" * 80)
