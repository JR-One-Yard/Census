#!/usr/bin/env python3
"""
🏢 WORKFORCE INDUSTRY CLUSTERING & COMMERCIAL PROPERTY DEMAND ANALYSIS
2021 Australian Census Data

This analysis identifies commercial property investment opportunities by:
1. Mapping industry concentrations across SA1/SA2 areas
2. Identifying emerging employment clusters outside traditional CBDs
3. Cross-referencing with commercial dwelling data
4. Calculating commercial property demand gaps
5. Predicting future commercial/mixed-use development needs

Compute Intensity: ⭐⭐⭐⭐ (High)
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("🏢 WORKFORCE INDUSTRY CLUSTERING & COMMERCIAL PROPERTY DEMAND ANALYSIS")
print("=" * 100)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS"
SA1_PATH = os.path.join(BASE_PATH, "SA1/AUS")
SA2_PATH = os.path.join(BASE_PATH, "SA2/AUS")
SA3_PATH = os.path.join(BASE_PATH, "SA3/AUS")
OUTPUT_DIR = "industry_clustering_analysis"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"📁 Output directory: {OUTPUT_DIR}/")
print()

# ============================================================================
# STEP 1: LOAD SA2 GEOGRAPHIC DATA
# ============================================================================

print("=" * 100)
print("STEP 1: LOADING GEOGRAPHIC AND BASELINE DATA")
print("=" * 100)

# Load basic population data (G01 has total population)
print("📊 Loading G01 - Basic population statistics...")
g01_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G01_AUST_SA2.csv"))
print(f"   ✓ Loaded {len(g01_sa2):,} SA2 areas")
print(f"   ✓ Total population: {g01_sa2['Tot_P_P'].sum():,}")

# Load medians and averages (G02)
print("📊 Loading G02 - Medians and averages...")
g02_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G02_AUST_SA2.csv"))
print(f"   ✓ Loaded median income data for {len(g02_sa2):,} SA2 areas")

print()

# ============================================================================
# STEP 2: LOAD OCCUPATION DATA - Identify Professional Workers
# ============================================================================

print("=" * 100)
print("STEP 2: LOADING OCCUPATION DATA (Professional Worker Identification)")
print("=" * 100)

# G60A: Occupation by Age and Sex (Males)
# G60B: Occupation by Age and Sex (Persons total)
print("💼 Loading G60A - Male occupation by age...")
g60a_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G60A_AUST_SA2.csv"))

print("💼 Loading G60B - Total occupation by age...")
g60b_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G60B_AUST_SA2.csv"))

# Calculate total professional workers (Managers + Professionals)
print("\n🎯 Calculating professional worker concentrations...")

# Extract Manager columns (all ages)
manager_cols_p = [col for col in g60b_sa2.columns if 'Manager' in col and col.startswith('P')]
professional_cols_p = [col for col in g60b_sa2.columns if 'Professional' in col and col.startswith('P')]
technical_cols_p = [col for col in g60b_sa2.columns if 'TechnicTrades' in col and col.startswith('P')]
clerical_cols_p = [col for col in g60b_sa2.columns if 'ClericalAdminis' in col and col.startswith('P')]

# Calculate totals
g60b_sa2['Total_Managers'] = g60b_sa2[manager_cols_p].sum(axis=1)
g60b_sa2['Total_Professionals'] = g60b_sa2[professional_cols_p].sum(axis=1)
g60b_sa2['Total_Technical_Trades'] = g60b_sa2[technical_cols_p].sum(axis=1)
g60b_sa2['Total_Clerical_Admin'] = g60b_sa2[clerical_cols_p].sum(axis=1)

# White collar workers = Managers + Professionals + Clerical
g60b_sa2['Total_White_Collar'] = (
    g60b_sa2['Total_Managers'] +
    g60b_sa2['Total_Professionals'] +
    g60b_sa2['Total_Clerical_Admin']
)

# High-value professional workers (Managers + Professionals only)
g60b_sa2['Total_High_Value_Professionals'] = (
    g60b_sa2['Total_Managers'] +
    g60b_sa2['Total_Professionals']
)

print(f"   ✓ Total Managers across all SA2s: {g60b_sa2['Total_Managers'].sum():,}")
print(f"   ✓ Total Professionals across all SA2s: {g60b_sa2['Total_Professionals'].sum():,}")
print(f"   ✓ Total White Collar Workers: {g60b_sa2['Total_White_Collar'].sum():,}")
print(f"   ✓ Total High-Value Professionals: {g60b_sa2['Total_High_Value_Professionals'].sum():,}")

print()

# ============================================================================
# STEP 3: LOAD INDUSTRY DATA - Where people work
# ============================================================================

print("=" * 100)
print("STEP 3: LOADING INDUSTRY OF EMPLOYMENT DATA")
print("=" * 100)

# G54A: Industry of Employment by Age (Males)
# Contains: Agriculture, Mining, Manufacturing, Construction, Retail, Finance, etc.
print("🏭 Loading G54A - Industry of employment by age (Males)...")
g54a_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G54A_AUST_SA2.csv"))

# Get column names to identify industries
industry_age_cols = g54a_sa2.columns.tolist()

# Industry categories (extracted from column names)
# M_Ag_For_Fshg, M_Min, M_Manufact, M_Elec_Gas_Wtr_Waste, M_Constru,
# M_WhlesaleTde, M_RetailTrade, M_Accom_food, M_Trans_post_wrehsg,
# M_Info_media_teleco, M_Fin_Insurance, M_RtnHir_REstate, M_Pro_scien_tec_s,
# M_Admin_supp, M_Public_admin_sfty, M_Educ_training, M_HlthCare_SocAsst,
# M_Art_recn, M_Oth_scs, M_ID_NS

print("   ✓ Analyzing industry categories...")

# Define key professional/office-based industries
professional_industries = {
    'Finance_Insurance': 'Fin_Insurance',
    'Professional_Scientific_Technical': 'Pro_scien_tec_s',
    'Info_Media_Telecom': 'Info_media_teleco',
    'Public_Admin': 'Public_admin_sfty',
    'Rental_Real_Estate': 'RtnHir_REstate',
}

# Calculate workers in professional industries
for industry_name, col_prefix in professional_industries.items():
    # Find columns matching this industry
    matching_cols = [col for col in g54a_sa2.columns if col_prefix in col and col.startswith('M_')]

    if matching_cols:
        g54a_sa2[f'Workers_{industry_name}'] = g54a_sa2[matching_cols].sum(axis=1)
        print(f"   ✓ {industry_name}: {g54a_sa2[f'Workers_{industry_name}'].sum():,} workers")

# Calculate total professional industry workers
# Get existing Workers_ columns that were actually created
workers_columns = [col for col in g54a_sa2.columns if col.startswith('Workers_')]
if workers_columns:
    g54a_sa2['Total_Professional_Industry_Workers'] = g54a_sa2[workers_columns].sum(axis=1)
    print(f"\n   ✓ Total Professional Industry Workers: {g54a_sa2['Total_Professional_Industry_Workers'].sum():,}")
else:
    g54a_sa2['Total_Professional_Industry_Workers'] = 0
    print(f"\n   ⚠ No professional industry columns found, using 0")

# Also load G54B for female workers
print("\n🏭 Loading G54B - Industry of employment by age (Females)...")
g54b_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G54B_AUST_SA2.csv"))

for industry_name, col_prefix in professional_industries.items():
    matching_cols = [col for col in g54b_sa2.columns if col_prefix in col and col.startswith('F_')]
    if matching_cols:
        g54b_sa2[f'Workers_{industry_name}'] = g54b_sa2[matching_cols].sum(axis=1)

# Get existing Workers_ columns that were actually created for females
workers_columns_f = [col for col in g54b_sa2.columns if col.startswith('Workers_')]
if workers_columns_f:
    g54b_sa2['Total_Professional_Industry_Workers'] = g54b_sa2[workers_columns_f].sum(axis=1)
    print(f"   ✓ Female Professional Industry Workers: {g54b_sa2['Total_Professional_Industry_Workers'].sum():,}")
else:
    g54b_sa2['Total_Professional_Industry_Workers'] = 0
    print(f"   ⚠ No professional industry columns found for females, using 0")

print()

# ============================================================================
# STEP 4: LOAD DWELLING DATA - Commercial Property Stock
# ============================================================================

print("=" * 100)
print("STEP 4: LOADING DWELLING TYPE DATA (Commercial Property Stock)")
print("=" * 100)

# G37: Dwelling Structure by Tenure
# Contains: Separate house, Semi-detached, Flat/apartment, Other dwelling
print("🏘️  Loading G37 - Dwelling structure by tenure...")
g37_sa2 = pd.read_csv(os.path.join(SA2_PATH, "2021Census_G37_AUST_SA2.csv"))

# Column patterns: O_OR_DS_Sep_house, O_OR_DS_SemiD_ro_or_tce_h_th, O_OR_DS_Flat_apart, O_OR_DS_Oth_dwell

# Calculate dwelling types
flat_cols = [col for col in g37_sa2.columns if 'Flat' in col or 'apart' in col]
separate_house_cols = [col for col in g37_sa2.columns if 'Sep_house' in col]
other_dwelling_cols = [col for col in g37_sa2.columns if 'Oth_dwell' in col]

g37_sa2['Total_Flats_Apartments'] = g37_sa2[flat_cols].sum(axis=1) if flat_cols else 0
g37_sa2['Total_Separate_Houses'] = g37_sa2[separate_house_cols].sum(axis=1) if separate_house_cols else 0
g37_sa2['Total_Other_Dwellings'] = g37_sa2[other_dwelling_cols].sum(axis=1) if other_dwelling_cols else 0

# Proxy for commercial density: High apartment/flat density often indicates mixed-use areas
print(f"   ✓ Total Flats/Apartments: {g37_sa2['Total_Flats_Apartments'].sum():,}")
print(f"   ✓ Total Separate Houses: {g37_sa2['Total_Separate_Houses'].sum():,}")
print(f"   ✓ Total Other Dwellings: {g37_sa2['Total_Other_Dwellings'].sum():,}")

# Calculate commercial density proxy
# High apartments + other dwellings = likely mixed-use/commercial areas
g37_sa2['Commercial_Density_Proxy'] = (
    g37_sa2['Total_Flats_Apartments'] * 0.7 +  # Apartments often in commercial areas
    g37_sa2['Total_Other_Dwellings'] * 0.3     # Other dwellings may include commercial
)

print()

# ============================================================================
# STEP 5: MERGE ALL DATA AND CALCULATE METRICS
# ============================================================================

print("=" * 100)
print("STEP 5: MERGING DATA AND CALCULATING COMMERCIAL DEMAND METRICS")
print("=" * 100)

# Merge all datasets on SA2_CODE_2021
print("🔗 Merging datasets...")
analysis_df = g01_sa2[['SA2_CODE_2021', 'Tot_P_P']].copy()
analysis_df.columns = ['SA2_CODE', 'Total_Population']

# Merge G02 (medians)
analysis_df = analysis_df.merge(
    g02_sa2[['SA2_CODE_2021', 'Median_tot_prsnl_inc_weekly', 'Median_age_persons']],
    left_on='SA2_CODE', right_on='SA2_CODE_2021', how='left'
).drop('SA2_CODE_2021', axis=1)

# Merge G60B (occupation)
occupation_cols = ['SA2_CODE_2021', 'Total_Managers', 'Total_Professionals',
                   'Total_White_Collar', 'Total_High_Value_Professionals']
analysis_df = analysis_df.merge(
    g60b_sa2[occupation_cols],
    left_on='SA2_CODE', right_on='SA2_CODE_2021', how='left'
).drop('SA2_CODE_2021', axis=1)

# Merge G54A (male industry workers)
g54a_industry = g54a_sa2[['SA2_CODE_2021', 'Total_Professional_Industry_Workers']].copy()
g54a_industry.columns = ['SA2_CODE', 'Male_Professional_Industry_Workers']

analysis_df = analysis_df.merge(g54a_industry, on='SA2_CODE', how='left')

# Merge G54B (female industry workers)
g54b_industry = g54b_sa2[['SA2_CODE_2021', 'Total_Professional_Industry_Workers']].copy()
g54b_industry.columns = ['SA2_CODE', 'Female_Professional_Industry_Workers']

analysis_df = analysis_df.merge(g54b_industry, on='SA2_CODE', how='left')

# Merge G37 (dwelling types)
dwelling_cols = ['SA2_CODE_2021', 'Total_Flats_Apartments', 'Total_Separate_Houses',
                 'Total_Other_Dwellings', 'Commercial_Density_Proxy']
analysis_df = analysis_df.merge(
    g37_sa2[dwelling_cols],
    left_on='SA2_CODE', right_on='SA2_CODE_2021', how='left'
).drop('SA2_CODE_2021', axis=1)

# Fill NaN values with 0
analysis_df = analysis_df.fillna(0)

print(f"   ✓ Merged data for {len(analysis_df):,} SA2 areas")

# Calculate combined metrics
print("\n📈 Calculating commercial demand metrics...")

# Total professional industry workers (combined male + female)
analysis_df['Total_Professional_Industry_Workers'] = (
    analysis_df['Male_Professional_Industry_Workers'] +
    analysis_df['Female_Professional_Industry_Workers']
)

# Professional worker density (per 1000 population)
analysis_df['Professional_Density_per_1000'] = (
    analysis_df['Total_High_Value_Professionals'] / (analysis_df['Total_Population'] + 1) * 1000
)

# White collar density
analysis_df['White_Collar_Density_per_1000'] = (
    analysis_df['Total_White_Collar'] / (analysis_df['Total_Population'] + 1) * 1000
)

# Professional industry concentration
analysis_df['Professional_Industry_Concentration'] = (
    analysis_df['Total_Professional_Industry_Workers'] / (analysis_df['Total_Population'] + 1) * 1000
)

# Commercial stock per capita (apartments + other dwellings as proxy)
total_dwellings = (analysis_df['Total_Flats_Apartments'] +
                  analysis_df['Total_Separate_Houses'] +
                  analysis_df['Total_Other_Dwellings'])

analysis_df['Commercial_Stock_Ratio'] = (
    analysis_df['Commercial_Density_Proxy'] / (total_dwellings + 1)
)

# ============================================================================
# STEP 6: CALCULATE COMMERCIAL PROPERTY DEMAND GAP
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: CALCULATING COMMERCIAL PROPERTY DEMAND GAPS")
print("=" * 100)

# Normalize scores (0-100 scale)
def normalize_score(series, higher_is_better=True):
    """Normalize series to 0-100 scale"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)

    if higher_is_better:
        return ((series - min_val) / (max_val - min_val)) * 100
    else:
        return ((max_val - series) / (max_val - min_val)) * 100

print("📊 Normalizing metrics to 0-100 scale...")

# High professional workers = HIGH DEMAND (higher is better)
analysis_df['Score_Professional_Demand'] = normalize_score(
    analysis_df['Total_High_Value_Professionals'], higher_is_better=True
)

# High professional density = HIGH DEMAND (higher is better)
analysis_df['Score_Professional_Density'] = normalize_score(
    analysis_df['Professional_Density_per_1000'], higher_is_better=True
)

# High professional industry concentration = HIGH DEMAND (higher is better)
analysis_df['Score_Industry_Concentration'] = normalize_score(
    analysis_df['Professional_Industry_Concentration'], higher_is_better=True
)

# Low commercial stock = OPPORTUNITY (lower is better, so invert)
analysis_df['Score_Commercial_Deficit'] = normalize_score(
    analysis_df['Commercial_Density_Proxy'], higher_is_better=False
)

# High income = BETTER MARKET (higher is better)
analysis_df['Score_Income'] = normalize_score(
    analysis_df['Median_tot_prsnl_inc_weekly'], higher_is_better=True
)

# Calculate COMPOSITE OPPORTUNITY SCORE
# Weight factors:
# - Professional demand: 30%
# - Professional density: 25%
# - Industry concentration: 20%
# - Commercial deficit: 15%
# - Income: 10%

print("\n🎯 Calculating composite opportunity scores...")

analysis_df['Commercial_Opportunity_Score'] = (
    analysis_df['Score_Professional_Demand'] * 0.30 +
    analysis_df['Score_Professional_Density'] * 0.25 +
    analysis_df['Score_Industry_Concentration'] * 0.20 +
    analysis_df['Score_Commercial_Deficit'] * 0.15 +
    analysis_df['Score_Income'] * 0.10
)

# Calculate DEMAND GAP INDEX
# High professionals + Low commercial stock = High demand gap
analysis_df['Demand_Gap_Index'] = (
    (analysis_df['Score_Professional_Demand'] + analysis_df['Score_Professional_Density']) / 2 *
    analysis_df['Score_Commercial_Deficit'] / 100
)

print("   ✓ Calculated Commercial Opportunity Score (weighted composite)")
print("   ✓ Calculated Demand Gap Index (professionals × commercial deficit)")

# ============================================================================
# STEP 7: IDENTIFY EMPLOYMENT CLUSTERS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: IDENTIFYING EMPLOYMENT CLUSTERS")
print("=" * 100)

# Employment cluster = high concentration of professional workers relative to population

# Define cluster thresholds
CLUSTER_THRESHOLD_PROFESSIONALS = analysis_df['Total_High_Value_Professionals'].quantile(0.75)  # Top 25%
CLUSTER_THRESHOLD_DENSITY = analysis_df['Professional_Density_per_1000'].quantile(0.75)  # Top 25%

print(f"🎯 Cluster identification thresholds:")
print(f"   • High-value professionals: {CLUSTER_THRESHOLD_PROFESSIONALS:,.0f}+ workers")
print(f"   • Professional density: {CLUSTER_THRESHOLD_DENSITY:.1f}+ per 1,000 population")

# Identify clusters
analysis_df['Is_Employment_Cluster'] = (
    (analysis_df['Total_High_Value_Professionals'] >= CLUSTER_THRESHOLD_PROFESSIONALS) &
    (analysis_df['Professional_Density_per_1000'] >= CLUSTER_THRESHOLD_DENSITY)
)

# Identify emerging clusters (high growth potential)
# = High professionals + Low commercial stock + High income
analysis_df['Is_Emerging_Cluster'] = (
    (analysis_df['Total_High_Value_Professionals'] >= analysis_df['Total_High_Value_Professionals'].quantile(0.60)) &
    (analysis_df['Score_Commercial_Deficit'] >= 60) &  # Low commercial stock
    (analysis_df['Score_Income'] >= 50)  # Above median income
)

num_clusters = analysis_df['Is_Employment_Cluster'].sum()
num_emerging = analysis_df['Is_Emerging_Cluster'].sum()

print(f"\n   ✓ Identified {num_clusters} established employment clusters")
print(f"   ✓ Identified {num_emerging} emerging employment clusters")

# ============================================================================
# STEP 8: GENERATE OUTPUT RANKINGS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 8: GENERATING OUTPUT FILES")
print("=" * 100)

# Filter out areas with very low population (< 100)
analysis_df_filtered = analysis_df[analysis_df['Total_Population'] >= 100].copy()

print(f"📊 Filtered to {len(analysis_df_filtered):,} SA2 areas (population >= 100)")

# TOP COMMERCIAL PROPERTY OPPORTUNITIES (by Opportunity Score)
print("\n💰 Generating top commercial property opportunities...")
top_opportunities = analysis_df_filtered.nlargest(500, 'Commercial_Opportunity_Score')[[
    'SA2_CODE',
    'Total_Population',
    'Total_High_Value_Professionals',
    'Professional_Density_per_1000',
    'Total_Professional_Industry_Workers',
    'Professional_Industry_Concentration',
    'Commercial_Density_Proxy',
    'Median_tot_prsnl_inc_weekly',
    'Commercial_Opportunity_Score',
    'Demand_Gap_Index',
    'Is_Employment_Cluster',
    'Is_Emerging_Cluster'
]].copy()

top_opportunities.columns = [
    'SA2_Code',
    'Population',
    'High_Value_Professionals',
    'Professional_Density_per_1000',
    'Professional_Industry_Workers',
    'Professional_Industry_Concentration',
    'Commercial_Density_Proxy',
    'Median_Weekly_Income',
    'Opportunity_Score',
    'Demand_Gap_Index',
    'Is_Established_Cluster',
    'Is_Emerging_Cluster'
]

# Round numeric columns
numeric_cols = top_opportunities.select_dtypes(include=[np.number]).columns
top_opportunities[numeric_cols] = top_opportunities[numeric_cols].round(2)

output_file_opportunities = os.path.join(OUTPUT_DIR, 'top_500_commercial_property_opportunities.csv')
top_opportunities.to_csv(output_file_opportunities, index=False)
print(f"   ✓ Saved: {output_file_opportunities}")

# TOP DEMAND GAP AREAS (High professionals + Low commercial stock)
print("\n🎯 Generating top demand gap areas...")
top_demand_gaps = analysis_df_filtered.nlargest(500, 'Demand_Gap_Index')[[
    'SA2_CODE',
    'Total_Population',
    'Total_High_Value_Professionals',
    'Professional_Density_per_1000',
    'Commercial_Density_Proxy',
    'Median_tot_prsnl_inc_weekly',
    'Demand_Gap_Index',
    'Commercial_Opportunity_Score',
    'Is_Employment_Cluster',
    'Is_Emerging_Cluster'
]].copy()

top_demand_gaps.columns = [
    'SA2_Code',
    'Population',
    'High_Value_Professionals',
    'Professional_Density_per_1000',
    'Commercial_Density_Proxy',
    'Median_Weekly_Income',
    'Demand_Gap_Index',
    'Opportunity_Score',
    'Is_Established_Cluster',
    'Is_Emerging_Cluster'
]

numeric_cols = top_demand_gaps.select_dtypes(include=[np.number]).columns
top_demand_gaps[numeric_cols] = top_demand_gaps[numeric_cols].round(2)

output_file_gaps = os.path.join(OUTPUT_DIR, 'top_500_commercial_demand_gaps.csv')
top_demand_gaps.to_csv(output_file_gaps, index=False)
print(f"   ✓ Saved: {output_file_gaps}")

# EMPLOYMENT CLUSTERS
print("\n🏢 Generating employment clusters...")
employment_clusters = analysis_df_filtered[analysis_df_filtered['Is_Employment_Cluster']][[
    'SA2_CODE',
    'Total_Population',
    'Total_High_Value_Professionals',
    'Total_Managers',
    'Total_Professionals',
    'Professional_Density_per_1000',
    'Total_Professional_Industry_Workers',
    'Commercial_Density_Proxy',
    'Median_tot_prsnl_inc_weekly',
    'Commercial_Opportunity_Score',
    'Demand_Gap_Index'
]].copy()

employment_clusters = employment_clusters.sort_values('Total_High_Value_Professionals', ascending=False)

employment_clusters.columns = [
    'SA2_Code',
    'Population',
    'High_Value_Professionals',
    'Managers',
    'Professionals',
    'Professional_Density_per_1000',
    'Professional_Industry_Workers',
    'Commercial_Density_Proxy',
    'Median_Weekly_Income',
    'Opportunity_Score',
    'Demand_Gap_Index'
]

numeric_cols = employment_clusters.select_dtypes(include=[np.number]).columns
employment_clusters[numeric_cols] = employment_clusters[numeric_cols].round(2)

output_file_clusters = os.path.join(OUTPUT_DIR, 'employment_clusters_all.csv')
employment_clusters.to_csv(output_file_clusters, index=False)
print(f"   ✓ Saved: {output_file_clusters} ({len(employment_clusters)} clusters)")

# EMERGING CLUSTERS
print("\n🌱 Generating emerging clusters...")
emerging_clusters = analysis_df_filtered[analysis_df_filtered['Is_Emerging_Cluster']][[
    'SA2_CODE',
    'Total_Population',
    'Total_High_Value_Professionals',
    'Professional_Density_per_1000',
    'Total_Professional_Industry_Workers',
    'Commercial_Density_Proxy',
    'Median_tot_prsnl_inc_weekly',
    'Commercial_Opportunity_Score',
    'Demand_Gap_Index'
]].copy()

emerging_clusters = emerging_clusters.sort_values('Commercial_Opportunity_Score', ascending=False)

emerging_clusters.columns = [
    'SA2_Code',
    'Population',
    'High_Value_Professionals',
    'Professional_Density_per_1000',
    'Professional_Industry_Workers',
    'Commercial_Density_Proxy',
    'Median_Weekly_Income',
    'Opportunity_Score',
    'Demand_Gap_Index'
]

numeric_cols = emerging_clusters.select_dtypes(include=[np.number]).columns
emerging_clusters[numeric_cols] = emerging_clusters[numeric_cols].round(2)

output_file_emerging = os.path.join(OUTPUT_DIR, 'emerging_employment_clusters.csv')
emerging_clusters.to_csv(output_file_emerging, index=False)
print(f"   ✓ Saved: {output_file_emerging} ({len(emerging_clusters)} emerging clusters)")

# FULL DATASET
print("\n💾 Saving complete analysis dataset...")
output_file_full = os.path.join(OUTPUT_DIR, 'full_commercial_property_analysis.csv')

# Select key columns for full export
full_export = analysis_df_filtered[[
    'SA2_CODE',
    'Total_Population',
    'Median_age_persons',
    'Median_tot_prsnl_inc_weekly',
    'Total_Managers',
    'Total_Professionals',
    'Total_White_Collar',
    'Total_High_Value_Professionals',
    'Professional_Density_per_1000',
    'Total_Professional_Industry_Workers',
    'Professional_Industry_Concentration',
    'Total_Flats_Apartments',
    'Total_Separate_Houses',
    'Commercial_Density_Proxy',
    'Commercial_Stock_Ratio',
    'Commercial_Opportunity_Score',
    'Demand_Gap_Index',
    'Is_Employment_Cluster',
    'Is_Emerging_Cluster',
    'Score_Professional_Demand',
    'Score_Professional_Density',
    'Score_Industry_Concentration',
    'Score_Commercial_Deficit',
    'Score_Income'
]].copy()

# Round numeric columns
numeric_cols = full_export.select_dtypes(include=[np.number]).columns
full_export[numeric_cols] = full_export[numeric_cols].round(2)

full_export.to_csv(output_file_full, index=False)
print(f"   ✓ Saved: {output_file_full} ({len(full_export)} SA2 areas)")

# ============================================================================
# STEP 9: GENERATE SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 9: GENERATING SUMMARY STATISTICS & INSIGHTS")
print("=" * 100)

summary_stats = {
    'Total_SA2_Areas_Analyzed': len(analysis_df_filtered),
    'Total_Population': int(analysis_df_filtered['Total_Population'].sum()),
    'Total_High_Value_Professionals': int(analysis_df_filtered['Total_High_Value_Professionals'].sum()),
    'Total_Managers': int(analysis_df_filtered['Total_Managers'].sum()),
    'Total_Professionals': int(analysis_df_filtered['Total_Professionals'].sum()),
    'Total_White_Collar_Workers': int(analysis_df_filtered['Total_White_Collar'].sum()),
    'Total_Professional_Industry_Workers': int(analysis_df_filtered['Total_Professional_Industry_Workers'].sum()),
    'Number_of_Employment_Clusters': int(num_clusters),
    'Number_of_Emerging_Clusters': int(num_emerging),
    'Average_Professional_Density_per_1000': float(analysis_df_filtered['Professional_Density_per_1000'].mean()),
    'Median_Opportunity_Score': float(analysis_df_filtered['Commercial_Opportunity_Score'].median()),
    'Highest_Opportunity_Score': float(analysis_df_filtered['Commercial_Opportunity_Score'].max()),
    'Average_Demand_Gap_Index': float(analysis_df_filtered['Demand_Gap_Index'].mean()),
}

# Save summary statistics
summary_df = pd.DataFrame([summary_stats]).T
summary_df.columns = ['Value']
output_file_summary = os.path.join(OUTPUT_DIR, 'analysis_summary_statistics.csv')
summary_df.to_csv(output_file_summary)
print(f"\n   ✓ Saved: {output_file_summary}")

# Print summary
print("\n📊 ANALYSIS SUMMARY:")
print("=" * 100)
for key, value in summary_stats.items():
    if isinstance(value, float):
        print(f"   {key.replace('_', ' ')}: {value:,.2f}")
    else:
        print(f"   {key.replace('_', ' ')}: {value:,}")

# ============================================================================
# FINAL OUTPUT
# ============================================================================

print("\n" + "=" * 100)
print("✅ ANALYSIS COMPLETE!")
print("=" * 100)
print(f"\n📁 All outputs saved to: {OUTPUT_DIR}/")
print("\n📄 Generated Files:")
print(f"   1. top_500_commercial_property_opportunities.csv")
print(f"   2. top_500_commercial_demand_gaps.csv")
print(f"   3. employment_clusters_all.csv")
print(f"   4. emerging_employment_clusters.csv")
print(f"   5. full_commercial_property_analysis.csv")
print(f"   6. analysis_summary_statistics.csv")
print("\n" + "=" * 100)
