#!/usr/bin/env python3
"""
Transit-Oriented Development (TOD) Scoring & Commuter Shed Optimization
===============================================================================
Analyzes 61,844 SA1 areas to identify optimal locations for transit investment

Key Analyses:
1. Car dependency metrics for all SA1s
2. Employment center identification (SA2/SA3 level)
3. Commute pain point identification
4. TOD potential scoring
5. Travel time optimization modeling

Author: Claude Code
License: MIT
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("TRANSIT-ORIENTED DEVELOPMENT (TOD) SCORING & COMMUTER OPTIMIZATION ANALYSIS")
print("=" * 100)
print("\nProcessing 61,844 SA1 areas across Australia...")
print("This is a compute-intensive analysis using the full 2021 Census dataset\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS")

# Geographic levels
SA1_PATH = BASE_PATH / "SA1" / "AUS"
SA2_PATH = BASE_PATH / "SA2" / "AUS"
SA3_PATH = BASE_PATH / "SA3" / "AUS"

# Key data tables
TABLES = {
    'G01': 'Basic Demographics',
    'G02': 'Medians and Averages',
    'G40': 'Dwelling Structure',
    'G43': 'Labour Force Status',
    'G51A': 'Occupation (Males)',
    'G51B': 'Occupation (Females)',
    'G54A': 'Industry by Age (Males)',
    'G62': 'Method of Travel to Work'
}

# ============================================================================
# STEP 1: LOAD SA1 TRANSPORTATION DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 1: LOADING SA1 TRANSPORTATION & EMPLOYMENT DATA (61,844 areas)")
print("=" * 100)

# Load G62 - Method of Travel to Work
print("\n[1/5] Loading G62 - Method of Travel to Work data...")
g62_sa1 = pd.read_csv(SA1_PATH / "2021Census_G62_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g62_sa1):,} SA1 areas with {len(g62_sa1.columns)} transportation columns")

# Load G43 - Labour Force Status
print("\n[2/5] Loading G43 - Labour Force Status data...")
g43_sa1 = pd.read_csv(SA1_PATH / "2021Census_G43_AUST_SA1.csv")
print(f"  ✓ Loaded employment status for {len(g43_sa1):,} SA1 areas")

# Load G01 - Basic Demographics
print("\n[3/5] Loading G01 - Population data...")
g01_sa1 = pd.read_csv(SA1_PATH / "2021Census_G01_AUST_SA1.csv")
print(f"  ✓ Loaded population data for {len(g01_sa1):,} SA1 areas")

# Load G40 - Dwelling Structure
print("\n[4/5] Loading G40 - Dwelling Structure data...")
g40_sa1 = pd.read_csv(SA1_PATH / "2021Census_G40_AUST_SA1.csv")
print(f"  ✓ Loaded dwelling data for {len(g40_sa1):,} SA1 areas")

# Load G02 - Medians
print("\n[5/5] Loading G02 - Median statistics...")
g02_sa1 = pd.read_csv(SA1_PATH / "2021Census_G02_AUST_SA1.csv")
print(f"  ✓ Loaded median statistics for {len(g02_sa1):,} SA1 areas")

# ============================================================================
# STEP 2: CALCULATE TRANSPORTATION METRICS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: CALCULATING CAR DEPENDENCY & TRANSPORTATION METRICS")
print("=" * 100)

print("\n[Processing all 61,844 SA1 areas...]")

# Create master DataFrame
df_transport = g62_sa1.copy()
df_transport.columns = df_transport.columns.str.strip()

# Calculate total commuters by mode (one method)
df_transport['total_train'] = df_transport['One_method_Train_P']
df_transport['total_bus'] = df_transport['One_method_Bus_P']
df_transport['total_ferry'] = df_transport['One_method_Ferry_P']
df_transport['total_tram'] = df_transport['One_met_Tram_or_lt_rail_P']
df_transport['total_car_driver'] = df_transport['One_method_Car_as_driver_P']
df_transport['total_car_passenger'] = df_transport['One_method_Car_as_passenger_P']
df_transport['total_bicycle'] = df_transport['One_method_Bicycle_P']
df_transport['total_walked'] = df_transport['One_method_Walked_only_P']
df_transport['total_motorbike'] = df_transport['One_method_Motorbike_scootr_P']

# Add two-method combinations (multimodal transit users)
df_transport['total_train'] += (
    df_transport['Two_methods_Train_Bus_P'] +
    df_transport['Two_methods_Train_Ferry_P'] +
    df_transport.get('Two_methods_Train_Tot_P', 0)
)

df_transport['total_bus'] += (
    df_transport['Two_methods_Train_Bus_P'] +
    df_transport['Two_methods_Bus_Ferry_P'] +
    df_transport.get('Two_methods_Bus_Tot_P', 0)
)

# Calculate aggregated metrics
df_transport['total_public_transit'] = (
    df_transport['total_train'] +
    df_transport['total_bus'] +
    df_transport['total_ferry'] +
    df_transport['total_tram']
)

df_transport['total_car'] = (
    df_transport['total_car_driver'] +
    df_transport['total_car_passenger']
)

df_transport['total_active_transport'] = (
    df_transport['total_bicycle'] +
    df_transport['total_walked']
)

# Total commuters
df_transport['total_commuters'] = (
    df_transport['total_public_transit'] +
    df_transport['total_car'] +
    df_transport['total_active_transport'] +
    df_transport['total_motorbike'] +
    df_transport.get('One_method_Truck_P', 0) +
    df_transport.get('One_method_Other_P', 0)
)

# ============================================================================
# STEP 3: CALCULATE CAR DEPENDENCY METRICS
# ============================================================================

print("\n[Calculating car dependency metrics...]")

# Avoid division by zero
df_transport['total_commuters_safe'] = df_transport['total_commuters'].replace(0, np.nan)

# Car dependency ratio (0-1, higher = more car dependent)
df_transport['car_dependency_ratio'] = (
    df_transport['total_car'] / df_transport['total_commuters_safe']
)

# Public transit usage ratio
df_transport['public_transit_ratio'] = (
    df_transport['total_public_transit'] / df_transport['total_commuters_safe']
)

# Active transport ratio
df_transport['active_transport_ratio'] = (
    df_transport['total_active_transport'] / df_transport['total_commuters_safe']
)

# Fill NaN with 0 for ratios
for col in ['car_dependency_ratio', 'public_transit_ratio', 'active_transport_ratio']:
    df_transport[col] = df_transport[col].fillna(0)

# Calculate "commute pain" score (high car dependency + high commuter count)
# This identifies areas with lots of car commuters who could benefit from transit
df_transport['commute_pain_score'] = (
    df_transport['car_dependency_ratio'] *
    np.log1p(df_transport['total_commuters'])  # Log scale to normalize
)

print(f"\n  ✓ Car dependency calculated for {len(df_transport):,} SA1 areas")
print(f"  ✓ Average car dependency: {df_transport['car_dependency_ratio'].mean():.1%}")
print(f"  ✓ Average public transit usage: {df_transport['public_transit_ratio'].mean():.1%}")
print(f"  ✓ Average active transport: {df_transport['active_transport_ratio'].mean():.1%}")

# ============================================================================
# STEP 4: LOAD SA2/SA3 EMPLOYMENT CENTER DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: IDENTIFYING EMPLOYMENT CENTERS (SA2 & SA3 LEVEL)")
print("=" * 100)

print("\n[1/4] Loading SA2 employment data...")
g43_sa2 = pd.read_csv(SA2_PATH / "2021Census_G43_AUST_SA2.csv")
print(f"  ✓ Loaded {len(g43_sa2):,} SA2 areas")

print("\n[2/4] Loading SA2 population data...")
g01_sa2 = pd.read_csv(SA2_PATH / "2021Census_G01_AUST_SA2.csv")
print(f"  ✓ Loaded population for {len(g01_sa2):,} SA2 areas")

print("\n[3/4] Loading SA3 employment data...")
g43_sa3 = pd.read_csv(SA3_PATH / "2021Census_G43_AUST_SA3.csv")
print(f"  ✓ Loaded {len(g43_sa3):,} SA3 areas")

print("\n[4/4] Loading SA3 population data...")
g01_sa3 = pd.read_csv(SA3_PATH / "2021Census_G01_AUST_SA3.csv")
print(f"  ✓ Loaded population for {len(g01_sa3):,} SA3 areas")

# Calculate employment density for SA2
df_sa2_employment = pd.DataFrame({
    'SA2_CODE_2021': g43_sa2['SA2_CODE_2021'],
    'employed_full_time': g43_sa2['lfs_Emplyed_wrked_full_time_P'],
    'employed_part_time': g43_sa2['lfs_Emplyed_wrked_part_time_P'],
    'total_employed': (
        g43_sa2['lfs_Emplyed_wrked_full_time_P'] +
        g43_sa2['lfs_Emplyed_wrked_part_time_P'] +
        g43_sa2.get('lfs_Employed_away_from_work_P', 0)
    ),
    'total_population': g01_sa2['Tot_P_P']
})

df_sa2_employment['employment_density'] = (
    df_sa2_employment['total_employed'] /
    df_sa2_employment['total_population'].replace(0, np.nan)
)
df_sa2_employment['employment_density'] = df_sa2_employment['employment_density'].fillna(0)

# Calculate employment density for SA3
df_sa3_employment = pd.DataFrame({
    'SA3_CODE_2021': g43_sa3['SA3_CODE_2021'],
    'employed_full_time': g43_sa3['lfs_Emplyed_wrked_full_time_P'],
    'employed_part_time': g43_sa3['lfs_Emplyed_wrked_part_time_P'],
    'total_employed': (
        g43_sa3['lfs_Emplyed_wrked_full_time_P'] +
        g43_sa3['lfs_Emplyed_wrked_part_time_P'] +
        g43_sa3.get('lfs_Employed_away_from_work_P', 0)
    ),
    'total_population': g01_sa3['Tot_P_P']
})

df_sa3_employment['employment_density'] = (
    df_sa3_employment['total_employed'] /
    df_sa3_employment['total_population'].replace(0, np.nan)
)
df_sa3_employment['employment_density'] = df_sa3_employment['employment_density'].fillna(0)

# Identify major employment centers
sa2_employment_centers = df_sa2_employment.nlargest(100, 'total_employed')
sa3_employment_centers = df_sa3_employment.nlargest(50, 'total_employed')

print(f"\n  ✓ Identified top 100 SA2 employment centers")
print(f"  ✓ Identified top 50 SA3 employment centers")
print(f"  ✓ Average SA2 employment density: {df_sa2_employment['employment_density'].mean():.1%}")
print(f"  ✓ Average SA3 employment density: {df_sa3_employment['employment_density'].mean():.1%}")

# ============================================================================
# STEP 5: EXTRACT SA1 GEOGRAPHIC HIERARCHY
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: LINKING SA1 AREAS TO EMPLOYMENT CENTERS")
print("=" * 100)

print("\n[Loading geographic hierarchy...]")

# SA1 codes contain hierarchical geographic information
# SA1 format: First 1 digit = STE, next 3 = SA2, next 2 = SA3
# We need to extract SA2/SA3 codes from SA1 codes

def extract_sa2_from_sa1(sa1_code):
    """Extract SA2 code from SA1 code (first 9 digits)"""
    return int(str(sa1_code)[:9])

def extract_sa3_from_sa1(sa1_code):
    """Extract SA3 code from SA1 code (first 5 digits)"""
    return int(str(sa1_code)[:5])

# Add SA2 and SA3 hierarchy to transport data
df_transport['SA2_CODE'] = df_transport['SA1_CODE_2021'].apply(extract_sa2_from_sa1)
df_transport['SA3_CODE'] = df_transport['SA1_CODE_2021'].apply(extract_sa3_from_sa1)

# Merge with employment data
df_transport = df_transport.merge(
    df_sa2_employment[['SA2_CODE_2021', 'total_employed', 'employment_density']],
    left_on='SA2_CODE',
    right_on='SA2_CODE_2021',
    how='left',
    suffixes=('', '_sa2')
)

df_transport = df_transport.merge(
    df_sa3_employment[['SA3_CODE_2021', 'total_employed', 'employment_density']],
    left_on='SA3_CODE',
    right_on='SA3_CODE_2021',
    how='left',
    suffixes=('', '_sa3')
)

# Rename columns for clarity
df_transport.rename(columns={
    'total_employed': 'sa2_employment',
    'employment_density': 'sa2_employment_density',
    'total_employed_sa3': 'sa3_employment',
    'employment_density_sa3': 'sa3_employment_density'
}, inplace=True)

print(f"  ✓ Linked {len(df_transport):,} SA1 areas to SA2/SA3 employment centers")

# ============================================================================
# STEP 6: ADD HOUSING DENSITY DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: CALCULATING HOUSING DENSITY METRICS")
print("=" * 100)

print("\n[Processing dwelling structure data...]")

# Merge population data
df_transport = df_transport.merge(
    g01_sa1[['SA1_CODE_2021', 'Tot_P_P']],
    on='SA1_CODE_2021',
    how='left'
)
df_transport.rename(columns={'Tot_P_P': 'total_population'}, inplace=True)

# Merge dwelling data
dwelling_cols = ['SA1_CODE_2021']
if 'Total_Total' in g40_sa1.columns:
    dwelling_cols.append('Total_Total')
    df_transport = df_transport.merge(
        g40_sa1[dwelling_cols],
        on='SA1_CODE_2021',
        how='left'
    )
    df_transport.rename(columns={'Total_Total': 'total_dwellings'}, inplace=True)
else:
    # Sum all dwelling types if Total not available
    df_transport['total_dwellings'] = 0

# Calculate housing density metrics
df_transport['population_density_score'] = np.log1p(df_transport['total_population'])

print(f"  ✓ Added housing density data for {len(df_transport):,} SA1 areas")
print(f"  ✓ Average population per SA1: {df_transport['total_population'].mean():.0f}")

# ============================================================================
# STEP 7: BUILD TOD SCORING ALGORITHM
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: BUILDING TOD POTENTIAL SCORING ALGORITHM")
print("=" * 100)

print("\n[Calculating comprehensive TOD scores...]")

# ============================================================================
# TOD Scoring Methodology
# ============================================================================
#
# Score Components (each 0-100):
#
# 1. Car Dependency Score (40% weight)
#    - High car dependency = high opportunity for modal shift
#    - Measures current reliance on private vehicles
#
# 2. Commuter Volume Score (30% weight)
#    - High commuter volume = more people benefit from transit
#    - Uses logarithmic scale to normalize
#
# 3. Employment Proximity Score (20% weight)
#    - Proximity to major employment centers
#    - Higher SA2/SA3 employment = better TOD location
#
# 4. Current Transit Gap Score (10% weight)
#    - Low current public transit usage + high car dependency
#    - Identifies underserved areas
#
# Final TOD Score: Weighted sum of components (0-100)
# ============================================================================

# Component 1: Car Dependency Score (0-100)
df_transport['car_dependency_score'] = df_transport['car_dependency_ratio'] * 100

# Component 2: Commuter Volume Score (0-100)
# Normalize using percentile ranking
from scipy import stats
df_transport['commuter_volume_score'] = (
    stats.rankdata(df_transport['total_commuters'], method='average') /
    len(df_transport) * 100
)

# Component 3: Employment Proximity Score (0-100)
# Based on SA2 and SA3 employment density
df_transport['sa2_employment_density'] = df_transport['sa2_employment_density'].fillna(0)
df_transport['sa3_employment_density'] = df_transport['sa3_employment_density'].fillna(0)

df_transport['employment_proximity_score'] = (
    stats.rankdata(df_transport['sa2_employment_density'], method='average') /
    len(df_transport) * 50 +
    stats.rankdata(df_transport['sa3_employment_density'], method='average') /
    len(df_transport) * 50
)

# Component 4: Transit Gap Score (0-100)
# High car dependency + Low public transit usage
df_transport['transit_gap_score'] = (
    df_transport['car_dependency_ratio'] * (1 - df_transport['public_transit_ratio'])
) * 100

# ============================================================================
# FINAL TOD SCORE (Weighted Sum)
# ============================================================================

WEIGHTS = {
    'car_dependency': 0.40,
    'commuter_volume': 0.30,
    'employment_proximity': 0.20,
    'transit_gap': 0.10
}

df_transport['tod_score'] = (
    df_transport['car_dependency_score'] * WEIGHTS['car_dependency'] +
    df_transport['commuter_volume_score'] * WEIGHTS['commuter_volume'] +
    df_transport['employment_proximity_score'] * WEIGHTS['employment_proximity'] +
    df_transport['transit_gap_score'] * WEIGHTS['transit_gap']
)

print(f"\n  ✓ TOD scores calculated for all {len(df_transport):,} SA1 areas")
print(f"\n  Score Distribution:")
print(f"    - Mean TOD Score: {df_transport['tod_score'].mean():.1f}")
print(f"    - Median TOD Score: {df_transport['tod_score'].median():.1f}")
print(f"    - Std Dev: {df_transport['tod_score'].std():.1f}")
print(f"    - Min: {df_transport['tod_score'].min():.1f}")
print(f"    - Max: {df_transport['tod_score'].max():.1f}")

# ============================================================================
# STEP 8: IDENTIFY COMMUTE PAIN POINTS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: IDENTIFYING COMMUTE PAIN POINTS")
print("=" * 100)

# Define pain point criteria:
# 1. High car dependency (>75%)
# 2. High commuter volume (>500 commuters)
# 3. Low public transit usage (<10%)

pain_point_mask = (
    (df_transport['car_dependency_ratio'] > 0.75) &
    (df_transport['total_commuters'] > 500) &
    (df_transport['public_transit_ratio'] < 0.10)
)

df_pain_points = df_transport[pain_point_mask].copy()
df_pain_points = df_pain_points.sort_values('commute_pain_score', ascending=False)

print(f"\n  ✓ Identified {len(df_pain_points):,} commute pain point SA1 areas")
print(f"  ✓ These areas represent {df_pain_points['total_commuters'].sum():,} car-dependent commuters")

# ============================================================================
# STEP 9: GENERATE RESULTS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 8: GENERATING COMPREHENSIVE RESULTS")
print("=" * 100)

# Top TOD opportunities (highest scores)
top_tod_opportunities = df_transport.nlargest(1000, 'tod_score')

print("\n[1/5] Top TOD Opportunities (Top 1000 SA1 areas)...")
print(f"  ✓ Average TOD Score: {top_tod_opportunities['tod_score'].mean():.1f}")
print(f"  ✓ Average car dependency: {top_tod_opportunities['car_dependency_ratio'].mean():.1%}")
print(f"  ✓ Total commuters in top 1000: {top_tod_opportunities['total_commuters'].sum():,}")

# High car dependency areas
high_car_dependency = df_transport[df_transport['car_dependency_ratio'] > 0.9]

print("\n[2/5] High Car Dependency Areas (>90% car usage)...")
print(f"  ✓ Found {len(high_car_dependency):,} SA1 areas")
print(f"  ✓ Total car commuters: {high_car_dependency['total_car'].sum():,}")

# Good public transit areas (for comparison)
good_transit = df_transport[df_transport['public_transit_ratio'] > 0.3]

print("\n[3/5] Good Public Transit Areas (>30% transit usage)...")
print(f"  ✓ Found {len(good_transit):,} SA1 areas")
print(f"  ✓ Average transit usage: {good_transit['public_transit_ratio'].mean():.1%}")

# Active transport strongholds
active_transport_areas = df_transport[df_transport['active_transport_ratio'] > 0.2]

print("\n[4/5] Active Transport Strongholds (>20% walk/bike)...")
print(f"  ✓ Found {len(active_transport_areas):,} SA1 areas")
print(f"  ✓ Average active transport: {active_transport_areas['active_transport_ratio'].mean():.1%}")

# Multimodal opportunities (near employment centers with low transit)
multimodal_opportunities = df_transport[
    (df_transport['sa2_employment_density'] > df_transport['sa2_employment_density'].quantile(0.75)) &
    (df_transport['public_transit_ratio'] < 0.15) &
    (df_transport['total_commuters'] > 300)
]

print("\n[5/5] Multimodal Transit Opportunities...")
print(f"  ✓ Found {len(multimodal_opportunities):,} SA1 areas near employment centers")
print(f"  ✓ Potential new transit users: {multimodal_opportunities['total_commuters'].sum():,}")

# ============================================================================
# STEP 10: SAVE RESULTS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 9: SAVING RESULTS TO CSV FILES")
print("=" * 100)

# Prepare output columns
output_cols = [
    'SA1_CODE_2021', 'SA2_CODE', 'SA3_CODE',
    'total_commuters', 'total_car', 'total_public_transit', 'total_active_transport',
    'car_dependency_ratio', 'public_transit_ratio', 'active_transport_ratio',
    'total_population', 'sa2_employment', 'sa2_employment_density',
    'sa3_employment', 'sa3_employment_density',
    'car_dependency_score', 'commuter_volume_score',
    'employment_proximity_score', 'transit_gap_score',
    'tod_score', 'commute_pain_score'
]

# Save top TOD opportunities
top_tod_opportunities[output_cols].to_csv('tod_top_1000_opportunities.csv', index=False)
print("\n  ✓ Saved: tod_top_1000_opportunities.csv (1,000 records)")

# Save commute pain points
if len(df_pain_points) > 0:
    df_pain_points[output_cols].to_csv('tod_commute_pain_points.csv', index=False)
    print(f"  ✓ Saved: tod_commute_pain_points.csv ({len(df_pain_points):,} records)")

# Save high car dependency areas
high_car_dependency[output_cols].to_csv('tod_high_car_dependency.csv', index=False)
print(f"  ✓ Saved: tod_high_car_dependency.csv ({len(high_car_dependency):,} records)")

# Save multimodal opportunities
multimodal_opportunities[output_cols].to_csv('tod_multimodal_opportunities.csv', index=False)
print(f"  ✓ Saved: tod_multimodal_opportunities.csv ({len(multimodal_opportunities):,} records)")

# Save complete dataset
df_transport[output_cols].to_csv('tod_complete_sa1_analysis.csv', index=False)
print(f"  ✓ Saved: tod_complete_sa1_analysis.csv (ALL {len(df_transport):,} SA1 areas)")

# ============================================================================
# STEP 11: SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 100)
print("FINAL SUMMARY STATISTICS")
print("=" * 100)

summary_stats = {
    'Total SA1 Areas Analyzed': len(df_transport),
    'Total Commuters': df_transport['total_commuters'].sum(),
    'Total Car Commuters': df_transport['total_car'].sum(),
    'Total Public Transit Commuters': df_transport['total_public_transit'].sum(),
    'Total Active Transport Commuters': df_transport['total_active_transport'].sum(),
    'Average Car Dependency': f"{df_transport['car_dependency_ratio'].mean():.1%}",
    'Average Public Transit Usage': f"{df_transport['public_transit_ratio'].mean():.1%}",
    'Average Active Transport': f"{df_transport['active_transport_ratio'].mean():.1%}",
    'SA1 Areas with >90% Car Dependency': len(high_car_dependency),
    'SA1 Areas with >30% Transit Usage': len(good_transit),
    'Identified Commute Pain Points': len(df_pain_points),
    'Potential Transit Users in Pain Points': df_pain_points['total_commuters'].sum() if len(df_pain_points) > 0 else 0,
    'Top 100 TOD Opportunity Areas - Avg Score': f"{top_tod_opportunities.head(100)['tod_score'].mean():.1f}",
}

print("\n")
for key, value in summary_stats.items():
    print(f"  {key:.<50} {value:>20,}" if isinstance(value, int) else f"  {key:.<50} {value:>20}")

# Save summary stats
pd.DataFrame([summary_stats]).T.to_csv('tod_summary_statistics.csv', header=['Value'])
print(f"\n  ✓ Saved: tod_summary_statistics.csv")

print("\n" + "=" * 100)
print("✓ TOD ANALYSIS COMPLETE!")
print("=" * 100)

print("\n" + "=" * 100)
print("KEY INSIGHTS FOR TRANSIT INVESTMENT")
print("=" * 100)

print("\n1. HIGHEST TOD POTENTIAL AREAS (Top 10 SA1s):")
top_10 = top_tod_opportunities.head(10)
for idx, row in enumerate(top_10.itertuples(), 1):
    print(f"\n   #{idx}. SA1 {row.SA1_CODE_2021}")
    print(f"       TOD Score: {row.tod_score:.1f}/100")
    print(f"       Car Dependency: {row.car_dependency_ratio:.1%}")
    print(f"       Total Commuters: {row.total_commuters:,}")
    print(f"       Transit Usage: {row.public_transit_ratio:.1%}")
    print(f"       SA2 Employment: {row.sa2_employment:,}")

print("\n2. MODAL SPLIT ACROSS AUSTRALIA:")
total_commuters = df_transport['total_commuters'].sum()
print(f"\n   Total Commuters: {total_commuters:,}")
print(f"   Car: {df_transport['total_car'].sum()/total_commuters:.1%} ({df_transport['total_car'].sum():,})")
print(f"   Public Transit: {df_transport['total_public_transit'].sum()/total_commuters:.1%} ({df_transport['total_public_transit'].sum():,})")
print(f"   Active Transport: {df_transport['total_active_transport'].sum()/total_commuters:.1%} ({df_transport['total_active_transport'].sum():,})")

print("\n3. TRANSIT INVESTMENT OPPORTUNITY:")
potential_modal_shift = df_transport[
    (df_transport['tod_score'] > 60) &
    (df_transport['car_dependency_ratio'] > 0.7)
]
print(f"\n   Areas with TOD Score >60 and Car Dependency >70%: {len(potential_modal_shift):,}")
print(f"   Potential commuters for modal shift: {potential_modal_shift['total_car'].sum():,}")
print(f"   If 20% shift to transit: {int(potential_modal_shift['total_car'].sum() * 0.2):,} new transit users")

print("\n" + "=" * 100)
print("Analysis files saved. Ready for visualization and further analysis!")
print("=" * 100 + "\n")
