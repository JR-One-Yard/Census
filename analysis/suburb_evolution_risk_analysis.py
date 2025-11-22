#!/usr/bin/env python3
"""
Suburb Evolution Analysis - Target Suburbs Future Trends

Analyzes the top AI advisory target suburbs to understand:
1. Current dwelling types (houses vs. apartments vs. semi-detached)
2. Demographic aging patterns
3. Subdivision/densification risk
4. Strategic implications for the AI advisory service
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
DATA_DIR = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

print("=" * 120)
print("SUBURB EVOLUTION ANALYSIS - FUTURE TRENDS FOR TARGET SUBURBS")
print("=" * 120)
print()

# ============================================================================
# Load Previous Results
# ============================================================================

print("Loading previous analysis results...")

# Load the top 50 Sydney suburbs
top50_file = RESULTS_DIR / "sydney_ai_advisory_target_suburbs_top50.csv"
top50_df = pd.read_csv(top50_file)

print(f"Loaded {len(top50_df)} top target suburbs")
print()

# ============================================================================
# Load Dwelling Type Data
# ============================================================================

print("Loading dwelling type data...")

# G41 - Dwelling Structure by Number of Bedrooms
g41_file = DATA_DIR / "2021Census_G41_AUST_SAL.csv"
dwelling_df = pd.read_csv(g41_file)

# Calculate dwelling type percentages
dwelling_df['Total_Dwellings'] = dwelling_df['Total_Total']
dwelling_df['Separate_House'] = dwelling_df['Separate_house_Total']
dwelling_df['Semi_Detached'] = (dwelling_df['Se_d_r_or_t_h_t_1_st_Total'] +
                                 dwelling_df['Se_d_r_or_t_h_t_2_sts_Total'])
dwelling_df['Apartment'] = dwelling_df['Flt_apart_Tot_Total']

dwelling_df['Separate_House_Pct'] = (dwelling_df['Separate_House'] / dwelling_df['Total_Dwellings'] * 100).fillna(0)
dwelling_df['Semi_Detached_Pct'] = (dwelling_df['Semi_Detached'] / dwelling_df['Total_Dwellings'] * 100).fillna(0)
dwelling_df['Apartment_Pct'] = (dwelling_df['Apartment'] / dwelling_df['Total_Dwellings'] * 100).fillna(0)

# Note: Tenure data (owner vs renter) is less critical for this analysis
# We'll use dwelling type and age demographics as primary indicators

# ============================================================================
# Load Age Demographics for Broader Analysis
# ============================================================================

print("Loading detailed age demographics...")

g01_file = DATA_DIR / "2021Census_G01_AUST_SAL.csv"
age_df = pd.read_csv(g01_file)

# Calculate age brackets
age_df['Age_25_34_yr_P'] = age_df['Age_25_34_yr_M'] + age_df['Age_25_34_yr_F']
age_df['Age_35_44_yr_P'] = age_df['Age_35_44_yr_M'] + age_df['Age_35_44_yr_F']
age_df['Age_45_54_yr_P'] = age_df['Age_45_54_yr_M'] + age_df['Age_45_54_yr_F']
age_df['Age_55_64_yr_P'] = age_df['Age_55_64_yr_M'] + age_df['Age_55_64_yr_F']
age_df['Age_65_74_yr_P'] = age_df['Age_65_74_yr_M'] + age_df['Age_65_74_yr_F']
age_df['Age_75_84_yr_P'] = age_df['Age_75_84_yr_M'] + age_df['Age_75_84_yr_F']
age_df['Total_Population'] = age_df['Tot_P_P']

age_df['Age_25_34_Pct'] = (age_df['Age_25_34_yr_P'] / age_df['Total_Population'] * 100).fillna(0)
age_df['Age_35_44_Pct'] = (age_df['Age_35_44_yr_P'] / age_df['Total_Population'] * 100).fillna(0)
age_df['Age_45_54_Pct'] = (age_df['Age_45_54_yr_P'] / age_df['Total_Population'] * 100).fillna(0)
age_df['Age_55_64_Pct'] = (age_df['Age_55_64_yr_P'] / age_df['Total_Population'] * 100).fillna(0)
age_df['Age_65_74_Pct'] = (age_df['Age_65_74_yr_P'] / age_df['Total_Population'] * 100).fillna(0)
age_df['Age_75_Plus_Pct'] = ((age_df['Age_75_84_yr_P'] + age_df['Age_85ov_M'] + age_df['Age_85ov_F']) / age_df['Total_Population'] * 100).fillna(0)

# ============================================================================
# Load SAL Names
# ============================================================================

metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
sal_names_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

# ============================================================================
# Merge Data with Top 50 Suburbs
# ============================================================================

# Create a mapping from suburb names to SAL codes
suburb_codes = sal_names_df.set_index('Census_Name_2021')['Census_Code_2021'].to_dict()

# Add SAL codes to top50
top50_df['SAL_CODE_2021'] = top50_df['Suburb'].map(suburb_codes)

# Merge with dwelling data
top50_analysis = top50_df.merge(
    dwelling_df[['SAL_CODE_2021', 'Total_Dwellings', 'Separate_House', 'Semi_Detached', 'Apartment',
                 'Separate_House_Pct', 'Semi_Detached_Pct', 'Apartment_Pct']],
    on='SAL_CODE_2021',
    how='left'
)

# Merge with detailed age data
top50_analysis = top50_analysis.merge(
    age_df[['SAL_CODE_2021', 'Age_25_34_Pct', 'Age_35_44_Pct', 'Age_45_54_Pct',
            'Age_55_64_Pct', 'Age_65_74_Pct', 'Age_75_Plus_Pct']],
    on='SAL_CODE_2021',
    how='left'
)

# ============================================================================
# Calculate Evolution Risk Metrics
# ============================================================================

print("Calculating evolution risk metrics...")
print()

# Subdivision Risk Score (0-100)
# Higher score = higher risk of subdivision/redevelopment
top50_analysis['Subdivision_Risk_Score'] = (
    # High house % = more land to subdivide
    top50_analysis['Separate_House_Pct'] * 0.50 +
    # Older population = more likely to sell/downsize
    (top50_analysis['Age_65_74_Pct'] + top50_analysis['Age_75_Plus_Pct']) * 2.5 +
    # Low apartment % means more potential for densification
    (100 - top50_analysis['Apartment_Pct']) * 0.20
)

# Normalize to 0-100
min_score = top50_analysis['Subdivision_Risk_Score'].min()
max_score = top50_analysis['Subdivision_Risk_Score'].max()
top50_analysis['Subdivision_Risk_Score'] = ((top50_analysis['Subdivision_Risk_Score'] - min_score) / (max_score - min_score) * 100)

# Categorize risk
def risk_category(score):
    if score >= 70:
        return 'Very High'
    elif score >= 50:
        return 'High'
    elif score >= 30:
        return 'Moderate'
    else:
        return 'Low'

top50_analysis['Risk_Category'] = top50_analysis['Subdivision_Risk_Score'].apply(risk_category)

# Sort by subdivision risk
top50_analysis = top50_analysis.sort_values('Subdivision_Risk_Score', ascending=False)

# ============================================================================
# ANALYSIS 1: Top 20 Suburbs at Highest Risk of Redevelopment
# ============================================================================

print("=" * 120)
print("TOP 20 SUBURBS AT HIGHEST RISK OF SUBDIVISION/REDEVELOPMENT")
print("=" * 120)
print()
print("These suburbs combine large land plots + aging population + high ownership = highest redevelopment pressure")
print()

print(f"{'Rank':<5}{'Suburb':<25}{'Region':<20}{'Risk':<8}{'House%':<8}{'Apt%':<8}{'65+%':<8}{'Target Score':<12}")
print(f"{'':5}{'':25}{'':20}{'Score':<8}{'':8}{'':8}{'':8}{'(0-100)':<12}")
print("-" * 120)

high_risk = top50_analysis.head(20)
for idx, row in high_risk.iterrows():
    rank = list(high_risk.index).index(idx) + 1
    print(f"{rank:<5}{row['Suburb']:<25}{row['Region']:<20}{row['Subdivision_Risk_Score']:>6.1f}  "
          f"{row['Separate_House_Pct']:>6.1f}%  {row['Apartment_Pct']:>6.1f}%  "
          f"{(row['Age_65_74_Pct'] + row['Age_75_Plus_Pct']):>6.1f}%  {row['Target_Score']:>10.1f}")

print()
print("INSIGHTS - High Redevelopment Risk Suburbs:")
print(f"  Average house %: {high_risk['Separate_House_Pct'].mean():.1f}%")
print(f"  Average apartment %: {high_risk['Apartment_Pct'].mean():.1f}%")
print(f"  Average age 65+: {(high_risk['Age_65_74_Pct'] + high_risk['Age_75_Plus_Pct']).mean():.1f}%")
print()

# ============================================================================
# ANALYSIS 2: Dwelling Type Patterns by Region
# ============================================================================

print("=" * 120)
print("DWELLING TYPE PATTERNS BY REGION")
print("=" * 120)
print()

region_summary = top50_analysis.groupby('Region').agg({
    'Separate_House_Pct': 'mean',
    'Semi_Detached_Pct': 'mean',
    'Apartment_Pct': 'mean',
    'Age_65_74_Pct': 'mean',
    'Age_75_Plus_Pct': 'mean',
    'Subdivision_Risk_Score': 'mean',
    'Suburb': 'count'
}).round(1)

region_summary.columns = ['House%', 'Semi%', 'Apt%', '65-74%', '75+%', 'Risk', 'Count']
region_summary = region_summary.sort_values('Risk', ascending=False)

print(f"{'Region':<25}{'Suburbs':<8}{'House%':<8}{'Semi%':<8}{'Apt%':<8}{'65+%':<8}{'Risk Score':<10}")
print("-" * 120)

for region, row in region_summary.iterrows():
    age_65_plus = row['65-74%'] + row['75+%']
    print(f"{region:<25}{row['Count']:<8.0f}{row['House%']:>6.1f}%  {row['Semi%']:>6.1f}%  "
          f"{row['Apt%']:>6.1f}%  {age_65_plus:>6.1f}%  {row['Risk']:>8.1f}")

print()

# ============================================================================
# ANALYSIS 3: Strategic Implications
# ============================================================================

print("=" * 120)
print("STRATEGIC IMPLICATIONS FOR AI ADVISORY SERVICE")
print("=" * 120)
print()

print("1. PROPERTY REDEVELOPMENT IS A MAJOR OPPORTUNITY")
print("-" * 120)
print()

very_high_risk = top50_analysis[top50_analysis['Risk_Category'] == 'Very High']
high_risk_count = top50_analysis[top50_analysis['Risk_Category'].isin(['Very High', 'High'])]

print(f"   • {len(very_high_risk)} suburbs at VERY HIGH risk of redevelopment")
print(f"   • {len(high_risk_count)} suburbs at HIGH or VERY HIGH risk")
print(f"   • Average house %: {top50_analysis['Separate_House_Pct'].mean():.1f}% (large land plots)")
print(f"   • Average age 65+: {(top50_analysis['Age_65_74_Pct'] + top50_analysis['Age_75_Plus_Pct']).mean():.1f}%")
print()
print("   SERVICE ANGLE: 'AI's Impact on Property Development & Urban Planning'")
print("   • How AI is changing property valuation models")
print("   • AI-driven urban planning and zoning decisions")
print("   • Optimizing subdivision timing using AI market analysis")
print("   • Estate planning for high-value properties in changing markets")
print()

print("2. DOWNSIZING DECISIONS ARE IMMINENT")
print("-" * 120)
print()
print(f"   • {(top50_analysis['Age_65_74_Pct']).mean():.1f}% are 65-74 (prime downsizing age)")
print(f"   • {(top50_analysis['Age_75_Plus_Pct']).mean():.1f}% are 75+ (may need care/smaller home)")
print(f"   • {top50_analysis['Separate_House_Pct'].mean():.1f}% live in separate houses (large plots to sell)")
print()
print("   SERVICE ANGLE: 'Guiding Your Family Through Major Transitions'")
print("   • When to sell the family home (AI-powered market timing)")
print("   • Where to downsize (AI analysis of lifestyle vs. financial factors)")
print("   • How AI is changing retirement living options")
print("   • Legacy planning in an AI-transformed economy")
print()

print("3. INTERGENERATIONAL WEALTH TRANSFER")
print("-" * 120)
print()
avg_mortgage = top50_analysis['Median_Mortgage_Monthly'].mean()
avg_house_pct = top50_analysis['Separate_House_Pct'].mean()

print(f"   • High house ownership rate ({avg_house_pct:.1f}%) means large land holdings")
print(f"   • Properties worth $3-8M in these suburbs (based on mortgage data)")
print(f"   • Adult children (30-50) inheriting/receiving these properties")
print()
print("   SERVICE ANGLE: 'Positioning Your Children for an AI Economy'")
print("   • Should they keep/sell inherited property in an AI-disrupted market?")
print("   • What careers/industries will AI transform (avoid) or enhance (pursue)?")
print("   • How to structure intergenerational wealth in volatile AI economy")
print()

print("4. HERITAGE vs. DEVELOPMENT TENSION")
print("-" * 120)
print()

# Identify likely heritage-protected suburbs
heritage_likely = ['Castlecrag', 'Hunters Hill', 'Mosman', 'Woollahra', 'Paddington (NSW)',
                   'Balmain', 'Balmain East', 'Vaucluse']
heritage_suburbs = top50_analysis[top50_analysis['Suburb'].isin(heritage_likely)]

print(f"   • {len(heritage_suburbs)} suburbs likely have heritage overlays")
print(f"   • These suburbs: {', '.join(heritage_likely[:5])}, etc.")
print(f"   • Heritage protection = LIMITED subdivision potential")
print(f"   • But still have downsizing pressure from aging owners")
print()
print("   IMPLICATION: Focus on downsizing/estate planning, NOT subdivision")
print()

print("5. REGIONAL VARIATION")
print("-" * 120)
print()
print("   HIGHEST RISK REGIONS (Redevelopment Pressure):")
for region, row in region_summary.head(3).iterrows():
    print(f"     • {region}: {row['Risk']:.1f} risk score, {row['House%']:.1f}% houses")

print()
print("   LOWEST RISK REGIONS (Already Dense):")
for region, row in region_summary.tail(2).iterrows():
    print(f"     • {region}: {row['Risk']:.1f} risk score, {row['Apt%']:.1f}% apartments")

print()
print("=" * 120)
print()

# ============================================================================
# ANALYSIS 4: Time Horizon for Evolution
# ============================================================================

print("=" * 120)
print("TIME HORIZON ANALYSIS - WHEN WILL THESE SUBURBS CHANGE?")
print("=" * 120)
print()

print("Based on demographic aging patterns:")
print()

print("IMMEDIATE (2024-2029): Early downsizers")
print("-" * 120)
age_75_plus_high = top50_analysis[top50_analysis['Age_75_Plus_Pct'] >= 8.0]
print(f"   • {len(age_75_plus_high)} suburbs with 8%+ population aged 75+ (health/mobility issues)")
print(f"   • These residents will likely downsize/move in next 5 years")
print(f"   • Top suburbs: {', '.join(age_75_plus_high.nsmallest(5, 'Target_Score')['Suburb'].values)}")
print()

print("MEDIUM-TERM (2029-2039): Peak downsizing wave")
print("-" * 120)
age_65_74_high = top50_analysis[top50_analysis['Age_65_74_Pct'] >= 15.0]
print(f"   • {len(age_65_74_high)} suburbs with 15%+ population aged 65-74")
print(f"   • As these residents reach 75-84, major downsizing wave")
print(f"   • This is YOUR TARGET MARKET for AI advisory service (next 10 years)")
print()

print("LONG-TERM (2039-2049): Generational transfer")
print("-" * 120)
age_55_64_pct = top50_analysis['Age_55_64_Pct'].mean()
print(f"   • {age_55_64_pct:.1f}% currently aged 55-64")
print(f"   • In 20 years, they'll be 75-84 (downsizing age)")
print(f"   • Properties will transfer to Gen X/Millennials (currently 30-50)")
print(f"   • This generation more likely to subdivide/develop")
print()

# ============================================================================
# Export Results
# ============================================================================

export_df = top50_analysis[[
    'Suburb', 'Region', 'Target_Score', 'Subdivision_Risk_Score', 'Risk_Category',
    'Separate_House_Pct', 'Semi_Detached_Pct', 'Apartment_Pct',
    'Age_55_64_Pct', 'Age_65_74_Pct', 'Age_75_Plus_Pct',
    'Manager_Pct', 'Median_Mortgage_Monthly'
]].copy()

export_df.to_csv(RESULTS_DIR / 'suburb_evolution_risk_analysis.csv', index=False)

print("=" * 120)
print()
print("Results exported to: results/suburb_evolution_risk_analysis.csv")
print()
print("=" * 120)
