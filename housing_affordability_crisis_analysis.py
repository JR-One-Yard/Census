#!/usr/bin/env python3
"""
Housing Affordability Crisis Deep Dive Analysis
2021 Australian Census Data

This script analyzes:
- Income quintiles across housing tenure types
- Mortgage/rent stress indicators
- Dwelling types and bedroom counts
- Family composition
- Age of residents

Outputs:
- Demographics most locked out of housing
- Future crisis areas
- Affordability "sweet spots"
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Data paths
DATA_DIR = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
SUBURB_MAPPING = "SAL_Suburb_Name_Mapping.csv"

print("=" * 80)
print("HOUSING AFFORDABILITY CRISIS DEEP DIVE ANALYSIS")
print("2021 Australian Census Data")
print("=" * 80)
print()

# =============================================================================
# STEP 1: LOAD ALL RELEVANT DATA
# =============================================================================
print("STEP 1: Loading Census Data...")
print("-" * 80)

# G02: Medians and Averages
print("Loading G02: Medians (income, rent, mortgage, age)...")
g02 = pd.read_csv(f"{DATA_DIR}2021Census_G02_AUST_SAL.csv")

# G37: Tenure Type by Dwelling Structure
print("Loading G37: Tenure types (owned outright, mortgage, renting)...")
g37 = pd.read_csv(f"{DATA_DIR}2021Census_G37_AUST_SAL.csv")

# G38: Mortgage Repayment by Dwelling Structure
print("Loading G38: Mortgage repayments by dwelling type...")
g38 = pd.read_csv(f"{DATA_DIR}2021Census_G38_AUST_SAL.csv")

# G39: Mortgage Repayment by Family Composition
print("Loading G39: Mortgage repayments by family composition...")
g39 = pd.read_csv(f"{DATA_DIR}2021Census_G39_AUST_SAL.csv")

# G40: Rent by Landlord Type
print("Loading G40: Rent by landlord type...")
g40 = pd.read_csv(f"{DATA_DIR}2021Census_G40_AUST_SAL.csv")

# G41: Number of Bedrooms by Dwelling Structure
print("Loading G41: Number of bedrooms by dwelling structure...")
g41 = pd.read_csv(f"{DATA_DIR}2021Census_G41_AUST_SAL.csv")

# G33: Household Income by Household Composition
print("Loading G33: Household income by household composition...")
g33 = pd.read_csv(f"{DATA_DIR}2021Census_G33_AUST_SAL.csv")

# G32: Family Income by Family Composition
print("Loading G32: Family income by family composition...")
g32 = pd.read_csv(f"{DATA_DIR}2021Census_G32_AUST_SAL.csv")

# G01: Population by Age and Sex
print("Loading G01: Demographics (age, education)...")
g01 = pd.read_csv(f"{DATA_DIR}2021Census_G01_AUST_SAL.csv")

# Load suburb name mapping
print("Loading suburb name mapping...")
try:
    suburb_mapping = pd.read_csv(SUBURB_MAPPING)
    suburb_mapping = suburb_mapping[['SAL_CODE_2021', 'SAL_NAME_2021']].copy()
except:
    print("  Note: Suburb mapping file not found. Will use SAL codes.")
    suburb_mapping = None

print(f"\nData loaded successfully!")
print(f"Total suburbs: {len(g02):,}")
print()

# =============================================================================
# STEP 2: CALCULATE HOUSING TENURE DISTRIBUTION
# =============================================================================
print("STEP 2: Analyzing Housing Tenure Distribution...")
print("-" * 80)

tenure_data = g37[['SAL_CODE_2021']].copy()

# Calculate total dwellings by tenure type
tenure_data['owned_outright'] = g37['O_OR_Total']
tenure_data['owned_mortgage'] = g37['O_MTG_Total']
tenure_data['renting_total'] = g37['R_Tot_Total']
tenure_data['renting_private'] = g37['R_RE_Agt_Total']
tenure_data['renting_social'] = g37['R_ST_h_auth_Total'] + g37['R_Com_Hp_Total']
tenure_data['total_dwellings'] = g37['Total_Total']

# Calculate percentages
tenure_data['pct_owned_outright'] = (tenure_data['owned_outright'] / tenure_data['total_dwellings'] * 100).round(1)
tenure_data['pct_owned_mortgage'] = (tenure_data['owned_mortgage'] / tenure_data['total_dwellings'] * 100).round(1)
tenure_data['pct_renting'] = (tenure_data['renting_total'] / tenure_data['total_dwellings'] * 100).round(1)
tenure_data['pct_renting_social'] = (tenure_data['renting_social'] / tenure_data['total_dwellings'] * 100).round(1)

print(f"Tenure distribution calculated for {len(tenure_data):,} suburbs")

# =============================================================================
# STEP 3: CALCULATE MORTGAGE STRESS INDICATORS
# =============================================================================
print("\nSTEP 3: Calculating Mortgage Stress Indicators...")
print("-" * 80)

mortgage_data = g02[['SAL_CODE_2021', 'Median_mortgage_repay_monthly',
                      'Median_tot_hhd_inc_weekly']].copy()

# Calculate mortgage stress ratio (30% rule)
# Monthly mortgage / (Monthly income based on weekly)
mortgage_data['monthly_income'] = mortgage_data['Median_tot_hhd_inc_weekly'] * 52 / 12
mortgage_data['mortgage_stress_ratio'] = (
    mortgage_data['Median_mortgage_repay_monthly'] / mortgage_data['monthly_income'] * 100
).round(1)

# Classify stress levels
mortgage_data['mortgage_stress_level'] = pd.cut(
    mortgage_data['mortgage_stress_ratio'],
    bins=[0, 30, 40, 50, 100],
    labels=['Manageable (<30%)', 'Moderate (30-40%)', 'Severe (40-50%)', 'Extreme (>50%)'],
    include_lowest=True
)

# Count households in mortgage stress by payment bands
# High mortgage stress: $3000+/month
high_mortgage_cols = [col for col in g38.columns if 'M_3000_3999' in col or 'M_4000_over' in col]
mortgage_data['high_mortgage_count'] = g38[high_mortgage_cols].sum(axis=1)

print(f"Mortgage stress calculated for {len(mortgage_data):,} suburbs")
print(f"\nMortgage Stress Distribution:")
print(mortgage_data['mortgage_stress_level'].value_counts())

# =============================================================================
# STEP 4: CALCULATE RENT STRESS INDICATORS
# =============================================================================
print("\nSTEP 4: Calculating Rent Stress Indicators...")
print("-" * 80)

rent_data = g02[['SAL_CODE_2021', 'Median_rent_weekly',
                  'Median_tot_hhd_inc_weekly']].copy()

# Calculate rent stress ratio (30% rule)
rent_data['rent_stress_ratio'] = (
    rent_data['Median_rent_weekly'] / rent_data['Median_tot_hhd_inc_weekly'] * 100
).round(1)

# Classify stress levels
rent_data['rent_stress_level'] = pd.cut(
    rent_data['rent_stress_ratio'],
    bins=[0, 30, 40, 50, 100],
    labels=['Manageable (<30%)', 'Moderate (30-40%)', 'Severe (40-50%)', 'Extreme (>50%)'],
    include_lowest=True
)

# Count households in rent stress by payment bands
# High rent stress: $450+/week
high_rent_cols = [col for col in g40.columns if any(x in col for x in ['R_450_549', 'R_550_649', 'R_650_749', 'R_750_849', 'R_850_949', 'R_950_over'])]
rent_data['high_rent_count'] = g40[high_rent_cols].sum(axis=1)

print(f"Rent stress calculated for {len(rent_data):,} suburbs")
print(f"\nRent Stress Distribution:")
print(rent_data['rent_stress_level'].value_counts())

# =============================================================================
# STEP 5: ANALYZE DWELLING TYPES AND BEDROOM COUNTS
# =============================================================================
print("\nSTEP 5: Analyzing Dwelling Types and Bedroom Availability...")
print("-" * 80)

dwelling_data = g41[['SAL_CODE_2021']].copy()

# Calculate dwelling type totals
dwelling_data['separate_houses'] = g41['Separate_house_Total']
dwelling_data['semi_detached'] = g41['Se_d_r_or_t_h_t_Tot_Total']
dwelling_data['flats_apartments'] = g41['Flt_apart_Tot_Total']
dwelling_data['total_dwellings'] = g41['Total_Total']

# Bedroom availability
dwelling_data['bedrooms_0_1'] = g41['Total_NofB_0_i_b'] + g41['Total_NofB_1']
dwelling_data['bedrooms_2'] = g41['Total_NofB_2']
dwelling_data['bedrooms_3'] = g41['Total_NofB_3']
dwelling_data['bedrooms_4_plus'] = g41['Total_NofB_4'] + g41['Total_NofB_5'] + g41['Total_NofB_6_or_m']

# Calculate percentages
dwelling_data['pct_apartments'] = (dwelling_data['flats_apartments'] / dwelling_data['total_dwellings'] * 100).round(1)
dwelling_data['pct_houses'] = (dwelling_data['separate_houses'] / dwelling_data['total_dwellings'] * 100).round(1)
dwelling_data['pct_small_dwellings'] = (dwelling_data['bedrooms_0_1'] / dwelling_data['total_dwellings'] * 100).round(1)

# Average persons per bedroom (from G02)
dwelling_data = dwelling_data.merge(
    g02[['SAL_CODE_2021', 'Average_num_psns_per_bedroom']],
    on='SAL_CODE_2021',
    how='left'
)

print(f"Dwelling analysis complete for {len(dwelling_data):,} suburbs")

# =============================================================================
# STEP 6: ANALYZE FAMILY COMPOSITION AND INCOME
# =============================================================================
print("\nSTEP 6: Analyzing Family Composition and Income...")
print("-" * 80)

family_data = g33[['SAL_CODE_2021']].copy()

# Total households by type
family_data['family_households'] = g33['Tot_Family_households']
family_data['non_family_households'] = g33['Tot_Non_family_households']
family_data['total_households'] = g33['Tot_Tot']

# Income quintiles - calculate from household income distribution
# Q1 (Bottom 20%): Low income
low_income_cols = [col for col in g33.columns if any(x in col for x in ['Neg_Nil', 'HI_1_149', 'HI_150_299', 'HI_300_399', 'HI_400_499', 'HI_500_649', 'HI_650_799'])]
family_data['low_income_households'] = g33[low_income_cols].sum(axis=1)

# Q5 (Top 20%): High income
high_income_cols = [col for col in g33.columns if 'HI_4000_more' in col]
family_data['high_income_households'] = g33[high_income_cols].sum(axis=1)

# Middle income
middle_income_cols = [col for col in g33.columns if any(x in col for x in ['HI_1500_1749', 'HI_1750_1999', 'HI_2000_2499', 'HI_2500_2999'])]
family_data['middle_income_households'] = g33[middle_income_cols].sum(axis=1)

# Calculate percentages
family_data['pct_low_income'] = (family_data['low_income_households'] / family_data['total_households'] * 100).round(1)
family_data['pct_high_income'] = (family_data['high_income_households'] / family_data['total_households'] * 100).round(1)

# Single parent families (from G32)
single_parent_cols = [col for col in g32.columns if '1PF' in col or 'One_parent_fam' in col]
family_data['single_parent_families'] = g32[single_parent_cols].sum(axis=1)

print(f"Family composition analyzed for {len(family_data):,} suburbs")

# =============================================================================
# STEP 7: ANALYZE AGE DEMOGRAPHICS
# =============================================================================
print("\nSTEP 7: Analyzing Age Demographics...")
print("-" * 80)

age_data = g01[['SAL_CODE_2021']].copy()

# Age groups
age_data['age_0_14'] = g01['Age_0_4_yr_P'] + g01['Age_5_14_yr_P']
age_data['age_15_24'] = g01['Age_15_19_yr_P'] + g01['Age_20_24_yr_P']
age_data['age_25_34'] = g01['Age_25_34_yr_P']
age_data['age_35_54'] = g01['Age_35_44_yr_P'] + g01['Age_45_54_yr_P']
age_data['age_55_74'] = g01['Age_55_64_yr_P'] + g01['Age_65_74_yr_P']
age_data['age_75_plus'] = g01['Age_75_84_yr_P'] + g01['Age_85ov_P']
age_data['total_population'] = g01['Tot_P_P']

# Key demographics
age_data['young_adults'] = age_data['age_15_24'] + age_data['age_25_34']
age_data['families_age'] = age_data['age_35_54']
age_data['retirees'] = age_data['age_55_74'] + age_data['age_75_plus']

# Percentages
age_data['pct_young_adults'] = (age_data['young_adults'] / age_data['total_population'] * 100).round(1)
age_data['pct_families_age'] = (age_data['families_age'] / age_data['total_population'] * 100).round(1)
age_data['pct_retirees'] = (age_data['retirees'] / age_data['total_population'] * 100).round(1)

# Median age from G02
age_data = age_data.merge(
    g02[['SAL_CODE_2021', 'Median_age_persons']],
    on='SAL_CODE_2021',
    how='left'
)

print(f"Age demographics analyzed for {len(age_data):,} suburbs")

# =============================================================================
# STEP 8: MERGE ALL DATA AND CREATE COMPREHENSIVE DATASET
# =============================================================================
print("\nSTEP 8: Creating Comprehensive Analysis Dataset...")
print("-" * 80)

# Start with base data
analysis = g02[['SAL_CODE_2021', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly',
                'Median_tot_hhd_inc_weekly', 'Median_mortgage_repay_monthly',
                'Median_rent_weekly', 'Average_household_size']].copy()

# Merge all datasets
analysis = analysis.merge(tenure_data, on='SAL_CODE_2021', how='left')
analysis = analysis.merge(mortgage_data[['SAL_CODE_2021', 'mortgage_stress_ratio',
                                          'mortgage_stress_level', 'high_mortgage_count']],
                          on='SAL_CODE_2021', how='left')
analysis = analysis.merge(rent_data[['SAL_CODE_2021', 'rent_stress_ratio',
                                      'rent_stress_level', 'high_rent_count']],
                          on='SAL_CODE_2021', how='left')
analysis = analysis.merge(dwelling_data[['SAL_CODE_2021', 'pct_apartments', 'pct_houses',
                                          'pct_small_dwellings', 'Average_num_psns_per_bedroom']],
                          on='SAL_CODE_2021', how='left')
analysis = analysis.merge(family_data[['SAL_CODE_2021', 'pct_low_income', 'pct_high_income',
                                        'single_parent_families', 'total_households']],
                          on='SAL_CODE_2021', how='left')
analysis = analysis.merge(age_data[['SAL_CODE_2021', 'pct_young_adults', 'pct_families_age',
                                     'pct_retirees', 'total_population']],
                          on='SAL_CODE_2021', how='left')

# Add suburb names if available
if suburb_mapping is not None:
    analysis = analysis.merge(suburb_mapping, on='SAL_CODE_2021', how='left')
    analysis = analysis.rename(columns={'SAL_NAME_2021': 'Suburb'})
else:
    analysis['Suburb'] = analysis['SAL_CODE_2021']

# Reorder columns
first_cols = ['SAL_CODE_2021', 'Suburb']
other_cols = [col for col in analysis.columns if col not in first_cols]
analysis = analysis[first_cols + other_cols]

# Remove rows with insufficient data
analysis = analysis[
    (analysis['total_population'] >= 100) &
    (analysis['total_dwellings'] >= 50) &
    (analysis['Median_tot_hhd_inc_weekly'] > 0)
].copy()

print(f"Comprehensive dataset created with {len(analysis):,} suburbs")
print()

# =============================================================================
# STEP 9: IDENTIFY LOCKED OUT DEMOGRAPHICS
# =============================================================================
print("STEP 9: Identifying Demographics Locked Out of Housing...")
print("-" * 80)

# Calculate affordability scores
# Lower score = less affordable = more locked out

# Homeownership lockout score (high rent, low ownership, young population)
analysis['homeownership_lockout_score'] = (
    analysis['pct_renting'] * 0.4 +
    analysis['rent_stress_ratio'] * 0.3 +
    analysis['pct_young_adults'] * 0.2 +
    (100 - analysis['pct_owned_outright']) * 0.1
).round(1)

# Family housing lockout score (single parents, small dwellings, high stress)
analysis['family_lockout_score'] = (
    analysis['pct_small_dwellings'] * 0.3 +
    analysis['rent_stress_ratio'] * 0.3 +
    analysis['pct_low_income'] * 0.2 +
    analysis['Average_num_psns_per_bedroom'] * 10 * 0.2  # Overcrowding indicator
).round(1)

# First home buyer lockout score (young, renting, high stress)
analysis['first_buyer_lockout_score'] = (
    analysis['mortgage_stress_ratio'] * 0.4 +
    analysis['pct_renting'] * 0.3 +
    analysis['pct_young_adults'] * 0.2 +
    (100 - analysis['pct_owned_mortgage']) * 0.1
).round(1)

print("\nTop 20 Suburbs - Young Adults Locked Out of Homeownership:")
locked_out_young = analysis.nlargest(20, 'homeownership_lockout_score')[
    ['Suburb', 'pct_young_adults', 'pct_renting', 'rent_stress_ratio',
     'Median_rent_weekly', 'homeownership_lockout_score']
]
print(locked_out_young.to_string(index=False))

print("\n\nTop 20 Suburbs - Families Locked Out:")
locked_out_families = analysis.nlargest(20, 'family_lockout_score')[
    ['Suburb', 'single_parent_families', 'pct_small_dwellings',
     'Average_num_psns_per_bedroom', 'rent_stress_ratio', 'family_lockout_score']
]
print(locked_out_families.to_string(index=False))

# =============================================================================
# STEP 10: IDENTIFY CRISIS AREAS
# =============================================================================
print("\n\nSTEP 10: Identifying Future Housing Crisis Areas...")
print("-" * 80)

# Crisis score combines multiple stress factors
analysis['crisis_score'] = (
    analysis['mortgage_stress_ratio'].fillna(0) * 0.25 +
    analysis['rent_stress_ratio'].fillna(0) * 0.25 +
    analysis['pct_renting'] * 0.2 +
    analysis['pct_low_income'] * 0.15 +
    analysis['Average_num_psns_per_bedroom'] * 10 * 0.15
).round(1)

# High crisis: Top 10%
crisis_threshold = analysis['crisis_score'].quantile(0.90)
crisis_areas = analysis[analysis['crisis_score'] >= crisis_threshold].copy()
crisis_areas = crisis_areas.sort_values('crisis_score', ascending=False)

print(f"\nIdentified {len(crisis_areas)} high-crisis areas (top 10%)")
print(f"\nTop 30 Housing Crisis Areas:")
crisis_top = crisis_areas.head(30)[
    ['Suburb', 'mortgage_stress_ratio', 'rent_stress_ratio',
     'pct_renting', 'pct_low_income', 'Median_tot_hhd_inc_weekly', 'crisis_score']
]
print(crisis_top.to_string(index=False))

# =============================================================================
# STEP 11: IDENTIFY AFFORDABILITY SWEET SPOTS
# =============================================================================
print("\n\nSTEP 11: Identifying Affordability Sweet Spots...")
print("-" * 80)

# Sweet spots: Low stress, decent housing, reasonable prices
# Criteria:
# - Mortgage stress < 30%
# - Rent stress < 30%
# - Good mix of dwelling types
# - Reasonable household income

sweet_spots = analysis[
    (analysis['mortgage_stress_ratio'] < 30) &
    (analysis['rent_stress_ratio'] < 30) &
    (analysis['Median_tot_hhd_inc_weekly'] > 800) &
    (analysis['Median_tot_hhd_inc_weekly'] < 2500) &
    (analysis['total_dwellings'] >= 100) &
    (analysis['pct_owned_mortgage'] > 20)  # Active homeownership market
].copy()

# Calculate affordability score (higher = better value)
sweet_spots['affordability_score'] = (
    (100 - sweet_spots['mortgage_stress_ratio']) * 0.3 +
    (100 - sweet_spots['rent_stress_ratio']) * 0.3 +
    sweet_spots['pct_houses'] * 0.2 +
    (100 - sweet_spots['pct_small_dwellings']) * 0.2
).round(1)

sweet_spots = sweet_spots.sort_values('affordability_score', ascending=False)

print(f"\nIdentified {len(sweet_spots)} affordability sweet spots")
print(f"\nTop 30 Affordability Sweet Spots:")
sweet_top = sweet_spots.head(30)[
    ['Suburb', 'Median_tot_hhd_inc_weekly', 'Median_mortgage_repay_monthly',
     'Median_rent_weekly', 'mortgage_stress_ratio', 'rent_stress_ratio',
     'pct_houses', 'affordability_score']
]
print(sweet_top.to_string(index=False))

# =============================================================================
# STEP 12: SAVE RESULTS
# =============================================================================
print("\n\nSTEP 12: Saving Results...")
print("-" * 80)

# Save comprehensive dataset
analysis.to_csv('housing_affordability_comprehensive.csv', index=False)
print("✓ Saved: housing_affordability_comprehensive.csv")

# Save locked out demographics
locked_out_young.to_csv('housing_lockout_young_adults.csv', index=False)
print("✓ Saved: housing_lockout_young_adults.csv")

locked_out_families.to_csv('housing_lockout_families.csv', index=False)
print("✓ Saved: housing_lockout_families.csv")

# Save crisis areas
crisis_areas.to_csv('housing_crisis_areas.csv', index=False)
print("✓ Saved: housing_crisis_areas.csv")

# Save sweet spots
sweet_spots.to_csv('housing_affordability_sweet_spots.csv', index=False)
print("✓ Saved: housing_affordability_sweet_spots.csv")

# =============================================================================
# STEP 13: GENERATE SUMMARY STATISTICS
# =============================================================================
print("\n\nSTEP 13: Summary Statistics...")
print("=" * 80)

print("\n📊 HOUSING TENURE DISTRIBUTION (National Average)")
print(f"  Owned Outright: {analysis['pct_owned_outright'].mean():.1f}%")
print(f"  Owned with Mortgage: {analysis['pct_owned_mortgage'].mean():.1f}%")
print(f"  Renting (Private): {(analysis['pct_renting'] - analysis['pct_renting_social']).mean():.1f}%")
print(f"  Renting (Social Housing): {analysis['pct_renting_social'].mean():.1f}%")

print("\n💰 HOUSING STRESS INDICATORS")
print(f"  Average Mortgage Stress Ratio: {analysis['mortgage_stress_ratio'].mean():.1f}%")
print(f"  Average Rent Stress Ratio: {analysis['rent_stress_ratio'].mean():.1f}%")
print(f"  Suburbs with Mortgage Stress >30%: {(analysis['mortgage_stress_ratio'] > 30).sum():,}")
print(f"  Suburbs with Rent Stress >30%: {(analysis['rent_stress_ratio'] > 30).sum():,}")

print("\n🏘️  DWELLING CHARACTERISTICS")
print(f"  Average % Separate Houses: {analysis['pct_houses'].mean():.1f}%")
print(f"  Average % Apartments: {analysis['pct_apartments'].mean():.1f}%")
print(f"  Average Persons per Bedroom: {analysis['Average_num_psns_per_bedroom'].mean():.2f}")

print("\n👨‍👩‍👧‍👦 HOUSEHOLD DEMOGRAPHICS")
print(f"  Average % Low Income (<$800/week): {analysis['pct_low_income'].mean():.1f}%")
print(f"  Average % High Income ($4000+/week): {analysis['pct_high_income'].mean():.1f}%")
print(f"  Average % Young Adults (15-34): {analysis['pct_young_adults'].mean():.1f}%")
print(f"  Median Age: {analysis['Median_age_persons'].median():.1f} years")

print("\n⚠️  KEY FINDINGS")
print(f"  High Crisis Areas Identified: {len(crisis_areas):,} suburbs")
print(f"  Affordability Sweet Spots: {len(sweet_spots):,} suburbs")
print(f"  Suburbs with >50% Renters: {(analysis['pct_renting'] > 50).sum():,}")
print(f"  Suburbs with Extreme Rent Stress (>50%): {(analysis['rent_stress_ratio'] > 50).sum():,}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print()
print("Output files created:")
print("  1. housing_affordability_comprehensive.csv - Full dataset")
print("  2. housing_lockout_young_adults.csv - Young adults locked out")
print("  3. housing_lockout_families.csv - Families locked out")
print("  4. housing_crisis_areas.csv - Future crisis areas")
print("  5. housing_affordability_sweet_spots.csv - Affordable areas")
print()
