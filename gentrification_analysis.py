#!/usr/bin/env python3
"""
Ultra-Granular Gentrification Risk/Opportunity Heatmap Analysis
Analyzes all 61,844 SA1 areas across Australia for gentrification potential

This compute-intensive analysis examines:
- Income vs. education mismatches (high education, lower income = gentrification trigger)
- Rental vs. ownership patterns
- Age demographics (young professionals moving in)
- Language/birthplace diversity changes
- Dwelling type transitions potential
- Spatial autocorrelation (Moran's I)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SA1/AUS")
OUTPUT_DIR = Path("gentrification_analysis_results")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("ULTRA-GRANULAR GENTRIFICATION RISK/OPPORTUNITY HEATMAP")
print("Analyzing 61,844+ SA1 areas across Australia")
print("=" * 80)
print()

# ============================================================================
# DATA LOADING
# ============================================================================

print("STEP 1: Loading SA1-level census data...")
print("-" * 80)

# Load basic demographics (G01) - Age structure, indigenous status, education
print("Loading G01 - Basic demographics and age structure...")
g01 = pd.read_csv(DATA_DIR / "2021Census_G01_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g01):,} SA1 areas")

# Load median income data (G02)
print("Loading G02 - Median income and rent data...")
g02 = pd.read_csv(DATA_DIR / "2021Census_G02_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g02):,} SA1 areas")

# Load detailed personal income (G17A)
print("Loading G17A - Detailed personal income distributions...")
g17a = pd.read_csv(DATA_DIR / "2021Census_G17A_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g17a):,} SA1 areas")

# Load education attainment (G16A)
print("Loading G16A - Educational attainment (Year 12 completion)...")
g16a = pd.read_csv(DATA_DIR / "2021Census_G16A_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g16a):,} SA1 areas")

# Load qualifications (G40)
print("Loading G40 - Higher education qualifications...")
g40 = pd.read_csv(DATA_DIR / "2021Census_G40_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g40):,} SA1 areas")

# Load household income (G33)
print("Loading G33 - Household income distributions...")
g33 = pd.read_csv(DATA_DIR / "2021Census_G33_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g33):,} SA1 areas")

# Load tenure and landlord type (G32)
print("Loading G32 - Housing tenure and family income...")
g32 = pd.read_csv(DATA_DIR / "2021Census_G32_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g32):,} SA1 areas")

# Load dwelling structure (G34)
print("Loading G34 - Dwelling structure types...")
g34 = pd.read_csv(DATA_DIR / "2021Census_G34_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g34):,} SA1 areas")

# Load birthplace (G09A)
print("Loading G09A - Country of birth...")
g09a = pd.read_csv(DATA_DIR / "2021Census_G09A_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g09a):,} SA1 areas")

# Load language spoken at home (G13A)
print("Loading G13A - Language spoken at home...")
g13a = pd.read_csv(DATA_DIR / "2021Census_G13A_AUST_SA1.csv")
print(f"  ✓ Loaded {len(g13a):,} SA1 areas")

print()
print(f"✓ All data loaded successfully")
print()

# ============================================================================
# FEATURE ENGINEERING - INCOME METRICS
# ============================================================================

print("STEP 2: Calculating income metrics and percentiles...")
print("-" * 80)

# Create main dataframe
df = g01[['SA1_CODE_2021']].copy()
df['total_population'] = g01['Tot_P_P']

# Add median income
df['median_personal_income'] = g02['Median_tot_prsnl_inc_weekly']
df['median_household_income'] = g02['Median_tot_hhd_inc_weekly']
df['median_rent_weekly'] = g02['Median_rent_weekly']
df['median_mortgage_monthly'] = g02['Median_mortgage_repay_monthly']

# Calculate income distribution metrics from G17A
# High earners (>$3000/week = $156k+/year)
high_income_cols = [col for col in g17a.columns if '3000_3499' in col or '3500_more' in col]
df['high_earners'] = g17a[high_income_cols].sum(axis=1)

# Low-moderate earners ($400-$1000/week = $21k-52k/year)
mid_income_cols = [col for col in g17a.columns if any(x in col for x in ['400_499', '500_649', '650_799', '800_999'])]
df['mid_earners'] = g17a[mid_income_cols].sum(axis=1)

# Total earners
total_cols = [col for col in g17a.columns if 'Tot_Tot' in col]
df['total_earners'] = g17a[total_cols].sum(axis=1)

# Calculate proportions
df['pct_high_earners'] = (df['high_earners'] / df['total_earners'].replace(0, np.nan)) * 100
df['pct_mid_earners'] = (df['mid_earners'] / df['total_earners'].replace(0, np.nan)) * 100

# Income percentile ranking (national)
df['income_percentile'] = df['median_personal_income'].rank(pct=True) * 100

print(f"  ✓ Calculated income metrics for {len(df):,} SA1 areas")
print(f"  ✓ Median personal income range: ${df['median_personal_income'].min():.0f} - ${df['median_personal_income'].max():.0f}/week")
print()

# ============================================================================
# FEATURE ENGINEERING - EDUCATION METRICS
# ============================================================================

print("STEP 3: Calculating education attainment scores...")
print("-" * 80)

# Year 12 completion rate from G01
df['year12_completed'] = g01['High_yr_schl_comp_Yr_12_eq_P']
df['year11_or_lower'] = g01['High_yr_schl_comp_Yr_11_eq_P'] + g01['High_yr_schl_comp_Yr_10_eq_P'] + \
                         g01['High_yr_schl_comp_Yr_9_eq_P'] + g01['High_yr_schl_comp_Yr_8_belw_P']
df['total_education_stated'] = df['year12_completed'] + df['year11_or_lower']

df['pct_year12'] = (df['year12_completed'] / df['total_education_stated'].replace(0, np.nan)) * 100

# Bachelor degree or higher from G40 (we'll need to parse this)
# G40 contains qualification levels - let's calculate tertiary education proportion
bachelor_cols = [col for col in g40.columns if 'Bach_dgr_lvl' in col]
postgrad_cols = [col for col in g40.columns if 'Pgrd_dgr_lvl' in col]

if bachelor_cols:
    df['bachelor_holders'] = g40[bachelor_cols].sum(axis=1)
else:
    df['bachelor_holders'] = 0

if postgrad_cols:
    df['postgrad_holders'] = g40[postgrad_cols].sum(axis=1)
else:
    df['postgrad_holders'] = 0

df['tertiary_educated'] = df['bachelor_holders'] + df['postgrad_holders']
df['pct_tertiary'] = (df['tertiary_educated'] / df['total_population'].replace(0, np.nan)) * 100

# Education percentile
df['education_percentile'] = df['pct_year12'].rank(pct=True) * 100

print(f"  ✓ Calculated education metrics")
print(f"  ✓ Year 12 completion range: {df['pct_year12'].min():.1f}% - {df['pct_year12'].max():.1f}%")
print()

# ============================================================================
# FEATURE ENGINEERING - INCOME-EDUCATION MISMATCH (KEY GENTRIFICATION SIGNAL)
# ============================================================================

print("STEP 4: Calculating income-education mismatch (gentrification trigger)...")
print("-" * 80)

# Normalize scores to 0-100 scale
df['income_score_norm'] = (df['income_percentile'] - df['income_percentile'].min()) / \
                           (df['income_percentile'].max() - df['income_percentile'].min()) * 100
df['education_score_norm'] = (df['education_percentile'] - df['education_percentile'].min()) / \
                              (df['education_percentile'].max() - df['education_percentile'].min()) * 100

# Mismatch score: High education but low-moderate income = GENTRIFICATION SIGNAL
# Positive mismatch = education exceeds income (gentrification potential)
df['edu_income_mismatch'] = df['education_score_norm'] - df['income_score_norm']

# Strong gentrification signal: High education (>60th percentile) + Lower income (<50th percentile)
df['gentrification_signal'] = ((df['education_percentile'] > 60) &
                                (df['income_percentile'] < 50)).astype(int) * 100

print(f"  ✓ Calculated income-education mismatch")
print(f"  ✓ Areas with strong gentrification signal: {df['gentrification_signal'].sum():,}")
print(f"  ✓ Mismatch range: {df['edu_income_mismatch'].min():.1f} to {df['edu_income_mismatch'].max():.1f}")
print()

# ============================================================================
# FEATURE ENGINEERING - AGE DEMOGRAPHICS (YOUNG PROFESSIONALS)
# ============================================================================

print("STEP 5: Analyzing age demographics (young professionals)...")
print("-" * 80)

# Young professionals age groups (25-44 years)
df['age_25_34'] = g01['Age_25_34_yr_P']
df['age_35_44'] = g01['Age_35_44_yr_P']
df['young_professionals'] = df['age_25_34'] + df['age_35_44']
df['pct_young_professionals'] = (df['young_professionals'] / df['total_population'].replace(0, np.nan)) * 100

# Younger cohort (20-24) - potential future gentrifiers
df['age_20_24'] = g01['Age_20_24_yr_P']
df['pct_age_20_24'] = (df['age_20_24'] / df['total_population'].replace(0, np.nan)) * 100

# Calculate youth influx score
df['youth_score'] = df['pct_young_professionals'] + (df['pct_age_20_24'] * 0.5)
df['youth_percentile'] = df['youth_score'].rank(pct=True) * 100

print(f"  ✓ Calculated age demographics")
print(f"  ✓ Young professionals range: {df['pct_young_professionals'].min():.1f}% - {df['pct_young_professionals'].max():.1f}%")
print()

# ============================================================================
# FEATURE ENGINEERING - RENTAL VS OWNERSHIP
# ============================================================================

print("STEP 6: Calculating rental vs ownership ratios...")
print("-" * 80)

# We'll use G33 household income to infer tenure patterns
# High rental areas with increasing income = gentrification
df['household_income_median'] = g02['Median_tot_hhd_inc_weekly']
df['rent_to_income_ratio'] = (df['median_rent_weekly'] * 52) / (df['household_income_median'] * 52) * 100

# Rental stress indicator (>30% of income on rent)
df['rental_stress'] = (df['rent_to_income_ratio'] > 30).astype(int) * 100

print(f"  ✓ Calculated tenure patterns")
print(f"  ✓ Areas with rental stress: {(df['rental_stress'] == 100).sum():,}")
print()

# ============================================================================
# FEATURE ENGINEERING - DIVERSITY METRICS
# ============================================================================

print("STEP 7: Analyzing language/birthplace diversity...")
print("-" * 80)

# Calculate diversity indices
# Non-English speaking background
df['birthplace_australia'] = g01['Birthplace_Australia_P']
df['birthplace_overseas'] = g01['Birthplace_Elsewhere_P']
df['pct_overseas_born'] = (df['birthplace_overseas'] / df['total_population'].replace(0, np.nan)) * 100

df['lang_english_only'] = g01['Lang_used_home_Eng_only_P']
df['lang_other'] = g01['Lang_used_home_Oth_Lang_P']
df['pct_non_english'] = (df['lang_other'] / df['total_population'].replace(0, np.nan)) * 100

# Diversity score (Simpson's diversity-like index)
df['diversity_score'] = (df['pct_overseas_born'] + df['pct_non_english']) / 2
df['diversity_percentile'] = df['diversity_score'].rank(pct=True) * 100

print(f"  ✓ Calculated diversity metrics")
print(f"  ✓ Overseas born range: {df['pct_overseas_born'].min():.1f}% - {df['pct_overseas_born'].max():.1f}%")
print()

# ============================================================================
# FEATURE ENGINEERING - DWELLING TYPES
# ============================================================================

print("STEP 8: Evaluating dwelling type composition...")
print("-" * 80)

# From G34 - dwelling structure
# Calculate proportions of different dwelling types
# Separate houses, semi-detached, apartments, etc.

# For now, we'll use a simple metric from G02
df['avg_household_size'] = g02['Average_household_size']
df['avg_persons_per_bedroom'] = g02['Average_num_psns_per_bedroom']

# Density score (inverse - lower household size might indicate apartments/gentrification)
df['density_score'] = 1 / df['avg_household_size'].replace(0, np.nan)
df['density_percentile'] = df['density_score'].rank(pct=True) * 100

print(f"  ✓ Calculated dwelling metrics")
print(f"  ✓ Average household size range: {df['avg_household_size'].min():.1f} - {df['avg_household_size'].max():.1f}")
print()

# ============================================================================
# MULTI-DIMENSIONAL GENTRIFICATION RISK SCORE
# ============================================================================

print("STEP 9: Building multi-dimensional gentrification risk score...")
print("-" * 80)

# Normalize all component scores to 0-100
def normalize_score(series):
    """Normalize a series to 0-100 scale"""
    return ((series - series.min()) / (series.max() - series.min()) * 100).fillna(0)

# Component scores
df['income_component'] = normalize_score(df['income_percentile'])
df['education_component'] = normalize_score(df['education_percentile'])
df['youth_component'] = normalize_score(df['youth_percentile'])
df['diversity_component'] = normalize_score(df['diversity_percentile'])
df['density_component'] = normalize_score(df['density_percentile'])

# Mismatch component (education exceeds income)
df['mismatch_component'] = normalize_score(df['edu_income_mismatch'].clip(lower=0))

# Weighted composite gentrification risk score
# Higher weights for key signals
weights = {
    'mismatch': 0.30,      # Income-education mismatch (strongest signal)
    'youth': 0.25,          # Young professionals moving in
    'education': 0.20,      # Education levels
    'diversity': 0.10,      # Diversity changes
    'density': 0.10,        # Urban density
    'income': 0.05          # Current income (inverse - lower income = higher risk)
}

df['gentrification_risk_score'] = (
    weights['mismatch'] * df['mismatch_component'] +
    weights['youth'] * df['youth_component'] +
    weights['education'] * df['education_component'] +
    weights['diversity'] * df['diversity_component'] +
    weights['density'] * df['density_component'] +
    weights['income'] * (100 - df['income_component'])  # Inverse income
)

# Percentile ranking
df['gentrification_risk_percentile'] = df['gentrification_risk_score'].rank(pct=True) * 100

# Risk categories
df['risk_category'] = pd.cut(df['gentrification_risk_percentile'],
                              bins=[0, 25, 50, 75, 90, 100],
                              labels=['Very Low', 'Low', 'Moderate', 'High', 'Very High'])

print(f"  ✓ Calculated composite gentrification risk scores")
print(f"  ✓ Score range: {df['gentrification_risk_score'].min():.2f} - {df['gentrification_risk_score'].max():.2f}")
print()
print("Risk Distribution:")
print(df['risk_category'].value_counts().sort_index())
print()

# ============================================================================
# SPATIAL AUTOCORRELATION (Moran's I)
# ============================================================================

print("STEP 10: Calculating spatial autocorrelation (Moran's I)...")
print("-" * 80)
print("⚠️  Note: Spatial autocorrelation requires geographic coordinates.")
print("    This analysis would need SA1 boundary shapefiles with lat/long coordinates.")
print("    Skipping for now - can be added with geospatial data.")
print()

# Placeholder for Moran's I calculation
# Would require:
# 1. SA1 geographic centroids (lat/long)
# 2. Spatial weights matrix
# 3. PySAL or similar library
# 4. Computation of Global and Local Moran's I

df['morans_i_local'] = np.nan  # Placeholder
df['spatial_cluster_type'] = 'Not Calculated'  # Placeholder

# ============================================================================
# GENERATE RANKINGS AND EXPORT
# ============================================================================

print("STEP 11: Generating final rankings and exporting results...")
print("-" * 80)

# Sort by gentrification risk score
df_ranked = df.sort_values('gentrification_risk_score', ascending=False).reset_index(drop=True)
df_ranked['rank'] = range(1, len(df_ranked) + 1)

# Select key columns for export
output_cols = [
    'rank',
    'SA1_CODE_2021',
    'gentrification_risk_score',
    'gentrification_risk_percentile',
    'risk_category',
    'total_population',
    'median_personal_income',
    'median_household_income',
    'median_rent_weekly',
    'income_percentile',
    'education_percentile',
    'pct_year12',
    'pct_tertiary',
    'edu_income_mismatch',
    'pct_young_professionals',
    'pct_age_20_24',
    'pct_overseas_born',
    'pct_non_english',
    'avg_household_size',
    'rental_stress',
    'income_component',
    'education_component',
    'youth_component',
    'mismatch_component',
    'diversity_component',
    'density_component'
]

df_export = df_ranked[output_cols].copy()

# Export full results
output_file = OUTPUT_DIR / "gentrification_risk_scores_all_sa1.csv"
df_export.to_csv(output_file, index=False)
print(f"  ✓ Exported full results: {output_file}")
print(f"    {len(df_export):,} SA1 areas")

# Export top 1000 highest risk areas
top_1000 = df_export.head(1000)
top_file = OUTPUT_DIR / "gentrification_risk_top_1000.csv"
top_1000.to_csv(top_file, index=False)
print(f"  ✓ Exported top 1000 highest risk areas: {top_file}")

# Export top 100 highest risk areas
top_100 = df_export.head(100)
top_100_file = OUTPUT_DIR / "gentrification_risk_top_100.csv"
top_100.to_csv(top_100_file, index=False)
print(f"  ✓ Exported top 100 highest risk areas: {top_100_file}")

# Export summary statistics by risk category
summary = df.groupby('risk_category').agg({
    'SA1_CODE_2021': 'count',
    'gentrification_risk_score': 'mean',
    'median_personal_income': 'median',
    'pct_year12': 'mean',
    'pct_young_professionals': 'mean',
    'edu_income_mismatch': 'mean'
}).round(2)
summary.columns = ['Count', 'Avg_Risk_Score', 'Median_Income', 'Avg_Year12_Pct',
                   'Avg_Young_Prof_Pct', 'Avg_Edu_Income_Mismatch']
summary_file = OUTPUT_DIR / "gentrification_summary_by_category.csv"
summary.to_csv(summary_file)
print(f"  ✓ Exported summary statistics: {summary_file}")

print()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("=" * 80)
print("ANALYSIS COMPLETE - SUMMARY STATISTICS")
print("=" * 80)
print()
print(f"Total SA1 Areas Analyzed: {len(df):,}")
print()
print("Top 10 Highest Gentrification Risk SA1 Areas:")
print("-" * 80)
print(top_100[['rank', 'SA1_CODE_2021', 'gentrification_risk_score', 'risk_category',
               'median_personal_income', 'pct_year12', 'pct_young_professionals']].head(10).to_string(index=False))
print()
print("=" * 80)
print(f"Results saved to: {OUTPUT_DIR.absolute()}")
print("=" * 80)
print()
print("🎯 KEY INSIGHTS:")
print("  • Income-education mismatch is the strongest gentrification signal")
print("  • Young professional concentration (25-44 years) indicates transformation")
print("  • High education + moderate income = areas on the cusp of change")
print("  • These areas represent early-stage gentrification opportunities")
print()
print("📊 NEXT STEPS:")
print("  • Cross-reference with SA2/suburb names for geographic context")
print("  • Add spatial coordinates for Moran's I clustering analysis")
print("  • Overlay with property price data for validation")
print("  • Map results for visual heatmap generation")
print()
print("=" * 80)
