#!/usr/bin/env python3
"""
Analysis: Migration Patterns and Economic Outcomes
===================================================

This script analyzes the relationship between country of birth concentrations
in suburbs and economic indicators (income, education, employment).

IMPORTANT CAVEATS:
- Correlation does not imply causation
- Aggregate data doesn't predict individual outcomes
- Many confounding factors affect economic outcomes
- Historical migration patterns and policy affect current distributions
- This analysis is for policy research purposes only

Methodology:
1. Extract country of birth data for all suburbs (from G09 tables)
2. Extract economic indicators: income, education levels (from G02, G49)
3. Calculate concentration of each nationality in each suburb
4. Correlate nationality concentrations with economic outcomes
5. Rank countries by correlation strength

Data Sources:
- G09A-H: Country of birth by age and sex
- G02: Median income and age
- G49A-B: Highest educational qualifications
- G40: Employment status
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Data paths
DATA_DIR = Path("/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/")
SUBURB_MAPPING = Path("/home/user/Census/SAL_Suburb_Name_Mapping.csv")

print("=" * 80)
print("MIGRATION PATTERNS AND ECONOMIC OUTCOMES ANALYSIS")
print("2021 Australian Census Data")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load Economic Indicators
# ============================================================================
print("STEP 1: Loading economic indicators...")

# Load median income and age data (G02)
g02 = pd.read_csv(DATA_DIR / "2021Census_G02_AUST_SAL.csv")
print(f"  ✓ Loaded income/age data for {len(g02):,} suburbs")

# Load education data (G49A - Males, G49B - Females/Persons)
g49a = pd.read_csv(DATA_DIR / "2021Census_G49A_AUST_SAL.csv")
g49b = pd.read_csv(DATA_DIR / "2021Census_G49B_AUST_SAL.csv")
print(f"  ✓ Loaded education data")

# Load employment data (G43 - Labour Force Status)
g43 = pd.read_csv(DATA_DIR / "2021Census_G43_AUST_SAL.csv")
print(f"  ✓ Loaded employment data")

# Load total population (G01)
g01 = pd.read_csv(DATA_DIR / "2021Census_G01_AUST_SAL.csv")
print(f"  ✓ Loaded population data")

# Load suburb names
suburb_names = pd.read_csv(SUBURB_MAPPING)
print(f"  ✓ Loaded suburb name mapping")
print()

# ============================================================================
# STEP 2: Calculate Education Levels per Suburb
# ============================================================================
print("STEP 2: Calculating education metrics...")

# Calculate tertiary education (Bachelor degree or higher)
bachelor_cols = [col for col in g49a.columns if 'BachDeg' in col]
postgrad_cols = [col for col in g49a.columns if 'PGrad_Deg' in col]
graddip_cols = [col for col in g49a.columns if 'GradDip_and_GradCert' in col]

g49a['Tertiary_Males'] = (
    g49a[bachelor_cols].sum(axis=1) +
    g49a[postgrad_cols].sum(axis=1) +
    g49a[graddip_cols].sum(axis=1)
)

# Same for females (in G49B)
bachelor_cols_f = [col for col in g49b.columns if 'BachDeg' in col and col.startswith('F_')]
postgrad_cols_f = [col for col in g49b.columns if 'PGrad_Deg' in col and col.startswith('F_')]
graddip_cols_f = [col for col in g49b.columns if 'GradDip_and_GradCert' in col and col.startswith('F_')]

g49b['Tertiary_Females'] = (
    g49b[bachelor_cols_f].sum(axis=1) +
    g49b[postgrad_cols_f].sum(axis=1) +
    g49b[graddip_cols_f].sum(axis=1)
)

# Merge education data
education = g49a[['SAL_CODE_2021', 'Tertiary_Males']].merge(
    g49b[['SAL_CODE_2021', 'Tertiary_Females']], on='SAL_CODE_2021'
)
education['Tertiary_Total'] = education['Tertiary_Males'] + education['Tertiary_Females']

print(f"  ✓ Calculated tertiary education rates for {len(education):,} suburbs")
print()

# ============================================================================
# STEP 3: Load Country of Birth Data
# ============================================================================
print("STEP 3: Loading country of birth data from G09 tables...")

# G09 tables are split into multiple files (A-H)
# Each contains different countries
g09_files = ['G09A', 'G09B', 'G09C', 'G09D', 'G09E', 'G09F', 'G09G', 'G09H']

# Extract all countries from each table
all_countries = set()
country_data = {}

for file_code in g09_files:
    filepath = DATA_DIR / f"2021Census_{file_code}_AUST_SAL.csv"
    df = pd.read_csv(filepath)

    # Find all country columns (those ending in _Tot for totals)
    # Format: M_CountryName_Tot, F_CountryName_Tot, P_CountryName_Tot
    country_cols = [col for col in df.columns if col.endswith('_Tot')]

    # Extract unique country names
    for col in country_cols:
        # Remove prefix (M_, F_, P_) and suffix (_Tot)
        if col.startswith('M_') or col.startswith('F_') or col.startswith('P_'):
            country = col[2:-4]  # Remove "M_" and "_Tot"
            if country not in ['COB_NS', 'Tot', 'Elsewhere']:
                all_countries.add(country)

                # Store Person totals (P_CountryName_Tot)
                p_col = f'P_{country}_Tot'
                if p_col in df.columns:
                    if country not in country_data:
                        country_data[country] = df[['SAL_CODE_2021', p_col]].copy()
                        country_data[country].rename(columns={p_col: 'Population'}, inplace=True)

print(f"  ✓ Found {len(all_countries)} countries in census data")
print(f"  ✓ Loaded birth country data for {len(country_data)} countries")
print()

# ============================================================================
# STEP 4: Create Master Dataset
# ============================================================================
print("STEP 4: Creating master dataset...")

# Start with G02 (income/age data)
master = g02[['SAL_CODE_2021', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly',
              'Median_tot_hhd_inc_weekly']].copy()

# Add total population
master = master.merge(g01[['SAL_CODE_2021', 'Tot_P_P']], on='SAL_CODE_2021', how='left')
master.rename(columns={'Tot_P_P': 'Total_Population'}, inplace=True)

# Add education data
master = master.merge(education[['SAL_CODE_2021', 'Tertiary_Total']], on='SAL_CODE_2021', how='left')

# Add employment rate (G43 - Labour Force Status)
# Calculate total employed (full-time + part-time + away from work)
if 'lfs_Emplyed_wrked_full_time_P' in g43.columns:
    g43['Total_Employed'] = (
        g43['lfs_Emplyed_wrked_full_time_P'] +
        g43['lfs_Emplyed_wrked_part_time_P'] +
        g43['lfs_Employed_away_from_work_P']
    )
    g43['Employment_Rate'] = (g43['Total_Employed'] / g43['P_15_yrs_over_P'] * 100)
    master = master.merge(g43[['SAL_CODE_2021', 'Employment_Rate']], on='SAL_CODE_2021', how='left')

# Add suburb names
master = master.merge(suburb_names[['SAL_CODE', 'Suburb_Name']],
                      left_on='SAL_CODE_2021', right_on='SAL_CODE', how='left')

# Calculate tertiary education rate
master['Tertiary_Rate'] = (master['Tertiary_Total'] / master['Total_Population'] * 100)

# Filter out very small suburbs (less than 100 people) to reduce noise
master = master[master['Total_Population'] >= 100].copy()

print(f"  ✓ Master dataset created with {len(master):,} suburbs")
print(f"  ✓ Suburbs with >100 population")
print()

# ============================================================================
# STEP 5: Calculate Country Concentrations and Correlations
# ============================================================================
print("STEP 5: Calculating country concentrations and economic correlations...")
print()

results = []

for country in sorted(country_data.keys()):
    # Merge country data with master dataset
    temp = master.merge(country_data[country], on='SAL_CODE_2021', how='left')
    temp['Population'] = temp['Population'].fillna(0)

    # Calculate concentration (% of suburb population)
    temp['Concentration'] = (temp['Population'] / temp['Total_Population'] * 100)

    # Filter to suburbs where this country has meaningful presence (>0.5%)
    meaningful = temp[temp['Concentration'] > 0.5].copy()

    if len(meaningful) < 10:  # Need at least 10 suburbs for meaningful correlation
        continue

    # Calculate correlations with economic indicators
    # (Only for suburbs where this nationality is present)
    corr_income = meaningful[['Concentration', 'Median_tot_prsnl_inc_weekly']].corr().iloc[0, 1]
    corr_education = meaningful[['Concentration', 'Tertiary_Rate']].corr().iloc[0, 1]
    corr_employment = meaningful[['Concentration', 'Employment_Rate']].corr().iloc[0, 1] if 'Employment_Rate' in meaningful.columns else np.nan

    # Calculate mean values for suburbs where this group is concentrated (>5%)
    high_concentration = temp[temp['Concentration'] > 5].copy()

    if len(high_concentration) > 0:
        avg_income = high_concentration['Median_tot_prsnl_inc_weekly'].median()
        avg_tertiary = high_concentration['Tertiary_Rate'].median()
        avg_employment = high_concentration['Employment_Rate'].median() if 'Employment_Rate' in high_concentration.columns else np.nan
        total_population = high_concentration['Population'].sum()
        num_suburbs = len(high_concentration)
    else:
        avg_income = np.nan
        avg_tertiary = np.nan
        avg_employment = np.nan
        total_population = 0
        num_suburbs = 0

    results.append({
        'Country': country,
        'Total_Population': country_data[country]['Population'].sum(),
        'Num_Suburbs_Present': len(meaningful),
        'Num_Suburbs_Concentrated': num_suburbs,
        'Median_Income_in_Concentration_Areas': avg_income,
        'Median_Tertiary_Rate_in_Concentration_Areas': avg_tertiary,
        'Median_Employment_Rate_in_Concentration_Areas': avg_employment,
        'Correlation_Income': corr_income,
        'Correlation_Education': corr_education,
        'Correlation_Employment': corr_employment,
    })

# Create results dataframe
results_df = pd.DataFrame(results)

# Create a composite score (normalized weighted average of correlations)
# Only include countries with at least 10,000 population for robust statistics
results_df = results_df[results_df['Total_Population'] >= 10000].copy()

# Normalize correlations to 0-100 scale
results_df['Income_Score'] = ((results_df['Correlation_Income'] + 1) / 2 * 100)
results_df['Education_Score'] = ((results_df['Correlation_Education'] + 1) / 2 * 100)
results_df['Employment_Score'] = ((results_df['Correlation_Employment'] + 1) / 2 * 100)

# Composite score (weighted average)
results_df['Composite_Score'] = (
    results_df['Income_Score'] * 0.4 +
    results_df['Education_Score'] * 0.4 +
    results_df['Employment_Score'] * 0.2
)

# Sort by composite score
results_df = results_df.sort_values('Composite_Score', ascending=False)

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()

# ============================================================================
# RESULTS: Top 10 Countries
# ============================================================================
print("TOP 10 COUNTRIES BY ECONOMIC INDICATORS")
print("(Countries with migrants in economically successful suburbs)")
print("-" * 80)
print()

top_10 = results_df.head(10)
for idx, row in top_10.iterrows():
    print(f"{row['Country'].replace('_', ' ')}")
    print(f"  Population in Australia: {row['Total_Population']:,.0f}")
    print(f"  Median Income in Concentration Areas: ${row['Median_Income_in_Concentration_Areas']:,.0f}/week")
    print(f"  Median Tertiary Education Rate: {row['Median_Tertiary_Rate_in_Concentration_Areas']:.1f}%")
    print(f"  Median Employment Rate: {row['Median_Employment_Rate_in_Concentration_Areas']:.1f}%")
    print(f"  Composite Economic Score: {row['Composite_Score']:.1f}/100")
    print()

# ============================================================================
# RESULTS: Bottom 10 Countries
# ============================================================================
print()
print("=" * 80)
print("BOTTOM 10 COUNTRIES BY ECONOMIC INDICATORS")
print("(Countries with migrants in economically challenged suburbs)")
print("-" * 80)
print()

bottom_10 = results_df.tail(10)
for idx, row in bottom_10.iterrows():
    print(f"{row['Country'].replace('_', ' ')}")
    print(f"  Population in Australia: {row['Total_Population']:,.0f}")
    print(f"  Median Income in Concentration Areas: ${row['Median_Income_in_Concentration_Areas']:,.0f}/week")
    print(f"  Median Tertiary Education Rate: {row['Median_Tertiary_Rate_in_Concentration_Areas']:.1f}%")
    print(f"  Median Employment Rate: {row['Median_Employment_Rate_in_Concentration_Areas']:.1f}%")
    print(f"  Composite Economic Score: {row['Composite_Score']:.1f}/100")
    print()

# ============================================================================
# Save Results
# ============================================================================
print()
print("=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save detailed results
output_file = "/home/user/Census/migration_economic_analysis.csv"
results_df.to_csv(output_file, index=False)
print(f"  ✓ Detailed results saved to: migration_economic_analysis.csv")

# Save top 10
top_10_file = "/home/user/Census/migration_top_10_countries.csv"
top_10.to_csv(top_10_file, index=False)
print(f"  ✓ Top 10 countries saved to: migration_top_10_countries.csv")

# Save bottom 10
bottom_10_file = "/home/user/Census/migration_bottom_10_countries.csv"
bottom_10.to_csv(bottom_10_file, index=False)
print(f"  ✓ Bottom 10 countries saved to: migration_bottom_10_countries.csv")

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("IMPORTANT DISCLAIMERS:")
print("- This analysis shows CORRELATION, not CAUSATION")
print("- Aggregate data does not predict individual outcomes")
print("- Historical migration policies affect current distributions")
print("- Confounding factors include: migration wave timing, refugee vs skilled migration,")
print("  family reunification policies, language barriers, credential recognition, etc.")
print("- This data should inform policy discussions, not determine individual assessments")
print("=" * 80)
