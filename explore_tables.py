#!/usr/bin/env python3
"""
Explore census tables to identify industry, occupation, and dwelling data
"""

import pandas as pd
import os
from pathlib import Path

# Base path for SA2 data
base_path = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS"
sa2_path = os.path.join(base_path, "SA2/AUS")
sa1_path = os.path.join(base_path, "SA1/AUS")

def explore_table_columns(table_name, path):
    """Load a table and show its columns"""
    file_path = os.path.join(path, f"2021Census_{table_name}_AUST_SA2.csv")

    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path, nrows=2)
        return {
            'table': table_name,
            'columns': list(df.columns),
            'num_columns': len(df.columns),
            'sample_columns': df.columns[1:min(10, len(df.columns))].tolist()
        }
    except Exception as e:
        return {'table': table_name, 'error': str(e)}

# Tables to explore (second release tables G43-G62 contain employment/industry data)
tables_to_check = [
    'G43', 'G44', 'G45',  # Labor force tables
    'G46A', 'G46B',        # Labor force by age/sex
    'G47A', 'G47B', 'G47C', 'G47D', 'G47E', 'G47F',  # Labor force details
    'G48A', 'G48B',        # Labor force status
    'G49A', 'G49B',        # Education (we know this one)
    'G50A', 'G50B', 'G50C',  # Labor related
    'G51A', 'G51B', 'G51C',  # Industry of employment possibly
    'G52A', 'G52B', 'G52C',  # Industry of employment possibly
    'G53A', 'G53B', 'G53C',  # Industry of employment possibly
    'G54A', 'G54B', 'G54C', 'G54D',  # Industry details
    'G55A', 'G55B', 'G55C', 'G55D',  # Industry details
    'G56A', 'G56B',        # Industry details
    'G57A', 'G57B',        # Income by labor force (we've seen this)
    'G58A', 'G58B',        # Income by labor force
    'G59A', 'G59B',        # Labor force income
    'G60A', 'G60B',        # Occupation (we know this - Managers, Professionals, etc.)
    'G61A', 'G61B',        # Occupation details
    'G62',                 # Unknown
]

# Also check dwelling tables from first release
dwelling_tables = [
    'G01',  # Selected person characteristics
    'G02',  # Medians and averages
    'G30',  # Dwelling structure
    'G31',  # Dwelling structure details
    'G32',  # Dwelling structure by household composition
    'G33',  # Household income
    'G34',  # Mortgage/rent
    'G35',  # Dwelling internet connection
    'G36',  # Dwelling structure by household composition
    'G37',  # Dwelling structure
    'G38',  # Dwelling structure
    'G39',  # Dwelling structure
    'G40',  # Tenure and landlord type
    'G41',  # Mortgage
    'G42',  # Rent
]

print("=" * 80)
print("EXPLORING EMPLOYMENT, INDUSTRY, AND OCCUPATION TABLES (G43-G62)")
print("=" * 80)

for table in tables_to_check:
    result = explore_table_columns(table, sa2_path)
    if result and 'error' not in result:
        print(f"\n{table}: {result['num_columns']} columns")

        # Check for specific keywords in columns
        col_str = ' '.join(result['columns']).lower()

        if 'indust' in col_str:
            print(f"  ✓ Contains INDUSTRY data")
            # Show industry-related columns
            industry_cols = [c for c in result['columns'] if 'indust' in c.lower()]
            print(f"    Industry columns: {', '.join(industry_cols[:10])}")

        if any(x in col_str for x in ['manager', 'profession', 'occupation', 'tech_trade']):
            print(f"  ✓ Contains OCCUPATION data")
            occ_cols = [c for c in result['columns'][1:6]]
            print(f"    Sample: {', '.join(occ_cols)}")

        if 'agri' in col_str or 'manufac' in col_str or 'retail' in col_str or 'fin_ins' in col_str:
            print(f"  ✓ Contains INDUSTRY SECTORS")

print("\n" + "=" * 80)
print("EXPLORING DWELLING TABLES (G30-G42)")
print("=" * 80)

for table in dwelling_tables:
    result = explore_table_columns(table, sa2_path)
    if result and 'error' not in result:
        print(f"\n{table}: {result['num_columns']} columns")
        print(f"  Sample columns: {', '.join(result['sample_columns'][:5])}")

        col_str = ' '.join(result['columns']).lower()

        if any(x in col_str for x in ['sep_house', 'semi_detach', 'flat', 'apart', 'o_dwell', 'dwelling']):
            print(f"  ✓ Contains DWELLING TYPE data")

print("\n" + "=" * 80)
print("CHECKING SPECIFIC KEY TABLES IN DETAIL")
print("=" * 80)

# Check G60A in detail (occupation)
print("\n📊 G60A - OCCUPATION by Age and Sex:")
df_occ = pd.read_csv(os.path.join(sa2_path, "2021Census_G60A_AUST_SA2.csv"), nrows=3)
print(f"Columns ({len(df_occ.columns)}): {', '.join(df_occ.columns[1:15].tolist())}")

# Look for industry tables
print("\n🏭 Searching for INDUSTRY tables...")
for table in ['G51A', 'G52A', 'G53A', 'G54A', 'G55A', 'G56A']:
    file_path = os.path.join(sa2_path, f"2021Census_{table}_AUST_SA2.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, nrows=2)
        print(f"\n{table}: First 10 columns:")
        print(f"  {', '.join(df.columns[1:11].tolist())}")

print("\n✅ Exploration complete!")
