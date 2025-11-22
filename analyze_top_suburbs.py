#!/usr/bin/env python3
"""
Analyze Australian Census 2021 Data
Find suburbs with highest tertiary education, income, and oldest age
"""

import csv
import pandas as pd

# File paths
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
MAPPING_FILE = "/home/user/Census/SAL_Suburb_Name_Mapping.csv"

print("="*100)
print("AUSTRALIAN CENSUS 2021 - TOP SUBURBS ANALYSIS")
print("="*100)

# Load suburb name mapping
print("\nLoading suburb name mapping...")
suburb_names = {}
with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        suburb_names[row['SAL_CODE']] = row['Suburb_Name']

print(f"Loaded {len(suburb_names):,} suburb names")

# ============================================================================
# PART 1: Top Suburbs by Median Age (Oldest Population)
# ============================================================================
print("\n" + "="*100)
print("TOP 20 SUBURBS WITH OLDEST MEDIAN AGE")
print("="*100)

df_medians = pd.read_csv(f"{DATA_DIR}2021Census_G02_AUST_SAL.csv")
df_medians['Suburb_Name'] = df_medians['SAL_CODE_2021'].map(suburb_names)

# Filter out suburbs with very low population (using median income as proxy)
df_medians_filtered = df_medians[df_medians['Median_tot_prsnl_inc_weekly'] > 0]

top_age = df_medians_filtered.nlargest(20, 'Median_age_persons')[
    ['Suburb_Name', 'SAL_CODE_2021', 'Median_age_persons',
     'Median_tot_prsnl_inc_weekly', 'Median_tot_hhd_inc_weekly']
]

for idx, row in top_age.iterrows():
    print(f"{row['Suburb_Name']:45} | Age: {row['Median_age_persons']:4} | "
          f"Personal Income: ${row['Median_tot_prsnl_inc_weekly']:6}/week | "
          f"Household: ${row['Median_tot_hhd_inc_weekly']:6}/week")

# ============================================================================
# PART 2: Top Suburbs by Median Income
# ============================================================================
print("\n" + "="*100)
print("TOP 20 SUBURBS WITH HIGHEST MEDIAN PERSONAL INCOME")
print("="*100)

top_income = df_medians_filtered.nlargest(20, 'Median_tot_prsnl_inc_weekly')[
    ['Suburb_Name', 'SAL_CODE_2021', 'Median_age_persons',
     'Median_tot_prsnl_inc_weekly', 'Median_tot_hhd_inc_weekly']
]

for idx, row in top_income.iterrows():
    print(f"{row['Suburb_Name']:45} | Income: ${row['Median_tot_prsnl_inc_weekly']:6}/week | "
          f"Age: {row['Median_age_persons']:4} | "
          f"Household: ${row['Median_tot_hhd_inc_weekly']:6}/week")

# ============================================================================
# PART 3: Top Suburbs by Tertiary Education
# ============================================================================
print("\n" + "="*100)
print("TOP 20 SUBURBS WITH HIGHEST TERTIARY EDUCATION (Bachelor Degree or Higher)")
print("="*100)

# Load education data (Males)
df_edu_m = pd.read_csv(f"{DATA_DIR}2021Census_G49A_AUST_SAL.csv")

# Calculate total people with Bachelor degree or higher (Males)
# Postgraduate Degrees
pgr_cols_m = [col for col in df_edu_m.columns if 'M_PGrad_Deg_' in col and 'Total' not in col]
# Graduate Diplomas/Certificates
grad_cols_m = [col for col in df_edu_m.columns if 'M_GradDip_and_GradCert_' in col and 'Total' not in col]
# Bachelor Degrees
bach_cols_m = [col for col in df_edu_m.columns if 'M_BachDeg_' in col and 'Total' not in col]

df_edu_m['Tertiary_Males'] = (
    df_edu_m[pgr_cols_m].sum(axis=1) +
    df_edu_m[grad_cols_m].sum(axis=1) +
    df_edu_m[bach_cols_m].sum(axis=1)
)

# Load education data (Females) - Note: G49B contains both F and P (Persons) data
df_edu_f = pd.read_csv(f"{DATA_DIR}2021Census_G49B_AUST_SAL.csv")

# Calculate total people with Bachelor degree or higher (Females)
pgr_cols_f = [col for col in df_edu_f.columns if 'F_PGrad_Deg_' in col and 'Total' not in col]
grad_cols_f = [col for col in df_edu_f.columns if 'F_GradDip_and_GradCert_' in col and 'Total' not in col]
bach_cols_f = [col for col in df_edu_f.columns if 'F_BachDeg_' in col and 'Total' not in col]

df_edu_f['Tertiary_Females'] = (
    df_edu_f[pgr_cols_f].sum(axis=1) +
    df_edu_f[grad_cols_f].sum(axis=1) +
    df_edu_f[bach_cols_f].sum(axis=1)
)

# Merge male and female data
df_edu = df_edu_m[['SAL_CODE_2021', 'Tertiary_Males']].merge(
    df_edu_f[['SAL_CODE_2021', 'Tertiary_Females']],
    on='SAL_CODE_2021'
)

df_edu['Tertiary_Total'] = df_edu['Tertiary_Males'] + df_edu['Tertiary_Females']
df_edu['Suburb_Name'] = df_edu['SAL_CODE_2021'].map(suburb_names)

# Merge with median data for context
df_edu = df_edu.merge(
    df_medians[['SAL_CODE_2021', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly']],
    on='SAL_CODE_2021',
    how='left'
)

# Filter suburbs with at least 100 people with tertiary education (to avoid tiny suburbs)
df_edu_filtered = df_edu[df_edu['Tertiary_Total'] >= 100]

top_education = df_edu_filtered.nlargest(20, 'Tertiary_Total')[
    ['Suburb_Name', 'SAL_CODE_2021', 'Tertiary_Total', 'Tertiary_Males',
     'Tertiary_Females', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly']
]

for idx, row in top_education.iterrows():
    print(f"{row['Suburb_Name']:45} | Tertiary: {row['Tertiary_Total']:7,} people | "
          f"Age: {row['Median_age_persons']:4} | "
          f"Income: ${row['Median_tot_prsnl_inc_weekly']:6}/week")

# ============================================================================
# PART 4: Combined Analysis - High Education + High Income + Older Age
# ============================================================================
print("\n" + "="*100)
print("TOP 20 SUBURBS: HIGH TERTIARY EDUCATION + HIGH INCOME + OLDER AGE")
print("(Normalized ranking combining all three factors)")
print("="*100)

# Create normalized scores (0-1 scale)
df_combined = df_edu_filtered.copy()
df_combined = df_combined.merge(
    df_medians[['SAL_CODE_2021', 'Median_tot_hhd_inc_weekly']],
    on='SAL_CODE_2021',
    how='left'
)

# Calculate percentile ranks (higher is better)
df_combined['Education_Score'] = df_combined['Tertiary_Total'].rank(pct=True)
df_combined['Income_Score'] = df_combined['Median_tot_prsnl_inc_weekly'].rank(pct=True)
df_combined['Age_Score'] = df_combined['Median_age_persons'].rank(pct=True)

# Combined score (equal weighting)
df_combined['Combined_Score'] = (
    df_combined['Education_Score'] +
    df_combined['Income_Score'] +
    df_combined['Age_Score']
) / 3

top_combined = df_combined.nlargest(20, 'Combined_Score')[
    ['Suburb_Name', 'SAL_CODE_2021', 'Combined_Score',
     'Tertiary_Total', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly',
     'Median_tot_hhd_inc_weekly']
]

for idx, row in top_combined.iterrows():
    print(f"{row['Suburb_Name']:45} | Score: {row['Combined_Score']:.3f} | "
          f"Tertiary: {row['Tertiary_Total']:6,} | "
          f"Age: {row['Median_age_persons']:4} | "
          f"Income: ${row['Median_tot_prsnl_inc_weekly']:6}/week")

# ============================================================================
# Save results to CSV
# ============================================================================
print("\n" + "="*100)
print("SAVING RESULTS TO CSV FILES")
print("="*100)

top_age.to_csv('/home/user/Census/results_top_age.csv', index=False)
print("✓ Saved: /home/user/Census/results_top_age.csv")

top_income.to_csv('/home/user/Census/results_top_income.csv', index=False)
print("✓ Saved: /home/user/Census/results_top_income.csv")

top_education.to_csv('/home/user/Census/results_top_education.csv', index=False)
print("✓ Saved: /home/user/Census/results_top_education.csv")

top_combined.to_csv('/home/user/Census/results_top_combined.csv', index=False)
print("✓ Saved: /home/user/Census/results_top_combined.csv")

print("\n" + "="*100)
print("ANALYSIS COMPLETE!")
print("="*100)
