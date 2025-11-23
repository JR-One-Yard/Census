#!/usr/bin/env python3
"""
Map SA2 codes to suburb/city names and enhance all analysis outputs
"""

import pandas as pd
import os
from pathlib import Path

print("=" * 100)
print("🗺️  MAPPING SA2 CODES TO SUBURB NAMES")
print("=" * 100)
print()

# Paths
METADATA_PATH = "2021_GCP_all_for_AUS_short-header/Metadata"
GEOGRAPHY_FILE = os.path.join(METADATA_PATH, "2021Census_geog_desc_1st_2nd_3rd_release.xlsx")
OUTPUT_DIR = "industry_clustering_analysis"
ENHANCED_DIR = os.path.join(OUTPUT_DIR, "enhanced_with_names")

# Create enhanced output directory
os.makedirs(ENHANCED_DIR, exist_ok=True)

# ============================================================================
# STEP 1: Load Geography Descriptor File
# ============================================================================

print("📂 Loading geography descriptor file...")
print(f"   File: {GEOGRAPHY_FILE}")

try:
    # Read the main structures sheet and filter for SA2
    geography_df = pd.read_excel(GEOGRAPHY_FILE, sheet_name='2021_ASGS_MAIN_Structures')
    print(f"   ✓ Loaded {len(geography_df):,} geographic areas")
    print(f"   ✓ Columns: {', '.join(geography_df.columns.tolist())}")

    # Filter for SA2 only
    if 'ASGS_Structure' in geography_df.columns:
        sa2_df = geography_df[geography_df['ASGS_Structure'] == 'SA2'].copy()
        print(f"   ✓ Filtered to {len(sa2_df):,} SA2 areas")
        geography_df = sa2_df
    else:
        print(f"   ⚠️  No ASGS_Structure column found")

except Exception as e:
    print(f"   ❌ Error reading Excel file: {e}")
    print(f"   Will proceed without suburb name mapping")
    geography_df = None

print()

# ============================================================================
# STEP 2: Create SA2 Code to Name Mapping
# ============================================================================

if geography_df is not None:
    print("=" * 100)
    print("CREATING SA2 CODE TO NAME MAPPING")
    print("=" * 100)
    print()

    # Display first few rows to understand structure
    print("📊 Geography data structure:")
    print(geography_df.head(3))
    print()

    # Identify code and name columns
    # Expected columns: Census_Code_2021 and Census_Name_2021
    code_col = 'Census_Code_2021'
    name_col = 'Census_Name_2021'

    if code_col in geography_df.columns and name_col in geography_df.columns:
        print(f"   ✓ Code column: {code_col}")
        print(f"   ✓ Name column: {name_col}")

        # Convert code to int for matching
        geography_df[code_col] = pd.to_numeric(geography_df[code_col], errors='coerce')
        geography_df = geography_df.dropna(subset=[code_col])
        geography_df[code_col] = geography_df[code_col].astype(int)

        # Create mapping dictionary
        sa2_mapping = dict(zip(geography_df[code_col], geography_df[name_col]))
        print(f"   ✓ Created mapping for {len(sa2_mapping):,} SA2 areas")

        # Show sample mappings
        print(f"\n   Sample mappings:")
        for i, (code, name) in enumerate(list(sa2_mapping.items())[:10]):
            print(f"      {code} → {name}")

    else:
        print(f"   ⚠️  Could not find expected columns")
        print(f"   Available columns: {', '.join(geography_df.columns.tolist())}")
        sa2_mapping = {}
else:
    sa2_mapping = {}
    print("⚠️  No geography mapping available")

print()

# ============================================================================
# STEP 3: Enhance All Analysis Files with Suburb Names
# ============================================================================

print("=" * 100)
print("ENHANCING ANALYSIS FILES WITH SUBURB NAMES")
print("=" * 100)
print()

def add_suburb_names(df, sa2_col='SA2_CODE', mapping=sa2_mapping):
    """Add suburb names to dataframe"""
    if mapping and sa2_col in df.columns:
        # Convert to int if needed
        df[sa2_col] = df[sa2_col].astype(int)

        # Map to suburb names
        df['Suburb_Name'] = df[sa2_col].map(mapping)

        # If no match, use "Unknown"
        df['Suburb_Name'] = df['Suburb_Name'].fillna('Unknown SA2')

        # Reorder columns to put Suburb_Name right after SA2_CODE
        cols = df.columns.tolist()
        sa2_idx = cols.index(sa2_col)
        cols.insert(sa2_idx + 1, cols.pop(cols.index('Suburb_Name')))
        df = df[cols]

    return df

# Files to enhance
files_to_enhance = [
    'top_500_commercial_property_opportunities.csv',
    'top_500_commercial_demand_gaps.csv',
    'employment_clusters_all.csv',
    'emerging_employment_clusters.csv',
    'high_opportunity_hotspots.csv',
    'portfolio_conservative.csv',
    'portfolio_balanced.csv',
    'portfolio_aggressive.csv',
]

# Also enhance state files
state_files = [f'top_opportunities_{state}.csv' for state in ['nsw', 'vic', 'qld', 'sa', 'wa', 'act']]
files_to_enhance.extend(state_files)

enhanced_count = 0

for filename in files_to_enhance:
    filepath = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(filepath):
        print(f"📝 Processing: {filename}")

        try:
            # Load file
            df = pd.read_csv(filepath)

            # Determine SA2 column name
            sa2_col = 'SA2_CODE' if 'SA2_CODE' in df.columns else 'SA2_Code'

            # Add suburb names
            df = add_suburb_names(df, sa2_col, sa2_mapping)

            # Save enhanced version
            output_path = os.path.join(ENHANCED_DIR, filename.replace('.csv', '_with_names.csv'))
            df.to_csv(output_path, index=False)

            # Count how many names were added
            if 'Suburb_Name' in df.columns:
                named_count = (df['Suburb_Name'] != 'Unknown SA2').sum()
                print(f"   ✓ Added suburb names: {named_count}/{len(df)} areas")
                print(f"   ✓ Saved: {output_path}")
                enhanced_count += 1

        except Exception as e:
            print(f"   ⚠️  Error processing {filename}: {e}")
    else:
        print(f"   ⚠️  File not found: {filename}")

print(f"\n✅ Enhanced {enhanced_count} files with suburb names")
print()

# ============================================================================
# STEP 4: Create Top Opportunities with Names (Human-Readable)
# ============================================================================

print("=" * 100)
print("CREATING HUMAN-READABLE TOP OPPORTUNITIES REPORT")
print("=" * 100)
print()

# Load top opportunities with names
top_opps_file = os.path.join(ENHANCED_DIR, 'top_500_commercial_property_opportunities_with_names.csv')

if os.path.exists(top_opps_file):
    top_opps = pd.read_csv(top_opps_file)

    # Create a readable top 50 report
    print("🏆 TOP 50 COMMERCIAL PROPERTY OPPORTUNITIES (with Suburb Names)")
    print("-" * 100)

    # Add state column function
    def get_state(code):
        code_str = str(code)
        if code_str.startswith('1'): return 'NSW'
        elif code_str.startswith('2'): return 'VIC'
        elif code_str.startswith('3'): return 'QLD'
        elif code_str.startswith('4'): return 'SA'
        elif code_str.startswith('5'): return 'WA'
        elif code_str.startswith('6'): return 'TAS'
        elif code_str.startswith('7'): return 'NT'
        elif code_str.startswith('8'): return 'ACT'
        else: return 'Unknown'

    # Add state to full dataframe first
    if 'State' not in top_opps.columns:
        top_opps['State'] = top_opps['SA2_Code'].apply(get_state)

    # Now select columns for top 50
    top_50 = top_opps.head(50)[[
        'SA2_Code',
        'Suburb_Name',
        'State',
        'Opportunity_Score',
        'High_Value_Professionals',
        'Professional_Density_per_1000',
        'Median_Weekly_Income',
        'Demand_Gap_Index',
        'Is_Emerging_Cluster'
    ]].copy().reset_index(drop=True)

    # Save top 50 with names
    top_50_file = os.path.join(ENHANCED_DIR, 'TOP_50_OPPORTUNITIES_READABLE.csv')
    top_50.to_csv(top_50_file, index=False)
    print(f"✅ Saved: {top_50_file}")

    # Display top 10
    print("\n📍 TOP 10 OPPORTUNITIES:")
    print("-" * 100)
    for i, row in top_50.head(10).iterrows():
        print(f"\n{i+1}. {row['Suburb_Name']} ({row['State']})")
        print(f"   Opportunity Score: {row['Opportunity_Score']:.2f}/100")
        print(f"   Professionals: {int(row['High_Value_Professionals']):,}")
        print(f"   Density: {row['Professional_Density_per_1000']:.1f} per 1,000")
        print(f"   Median Income: ${int(row['Median_Weekly_Income'])}/week")
        if row['Is_Emerging_Cluster']:
            print(f"   🌱 EMERGING CLUSTER - High Growth Potential")

print()

# ============================================================================
# STEP 5: Create Emerging Clusters Report with Names
# ============================================================================

print("=" * 100)
print("EMERGING EMPLOYMENT CLUSTERS (with Suburb Names)")
print("=" * 100)
print()

emerging_file = os.path.join(ENHANCED_DIR, 'emerging_employment_clusters_with_names.csv')

if os.path.exists(emerging_file):
    emerging = pd.read_csv(emerging_file)

    print(f"🌱 Found {len(emerging)} Emerging Employment Clusters:")
    print("-" * 100)

    for i, row in emerging.iterrows():
        # Add state
        code_str = str(row['SA2_Code'])
        if code_str.startswith('1'): state = 'NSW'
        elif code_str.startswith('2'): state = 'VIC'
        elif code_str.startswith('3'): state = 'QLD'
        elif code_str.startswith('8'): state = 'ACT'
        else: state = 'Unknown'

        print(f"\n{i+1}. {row['Suburb_Name']} ({state})")
        print(f"   Population: {int(row['Population']):,}")
        print(f"   High-Value Professionals: {int(row['High_Value_Professionals']):,}")
        print(f"   Professional Density: {row['Professional_Density_per_1000']:.1f} per 1,000")
        print(f"   Median Income: ${int(row['Median_Weekly_Income'])}/week")
        print(f"   Opportunity Score: {row['Opportunity_Score']:.2f}/100")
        print(f"   Demand Gap Index: {row['Demand_Gap_Index']:.2f}")
        print(f"   💡 Investment Opportunity: First-mover advantage in emerging commercial market")

print()

# ============================================================================
# STEP 6: Create State Summaries with Top Suburbs
# ============================================================================

print("=" * 100)
print("STATE-LEVEL TOP OPPORTUNITIES (with Suburb Names)")
print("=" * 100)
print()

for state in ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'ACT']:
    state_file = os.path.join(ENHANCED_DIR, f'top_opportunities_{state.lower()}_with_names.csv')

    if os.path.exists(state_file):
        state_df = pd.read_csv(state_file)

        print(f"\n🏆 {state} - Top 5 Opportunities:")
        print("-" * 100)

        for i, row in state_df.head(5).iterrows():
            print(f"{i+1}. {row['Suburb_Name']}")
            print(f"   Opportunity Score: {row['Opp_Score']:.2f} | "
                  f"Professionals: {int(row['Professionals']):,} | "
                  f"Demand Gap: {row['Demand_Gap']:.2f}")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 100)
print("✅ SUBURB NAME MAPPING COMPLETE!")
print("=" * 100)
print()
print(f"📂 Enhanced files saved to: {ENHANCED_DIR}/")
print()
print("📄 Key Enhanced Files:")
print("   1. TOP_50_OPPORTUNITIES_READABLE.csv (Top 50 with suburb names)")
print("   2. top_500_commercial_property_opportunities_with_names.csv")
print("   3. emerging_employment_clusters_with_names.csv")
print("   4. employment_clusters_all_with_names.csv")
print("   5. All state-level files with suburb names")
print()
print(f"📊 Total files enhanced: {enhanced_count}")
print()
print("=" * 100)
