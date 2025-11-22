#!/usr/bin/env python3
"""
Sydney Family Home Value Analysis Model
========================================
Comprehensive value analysis for Sydney suburbs combining:
- Quality metrics (education, employment, demographics, density)
- Price metrics (housing costs, affordability)
- Value Score = Quality Index / Price Index

Author: Policy Expert, Hedge Fund Manager, Real Estate Investor perspective
Date: 2025-11-22
"""

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
MAPPING_FILE = "/home/user/Census/SAL_Suburb_Name_Mapping.csv"
OUTPUT_DIR = "/home/user/Census"

print("=" * 120)
print(" " * 30 + "SYDNEY FAMILY HOME VALUE ANALYSIS MODEL")
print("=" * 120)
print("\nObjective: Identify Sydney suburbs offering best VALUE for families")
print("Value Formula: QUALITY INDEX / PRICE INDEX")
print("\n" + "=" * 120)

# ============================================================================
# STEP 1: Load Suburb Mapping and Identify Sydney Suburbs
# ============================================================================
print("\n[1/11] Loading suburb mapping and identifying Sydney suburbs...")

suburb_mapping = pd.read_csv(MAPPING_FILE)
print(f"   Total suburbs in Australia: {len(suburb_mapping):,}")

# Load geographic metadata to identify Greater Sydney suburbs
# We'll use a practical approach: identify NSW suburbs that are commonly known Sydney metro areas
# This includes suburbs from major Sydney LGAs and postcodes

# Known Greater Sydney LGAs (partial list of major ones)
SYDNEY_LGAS = [
    'Sydney', 'North Sydney', 'Mosman', 'Manly', 'Warringah', 'Pittwater',
    'Willoughby', 'Lane Cove', 'Hunters Hill', 'Ryde', 'Ku-ring-gai',
    'Hornsby', 'Parramatta', 'The Hills', 'Blacktown', 'Penrith',
    'Blue Mountains', 'Hawkesbury', 'Liverpool', 'Fairfield', 'Canterbury',
    'Bankstown', 'Strathfield', 'Burwood', 'Canada Bay', 'Auburn',
    'Holroyd', 'Baulkham Hills', 'Camden', 'Campbelltown', 'Wollondilly',
    'Wingecarribee', 'Sutherland', 'Hurstville', 'Kogarah', 'Rockdale',
    'Botany Bay', 'Randwick', 'Waverley', 'Woollahra', 'Leichhardt',
    'Marrickville', 'Ashfield', 'Botany'
]

# Alternative approach: Use well-known Sydney suburbs pattern
# Sydney suburbs typically don't have state suffixes unless there's ambiguity
# Let's use the top 100 NSW suburbs as a base and expand with known Sydney patterns

# For now, we'll use a pragmatic filter based on:
# 1. NSW suburbs (SAL codes 10001-15000 are NSW)
# 2. Exclude regional NSW areas (Blue Mountains, Central Coast, etc.)

# Load a sample census file to get all SAL codes
sample_data = pd.read_csv(f"{DATA_DIR}2021Census_G01_AUST_SAL.csv")

# NSW SAL codes typically start with SAL1xxxx (10001-15000 range)
# Greater Sydney is roughly SAL codes in specific ranges
# For accuracy, let's use a comprehensive list approach

# Read all suburb names and filter for Greater Sydney metro area
# We'll use suburbs that are clearly Sydney metro (not regional NSW)
sydney_suburbs = []

# Known patterns for Sydney suburbs vs regional NSW
regional_keywords = [
    'Blue Mountains', 'Central Coast', 'Newcastle', 'Wollongong', 'Shellharbour',
    'Lake Macquarie', 'Maitland', 'Cessnock', 'Port Stephens', 'Gosford',
    'Wyong', 'Shoalhaven', 'Kiama', 'Albury', 'Wagga Wagga', 'Orange',
    'Bathurst', 'Dubbo', 'Tamworth', 'Armidale', 'Coffs Harbour',
    'Port Macquarie', 'Tweed Heads', 'Byron', 'Ballina', 'Lismore',
    'Broken Hill', 'Griffith', 'Queanbeyan'
]

# Alternatively, let's use the existing NSW top 100 results as a seed
# and expand with known Greater Sydney suburbs
# Most Sydney suburbs in top 100 NSW are actually Sydney metro

# For this analysis, we'll use a comprehensive list of known Greater Sydney suburbs
# Based on ABS Greater Capital City Statistical Area (GCCSA) for Sydney

# Practical approach: Load all NSW suburbs (SAL10001-15999) and exclude regional areas
nsw_suburbs = suburb_mapping[
    (suburb_mapping['SAL_CODE'].str.startswith('SAL1')) &
    (suburb_mapping['SAL_CODE'].str.extract('(\d+)')[0].astype(int) >= 10001) &
    (suburb_mapping['SAL_CODE'].str.extract('(\d+)')[0].astype(int) < 16000)
].copy()

print(f"   NSW suburbs identified: {len(nsw_suburbs):,}")

# Filter out known regional NSW areas
def is_regional(suburb_name):
    """Check if suburb is in regional NSW (not Greater Sydney)"""
    if pd.isna(suburb_name):
        return True
    suburb_lower = suburb_name.lower()

    # Exclude clearly regional areas
    regional_exclude = [
        'newcastle', 'wollongong', 'shellharbour', 'lake macquarie', 'maitland',
        'cessnock', 'port stephens', 'gosford', 'wyong', 'blue mountains',
        'central coast', 'shoalhaven', 'kiama', 'albury', 'wagga', 'orange',
        'bathurst', 'dubbo', 'tamworth', 'armidale', 'coffs harbour',
        'port macquarie', 'tweed', 'byron', 'ballina', 'lismore', 'grafton',
        'broken hill', 'griffith', 'queanbeyan', 'goulburn', 'mudgee', 'lithgow',
        'katoomba', 'singleton', 'muswellbrook', 'taree', 'forster', 'nelson bay',
        'terrigal', 'umina', 'woy woy', 'nowra', 'goulburn', 'yass', 'bega',
        'narooma', 'moruya', 'batemans bay', 'ulladulla', 'bowral', 'moss vale',
        'mittagong', 'young', 'cowra', 'parkes', 'forbes'
    ]

    # Check if any regional keyword is in suburb name
    for keyword in regional_exclude:
        if keyword in suburb_lower:
            return True

    return False

# Filter Greater Sydney suburbs (NSW excluding regional)
sydney_filter = ~nsw_suburbs['Suburb_Name'].apply(is_regional)
sydney_suburbs_df = nsw_suburbs[sydney_filter].copy()

print(f"   Greater Sydney suburbs identified: {len(sydney_suburbs_df):,}")
print(f"   Regional NSW suburbs excluded: {len(nsw_suburbs) - len(sydney_suburbs_df):,}")

# Create Sydney SAL code set for filtering
sydney_sal_codes = set(sydney_suburbs_df['SAL_CODE'].values)

print(f"\n   ✓ Sydney suburb filter created: {len(sydney_sal_codes):,} suburbs")

# ============================================================================
# STEP 2: Load and Extract All Census Data
# ============================================================================
print("\n[2/11] Loading census data tables...")

# G01: Population and age/sex
df_pop = pd.read_csv(f"{DATA_DIR}2021Census_G01_AUST_SAL.csv")
df_pop = df_pop[df_pop['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G02: Medians and averages (age, income, mortgage, rent, household size)
df_medians = pd.read_csv(f"{DATA_DIR}2021Census_G02_AUST_SAL.csv")
df_medians = df_medians[df_medians['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G16A/B: School completion
df_school_a = pd.read_csv(f"{DATA_DIR}2021Census_G16A_AUST_SAL.csv")
df_school_a = df_school_a[df_school_a['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G49A: Tertiary education - contains both Males and Females
df_edu_all = pd.read_csv(f"{DATA_DIR}2021Census_G49A_AUST_SAL.csv")
df_edu_all = df_edu_all[df_edu_all['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G50A: Occupation (for professionals/managers)
df_occupation = pd.read_csv(f"{DATA_DIR}2021Census_G50A_AUST_SAL.csv")
df_occupation = df_occupation[df_occupation['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G52A: Employment status
df_employment = pd.read_csv(f"{DATA_DIR}2021Census_G52A_AUST_SAL.csv")
df_employment = df_employment[df_employment['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G53A: Hours worked (full-time vs part-time)
df_hours = pd.read_csv(f"{DATA_DIR}2021Census_G53A_AUST_SAL.csv")
df_hours = df_hours[df_hours['SAL_CODE_2021'].isin(sydney_sal_codes)]

# G18: Family composition
df_families = pd.read_csv(f"{DATA_DIR}2021Census_G18_AUST_SAL.csv")
df_families = df_families[df_families['SAL_CODE_2021'].isin(sydney_sal_codes)]

print(f"   ✓ Loaded {len(df_pop):,} Sydney suburbs across all census tables")

# ============================================================================
# STEP 3: Calculate Quality Metrics - EDUCATION
# ============================================================================
print("\n[3/11] Calculating education quality metrics...")

# Tertiary Education Rate (Bachelor+ degree holders)
# G49A contains both Male (M_) and Female (F_) data
# We'll use both to get totals

# Male tertiary education
pgr_cols_m = [col for col in df_edu_all.columns if 'M_PGrad_Deg_' in col and col != 'M_PGrad_Deg_Total']
grad_cols_m = [col for col in df_edu_all.columns if 'M_GradDip_and_GradCert_' in col and col != 'M_GradDip_and_GradCert_Total']
bach_cols_m = [col for col in df_edu_all.columns if 'M_BachDeg_' in col and col != 'M_BachDeg_Total']

df_edu_all['Tertiary_Males'] = (
    df_edu_all[pgr_cols_m].sum(axis=1) +
    df_edu_all[grad_cols_m].sum(axis=1) +
    df_edu_all[bach_cols_m].sum(axis=1)
)

# Female tertiary education
pgr_cols_f = [col for col in df_edu_all.columns if 'F_PGrad_Deg_' in col and col != 'F_PGrad_Deg_Total']
grad_cols_f = [col for col in df_edu_all.columns if 'F_GradDip_and_GradCert_' in col and col != 'F_GradDip_and_GradCert_Total']
bach_cols_f = [col for col in df_edu_all.columns if 'F_BachDeg_' in col and col != 'F_BachDeg_Total']

df_edu_all['Tertiary_Females'] = (
    df_edu_all[pgr_cols_f].sum(axis=1) +
    df_edu_all[grad_cols_f].sum(axis=1) +
    df_edu_all[bach_cols_f].sum(axis=1)
)

# Total tertiary and total adults
df_edu_all['Tertiary_Total'] = df_edu_all['Tertiary_Males'] + df_edu_all['Tertiary_Females']
df_edu_all['Total_Adults'] = df_edu_all['M_Tot_Total'] + df_edu_all['F_Tot_Total']

# Create education metrics dataframe
education_metrics = pd.DataFrame({
    'SAL_CODE_2021': df_edu_all['SAL_CODE_2021'],
    'Tertiary_Total': df_edu_all['Tertiary_Total'],
    'Adults_Total': df_edu_all['Total_Adults']
})

education_metrics['Tertiary_Pct'] = (
    education_metrics['Tertiary_Total'] / education_metrics['Adults_Total'] * 100
).fillna(0)

# Year 12 completion rate
year12_cols = [col for col in df_school_a.columns if 'Yr_12_eq' in col and col.startswith('P_')]
if year12_cols:
    df_school_a['Year12_Total'] = df_school_a[year12_cols].sum(axis=1)
    total_cols = [col for col in df_school_a.columns if col.startswith('P_') and 'Total' in col]
    if total_cols:
        df_school_a['School_Age_Total'] = df_school_a[total_cols[0]]
        df_school_a['Year12_Pct'] = (df_school_a['Year12_Total'] / df_school_a['School_Age_Total'] * 100).fillna(0)
        education_metrics = education_metrics.merge(
            df_school_a[['SAL_CODE_2021', 'Year12_Pct']],
            on='SAL_CODE_2021',
            how='left'
        )

print(f"   ✓ Education metrics calculated: Tertiary%, Year12%")

# ============================================================================
# STEP 4: Calculate Quality Metrics - EMPLOYMENT
# ============================================================================
print("\n[4/11] Calculating employment quality metrics...")

# Professional & Manager concentration
# Get managers and professionals columns
manager_cols = [col for col in df_occupation.columns if 'Managers' in col and col.startswith('P_')]
prof_cols = [col for col in df_occupation.columns if 'Professionals' in col and col.startswith('P_')]

if manager_cols and prof_cols:
    df_occupation['Managers_Total'] = df_occupation[manager_cols[0]]
    df_occupation['Professionals_Total'] = df_occupation[prof_cols[0]]

    # Total employed
    total_emp_col = [col for col in df_occupation.columns if col.startswith('P_Tot')]
    if total_emp_col:
        df_occupation['Total_Employed'] = df_occupation[total_emp_col[0]]
        df_occupation['Prof_Manager_Pct'] = (
            (df_occupation['Managers_Total'] + df_occupation['Professionals_Total']) /
            df_occupation['Total_Employed'] * 100
        ).fillna(0)

# Employment rate (employed / labor force)
employed_col = [col for col in df_employment.columns if 'Employed_Total' in col and col.startswith('P_')]
unemployed_col = [col for col in df_employment.columns if 'Unempl_tot' in col and col.startswith('P_')]

if employed_col and unemployed_col:
    df_employment['Employed'] = df_employment[employed_col[0]]
    df_employment['Unemployed'] = df_employment[unemployed_col[0]]
    df_employment['Labor_Force'] = df_employment['Employed'] + df_employment['Unemployed']
    df_employment['Employment_Rate'] = (df_employment['Employed'] / df_employment['Labor_Force'] * 100).fillna(0)
    df_employment['Unemployment_Rate'] = (df_employment['Unemployed'] / df_employment['Labor_Force'] * 100).fillna(0)

# Full-time employment rate
ft_col = [col for col in df_hours.columns if 'F_time' in col and col.startswith('P_')]
if ft_col:
    total_workers_col = [col for col in df_hours.columns if col.startswith('P_Tot')]
    if total_workers_col:
        df_hours['Fulltime'] = df_hours[ft_col[0]]
        df_hours['Total_Workers'] = df_hours[total_workers_col[0]]
        df_hours['Fulltime_Pct'] = (df_hours['Fulltime'] / df_hours['Total_Workers'] * 100).fillna(0)

# Merge employment metrics
employment_metrics = df_medians[['SAL_CODE_2021', 'Median_tot_prsnl_inc_weekly']].copy()
employment_metrics = employment_metrics.merge(
    df_occupation[['SAL_CODE_2021', 'Prof_Manager_Pct']] if 'Prof_Manager_Pct' in df_occupation.columns else df_occupation[['SAL_CODE_2021']],
    on='SAL_CODE_2021',
    how='left'
)
employment_metrics = employment_metrics.merge(
    df_employment[['SAL_CODE_2021', 'Employment_Rate', 'Unemployment_Rate']] if 'Employment_Rate' in df_employment.columns else df_employment[['SAL_CODE_2021']],
    on='SAL_CODE_2021',
    how='left'
)
employment_metrics = employment_metrics.merge(
    df_hours[['SAL_CODE_2021', 'Fulltime_Pct']] if 'Fulltime_Pct' in df_hours.columns else df_hours[['SAL_CODE_2021']],
    on='SAL_CODE_2021',
    how='left'
)

print(f"   ✓ Employment metrics calculated: Income, Prof%, Employment%, Fulltime%")

# ============================================================================
# STEP 5: Calculate Quality Metrics - DEMOGRAPHICS
# ============================================================================
print("\n[5/11] Calculating demographic quality metrics...")

# Family composition - couple families with children
couple_kids_cols = [col for col in df_families.columns if 'Couple_fam_with_children' in col and col.startswith('Total_')]
total_families_col = [col for col in df_families.columns if col == 'Total_Total_families']

if couple_kids_cols and total_families_col:
    df_families['Couple_With_Kids'] = df_families[couple_kids_cols[0]]
    df_families['Total_Families'] = df_families[total_families_col[0]]
    df_families['Family_Pct'] = (df_families['Couple_With_Kids'] / df_families['Total_Families'] * 100).fillna(0)

# Median age and household size from df_medians
demographic_metrics = df_medians[['SAL_CODE_2021', 'Median_age_persons', 'Average_household_size']].copy()
demographic_metrics = demographic_metrics.merge(
    df_families[['SAL_CODE_2021', 'Family_Pct']] if 'Family_Pct' in df_families.columns else df_families[['SAL_CODE_2021']],
    on='SAL_CODE_2021',
    how='left'
)

print(f"   ✓ Demographic metrics calculated: Age, Household size, Family%")

# ============================================================================
# STEP 6: Calculate Quality Metrics - DENSITY
# ============================================================================
print("\n[6/11] Calculating population density metrics...")

# Merge population with area data
density_metrics = df_pop[['SAL_CODE_2021', 'Tot_P_P']].copy()
density_metrics.columns = ['SAL_CODE_2021', 'Total_Population']

# Add area from mapping
area_data = suburb_mapping[suburb_mapping['SAL_CODE'].isin(sydney_sal_codes)][['SAL_CODE', 'Area_sqkm']].copy()
area_data.columns = ['SAL_CODE_2021', 'Area_sqkm']
density_metrics = density_metrics.merge(area_data, on='SAL_CODE_2021', how='left')

density_metrics['Density_per_sqkm'] = (density_metrics['Total_Population'] / density_metrics['Area_sqkm']).fillna(0)

# Density score (0-100): Optimal range 1,000-5,000 per sq km
def density_score(density):
    """Score density with optimal range 1,000-5,000 per sq km"""
    if density < 100:
        return 10  # Too sparse
    elif density < 1000:
        return 50 + (density - 100) / 900 * 30  # 50-80 score
    elif density <= 5000:
        return 80 + (density - 1000) / 4000 * 20  # 80-100 score (optimal)
    elif density <= 10000:
        return 100 - (density - 5000) / 5000 * 30  # 100-70 score
    else:
        return max(40 - (density - 10000) / 10000 * 30, 10)  # 70-10 score (too dense)

density_metrics['Density_Score'] = density_metrics['Density_per_sqkm'].apply(density_score)

print(f"   ✓ Density metrics calculated: Persons/sqkm, Density score")

# ============================================================================
# STEP 7: Calculate Price Metrics - HOUSING COSTS
# ============================================================================
print("\n[7/11] Calculating housing cost (price) metrics...")

# Mortgage and rent from df_medians
price_metrics = df_medians[[
    'SAL_CODE_2021',
    'Median_mortgage_repay_monthly',
    'Median_rent_weekly',
    'Median_tot_prsnl_inc_weekly',
    'Median_tot_hhd_inc_weekly'
]].copy()

# Calculate affordability ratios
# Mortgage to income ratio (monthly mortgage / monthly income)
price_metrics['Monthly_Income'] = price_metrics['Median_tot_prsnl_inc_weekly'] * 52 / 12
price_metrics['Mortgage_to_Income_Ratio'] = (
    price_metrics['Median_mortgage_repay_monthly'] / price_metrics['Monthly_Income']
).fillna(0)

# Rent to income ratio (weekly rent / weekly income)
price_metrics['Rent_to_Income_Ratio'] = (
    price_metrics['Median_rent_weekly'] / price_metrics['Median_tot_prsnl_inc_weekly']
).fillna(0)

print(f"   ✓ Price metrics calculated: Mortgage, Rent, Affordability ratios")

# ============================================================================
# STEP 8: Build Master Dataset
# ============================================================================
print("\n[8/11] Building master dataset with all metrics...")

# Start with all median data as base
master_df = df_medians.copy()

# Add suburb names
master_df = master_df.merge(
    suburb_mapping[suburb_mapping['SAL_CODE'].isin(sydney_sal_codes)][['SAL_CODE', 'Suburb_Name']].rename(columns={'SAL_CODE': 'SAL_CODE_2021'}),
    on='SAL_CODE_2021',
    how='left'
)

# Merge all metrics (only new columns to avoid duplicates with df_medians)
master_df = master_df.merge(education_metrics, on='SAL_CODE_2021', how='left')
# employment_metrics has Median_tot_prsnl_inc_weekly already in master_df, only merge new columns
emp_cols_to_merge = ['SAL_CODE_2021']
if 'Prof_Manager_Pct' in employment_metrics.columns:
    emp_cols_to_merge.append('Prof_Manager_Pct')
if 'Employment_Rate' in employment_metrics.columns:
    emp_cols_to_merge.append('Employment_Rate')
if 'Unemployment_Rate' in employment_metrics.columns:
    emp_cols_to_merge.append('Unemployment_Rate')
if 'Fulltime_Pct' in employment_metrics.columns:
    emp_cols_to_merge.append('Fulltime_Pct')
master_df = master_df.merge(employment_metrics[emp_cols_to_merge], on='SAL_CODE_2021', how='left')

# demographic_metrics has columns already in master_df, only merge Family_Pct if available
if 'Family_Pct' in demographic_metrics.columns:
    master_df = master_df.merge(demographic_metrics[['SAL_CODE_2021', 'Family_Pct']], on='SAL_CODE_2021', how='left')

master_df = master_df.merge(density_metrics, on='SAL_CODE_2021', how='left')

# price_metrics has columns already in master_df, only merge new calculated columns
master_df = master_df.merge(
    price_metrics[['SAL_CODE_2021', 'Monthly_Income', 'Mortgage_to_Income_Ratio', 'Rent_to_Income_Ratio']],
    on='SAL_CODE_2021',
    how='left'
)

# Filter out suburbs with insufficient data (very low population)
master_df = master_df[
    (master_df['Total_Population'] >= 500) &  # At least 500 people
    (master_df['Median_mortgage_repay_monthly'] > 0) &  # Has mortgage data
    (master_df['Median_tot_prsnl_inc_weekly'] > 0)  # Has income data
].copy()

print(f"   ✓ Master dataset created: {len(master_df):,} Sydney suburbs with complete data")

# ============================================================================
# STEP 9: Calculate Composite Quality and Price Indices
# ============================================================================
print("\n[9/11] Calculating composite Quality and Price indices...")

# Normalize all metrics to 0-100 scale using percentile ranking
def normalize_metric(series, higher_is_better=True):
    """Normalize metric to 0-100 scale using percentile rank"""
    if higher_is_better:
        return series.rank(pct=True) * 100
    else:
        return (1 - series.rank(pct=True)) * 100

# QUALITY METRICS (higher is better)
master_df['Education_Index'] = (
    normalize_metric(master_df['Tertiary_Pct']) * 0.6 +
    normalize_metric(master_df['Year12_Pct'].fillna(0)) * 0.4
) if 'Year12_Pct' in master_df.columns else normalize_metric(master_df['Tertiary_Pct'])

# Employment Index - build with available metrics
employment_components = [normalize_metric(master_df['Median_tot_prsnl_inc_weekly']) * 0.4]
employment_weights = 0.4

if 'Prof_Manager_Pct' in master_df.columns:
    employment_components.append(normalize_metric(master_df['Prof_Manager_Pct'].fillna(0)) * 0.3)
    employment_weights += 0.3

if 'Employment_Rate' in master_df.columns:
    employment_components.append(normalize_metric(master_df['Employment_Rate'].fillna(95)) * 0.15)
    employment_weights += 0.15

if 'Fulltime_Pct' in master_df.columns:
    employment_components.append(normalize_metric(master_df['Fulltime_Pct'].fillna(50)) * 0.15)
    employment_weights += 0.15

# Normalize to 100 scale
master_df['Employment_Index'] = sum(employment_components) / employment_weights * 100

# Demographics: Age score (optimal 35-50)
def age_score(age):
    """Score age with optimal range 35-50"""
    if pd.isna(age):
        return 50
    if 35 <= age <= 50:
        return 100
    elif age < 35:
        return 50 + (age - 20) / 15 * 50
    else:
        return max(100 - (age - 50) / 20 * 50, 20)

master_df['Age_Score'] = master_df['Median_age_persons'].apply(age_score)

# Household size score (optimal 2.5-3.5)
def household_score(size):
    """Score household size with optimal range 2.5-3.5"""
    if pd.isna(size):
        return 50
    if 2.5 <= size <= 3.5:
        return 100
    elif size < 2.5:
        return 50 + (size - 1.5) / 1.0 * 50
    else:
        return max(100 - (size - 3.5) / 1.5 * 50, 20)

master_df['Household_Score'] = master_df['Average_household_size'].apply(household_score)

# Demographics Index - build with available metrics
demo_components = [
    master_df['Age_Score'] * 0.4,
    master_df['Household_Score'] * 0.3
]
demo_weights = 0.7

if 'Family_Pct' in master_df.columns:
    demo_components.append(normalize_metric(master_df['Family_Pct'].fillna(40)) * 0.3)
    demo_weights += 0.3

# Normalize to 100 scale
master_df['Demographics_Index'] = sum(demo_components) / demo_weights * 100

master_df['Density_Index'] = master_df['Density_Score']

# COMPOSITE QUALITY INDEX
master_df['Quality_Index'] = (
    master_df['Education_Index'] * 0.30 +      # 30% education
    master_df['Employment_Index'] * 0.30 +     # 30% employment
    master_df['Demographics_Index'] * 0.25 +   # 25% demographics
    master_df['Density_Index'] * 0.15          # 15% density
)

# PRICE METRICS (lower is better for affordability)
# Normalize mortgage (lower is better)
master_df['Mortgage_Index'] = normalize_metric(master_df['Median_mortgage_repay_monthly'], higher_is_better=False)

# Normalize rent (lower is better)
master_df['Rent_Index'] = normalize_metric(master_df['Median_rent_weekly'], higher_is_better=False)

# Affordability score (lower ratio is better)
master_df['Affordability_Index'] = normalize_metric(master_df['Mortgage_to_Income_Ratio'], higher_is_better=False)

# COMPOSITE PRICE INDEX (lower values = lower price = better value)
# Note: We invert this for the value calculation
master_df['Price_Index_Raw'] = (
    (100 - master_df['Mortgage_Index']) * 0.50 +      # 50% weight to mortgage
    (100 - master_df['Rent_Index']) * 0.25 +          # 25% weight to rent
    (100 - master_df['Affordability_Index']) * 0.25   # 25% weight to affordability
)

# For value calculation, we want high price to give low score
# So we use the inverted price index
master_df['Price_Index'] = 100 - master_df['Price_Index_Raw']

print(f"   ✓ Quality Index: {master_df['Quality_Index'].mean():.1f} average (0-100 scale)")
print(f"   ✓ Price Index: {master_df['Price_Index'].mean():.1f} average (0-100 scale)")

# ============================================================================
# STEP 10: Calculate VALUE SCORE
# ============================================================================
print("\n[10/11] Calculating VALUE SCORES (Quality / Price)...")

# Value Score = Quality Index / Price Index * 100
# Higher value = better value for money
master_df['Value_Score'] = (master_df['Quality_Index'] / (master_df['Price_Index'] + 1)) * 100

# Also calculate "undervalued" metric using regression
# Fit a linear regression: Quality ~ Price
from sklearn.linear_model import LinearRegression

X = master_df[['Price_Index']].values
y = master_df['Quality_Index'].values
model = LinearRegression()
model.fit(X, y)

master_df['Expected_Quality'] = model.predict(X)
master_df['Value_Residual'] = master_df['Quality_Index'] - master_df['Expected_Quality']
# Positive residual = undervalued (better quality than expected for price)
master_df['Undervalued_Score'] = normalize_metric(master_df['Value_Residual'])

print(f"   ✓ Value Score calculated: {master_df['Value_Score'].mean():.1f} average")
print(f"   ✓ Undervalued Score calculated (regression residuals)")

# ============================================================================
# STEP 11: Generate Results and Visualizations
# ============================================================================
print("\n[11/11] Generating results and visualizations...")

# Sort by Value Score
results_value = master_df.sort_values('Value_Score', ascending=False).copy()

# Create output columns for top results
output_cols = [
    'Suburb_Name', 'SAL_CODE_2021',
    'Value_Score', 'Undervalued_Score',
    'Quality_Index', 'Price_Index',
    'Education_Index', 'Employment_Index', 'Demographics_Index', 'Density_Index',
    'Tertiary_Pct', 'Year12_Pct',
    'Prof_Manager_Pct', 'Median_tot_prsnl_inc_weekly', 'Employment_Rate',
    'Median_age_persons', 'Average_household_size', 'Family_Pct',
    'Density_per_sqkm', 'Total_Population',
    'Median_mortgage_repay_monthly', 'Median_rent_weekly',
    'Mortgage_to_Income_Ratio', 'Median_tot_hhd_inc_weekly'
]

# Filter to available columns
output_cols = [col for col in output_cols if col in results_value.columns]

# Save top 100 value suburbs
top_100_value = results_value[output_cols].head(100)
top_100_value.to_csv(f'{OUTPUT_DIR}/sydney_top_100_value_suburbs.csv', index=False)
print(f"   ✓ Saved: sydney_top_100_value_suburbs.csv")

# Save top 50 undervalued suburbs (best quality for price via regression)
results_undervalued = master_df.sort_values('Undervalued_Score', ascending=False).copy()
top_50_undervalued = results_undervalued[output_cols].head(50)
top_50_undervalued.to_csv(f'{OUTPUT_DIR}/sydney_top_50_undervalued_suburbs.csv', index=False)
print(f"   ✓ Saved: sydney_top_50_undervalued_suburbs.csv")

# Save all Sydney suburbs with scores
master_df[output_cols].to_csv(f'{OUTPUT_DIR}/sydney_all_suburbs_value_analysis.csv', index=False)
print(f"   ✓ Saved: sydney_all_suburbs_value_analysis.csv ({len(master_df):,} suburbs)")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n   Creating visualizations...")

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

# Create 2x2 subplot figure
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Sydney Family Home Value Analysis', fontsize=20, fontweight='bold', y=0.995)

# Plot 1: Quality vs Price Scatter with Efficient Frontier
ax1 = axes[0, 0]
scatter = ax1.scatter(
    master_df['Price_Index'],
    master_df['Quality_Index'],
    c=master_df['Value_Score'],
    s=master_df['Total_Population'] / 100,
    alpha=0.6,
    cmap='RdYlGn',
    edgecolors='black',
    linewidth=0.5
)
# Add regression line (efficient frontier)
price_range = np.linspace(master_df['Price_Index'].min(), master_df['Price_Index'].max(), 100)
quality_pred = model.predict(price_range.reshape(-1, 1))
ax1.plot(price_range, quality_pred, 'b--', linewidth=2, label='Efficient Frontier', alpha=0.7)

# Label top 10 value suburbs
top_10 = results_value.head(10)
for _, row in top_10.iterrows():
    ax1.annotate(
        row['Suburb_Name'],
        (row['Price_Index'], row['Quality_Index']),
        fontsize=7,
        alpha=0.8,
        xytext=(5, 5),
        textcoords='offset points'
    )

ax1.set_xlabel('Price Index (Higher = More Expensive)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Quality Index (Higher = Better Quality)', fontsize=12, fontweight='bold')
ax1.set_title('Quality vs Price - Sydney Suburbs\n(Size = Population, Color = Value Score)', fontsize=14, fontweight='bold')
ax1.legend()
plt.colorbar(scatter, ax=ax1, label='Value Score')
ax1.grid(True, alpha=0.3)

# Plot 2: Value Score Distribution
ax2 = axes[0, 1]
ax2.hist(master_df['Value_Score'], bins=40, color='green', alpha=0.7, edgecolor='black')
ax2.axvline(master_df['Value_Score'].median(), color='red', linestyle='--', linewidth=2, label=f'Median: {master_df["Value_Score"].median():.1f}')
ax2.axvline(master_df['Value_Score'].mean(), color='blue', linestyle='--', linewidth=2, label=f'Mean: {master_df["Value_Score"].mean():.1f}')
ax2.set_xlabel('Value Score', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Suburbs', fontsize=12, fontweight='bold')
ax2.set_title('Distribution of Value Scores\nAcross Sydney Suburbs', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# Plot 3: Top 20 Value Suburbs Bar Chart
ax3 = axes[1, 0]
top_20 = results_value.head(20)
y_pos = np.arange(len(top_20))
bars = ax3.barh(y_pos, top_20['Value_Score'], color='darkgreen', alpha=0.8, edgecolor='black')
ax3.set_yticks(y_pos)
ax3.set_yticklabels(top_20['Suburb_Name'], fontsize=9)
ax3.invert_yaxis()
ax3.set_xlabel('Value Score', fontsize=12, fontweight='bold')
ax3.set_title('Top 20 Value Suburbs for Families\n(Best Quality/Price Ratio)', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# Add value scores as labels
for i, (idx, row) in enumerate(top_20.iterrows()):
    ax3.text(row['Value_Score'] + 1, i, f"{row['Value_Score']:.1f}", va='center', fontsize=8)

# Plot 4: Component Breakdown for Top 10
ax4 = axes[1, 1]
top_10_indices = results_value.head(10)
components = ['Education_Index', 'Employment_Index', 'Demographics_Index', 'Density_Index']
component_labels = ['Education', 'Employment', 'Demographics', 'Density']

x = np.arange(len(top_10_indices))
width = 0.2

for i, (comp, label) in enumerate(zip(components, component_labels)):
    offset = (i - 1.5) * width
    ax4.bar(x + offset, top_10_indices[comp], width, label=label, alpha=0.8, edgecolor='black')

ax4.set_xlabel('Suburb', fontsize=12, fontweight='bold')
ax4.set_ylabel('Component Score (0-100)', fontsize=12, fontweight='bold')
ax4.set_title('Quality Index Breakdown - Top 10 Value Suburbs', fontsize=14, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(top_10_indices['Suburb_Name'], rotation=45, ha='right', fontsize=8)
ax4.legend(loc='upper right')
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/sydney_value_analysis_charts.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: sydney_value_analysis_charts.png")

# Additional visualization: Price vs Mortgage scatter
fig2, ax = plt.subplots(figsize=(14, 10))
scatter2 = ax.scatter(
    master_df['Median_mortgage_repay_monthly'],
    master_df['Quality_Index'],
    c=master_df['Value_Score'],
    s=100,
    alpha=0.6,
    cmap='RdYlGn',
    edgecolors='black',
    linewidth=0.5
)

# Label top 15 value suburbs
top_15 = results_value.head(15)
for _, row in top_15.iterrows():
    ax.annotate(
        row['Suburb_Name'],
        (row['Median_mortgage_repay_monthly'], row['Quality_Index']),
        fontsize=8,
        alpha=0.8,
        xytext=(5, 5),
        textcoords='offset points'
    )

ax.set_xlabel('Median Monthly Mortgage Repayment ($)', fontsize=14, fontweight='bold')
ax.set_ylabel('Quality Index (0-100)', fontsize=14, fontweight='bold')
ax.set_title('Quality vs Median Mortgage - Sydney Suburbs\n(Color = Value Score)', fontsize=16, fontweight='bold')
plt.colorbar(scatter2, ax=ax, label='Value Score')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/sydney_quality_vs_mortgage.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: sydney_quality_vs_mortgage.png")

# ============================================================================
# SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 120)
print(" " * 40 + "ANALYSIS COMPLETE - SUMMARY REPORT")
print("=" * 120)

print(f"\n📊 DATASET SUMMARY:")
print(f"   • Total Sydney suburbs analyzed: {len(master_df):,}")
print(f"   • Suburbs with complete data: {len(master_df):,}")
print(f"   • Total population covered: {master_df['Total_Population'].sum():,.0f}")

print(f"\n🎯 TOP 10 VALUE SUBURBS FOR FAMILIES:")
print(f"{'Rank':<6}{'Suburb':<35}{'Value':>8}  {'Quality':>8}  {'Price':>8}  {'Mortgage':>10}  {'Income':>10}")
print("-" * 105)
for i, (_, row) in enumerate(results_value.head(10).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<35}{row['Value_Score']:>8.1f}  "
          f"{row['Quality_Index']:>8.1f}  {row['Price_Index']:>8.1f}  "
          f"${row['Median_mortgage_repay_monthly']:>9,.0f}  "
          f"${row['Median_tot_prsnl_inc_weekly']:>9,.0f}/w")

print(f"\n💎 TOP 10 UNDERVALUED SUBURBS (Best Quality for Price via Regression):")
print(f"{'Rank':<6}{'Suburb':<35}{'Underval':>10}  {'Quality':>8}  {'Expected':>10}  {'Surplus':>8}")
print("-" * 105)
for i, (_, row) in enumerate(results_undervalued.head(10).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<35}{row['Undervalued_Score']:>10.1f}  "
          f"{row['Quality_Index']:>8.1f}  {row['Expected_Quality']:>10.1f}  "
          f"{row['Value_Residual']:>+8.1f}")

print(f"\n📈 KEY STATISTICS:")
print(f"   Average Quality Index: {master_df['Quality_Index'].mean():.1f}")
print(f"   Average Price Index: {master_df['Price_Index'].mean():.1f}")
print(f"   Average Value Score: {master_df['Value_Score'].mean():.1f}")
print(f"   Median Monthly Mortgage: ${master_df['Median_mortgage_repay_monthly'].median():,.0f}")
print(f"   Median Weekly Income: ${master_df['Median_tot_prsnl_inc_weekly'].median():,.0f}")
print(f"   Average Tertiary Education: {master_df['Tertiary_Pct'].mean():.1f}%")

print(f"\n📁 OUTPUT FILES:")
print(f"   • sydney_top_100_value_suburbs.csv - Top 100 suburbs by value score")
print(f"   • sydney_top_50_undervalued_suburbs.csv - Top 50 undervalued suburbs")
print(f"   • sydney_all_suburbs_value_analysis.csv - Complete dataset ({len(master_df):,} suburbs)")
print(f"   • sydney_value_analysis_charts.png - 4-panel visualization")
print(f"   • sydney_quality_vs_mortgage.png - Quality vs Mortgage scatter plot")

print("\n" + "=" * 120)
print(" " * 35 + "VALUE MODEL BUILD COMPLETE!")
print("=" * 120)
print()
