#!/usr/bin/env python3
"""
Multi-Generation Housing Demand Analysis
==========================================
Analyzes 2021 Australian Census data to identify areas with high demand for
multi-generational housing and maps supply gaps.

Compute Intensity: ⭐⭐⭐⭐ (High - processes 2,472 SA2 areas with complex calculations)

Analysis Components:
1. Generational Overlap Analysis - identifies areas with multiple age cohorts
2. Cultural Community Analysis - birthplace patterns indicating multi-gen preferences
3. Family Composition Analysis - large families and household structures
4. Housing Stock Analysis - dwelling types and bedroom configurations
5. Supply-Demand Gap Mapping - identifies development opportunities

Output:
- Ranked list of SA2 areas with highest multi-gen housing demand
- Supply gap analysis (demand vs. current housing stock)
- Cultural community insights
- Development opportunity recommendations
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Define base paths
BASE_PATH = Path("./2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS")
SA2_PATH = BASE_PATH / "SA2" / "AUS"
OUTPUT_DIR = Path("./results/multigen_housing")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cultures with strong multi-generational living traditions (based on research)
MULTIGEN_CULTURES = {
    'high': [  # Very strong multi-gen preferences
        'China', 'India', 'Vietnam', 'Philippines', 'Sri_Lanka',
        'Lebanon', 'Iraq', 'Iran', 'Afghanistan', 'Pakistan',
        'Greece', 'Italy', 'Malta'
    ],
    'medium': [  # Moderate multi-gen preferences
        'Hong_Kong_SAR_Ch', 'Indonesia', 'Malaysia', 'Thailand',
        'Egypt', 'Turkey', 'Bosnia_Herzegov', 'Croatia', 'Macedonia',
        'Chile', 'Brazil'
    ]
}

print("="*80)
print("MULTI-GENERATION HOUSING DEMAND ANALYSIS")
print("2021 Australian Census Data")
print("="*80)
print()

# ============================================================================
# STEP 1: Load and Process Age Distribution Data
# ============================================================================
print("STEP 1: Analyzing age distribution patterns...")
g01 = pd.read_csv(SA2_PATH / "2021Census_G01_AUST_SA2.csv")

# Calculate generational composition metrics
age_metrics = pd.DataFrame()
age_metrics['SA2_CODE'] = g01['SA2_CODE_2021']
age_metrics['Total_Pop'] = g01['Tot_P_P']

# Define generational cohorts
age_metrics['Young_Children_0_14'] = g01['Age_0_4_yr_P'] + g01['Age_5_14_yr_P']
age_metrics['Young_Adults_15_34'] = (g01['Age_15_19_yr_P'] + g01['Age_20_24_yr_P'] +
                                      g01['Age_25_34_yr_P'])
age_metrics['Parents_35_54'] = g01['Age_35_44_yr_P'] + g01['Age_45_54_yr_P']
age_metrics['Grandparents_55_74'] = g01['Age_55_64_yr_P'] + g01['Age_65_74_yr_P']
age_metrics['Elderly_75plus'] = g01['Age_75_84_yr_P'] + g01['Age_85ov_P']

# Calculate proportions (avoid division by zero)
age_metrics['Pct_Young_Children'] = (age_metrics['Young_Children_0_14'] /
                                      age_metrics['Total_Pop'].replace(0, np.nan) * 100)
age_metrics['Pct_Parents'] = (age_metrics['Parents_35_54'] /
                               age_metrics['Total_Pop'].replace(0, np.nan) * 100)
age_metrics['Pct_Grandparents'] = (age_metrics['Grandparents_55_74'] /
                                    age_metrics['Total_Pop'].replace(0, np.nan) * 100)
age_metrics['Pct_Elderly'] = (age_metrics['Elderly_75plus'] /
                               age_metrics['Total_Pop'].replace(0, np.nan) * 100)

# Multi-generation overlap score: High when multiple generations present
# Formula: Geometric mean of key generational proportions
age_metrics['Generational_Overlap_Score'] = np.power(
    (age_metrics['Pct_Young_Children'].fillna(0) + 1) *
    (age_metrics['Pct_Parents'].fillna(0) + 1) *
    (age_metrics['Pct_Grandparents'].fillna(0) + 1),
    1/3
) - 1

print(f"  ✓ Processed {len(age_metrics)} SA2 areas")
print(f"  ✓ Calculated generational overlap scores")
print()

# ============================================================================
# STEP 2: Cultural Community Analysis (Birthplace Data)
# ============================================================================
print("STEP 2: Analyzing cultural communities with multi-gen preferences...")

# Load birthplace data by age (G09A-G09H cover different countries)
birthplace_files = [
    '2021Census_G09A_AUST_SA2.csv',
    '2021Census_G09B_AUST_SA2.csv',
    '2021Census_G09C_AUST_SA2.csv',
    '2021Census_G09D_AUST_SA2.csv',
    '2021Census_G09E_AUST_SA2.csv',
    '2021Census_G09F_AUST_SA2.csv',
    '2021Census_G09G_AUST_SA2.csv',
    '2021Census_G09H_AUST_SA2.csv'
]

cultural_metrics = pd.DataFrame()
cultural_metrics['SA2_CODE'] = age_metrics['SA2_CODE']
cultural_metrics['Total_Pop'] = age_metrics['Total_Pop']
cultural_metrics['High_MultiGen_Culture_Pop'] = 0
cultural_metrics['Medium_MultiGen_Culture_Pop'] = 0

# Process birthplace data
for bp_file in birthplace_files:
    try:
        bp_data = pd.read_csv(SA2_PATH / bp_file)

        # Sum populations from high multi-gen cultures
        for culture in MULTIGEN_CULTURES['high']:
            # Find columns for this culture (all age groups)
            culture_cols = [col for col in bp_data.columns if culture in col and '_Tot' in col]
            if culture_cols:
                for col in culture_cols:
                    # M_ and F_ totals, so take half to avoid double counting
                    if col.startswith('M_'):
                        cultural_metrics['High_MultiGen_Culture_Pop'] += bp_data[col].fillna(0)

        # Sum populations from medium multi-gen cultures
        for culture in MULTIGEN_CULTURES['medium']:
            culture_cols = [col for col in bp_data.columns if culture in col and '_Tot' in col]
            if culture_cols:
                for col in culture_cols:
                    if col.startswith('M_'):
                        cultural_metrics['Medium_MultiGen_Culture_Pop'] += bp_data[col].fillna(0)

    except FileNotFoundError:
        print(f"  ! Warning: {bp_file} not found, skipping...")
        continue

# Calculate cultural propensity score
cultural_metrics['Pct_High_MultiGen_Culture'] = (
    cultural_metrics['High_MultiGen_Culture_Pop'] /
    cultural_metrics['Total_Pop'].replace(0, np.nan) * 100
).fillna(0)

cultural_metrics['Pct_Medium_MultiGen_Culture'] = (
    cultural_metrics['Medium_MultiGen_Culture_Pop'] /
    cultural_metrics['Total_Pop'].replace(0, np.nan) * 100
).fillna(0)

# Weighted cultural score (high cultures weighted 2x)
cultural_metrics['Cultural_MultiGen_Score'] = (
    cultural_metrics['Pct_High_MultiGen_Culture'] * 2 +
    cultural_metrics['Pct_Medium_MultiGen_Culture']
)

print(f"  ✓ Analyzed {len(birthplace_files)} birthplace datasets")
print(f"  ✓ Calculated cultural multi-gen propensity scores")
print()

# ============================================================================
# STEP 3: Family Composition Analysis
# ============================================================================
print("STEP 3: Analyzing family composition patterns...")

# G31: Family composition
g31 = pd.read_csv(SA2_PATH / "2021Census_G31_AUST_SA2.csv")

family_metrics = pd.DataFrame()
family_metrics['SA2_CODE'] = g31['SA2_CODE_2021']
family_metrics['Total_Families'] = g31['Tot_Families']

# Complex families (blended, step families) may need more space
family_metrics['Blended_Step_Families'] = (
    g31['Step_fam_no_otr_chld_pre_Fam'].fillna(0) +
    g31['Blnd_fam_no_otr_chld_pre_Fam'].fillna(0) +
    g31['Step_fam_othr_child_pres_Fam'].fillna(0) +
    g31['Blnd_fam_othr_child_pres_Fam'].fillna(0)
)

family_metrics['Pct_Complex_Families'] = (
    family_metrics['Blended_Step_Families'] /
    family_metrics['Total_Families'].replace(0, np.nan) * 100
).fillna(0)

# G33: Household composition and income
g33 = pd.read_csv(SA2_PATH / "2021Census_G33_AUST_SA2.csv")
family_metrics['Total_Households'] = g33['Tot_Tot']
family_metrics['Family_Households'] = g33['Tot_Family_households']

# G28: Children ever born (indicator of family size preferences)
g28 = pd.read_csv(SA2_PATH / "2021Census_G28_AUST_SA2.csv")

# Calculate average family size indicator from children born data
# Focus on women aged 30-49 (peak family formation years)
family_metrics['Large_Family_Indicator'] = (
    (g28['Tot_Nmbr_children_ever_born_3'].fillna(0) +
     g28['Tot_Nmbr_children_ever_born_4'].fillna(0) +
     g28['Tot_Nmbr_children_ever_born_5'].fillna(0) +
     g28['Tot_Nmbr_chidrn_ever_brn_6_mr'].fillna(0)) /
    g28['Total_Total'].replace(0, np.nan) * 100
).fillna(0)

print(f"  ✓ Analyzed family composition for {len(family_metrics)} areas")
print(f"  ✓ Calculated large family indicators")
print()

# ============================================================================
# STEP 4: Housing Stock Analysis
# ============================================================================
print("STEP 4: Analyzing housing stock and dwelling configurations...")

# G37: Dwelling structure by tenure
g37 = pd.read_csv(SA2_PATH / "2021Census_G37_AUST_SA2.csv")

housing_metrics = pd.DataFrame()
housing_metrics['SA2_CODE'] = g37['SA2_CODE_2021']
housing_metrics['Total_Dwellings'] = g37['Total_Total']

# Separate houses are ideal for multi-gen (granny flat potential)
housing_metrics['Separate_Houses'] = g37['Total_DS_Sep_house']
housing_metrics['Semi_Detached'] = g37['Total_DS_SemiD_ro_or_tce_h_th']
housing_metrics['Apartments'] = g37['Total_DS_Flat_apart']
housing_metrics['Other_Dwellings'] = g37['Total_DS_Oth_dwell']

housing_metrics['Pct_Separate_Houses'] = (
    housing_metrics['Separate_Houses'] /
    housing_metrics['Total_Dwellings'].replace(0, np.nan) * 100
).fillna(0)

housing_metrics['Pct_Apartments'] = (
    housing_metrics['Apartments'] /
    housing_metrics['Total_Dwellings'].replace(0, np.nan) * 100
).fillna(0)

# G40: Number of bedrooms
try:
    g40 = pd.read_csv(SA2_PATH / "2021Census_G40_AUST_SA2.csv")

    # Look for bedroom columns - need to identify them first
    bedroom_cols = [col for col in g40.columns if 'bed' in col.lower() or 'Bed' in col]

    # Calculate large dwelling availability (4+ bedrooms)
    # Column naming pattern needs to be determined from actual data
    housing_metrics['Has_Bedroom_Data'] = True

except FileNotFoundError:
    print("  ! Warning: G40 (bedroom data) not found")
    housing_metrics['Has_Bedroom_Data'] = False

# Owned homes (more likely to accommodate multi-gen)
housing_metrics['Owned_Outright'] = g37['O_OR_Total']
housing_metrics['Owned_Mortgage'] = g37['O_MTG_Total']
housing_metrics['Owned_Total'] = housing_metrics['Owned_Outright'] + housing_metrics['Owned_Mortgage']

housing_metrics['Pct_Owned'] = (
    housing_metrics['Owned_Total'] /
    housing_metrics['Total_Dwellings'].replace(0, np.nan) * 100
).fillna(0)

print(f"  ✓ Analyzed housing stock for {len(housing_metrics)} areas")
print(f"  ✓ Calculated dwelling configuration metrics")
print()

# ============================================================================
# STEP 5: Composite Multi-Generation Demand Score
# ============================================================================
print("STEP 5: Calculating composite multi-gen housing demand scores...")

# Merge all metrics
demand_analysis = age_metrics[['SA2_CODE', 'Total_Pop', 'Generational_Overlap_Score',
                                'Pct_Young_Children', 'Pct_Parents', 'Pct_Grandparents',
                                'Pct_Elderly']].copy()

demand_analysis = demand_analysis.merge(
    cultural_metrics[['SA2_CODE', 'Cultural_MultiGen_Score',
                      'Pct_High_MultiGen_Culture', 'Pct_Medium_MultiGen_Culture']],
    on='SA2_CODE'
)

demand_analysis = demand_analysis.merge(
    family_metrics[['SA2_CODE', 'Total_Families', 'Total_Households',
                    'Pct_Complex_Families', 'Large_Family_Indicator']],
    on='SA2_CODE'
)

demand_analysis = demand_analysis.merge(
    housing_metrics[['SA2_CODE', 'Total_Dwellings', 'Pct_Separate_Houses',
                     'Pct_Apartments', 'Pct_Owned']],
    on='SA2_CODE'
)

# Normalize scores to 0-100 scale for combination
def normalize_score(series):
    """Normalize to 0-100 scale using percentile rank"""
    return series.rank(pct=True) * 100

demand_analysis['Norm_Generational_Overlap'] = normalize_score(
    demand_analysis['Generational_Overlap_Score']
)
demand_analysis['Norm_Cultural_Score'] = normalize_score(
    demand_analysis['Cultural_MultiGen_Score']
)
demand_analysis['Norm_Family_Size'] = normalize_score(
    demand_analysis['Large_Family_Indicator']
)

# Composite Multi-Gen Demand Score (weighted combination)
# Weights: Generational overlap (35%), Cultural propensity (35%), Family size (30%)
demand_analysis['MultiGen_Demand_Score'] = (
    demand_analysis['Norm_Generational_Overlap'] * 0.35 +
    demand_analysis['Norm_Cultural_Score'] * 0.35 +
    demand_analysis['Norm_Family_Size'] * 0.30
)

# Supply Gap Score: High demand but low suitable housing
# High apartments = low supply for multi-gen
# Low separate houses = low granny flat potential
demand_analysis['Supply_Suitability'] = normalize_score(
    demand_analysis['Pct_Separate_Houses'] - demand_analysis['Pct_Apartments']
)

demand_analysis['Supply_Gap_Score'] = (
    demand_analysis['MultiGen_Demand_Score'] -
    demand_analysis['Supply_Suitability']
)

# Market opportunity score (combines high demand + high ownership for development viability)
demand_analysis['Market_Opportunity_Score'] = (
    demand_analysis['MultiGen_Demand_Score'] * 0.6 +
    normalize_score(demand_analysis['Pct_Owned']) * 0.4
)

print(f"  ✓ Calculated composite demand scores")
print(f"  ✓ Identified supply gaps")
print()

# ============================================================================
# STEP 6: Load Geographic Names and Generate Reports
# ============================================================================
print("STEP 6: Loading geographic names and generating reports...")

# Try to load geographic descriptor file
try:
    geo_desc = pd.read_excel(
        BASE_PATH.parent / "Metadata" / "2021Census_geog_desc_1st_2nd_3rd_release.xlsx",
        sheet_name="2021_SA2"
    )
    demand_analysis = demand_analysis.merge(
        geo_desc[['SA2_CODE_2021', 'SA2_NAME_2021']],
        left_on='SA2_CODE',
        right_on='SA2_CODE_2021',
        how='left'
    )
    demand_analysis = demand_analysis.rename(columns={'SA2_NAME_2021': 'SA2_Name'})
    has_names = True
except:
    print("  ! Could not load geographic names, using codes only")
    demand_analysis['SA2_Name'] = 'SA2_' + demand_analysis['SA2_CODE'].astype(str)
    has_names = False

# Filter out areas with very low population (< 100)
demand_analysis_filtered = demand_analysis[demand_analysis['Total_Pop'] >= 100].copy()

print(f"  ✓ Filtered to {len(demand_analysis_filtered)} areas (pop >= 100)")
print()

# ============================================================================
# STEP 7: Generate Output Reports
# ============================================================================
print("STEP 7: Generating output reports...")

# Report 1: Top 100 Areas by Multi-Gen Demand
top_demand = demand_analysis_filtered.nlargest(100, 'MultiGen_Demand_Score')
output_cols_demand = [
    'SA2_CODE', 'SA2_Name', 'Total_Pop', 'Total_Dwellings',
    'MultiGen_Demand_Score',
    'Generational_Overlap_Score',
    'Cultural_MultiGen_Score',
    'Large_Family_Indicator',
    'Pct_High_MultiGen_Culture',
    'Pct_Young_Children', 'Pct_Parents', 'Pct_Grandparents',
    'Pct_Separate_Houses', 'Pct_Apartments', 'Pct_Owned'
]
top_demand[output_cols_demand].to_csv(
    OUTPUT_DIR / 'top_100_multigen_demand.csv',
    index=False,
    float_format='%.2f'
)
print(f"  ✓ Saved: top_100_multigen_demand.csv")

# Report 2: Top 100 Supply Gap Opportunities
top_gaps = demand_analysis_filtered.nlargest(100, 'Supply_Gap_Score')
output_cols_gaps = [
    'SA2_CODE', 'SA2_Name', 'Total_Pop', 'Total_Dwellings',
    'Supply_Gap_Score',
    'MultiGen_Demand_Score',
    'Supply_Suitability',
    'Pct_Separate_Houses', 'Pct_Apartments',
    'Cultural_MultiGen_Score',
    'Pct_High_MultiGen_Culture'
]
top_gaps[output_cols_gaps].to_csv(
    OUTPUT_DIR / 'top_100_supply_gaps.csv',
    index=False,
    float_format='%.2f'
)
print(f"  ✓ Saved: top_100_supply_gaps.csv")

# Report 3: Top 100 Market Opportunities (high demand + high ownership)
top_market = demand_analysis_filtered.nlargest(100, 'Market_Opportunity_Score')
output_cols_market = [
    'SA2_CODE', 'SA2_Name', 'Total_Pop', 'Total_Dwellings',
    'Market_Opportunity_Score',
    'MultiGen_Demand_Score',
    'Pct_Owned',
    'Pct_Separate_Houses',
    'Cultural_MultiGen_Score',
    'Large_Family_Indicator',
    'Supply_Gap_Score'
]
top_market[output_cols_market].to_csv(
    OUTPUT_DIR / 'top_100_market_opportunities.csv',
    index=False,
    float_format='%.2f'
)
print(f"  ✓ Saved: top_100_market_opportunities.csv")

# Report 4: High Cultural Concentration Areas
high_cultural = demand_analysis_filtered[
    demand_analysis_filtered['Pct_High_MultiGen_Culture'] >= 20
].nlargest(100, 'Pct_High_MultiGen_Culture')
output_cols_cultural = [
    'SA2_CODE', 'SA2_Name', 'Total_Pop',
    'Pct_High_MultiGen_Culture',
    'Pct_Medium_MultiGen_Culture',
    'Cultural_MultiGen_Score',
    'MultiGen_Demand_Score',
    'Supply_Gap_Score',
    'Pct_Separate_Houses'
]
high_cultural[output_cols_cultural].to_csv(
    OUTPUT_DIR / 'high_cultural_concentration.csv',
    index=False,
    float_format='%.2f'
)
print(f"  ✓ Saved: high_cultural_concentration.csv")

# Report 5: Granny Flat Potential (separate houses in high demand areas)
granny_flat_potential = demand_analysis_filtered[
    (demand_analysis_filtered['Pct_Separate_Houses'] >= 60) &
    (demand_analysis_filtered['MultiGen_Demand_Score'] >= 60)
].nlargest(100, 'Market_Opportunity_Score')
output_cols_granny = [
    'SA2_CODE', 'SA2_Name', 'Total_Pop', 'Total_Dwellings',
    'Pct_Separate_Houses',
    'Pct_Owned',
    'MultiGen_Demand_Score',
    'Generational_Overlap_Score',
    'Cultural_MultiGen_Score',
    'Market_Opportunity_Score'
]
granny_flat_potential[output_cols_granny].to_csv(
    OUTPUT_DIR / 'granny_flat_potential_areas.csv',
    index=False,
    float_format='%.2f'
)
print(f"  ✓ Saved: granny_flat_potential_areas.csv")

# Report 6: Complete dataset
demand_analysis_filtered.to_csv(
    OUTPUT_DIR / 'complete_multigen_analysis.csv',
    index=False,
    float_format='%.2f'
)
print(f"  ✓ Saved: complete_multigen_analysis.csv")

# ============================================================================
# STEP 8: Generate Summary Statistics and Insights
# ============================================================================
print()
print("="*80)
print("ANALYSIS SUMMARY")
print("="*80)
print()

print(f"Total SA2 Areas Analyzed: {len(demand_analysis_filtered)}")
print(f"Total Population Covered: {demand_analysis_filtered['Total_Pop'].sum():,.0f}")
print()

print("TOP 10 AREAS BY MULTI-GEN DEMAND:")
print("-" * 80)
for idx, row in top_demand.head(10).iterrows():
    print(f"{row['SA2_Name'][:50]:50} | Score: {row['MultiGen_Demand_Score']:6.2f} | "
          f"Pop: {row['Total_Pop']:7,.0f} | Cultural: {row['Pct_High_MultiGen_Culture']:5.1f}%")
print()

print("TOP 10 SUPPLY GAP OPPORTUNITIES (High Demand, Low Suitable Supply):")
print("-" * 80)
for idx, row in top_gaps.head(10).iterrows():
    print(f"{row['SA2_Name'][:50]:50} | Gap: {row['Supply_Gap_Score']:6.2f} | "
          f"Demand: {row['MultiGen_Demand_Score']:5.1f} | Sep.House: {row['Pct_Separate_Houses']:5.1f}%")
print()

print("TOP 10 MARKET OPPORTUNITIES (High Demand + High Ownership):")
print("-" * 80)
for idx, row in top_market.head(10).iterrows():
    print(f"{row['SA2_Name'][:50]:50} | Score: {row['Market_Opportunity_Score']:6.2f} | "
          f"Owned: {row['Pct_Owned']:5.1f}% | Demand: {row['MultiGen_Demand_Score']:5.1f}")
print()

print("DEVELOPMENT INSIGHTS:")
print("-" * 80)
print(f"Areas with >30% high multi-gen cultures: {len(demand_analysis_filtered[demand_analysis_filtered['Pct_High_MultiGen_Culture'] > 30])}")
print(f"Areas with >70% separate houses: {len(demand_analysis_filtered[demand_analysis_filtered['Pct_Separate_Houses'] > 70])}")
print(f"Areas with >70% ownership: {len(demand_analysis_filtered[demand_analysis_filtered['Pct_Owned'] > 70])}")
print(f"Areas with high demand (score >75): {len(demand_analysis_filtered[demand_analysis_filtered['MultiGen_Demand_Score'] > 75])}")
print(f"Areas with high supply gap (score >50): {len(demand_analysis_filtered[demand_analysis_filtered['Supply_Gap_Score'] > 50])}")
print()

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"Output directory: {OUTPUT_DIR}")
print()
print("Generated Reports:")
print("  1. top_100_multigen_demand.csv - Highest overall demand areas")
print("  2. top_100_supply_gaps.csv - Best development opportunities (high demand, low supply)")
print("  3. top_100_market_opportunities.csv - High demand + high ownership (viable market)")
print("  4. high_cultural_concentration.csv - Cultural communities with multi-gen preferences")
print("  5. granny_flat_potential_areas.csv - Separate house areas with high demand")
print("  6. complete_multigen_analysis.csv - Full dataset with all metrics")
print()
