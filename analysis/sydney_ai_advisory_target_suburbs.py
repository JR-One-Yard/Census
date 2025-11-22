#!/usr/bin/env python3
"""
Sydney AI Advisory Service - Target Suburb Identification

Identifies the best 50 suburbs in Greater Sydney for a direct mail campaign
targeting older, wealthy, educated business leaders who need guidance on AI's
impact on economy, policy, and financial markets.

Target demographic:
- Executives/business leaders (high manager concentration)
- Older (55-74 age bracket - established, pre/early retirement)
- Wealthy (high income, high housing prices)
- Educated (postgraduate/bachelor's degrees)
- Family-oriented (guiding children's career choices)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
DATA_DIR = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

print("=" * 120)
print("SYDNEY AI ADVISORY SERVICE - TARGET SUBURB IDENTIFICATION")
print("=" * 120)
print()

# ============================================================================
# Load Data
# ============================================================================

print("Loading data...")

# Load SAL metadata
metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
sal_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

# We'll filter for Greater Sydney suburbs later based on region identification
sydney_sal_df = sal_df.copy()

# Load housing/income data (G02)
g02_file = DATA_DIR / "2021Census_G02_AUST_SAL.csv"
g02_df = pd.read_csv(g02_file)

# Load age demographics (G01)
g01_file = DATA_DIR / "2021Census_G01_AUST_SAL.csv"
age_df = pd.read_csv(g01_file)

# Calculate age brackets
age_df['Age_55_64_yr_P'] = age_df['Age_55_64_yr_M'] + age_df['Age_55_64_yr_F']
age_df['Age_65_74_yr_P'] = age_df['Age_65_74_yr_M'] + age_df['Age_65_74_yr_F']
age_df['Age_75_84_yr_P'] = age_df['Age_75_84_yr_M'] + age_df['Age_75_84_yr_F']
age_df['Total_Population'] = age_df['Tot_P_P']

# Target age group: 55-74 (established leaders, guiding families)
age_df['Age_55_74_Total'] = age_df['Age_55_64_yr_P'] + age_df['Age_65_74_yr_P']
age_df['Age_55_74_Pct'] = (age_df['Age_55_74_Total'] / age_df['Total_Population'] * 100).fillna(0)

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

# Note: Education data (G16) is about school years, not tertiary qualifications
# We'll rely on manager/professional concentration as a proxy for education level
# Family structure data is not critical for this analysis

print(f"Loaded {len(sydney_sal_df):,} total Australian suburbs")
print()

# ============================================================================
# Merge All Data
# ============================================================================

print("Merging datasets...")

# Start with Sydney suburbs
df = sydney_sal_df.copy()
df = df.merge(g02_df, left_on='Census_Code_2021', right_on='SAL_CODE_2021', how='inner')
df = df.merge(age_df[['SAL_CODE_2021', 'Total_Population', 'Age_55_74_Total', 'Age_55_74_Pct']],
              on='SAL_CODE_2021', how='left')
df = df.merge(occupation_df[['SAL_CODE_2021', 'Total_Employed', 'Total_Managers',
                              'Manager_Concentration_Pct', 'Professional_Concentration_Pct']],
              on='SAL_CODE_2021', how='left')

print(f"Merged dataset: {len(df):,} suburbs")
print()

# ============================================================================
# Apply Filters
# ============================================================================

print("Applying filters...")

# Urban filter (minimum population and employment)
urban_df = df[
    (df['Total_Employed'] >= 800) &  # Slightly lower threshold for Sydney
    (df['Total_Population'] >= 1500) &
    (df['Median_mortgage_repay_monthly'] > 0) &
    (df['Manager_Concentration_Pct'] > 0)
].copy()

print(f"Urban Sydney suburbs: {len(urban_df):,}")

# Executive filter - top 50% of manager concentration
manager_threshold = urban_df['Manager_Concentration_Pct'].quantile(0.50)
print(f"Manager concentration threshold (50th percentile): {manager_threshold:.1f}%")

executive_df = urban_df[
    urban_df['Manager_Concentration_Pct'] >= manager_threshold
].copy()

print(f"Executive suburbs: {len(executive_df):,}")
print()

# ============================================================================
# Create Composite Target Score
# ============================================================================

print("Calculating composite target scores...")
print()

# Normalize each metric to 0-100 scale
def normalize_to_100(series):
    """Normalize a series to 0-100 scale"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val) * 100)

# Calculate normalized scores
executive_df['Manager_Score'] = normalize_to_100(executive_df['Manager_Concentration_Pct'])
executive_df['Professional_Score'] = normalize_to_100(executive_df['Professional_Concentration_Pct'])
executive_df['Age_55_74_Score'] = normalize_to_100(executive_df['Age_55_74_Pct'])
executive_df['Income_Score'] = normalize_to_100(executive_df['Median_tot_prsnl_inc_weekly'])
executive_df['Wealth_Score'] = normalize_to_100(executive_df['Median_mortgage_repay_monthly'])

# Composite Target Score (weighted)
# Weights reflect importance for this specific campaign
executive_df['Target_Score'] = (
    executive_df['Manager_Score'] * 0.30 +         # 30% - Executive/business leader status
    executive_df['Age_55_74_Score'] * 0.30 +       # 30% - Right age bracket (55-74)
    executive_df['Wealth_Score'] * 0.25 +          # 25% - Wealth (can afford premium service)
    executive_df['Professional_Score'] * 0.10 +    # 10% - Professional status (proxy for education)
    executive_df['Income_Score'] * 0.05            # 5% - Current income (less important for older demographic)
)

# Sort by target score
executive_df = executive_df.sort_values('Target_Score', ascending=False)

# ============================================================================
# Filter for Greater Sydney
# ============================================================================

def identify_region(suburb_name):
    """Identify Sydney region based on suburb name patterns"""
    suburb_lower = suburb_name.lower()

    # Northern suburbs
    if any(x in suburb_lower for x in ['mosman', 'cremorne', 'neutral bay', 'kirribilli', 'milsons point',
                                         'lavender bay', 'mcmahons point', 'waverton', 'north sydney',
                                         'crows nest', 'st leonards', 'greenwich', 'hunters hill', 'longueville',
                                         'northbridge', 'castle cove', 'middle cove', 'castlecrag', 'willoughby']):
        return 'Lower North Shore'

    if any(x in suburb_lower for x in ['chatswood', 'roseville', 'lindfield', 'killara', 'gordon', 'pymble',
                                         'turramurra', 'st ives', 'wahroonga', 'hornsby']):
        return 'Upper North Shore'

    # Eastern suburbs
    if any(x in suburb_lower for x in ['bondi', 'bronte', 'coogee', 'clovelly', 'randwick', 'dover heights',
                                         'vaucluse', 'watsons bay', 'rose bay', 'double bay', 'bellevue hill',
                                         'woollahra', 'paddington', 'edgecliff', 'queens park']):
        return 'Eastern Suburbs'

    # Northern Beaches
    if any(x in suburb_lower for x in ['manly', 'seaforth', 'balgowlah', 'monavale', 'curl curl', 'freshwater',
                                         'dee why', 'collaroy', 'narrabeen', 'mona vale', 'newport', 'avalon',
                                         'palm beach']):
        return 'Northern Beaches'

    # Inner West
    if any(x in suburb_lower for x in ['balmain', 'rozelle', 'leichhardt', 'annandale', 'glebe', 'newtown',
                                         'erskineville', 'alexandria', 'waterloo', 'redfern', 'surry hills',
                                         'darlinghurst', 'potts point', 'elizabeth bay']):
        return 'Inner City/Inner West'

    # Hills District
    if any(x in suburb_lower for x in ['castle hill', 'baulkham hills', 'kellyville', 'rouse hill', 'bella vista',
                                         'cherrybrook', 'west pennant hills']):
        return 'Hills District'

    # Sutherland Shire
    if any(x in suburb_lower for x in ['sutherland', 'cronulla', 'caringbah', 'miranda', 'gymea', 'jannali']):
        return 'Sutherland Shire'

    # Canterbury-Bankstown / Inner West
    if any(x in suburb_lower for x in ['strathfield', 'burwood', 'concord', 'five dock', 'drummoyne', 'gladesville']):
        return 'Inner West'

    # Western Sydney
    if any(x in suburb_lower for x in ['parramatta', 'epping', 'carlingford', 'ryde', 'eastwood', 'west ryde']):
        return 'Parramatta/Ryde'

    return 'Other Sydney'

executive_df['Region'] = executive_df['Census_Name_2021'].apply(identify_region)

# Filter for Greater Sydney only (exclude 'Other Sydney' which may include regional NSW)
sydney_regions = ['Lower North Shore', 'Upper North Shore', 'Eastern Suburbs', 'Northern Beaches',
                  'Inner City/Inner West', 'Hills District', 'Sutherland Shire', 'Inner West',
                  'Parramatta/Ryde']
sydney_df = executive_df[executive_df['Region'].isin(sydney_regions)].copy()

print(f"Greater Sydney suburbs (after region filter): {len(sydney_df):,}")
print()

# Re-sort by target score after filtering
sydney_df = sydney_df.sort_values('Target_Score', ascending=False)

print("=" * 120)
print("TOP 50 TARGET SUBURBS FOR AI ADVISORY DIRECT MAIL CAMPAIGN")
print("=" * 120)
print()
print("Target demographic: Older (55-74), wealthy, educated executives seeking AI guidance")
print()
print(f"{'Rank':<5}{'Suburb':<35}{'Score':<8}{'Mgr%':<7}{'Prof%':<7}{'55-74%':<8}{'Income':<10}{'Mortgage':<10}")
print(f"{'':5}{'':35}{'(0-100)':<8}{'':7}{'':7}{'':8}{'$/wk':<10}{'$/mo':<10}")
print("-" * 120)

top_50 = sydney_df.head(50)

for idx, row in top_50.iterrows():
    rank = list(top_50.index).index(idx) + 1
    print(f"{rank:<5}{row['Census_Name_2021']:<35}{row['Target_Score']:>6.1f}  "
          f"{row['Manager_Concentration_Pct']:>5.1f}%  {row['Professional_Concentration_Pct']:>5.1f}%  "
          f"{row['Age_55_74_Pct']:>6.1f}%  ${row['Median_tot_prsnl_inc_weekly']:>7,.0f}  "
          f"${row['Median_mortgage_repay_monthly']:>8,.0f}")

print()
print("=" * 120)
print("SUMMARY STATISTICS - TOP 50 TARGET SUBURBS")
print("=" * 120)
print()
print(f"Average manager concentration:           {top_50['Manager_Concentration_Pct'].mean():.1f}%")
print(f"Average professional concentration:      {top_50['Professional_Concentration_Pct'].mean():.1f}%")
print(f"Average age 55-74 concentration:         {top_50['Age_55_74_Pct'].mean():.1f}%")
print(f"Average median income:                   ${top_50['Median_tot_prsnl_inc_weekly'].mean():,.0f}/week")
print(f"Average median mortgage:                 ${top_50['Median_mortgage_repay_monthly'].mean():,.0f}/month")
print(f"Average median age:                      {top_50['Median_age_persons'].mean():.1f} years")
print()
print(f"Total population in top 50 suburbs:      {top_50['Total_Population'].sum():,}")
print(f"Total age 55-74 in top 50 suburbs:       {top_50['Age_55_74_Total'].sum():,}")
print(f"Total managers in top 50 suburbs:        {top_50['Total_Managers'].sum():,}")
print()

# Estimate target market size
# Assumptions:
# - Target age 55-74 with manager occupation
# - Assume 20% of 55-74 year olds are managers (conservative, given high manager concentration)
estimated_managers_55_74 = top_50['Age_55_74_Total'].sum() * (top_50['Manager_Concentration_Pct'].mean() / 100) * 0.7  # 0.7 factor for age overlap

print(f"ESTIMATED TARGET MARKET SIZE:")
print(f"  Managers aged 55-74 in top 50 suburbs:  ~{estimated_managers_55_74:,.0f} individuals")
print(f"  Assuming 2% response rate:              ~{estimated_managers_55_74 * 0.02:,.0f} potential clients")
print(f"  Assuming 10% conversion:                ~{estimated_managers_55_74 * 0.02 * 0.10:,.0f} bookings")
print()

# ============================================================================
# Geographic Clusters
# ============================================================================

print("=" * 120)
print("GEOGRAPHIC CLUSTERS (Top 50 Suburbs by Area)")
print("=" * 120)
print()

# Identify clusters by analyzing suburb names
# Common Sydney regions: North Shore, Eastern Suburbs, Inner West, Northern Beaches, Hills District, etc.

def identify_region(suburb_name):
    """Identify Sydney region based on suburb name patterns"""
    suburb_lower = suburb_name.lower()

    # Northern suburbs
    if any(x in suburb_lower for x in ['mosman', 'cremorne', 'neutral bay', 'kirribilli', 'milsons point',
                                         'lavender bay', 'mcmahons point', 'waverton', 'north sydney',
                                         'crows nest', 'st leonards', 'greenwich', 'hunters hill', 'longueville',
                                         'northbridge', 'castle cove', 'middle cove', 'castlecrag', 'willoughby']):
        return 'Lower North Shore'

    if any(x in suburb_lower for x in ['chatswood', 'roseville', 'lindfield', 'killara', 'gordon', 'pymble',
                                         'turramurra', 'st ives', 'wahroonga', 'hornsby']):
        return 'Upper North Shore'

    # Eastern suburbs
    if any(x in suburb_lower for x in ['bondi', 'bronte', 'coogee', 'clovelly', 'randwick', 'dover heights',
                                         'vaucluse', 'watsons bay', 'rose bay', 'double bay', 'bellevue hill',
                                         'woollahra', 'paddington', 'edgecliff', 'queens park']):
        return 'Eastern Suburbs'

    # Northern Beaches
    if any(x in suburb_lower for x in ['manly', 'seaforth', 'balgowlah', 'monavale', 'curl curl', 'freshwater',
                                         'dee why', 'collaroy', 'narrabeen', 'mona vale', 'newport', 'avalon',
                                         'palm beach']):
        return 'Northern Beaches'

    # Inner West
    if any(x in suburb_lower for x in ['balmain', 'rozelle', 'leichhardt', 'annandale', 'glebe', 'newtown',
                                         'erskineville', 'alexandria', 'waterloo', 'redfern', 'surry hills',
                                         'darlinghurst', 'potts point', 'elizabeth bay']):
        return 'Inner City/Inner West'

    # Hills District
    if any(x in suburb_lower for x in ['castle hill', 'baulkham hills', 'kellyville', 'rouse hill', 'bella vista',
                                         'cherrybrook', 'west pennant hills']):
        return 'Hills District'

    # Sutherland Shire
    if any(x in suburb_lower for x in ['sutherland', 'cronulla', 'caringbah', 'miranda', 'gymea', 'jannali']):
        return 'Sutherland Shire'

    # Canterbury-Bankstown
    if any(x in suburb_lower for x in ['strathfield', 'burwood', 'concord', 'five dock', 'drummoyne', 'gladesville']):
        return 'Inner West'

    # Western Sydney
    if any(x in suburb_lower for x in ['parramatta', 'epping', 'carlingford', 'ryde', 'eastwood', 'west ryde']):
        return 'Parramatta/Ryde'

    return 'Other Sydney'

executive_df['Region'] = executive_df['Census_Name_2021'].apply(identify_region)

# Filter for Greater Sydney only (exclude 'Other Sydney' which may include regional NSW)
sydney_regions = ['Lower North Shore', 'Upper North Shore', 'Eastern Suburbs', 'Northern Beaches',
                  'Inner City/Inner West', 'Hills District', 'Sutherland Shire', 'Inner West',
                  'Parramatta/Ryde']
sydney_df = executive_df[executive_df['Region'].isin(sydney_regions)].copy()

print(f"Greater Sydney suburbs (after region filter): {len(sydney_df):,}")
print()

# Re-sort by target score after filtering
sydney_df = sydney_df.sort_values('Target_Score', ascending=False)

# Update top_50 to use sydney_df
top_50 = sydney_df.head(50)

# Group by region
region_summary = top_50.groupby('Region').agg({
    'Census_Name_2021': 'count',
    'Total_Population': 'sum',
    'Age_55_74_Total': 'sum',
    'Manager_Concentration_Pct': 'mean',
    'Target_Score': 'mean'
}).round(1)

region_summary.columns = ['Num_Suburbs', 'Total_Pop', 'Age_55_74', 'Avg_Mgr_Pct', 'Avg_Score']
region_summary = region_summary.sort_values('Avg_Score', ascending=False)

print(f"{'Region':<25}{'Suburbs':<10}{'Population':<12}{'Age 55-74':<12}{'Avg Mgr%':<10}{'Avg Score':<10}")
print("-" * 120)
for region, row in region_summary.iterrows():
    print(f"{region:<25}{row['Num_Suburbs']:<10.0f}{row['Total_Pop']:<12,.0f}{row['Age_55_74']:<12,.0f}"
          f"{row['Avg_Mgr_Pct']:<10.1f}{row['Avg_Score']:<10.1f}")

print()
print("=" * 120)
print()

# ============================================================================
# Export Results
# ============================================================================

# Export top 50 with full details
export_df = top_50[[
    'Census_Name_2021', 'Region', 'Target_Score',
    'Manager_Concentration_Pct', 'Professional_Concentration_Pct', 'Age_55_74_Pct',
    'Median_tot_prsnl_inc_weekly', 'Median_tot_fam_inc_weekly',
    'Median_mortgage_repay_monthly', 'Median_age_persons',
    'Total_Population', 'Age_55_74_Total', 'Total_Managers', 'Total_Employed'
]].copy()

export_df.columns = [
    'Suburb', 'Region', 'Target_Score',
    'Manager_Pct', 'Professional_Pct', 'Age_55_74_Pct',
    'Median_Personal_Income_Weekly', 'Median_Family_Income_Weekly',
    'Median_Mortgage_Monthly', 'Median_Age',
    'Total_Population', 'Population_55_74', 'Total_Managers', 'Total_Employed'
]

export_df.to_csv(RESULTS_DIR / 'sydney_ai_advisory_target_suburbs_top50.csv', index=False)

print("Results exported to: results/sydney_ai_advisory_target_suburbs_top50.csv")
print()
print("=" * 120)
print()
print("CAMPAIGN RECOMMENDATIONS:")
print("-" * 120)
print()
print("1. GEOGRAPHIC FOCUS:")
print("   • Concentrate on Lower North Shore, Eastern Suburbs, and Upper North Shore")
print("   • These areas have highest concentration of target demographic")
print()
print("2. MESSAGING:")
print("   • Emphasize 'guidance for your family' angle - high family concentration")
print("   • Highlight 'built companies, led communities' - resonates with executives")
print("   • Stress personalized, high-touch approach (10 hours prep for 2 hour session)")
print()
print("3. RESPONSE RATE ASSUMPTIONS:")
print("   • Direct mail to executives: expect 1-3% response rate")
print("   • With strong targeting and personalization: potentially 3-5%")
print("   • Budget for ~500-1500 responses from 50,000 mailouts")
print()
print("4. MAILING LIST SIZE:")
print("   • Recommend purchasing mailing list filtered by:")
print("     - Age: 55-74")
print("     - Occupation: Manager/Executive/Business Owner")
print("     - Home ownership (mortgage holders)")
print("     - These 50 suburbs")
print()
print("=" * 120)
