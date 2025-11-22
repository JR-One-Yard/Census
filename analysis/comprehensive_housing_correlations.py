#!/usr/bin/env python3
"""
Comprehensive Housing Price Correlation Analysis

This script performs three main analyses:
1. Identifies "value" executive suburbs (low price + high executive concentration)
2. Analyzes rent vs. mortgage gap patterns
3. Runs comprehensive correlation analysis with all available Census variables
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
DATA_DIR = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

print("=" * 110)
print("COMPREHENSIVE HOUSING PRICE CORRELATION ANALYSIS")
print("=" * 110)
print()

# ============================================================================
# PART 1: Load and Prepare Data
# ============================================================================

print("Loading data...")

# Load basic demographics and housing data (G02)
g02_file = DATA_DIR / "2021Census_G02_AUST_SAL.csv"
g02_df = pd.read_csv(g02_file)

# Load occupation data (G60A)
g60a_file = DATA_DIR / "2021Census_G60A_AUST_SAL.csv"
occupation_df = pd.read_csv(g60a_file)

# Calculate manager and professional concentrations
occupation_df['Total_Managers'] = (
    occupation_df['M_Tot_Managers'] + occupation_df['F_Tot_Managers']
)
occupation_df['Total_Professionals'] = (
    occupation_df['M_Tot_Professionals'] + occupation_df['F_Tot_Professionals']
)
occupation_df['Total_Employed'] = (
    occupation_df['M_Tot_Tot'] + occupation_df['F_Tot_Tot']
)

occupation_df['Manager_Concentration_Pct'] = (
    occupation_df['Total_Managers'] / occupation_df['Total_Employed'] * 100
).fillna(0)

occupation_df['Professional_Concentration_Pct'] = (
    occupation_df['Total_Professionals'] / occupation_df['Total_Employed'] * 100
).fillna(0)

occupation_df['Manager_Plus_Professional_Pct'] = (
    occupation_df['Manager_Concentration_Pct'] + occupation_df['Professional_Concentration_Pct']
)

# Merge datasets
df = g02_df.merge(
    occupation_df[['SAL_CODE_2021', 'Total_Employed', 'Manager_Concentration_Pct',
                   'Professional_Concentration_Pct', 'Manager_Plus_Professional_Pct']],
    on='SAL_CODE_2021',
    how='left'
)

# Load SAL names from metadata
metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
sal_names_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()
df = df.merge(sal_names_df, left_on='SAL_CODE_2021', right_on='Census_Code_2021', how='left')
df.rename(columns={'Census_Name_2021': 'SAL_NAME_2021'}, inplace=True)

# Apply urban filter
urban_df = df[
    (df['Total_Employed'] >= 1000) &
    (df['Median_mortgage_repay_monthly'] > 0) &
    (df['Manager_Concentration_Pct'] > 0)
].copy()

print(f"Total suburbs: {len(df):,}")
print(f"Urban suburbs with data: {len(urban_df):,}")
print()

# ============================================================================
# PART 2: "Value" Executive Suburbs (Low Price + High Executive)
# ============================================================================

print("=" * 110)
print("ANALYSIS 1: 'VALUE' EXECUTIVE SUBURBS")
print("=" * 110)
print()

# Define quadrants
mortgage_threshold_25 = urban_df['Median_mortgage_repay_monthly'].quantile(0.25)
mortgage_threshold_75 = urban_df['Median_mortgage_repay_monthly'].quantile(0.75)
manager_threshold_25 = urban_df['Manager_Concentration_Pct'].quantile(0.25)
manager_threshold_75 = urban_df['Manager_Concentration_Pct'].quantile(0.75)

print(f"25th percentile mortgage: ${mortgage_threshold_25:,.0f}/month")
print(f"75th percentile mortgage: ${mortgage_threshold_75:,.0f}/month")
print(f"25th percentile manager concentration: {manager_threshold_25:.1f}%")
print(f"75th percentile manager concentration: {manager_threshold_75:.1f}%")
print()

# Quadrant 3: Low Price + High Executive (The "Value" Suburbs)
value_suburbs = urban_df[
    (urban_df['Median_mortgage_repay_monthly'] <= mortgage_threshold_25) &
    (urban_df['Manager_Concentration_Pct'] >= manager_threshold_75)
].copy()

value_suburbs = value_suburbs.sort_values('Manager_Concentration_Pct', ascending=False)

print(f"Found {len(value_suburbs)} 'VALUE' suburbs (low price + high executive concentration)")
print()
print("TOP 30 VALUE EXECUTIVE SUBURBS")
print("Criteria: Mortgage ≤ ${:,.0f}/month AND Manager % ≥ {:.1f}%".format(
    mortgage_threshold_25, manager_threshold_75))
print()
print(f"{'Rank':<6}{'Suburb':<45}{'Mortgage':<12}{'Mgr %':<9}{'M+P %':<9}{'Med Inc':<12}")
print(f"{'':6}{'':45}{'$/month':<12}{'':9}{'':9}{'$/week':<12}")
print("-" * 110)

for idx, row in value_suburbs.head(30).iterrows():
    rank = value_suburbs.index.get_loc(idx) + 1
    print(f"{rank:<6}{row['SAL_NAME_2021']:<45}${row['Median_mortgage_repay_monthly']:>10,.0f}  "
          f"{row['Manager_Concentration_Pct']:>6.1f}%  {row['Manager_Plus_Professional_Pct']:>6.1f}%  "
          f"${row['Median_tot_prsnl_inc_weekly']:>10,.0f}")

print()
print(f"Average mortgage in value suburbs: ${value_suburbs['Median_mortgage_repay_monthly'].mean():,.0f}/month")
print(f"Average manager % in value suburbs: {value_suburbs['Manager_Concentration_Pct'].mean():.1f}%")
print(f"Average income in value suburbs: ${value_suburbs['Median_tot_prsnl_inc_weekly'].mean():,.0f}/week")
print()

# Export value suburbs
value_suburbs_export = value_suburbs[[
    'SAL_NAME_2021', 'Median_mortgage_repay_monthly', 'Manager_Concentration_Pct',
    'Professional_Concentration_Pct', 'Manager_Plus_Professional_Pct',
    'Median_tot_prsnl_inc_weekly', 'Median_rent_weekly', 'Total_Employed'
]].copy()
value_suburbs_export.columns = [
    'Suburb', 'Median_Mortgage_Monthly', 'Manager_Pct', 'Professional_Pct',
    'Manager_Plus_Prof_Pct', 'Median_Personal_Income_Weekly', 'Median_Rent_Weekly',
    'Total_Employed'
]
value_suburbs_export.to_csv(RESULTS_DIR / 'value_executive_suburbs.csv', index=False)

# ============================================================================
# PART 3: Rent vs. Mortgage Gap Analysis
# ============================================================================

print("=" * 110)
print("ANALYSIS 2: RENT vs. MORTGAGE GAP")
print("=" * 110)
print()

# Filter for suburbs with both rent and mortgage data
rent_mortgage_df = urban_df[
    (urban_df['Median_rent_weekly'] > 0) &
    (urban_df['Median_mortgage_repay_monthly'] > 0)
].copy()

# Calculate correlations
rent_manager_corr = rent_mortgage_df['Median_rent_weekly'].corr(
    rent_mortgage_df['Manager_Concentration_Pct']
)
mortgage_manager_corr = rent_mortgage_df['Median_mortgage_repay_monthly'].corr(
    rent_mortgage_df['Manager_Concentration_Pct']
)

print(f"Rent vs. Manager Concentration:           r = {rent_manager_corr:.3f}")
print(f"Mortgage vs. Manager Concentration:        r = {mortgage_manager_corr:.3f}")
print(f"Gap (Mortgage - Rent correlation):         Δr = {mortgage_manager_corr - rent_manager_corr:.3f}")
print()

# Find suburbs with high rent but low mortgage (rental investment hotspots?)
rent_mortgage_df['Rent_to_Mortgage_Ratio'] = (
    rent_mortgage_df['Median_rent_weekly'] * 52 / 12 /
    rent_mortgage_df['Median_mortgage_repay_monthly']
)

# High rental yield suburbs (high rent relative to mortgage)
high_yield = rent_mortgage_df.nlargest(20, 'Rent_to_Mortgage_Ratio')

print("HIGH RENTAL YIELD SUBURBS (High Rent Relative to Mortgage)")
print("These may be investment hotspots or rental-dominated markets")
print()
print(f"{'Rank':<6}{'Suburb':<40}{'Rent/Week':<12}{'Mortgage/Mo':<14}{'Ratio':<8}{'Mgr %':<9}")
print("-" * 110)

for idx, (i, row) in enumerate(high_yield.iterrows(), 1):
    print(f"{idx:<6}{row['SAL_NAME_2021']:<40}${row['Median_rent_weekly']:>9,.0f}  "
          f"${row['Median_mortgage_repay_monthly']:>11,.0f}  "
          f"{row['Rent_to_Mortgage_Ratio']:>6.2f}  {row['Manager_Concentration_Pct']:>6.1f}%")

print()

# ============================================================================
# PART 4: Comprehensive Correlation Analysis
# ============================================================================

print("=" * 110)
print("ANALYSIS 3: COMPREHENSIVE CORRELATION ANALYSIS")
print("=" * 110)
print()
print("Testing ALL numeric variables for correlation with housing prices...")
print()

# Get all numeric columns
numeric_cols = urban_df.select_dtypes(include=[np.number]).columns.tolist()

# Remove the housing price variables themselves
exclude_cols = ['SAL_CODE_2021', 'Median_mortgage_repay_monthly', 'Median_rent_weekly']
test_cols = [col for col in numeric_cols if col not in exclude_cols]

# Calculate correlations with mortgage
mortgage_correlations = []
for col in test_cols:
    valid_data = urban_df[[col, 'Median_mortgage_repay_monthly']].dropna()
    if len(valid_data) > 100:  # Only if we have enough data
        corr = valid_data[col].corr(valid_data['Median_mortgage_repay_monthly'])
        if not np.isnan(corr):
            mortgage_correlations.append({
                'Variable': col,
                'Correlation': corr,
                'Abs_Correlation': abs(corr),
                'N_Observations': len(valid_data)
            })

# Calculate correlations with rent
rent_correlations = []
for col in test_cols:
    valid_data = urban_df[[col, 'Median_rent_weekly']].dropna()
    if len(valid_data) > 100:
        corr = valid_data[col].corr(valid_data['Median_rent_weekly'])
        if not np.isnan(corr):
            rent_correlations.append({
                'Variable': col,
                'Correlation': corr,
                'Abs_Correlation': abs(corr),
                'N_Observations': len(valid_data)
            })

# Convert to DataFrames and sort
mortgage_corr_df = pd.DataFrame(mortgage_correlations).sort_values('Abs_Correlation', ascending=False)
rent_corr_df = pd.DataFrame(rent_correlations).sort_values('Abs_Correlation', ascending=False)

# Display top correlations with MORTGAGE
print("TOP 30 CORRELATIONS WITH MEDIAN MORTGAGE (Monthly)")
print()
print(f"{'Rank':<6}{'Variable':<50}{'Correlation':<15}{'N Obs':<10}")
print("-" * 110)

for idx, row in mortgage_corr_df.head(30).iterrows():
    rank = mortgage_corr_df.index.get_loc(idx) + 1
    print(f"{rank:<6}{row['Variable']:<50}{row['Correlation']:>13.3f}  {row['N_Observations']:>8,.0f}")

print()
print()

# Display top correlations with RENT
print("TOP 30 CORRELATIONS WITH MEDIAN RENT (Weekly)")
print()
print(f"{'Rank':<6}{'Variable':<50}{'Correlation':<15}{'N Obs':<10}")
print("-" * 110)

for idx, row in rent_corr_df.head(30).iterrows():
    rank = rent_corr_df.index.get_loc(idx) + 1
    print(f"{rank:<6}{row['Variable']:<50}{row['Correlation']:>13.3f}  {row['N_Observations']:>8,.0f}")

print()
print()

# Export correlation results
mortgage_corr_df.to_csv(RESULTS_DIR / 'mortgage_correlations_comprehensive.csv', index=False)
rent_corr_df.to_csv(RESULTS_DIR / 'rent_correlations_comprehensive.csv', index=False)

# ============================================================================
# PART 5: Statistical Commentary
# ============================================================================

print("=" * 110)
print("STATISTICAL COMMENTARY: CAUSATION vs. CORRELATION")
print("=" * 110)
print()

# Group correlations by strength
very_strong_mortgage = mortgage_corr_df[mortgage_corr_df['Abs_Correlation'] >= 0.7]
strong_mortgage = mortgage_corr_df[(mortgage_corr_df['Abs_Correlation'] >= 0.5) &
                                    (mortgage_corr_df['Abs_Correlation'] < 0.7)]

print(f"Variables with VERY STRONG correlation (|r| ≥ 0.7): {len(very_strong_mortgage)}")
print(f"Variables with STRONG correlation (0.5 ≤ |r| < 0.7): {len(strong_mortgage)}")
print()

print("VERY STRONG CORRELATIONS (|r| ≥ 0.7):")
print("-" * 110)
for idx, row in very_strong_mortgage.iterrows():
    print(f"  • {row['Variable']:<50} r = {row['Correlation']:>6.3f}")

print()
print("=" * 110)
print()
print("Results exported:")
print("  - results/value_executive_suburbs.csv")
print("  - results/mortgage_correlations_comprehensive.csv")
print("  - results/rent_correlations_comprehensive.csv")
print("=" * 110)
