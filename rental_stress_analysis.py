#!/usr/bin/env python3
"""
Rental Stress & Social Housing Demand Forecasting Analysis
============================================================
Analyzes 2021 Australian Census data at SA1 level to:
1. Calculate rental affordability metrics across all SA1s
2. Identify low-income household concentrations
3. Compute public housing vs. demand gaps
4. Predict future rental stress hotspots
5. Identify areas at risk of displacement
6. Determine optimal social housing investment locations
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SA1/AUS")
OUTPUT_DIR = Path("rental_stress_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Rental stress thresholds (based on Australian housing affordability standards)
RENTAL_STRESS_THRESHOLD = 0.30  # 30% of income on rent = housing stress
SEVERE_STRESS_THRESHOLD = 0.50  # 50% of income on rent = severe stress
LOW_INCOME_THRESHOLD = 800      # Weekly household income < $800 = low income

print("=" * 80)
print("RENTAL STRESS & SOCIAL HOUSING DEMAND FORECASTING")
print("2021 Australian Census - SA1 Level Analysis")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load Census Data
# ============================================================================
print("STEP 1: Loading census data...")
print("-" * 80)

# Load G02 - Median rent and income
print("  → Loading G02 (Median rent & income)...")
g02 = pd.read_csv(DATA_DIR / "2021Census_G02_AUST_SA1.csv")
print(f"     Loaded {len(g02):,} SA1 areas")

# Load G37 - Tenure type by dwelling structure
print("  → Loading G37 (Tenure type)...")
g37 = pd.read_csv(DATA_DIR / "2021Census_G37_AUST_SA1.csv")
print(f"     Loaded {len(g37):,} SA1 areas")

# Load G40 - Rental by landlord type (includes public housing)
print("  → Loading G40 (Rental by landlord type)...")
g40 = pd.read_csv(DATA_DIR / "2021Census_G40_AUST_SA1.csv")
print(f"     Loaded {len(g40):,} SA1 areas")

# Load G33 - Household income distribution
print("  → Loading G33 (Household income distribution)...")
g33 = pd.read_csv(DATA_DIR / "2021Census_G33_AUST_SA1.csv")
print(f"     Loaded {len(g33):,} SA1 areas")

# Load G01 - Population data
print("  → Loading G01 (Population data)...")
g01 = pd.read_csv(DATA_DIR / "2021Census_G01_AUST_SA1.csv")
print(f"     Loaded {len(g01):,} SA1 areas")

# Load G43 - Labour force status
print("  → Loading G43 (Labour force status)...")
g43 = pd.read_csv(DATA_DIR / "2021Census_G43_AUST_SA1.csv")
print(f"     Loaded {len(g43):,} SA1 areas")

print()

# ============================================================================
# STEP 2: Calculate Rental Affordability Metrics
# ============================================================================
print("STEP 2: Calculating rental affordability metrics...")
print("-" * 80)

# Create main analysis dataframe
df = g02[['SA1_CODE_2021', 'Median_rent_weekly', 'Median_tot_hhd_inc_weekly',
          'Median_tot_prsnl_inc_weekly', 'Median_age_persons', 'Average_household_size']].copy()

# Calculate rent-to-income ratio
df['rent_to_income_ratio'] = df['Median_rent_weekly'] / df['Median_tot_hhd_inc_weekly']

# Flag rental stress levels
df['rental_stress'] = (df['rent_to_income_ratio'] >= RENTAL_STRESS_THRESHOLD).astype(int)
df['severe_rental_stress'] = (df['rent_to_income_ratio'] >= SEVERE_STRESS_THRESHOLD).astype(int)

# Calculate stress category
def categorize_stress(ratio):
    if pd.isna(ratio) or ratio == 0:
        return 'No Data'
    elif ratio >= SEVERE_STRESS_THRESHOLD:
        return 'Severe Stress (50%+)'
    elif ratio >= RENTAL_STRESS_THRESHOLD:
        return 'Moderate Stress (30-50%)'
    else:
        return 'Affordable (<30%)'

df['stress_category'] = df['rent_to_income_ratio'].apply(categorize_stress)

print(f"  → Processed {len(df):,} SA1 areas")
print(f"  → Areas with rental stress (≥30%): {df['rental_stress'].sum():,} ({df['rental_stress'].sum()/len(df)*100:.1f}%)")
print(f"  → Areas with severe stress (≥50%): {df['severe_rental_stress'].sum():,} ({df['severe_rental_stress'].sum()/len(df)*100:.1f}%)")
print()

# ============================================================================
# STEP 3: Identify Low-Income Household Concentrations
# ============================================================================
print("STEP 3: Identifying low-income household concentrations...")
print("-" * 80)

# Calculate low-income household counts from G33
low_income_cols = [col for col in g33.columns if any(x in col for x in ['HI_1_149', 'HI_150_299', 'HI_300_399', 'HI_400_499', 'HI_500_649', 'HI_650_799'])]
g33['low_income_households'] = g33[low_income_cols].sum(axis=1)
g33['total_households'] = g33['Tot_Tot']
g33['low_income_pct'] = (g33['low_income_households'] / g33['total_households'] * 100).fillna(0)

# Merge with main dataframe
df = df.merge(g33[['SA1_CODE_2021', 'low_income_households', 'total_households', 'low_income_pct']],
              on='SA1_CODE_2021', how='left')

# Flag high concentration areas (>50% low income households)
df['high_low_income_concentration'] = (df['low_income_pct'] > 50).astype(int)

print(f"  → Average low-income household percentage: {df['low_income_pct'].mean():.1f}%")
print(f"  → SA1s with >50% low-income households: {df['high_low_income_concentration'].sum():,}")
print(f"  → Total low-income households identified: {df['low_income_households'].sum():,.0f}")
print()

# ============================================================================
# STEP 4: Compute Public Housing vs. Demand Gaps
# ============================================================================
print("STEP 4: Computing public housing vs. demand gaps...")
print("-" * 80)

# Extract public housing data from G37 (State/Territory housing authority)
public_housing_cols = [col for col in g37.columns if 'R_ST_h_auth' in col or 'R_Ste_ter_hsg_auth' in col]
g37['public_housing_dwellings'] = g37[public_housing_cols].sum(axis=1)

# Extract total rental dwellings
rental_cols = [col for col in g37.columns if col.startswith('R_') and 'Total' in col]
if rental_cols:
    g37['total_rental_dwellings'] = g37[rental_cols].sum(axis=1)
else:
    # Alternative: sum all rental types
    all_rental_cols = [col for col in g37.columns if col.startswith('R_')]
    g37['total_rental_dwellings'] = g37[all_rental_cols].sum(axis=1)

# Calculate total dwellings
total_dwelling_cols = [col for col in g37.columns if 'Tot_Tot' in col]
if total_dwelling_cols:
    g37['total_dwellings'] = g37[total_dwelling_cols[0]]
else:
    g37['total_dwellings'] = g37[[col for col in g37.columns if col.endswith('_Tot')]].iloc[:, -1]

# Merge public housing data
df = df.merge(g37[['SA1_CODE_2021', 'public_housing_dwellings', 'total_rental_dwellings', 'total_dwellings']],
              on='SA1_CODE_2021', how='left')

# Calculate public housing supply rate
df['public_housing_rate'] = (df['public_housing_dwellings'] / df['total_dwellings'] * 100).fillna(0)

# Estimate public housing demand (low-income households in rental stress)
df['estimated_demand'] = df['low_income_households'] * (df['rental_stress'].fillna(0))

# Calculate supply-demand gap
df['public_housing_gap'] = df['estimated_demand'] - df['public_housing_dwellings']
df['supply_demand_ratio'] = (df['public_housing_dwellings'] / df['estimated_demand']).replace([np.inf, -np.inf], 0).fillna(0)

# Flag areas with critical gaps (demand > supply by 10+ dwellings)
df['critical_housing_gap'] = (df['public_housing_gap'] > 10).astype(int)

print(f"  → Total public housing dwellings: {df['public_housing_dwellings'].sum():,.0f}")
print(f"  → Total estimated demand: {df['estimated_demand'].sum():,.0f}")
print(f"  → Total supply-demand gap: {df['public_housing_gap'].sum():,.0f}")
print(f"  → SA1s with critical gaps (>10 dwellings): {df['critical_housing_gap'].sum():,}")
print(f"  → Average public housing rate: {df['public_housing_rate'].mean():.2f}%")
print()

# ============================================================================
# STEP 5: Add Employment Accessibility Data
# ============================================================================
print("STEP 5: Integrating employment accessibility data...")
print("-" * 80)

# Add unemployment rate from G43
df = df.merge(g43[['SA1_CODE_2021', 'Percent_Unem_loyment_P', 'Percnt_LabForc_prticipation_P']],
              on='SA1_CODE_2021', how='left')

# Rename for clarity
df.rename(columns={
    'Percent_Unem_loyment_P': 'unemployment_rate',
    'Percnt_LabForc_prticipation_P': 'labour_force_participation'
}, inplace=True)

print(f"  → Average unemployment rate: {df['unemployment_rate'].mean():.2f}%")
print(f"  → Average labour force participation: {df['labour_force_participation'].mean():.2f}%")
print()

# ============================================================================
# STEP 6: Calculate Composite Risk Scores
# ============================================================================
print("STEP 6: Calculating composite rental stress and displacement risk scores...")
print("-" * 80)

# Normalize key metrics (0-1 scale)
def normalize_score(series, inverse=False):
    """Normalize series to 0-1 scale. If inverse=True, lower values get higher scores."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0, index=series.index)
    normalized = (series - min_val) / (max_val - min_val)
    return (1 - normalized) if inverse else normalized

# Create normalized scores (higher = more risk)
df['norm_rent_income_ratio'] = normalize_score(df['rent_to_income_ratio'].fillna(0))
df['norm_low_income_pct'] = normalize_score(df['low_income_pct'].fillna(0))
df['norm_public_housing_gap'] = normalize_score(df['public_housing_gap'].fillna(0))
df['norm_unemployment'] = normalize_score(df['unemployment_rate'].fillna(0))
df['norm_public_housing_rate'] = normalize_score(df['public_housing_rate'].fillna(0), inverse=True)

# Calculate composite rental stress score (weighted average)
df['rental_stress_score'] = (
    df['norm_rent_income_ratio'] * 0.35 +      # 35% weight on rent-to-income
    df['norm_low_income_pct'] * 0.25 +          # 25% weight on low-income concentration
    df['norm_public_housing_gap'] * 0.20 +      # 20% weight on housing gap
    df['norm_unemployment'] * 0.10 +            # 10% weight on unemployment
    df['norm_public_housing_rate'] * 0.10       # 10% weight on low public housing supply
) * 100  # Scale to 0-100

# Calculate displacement risk score (areas likely to experience gentrification/displacement)
df['displacement_risk_score'] = (
    df['norm_rent_income_ratio'] * 0.30 +      # 30% weight on affordability pressure
    df['norm_low_income_pct'] * 0.30 +          # 30% weight on vulnerable population
    df['norm_public_housing_rate'] * 0.20 +     # 20% weight on low social housing
    df['norm_unemployment'] * 0.20              # 20% weight on economic vulnerability
) * 100  # Scale to 0-100

# Categorize risk levels
def categorize_risk(score):
    if pd.isna(score) or score == 0:
        return 'No Data'
    elif score >= 75:
        return 'Critical (75-100)'
    elif score >= 50:
        return 'High (50-75)'
    elif score >= 25:
        return 'Moderate (25-50)'
    else:
        return 'Low (0-25)'

df['stress_risk_category'] = df['rental_stress_score'].apply(categorize_risk)
df['displacement_risk_category'] = df['displacement_risk_score'].apply(categorize_risk)

print(f"  → Average rental stress score: {df['rental_stress_score'].mean():.2f}/100")
print(f"  → Average displacement risk score: {df['displacement_risk_score'].mean():.2f}/100")
print()

print("  Risk distribution (Rental Stress):")
print(df['stress_risk_category'].value_counts().sort_index())
print()

print("  Risk distribution (Displacement Risk):")
print(df['displacement_risk_category'].value_counts().sort_index())
print()

# ============================================================================
# STEP 7: Identify Optimal Social Housing Investment Locations
# ============================================================================
print("STEP 7: Identifying optimal social housing investment locations...")
print("-" * 80)

# Calculate investment priority score
# High priority = high rental stress + low public housing + high demand
df['investment_priority_score'] = (
    df['rental_stress_score'] * 0.40 +          # 40% weight on rental stress
    df['norm_public_housing_gap'] * 100 * 0.30 + # 30% weight on supply gap
    df['norm_low_income_pct'] * 100 * 0.20 +     # 20% weight on vulnerable population
    df['norm_unemployment'] * 100 * 0.10         # 10% weight on unemployment
)

def categorize_investment(score):
    if pd.isna(score) or score == 0:
        return 'No Priority'
    elif score >= 75:
        return 'Critical Priority'
    elif score >= 50:
        return 'High Priority'
    elif score >= 25:
        return 'Moderate Priority'
    else:
        return 'Low Priority'

df['investment_priority'] = df['investment_priority_score'].apply(categorize_investment)

print(f"  → Average investment priority score: {df['investment_priority_score'].mean():.2f}/100")
print()

print("  Investment priority distribution:")
print(df['investment_priority'].value_counts().sort_index())
print()

# ============================================================================
# STEP 8: Generate Summary Statistics
# ============================================================================
print("=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print()

print("RENTAL AFFORDABILITY")
print("-" * 40)
print(f"Total SA1 areas analyzed: {len(df):,}")
print(f"Areas with rental stress (≥30%): {df['rental_stress'].sum():,} ({df['rental_stress'].sum()/len(df)*100:.1f}%)")
print(f"Areas with severe stress (≥50%): {df['severe_rental_stress'].sum():,} ({df['severe_rental_stress'].sum()/len(df)*100:.1f}%)")
print(f"Average rent-to-income ratio: {df['rent_to_income_ratio'].mean():.1%}")
print(f"Median weekly rent: ${df['Median_rent_weekly'].median():,.0f}")
print(f"Median weekly household income: ${df['Median_tot_hhd_inc_weekly'].median():,.0f}")
print()

print("LOW-INCOME HOUSEHOLDS")
print("-" * 40)
print(f"Total households: {df['total_households'].sum():,.0f}")
print(f"Low-income households: {df['low_income_households'].sum():,.0f} ({df['low_income_households'].sum()/df['total_households'].sum()*100:.1f}%)")
print(f"SA1s with >50% low-income: {df['high_low_income_concentration'].sum():,}")
print()

print("PUBLIC HOUSING")
print("-" * 40)
print(f"Total public housing dwellings: {df['public_housing_dwellings'].sum():,.0f}")
print(f"Total rental dwellings: {df['total_rental_dwellings'].sum():,.0f}")
print(f"Public housing as % of rentals: {df['public_housing_dwellings'].sum()/df['total_rental_dwellings'].sum()*100:.2f}%")
print(f"Estimated demand (low-income + stress): {df['estimated_demand'].sum():,.0f}")
print(f"Supply-demand gap: {df['public_housing_gap'].sum():,.0f} dwellings")
print(f"SA1s with critical gaps: {df['critical_housing_gap'].sum():,}")
print()

print("RISK SCORES")
print("-" * 40)
print(f"Critical rental stress areas (≥75): {(df['rental_stress_score'] >= 75).sum():,}")
print(f"High displacement risk areas (≥75): {(df['displacement_risk_score'] >= 75).sum():,}")
print(f"Critical investment priority areas: {(df['investment_priority'] == 'Critical Priority').sum():,}")
print()

# ============================================================================
# STEP 9: Export Results
# ============================================================================
print("=" * 80)
print("EXPORTING RESULTS")
print("=" * 80)
print()

# Export full analysis
output_file = OUTPUT_DIR / "rental_stress_analysis_full.csv"
df.to_csv(output_file, index=False)
print(f"✓ Full analysis exported: {output_file}")
print(f"  ({len(df):,} SA1 areas)")

# Export top rental stress hotspots
top_stress = df.nlargest(1000, 'rental_stress_score')
stress_file = OUTPUT_DIR / "top_1000_rental_stress_hotspots.csv"
top_stress.to_csv(stress_file, index=False)
print(f"✓ Top 1000 rental stress hotspots: {stress_file}")

# Export top displacement risk areas
top_displacement = df.nlargest(1000, 'displacement_risk_score')
displacement_file = OUTPUT_DIR / "top_1000_displacement_risk_areas.csv"
top_displacement.to_csv(displacement_file, index=False)
print(f"✓ Top 1000 displacement risk areas: {displacement_file}")

# Export critical investment priorities
critical_investment = df.nlargest(500, 'investment_priority_score')
investment_file = OUTPUT_DIR / "top_500_investment_priorities.csv"
critical_investment.to_csv(investment_file, index=False)
print(f"✓ Top 500 investment priorities: {investment_file}")

# Export areas with critical public housing gaps
critical_gaps = df[df['critical_housing_gap'] == 1].nlargest(1000, 'public_housing_gap')
gaps_file = OUTPUT_DIR / "critical_public_housing_gaps.csv"
critical_gaps.to_csv(gaps_file, index=False)
print(f"✓ Critical public housing gaps: {gaps_file}")
print(f"  ({len(critical_gaps):,} SA1 areas)")

# ============================================================================
# STEP 10: Generate Summary Report
# ============================================================================
report_file = OUTPUT_DIR / "ANALYSIS_SUMMARY.md"
with open(report_file, 'w') as f:
    f.write("# Rental Stress & Social Housing Demand Forecasting Analysis\n")
    f.write("## 2021 Australian Census - SA1 Level Analysis\n\n")

    f.write("---\n\n")
    f.write("## Executive Summary\n\n")
    f.write(f"This analysis processed **{len(df):,} SA1 statistical areas** across Australia to identify:\n")
    f.write("1. Rental affordability stress hotspots\n")
    f.write("2. Low-income household concentrations\n")
    f.write("3. Public housing supply-demand gaps\n")
    f.write("4. Areas at risk of displacement\n")
    f.write("5. Optimal social housing investment locations\n\n")

    f.write("---\n\n")
    f.write("## Key Findings\n\n")

    f.write("### Rental Affordability Crisis\n\n")
    f.write(f"- **{df['rental_stress'].sum():,} SA1 areas ({df['rental_stress'].sum()/len(df)*100:.1f}%)** experiencing rental stress (rent ≥30% of income)\n")
    f.write(f"- **{df['severe_rental_stress'].sum():,} SA1 areas ({df['severe_rental_stress'].sum()/len(df)*100:.1f}%)** in severe rental stress (rent ≥50% of income)\n")
    f.write(f"- Average rent-to-income ratio: **{df['rent_to_income_ratio'].mean():.1%}**\n")
    f.write(f"- Median weekly rent: **${df['Median_rent_weekly'].median():,.0f}**\n")
    f.write(f"- Median weekly household income: **${df['Median_tot_hhd_inc_weekly'].median():,.0f}**\n\n")

    f.write("### Low-Income Household Vulnerability\n\n")
    f.write(f"- Total households analyzed: **{df['total_households'].sum():,.0f}**\n")
    f.write(f"- Low-income households (<$800/week): **{df['low_income_households'].sum():,.0f}** ({df['low_income_households'].sum()/df['total_households'].sum()*100:.1f}%)\n")
    f.write(f"- SA1s with >50% low-income households: **{df['high_low_income_concentration'].sum():,}**\n")
    f.write(f"- Average low-income percentage: **{df['low_income_pct'].mean():.1f}%**\n\n")

    f.write("### Public Housing Supply Crisis\n\n")
    f.write(f"- Total public housing dwellings: **{df['public_housing_dwellings'].sum():,.0f}**\n")
    f.write(f"- Total rental dwellings: **{df['total_rental_dwellings'].sum():,.0f}**\n")
    f.write(f"- Public housing as % of rentals: **{df['public_housing_dwellings'].sum()/df['total_rental_dwellings'].sum()*100:.2f}%**\n")
    f.write(f"- Estimated demand (low-income in stress): **{df['estimated_demand'].sum():,.0f}**\n")
    f.write(f"- **Supply-demand gap: {df['public_housing_gap'].sum():,.0f} dwellings**\n")
    f.write(f"- SA1s with critical gaps (>10 dwellings): **{df['critical_housing_gap'].sum():,}**\n\n")

    f.write("### Risk Assessment\n\n")
    f.write(f"- SA1s with critical rental stress (score ≥75): **{(df['rental_stress_score'] >= 75).sum():,}**\n")
    f.write(f"- SA1s with high displacement risk (score ≥75): **{(df['displacement_risk_score'] >= 75).sum():,}**\n")
    f.write(f"- SA1s requiring critical investment priority: **{(df['investment_priority'] == 'Critical Priority').sum():,}**\n")
    f.write(f"- Average rental stress score: **{df['rental_stress_score'].mean():.2f}/100**\n")
    f.write(f"- Average displacement risk score: **{df['displacement_risk_score'].mean():.2f}/100**\n\n")

    f.write("---\n\n")
    f.write("## Methodology\n\n")

    f.write("### Data Sources\n")
    f.write("- **G02**: Median rent & household income\n")
    f.write("- **G33**: Household income distributions\n")
    f.write("- **G37**: Tenure type (owned/rented/public housing)\n")
    f.write("- **G40**: Rental by landlord type\n")
    f.write("- **G43**: Labour force status\n\n")

    f.write("### Key Metrics\n\n")
    f.write("1. **Rent-to-Income Ratio**: Weekly rent / Weekly household income\n")
    f.write("   - Stress threshold: ≥30%\n")
    f.write("   - Severe stress threshold: ≥50%\n\n")

    f.write("2. **Low-Income Households**: Households earning <$800/week\n\n")

    f.write("3. **Public Housing Gap**: Estimated demand - Current supply\n")
    f.write("   - Demand = Low-income households in rental stress\n\n")

    f.write("4. **Rental Stress Score** (0-100):\n")
    f.write("   - Rent-to-income ratio: 35%\n")
    f.write("   - Low-income concentration: 25%\n")
    f.write("   - Public housing gap: 20%\n")
    f.write("   - Unemployment rate: 10%\n")
    f.write("   - Public housing supply: 10%\n\n")

    f.write("5. **Displacement Risk Score** (0-100):\n")
    f.write("   - Affordability pressure: 30%\n")
    f.write("   - Vulnerable population: 30%\n")
    f.write("   - Low social housing: 20%\n")
    f.write("   - Economic vulnerability: 20%\n\n")

    f.write("6. **Investment Priority Score** (0-100):\n")
    f.write("   - Rental stress: 40%\n")
    f.write("   - Supply-demand gap: 30%\n")
    f.write("   - Vulnerable population: 20%\n")
    f.write("   - Unemployment: 10%\n\n")

    f.write("---\n\n")
    f.write("## Output Files\n\n")
    f.write("1. `rental_stress_analysis_full.csv` - Complete analysis for all SA1 areas\n")
    f.write("2. `top_1000_rental_stress_hotspots.csv` - Highest rental stress areas\n")
    f.write("3. `top_1000_displacement_risk_areas.csv` - Areas most at risk of displacement\n")
    f.write("4. `top_500_investment_priorities.csv` - Optimal social housing investment locations\n")
    f.write("5. `critical_public_housing_gaps.csv` - Areas with critical supply-demand gaps\n\n")

    f.write("---\n\n")
    f.write("## Policy Implications\n\n")
    f.write("### Immediate Action Required\n\n")
    f.write(f"1. **Address Critical Supply Gap**: {df['public_housing_gap'].sum():,.0f} additional public housing dwellings needed\n")
    f.write(f"2. **Target High-Risk Areas**: {(df['rental_stress_score'] >= 75).sum():,} SA1s require immediate intervention\n")
    f.write(f"3. **Prevent Displacement**: {(df['displacement_risk_score'] >= 75).sum():,} areas at critical risk\n\n")

    f.write("### Investment Priorities\n\n")
    f.write("Focus social housing investment on:\n")
    f.write("- Areas with high rental stress scores (≥75)\n")
    f.write("- High concentrations of low-income households (>50%)\n")
    f.write("- Large supply-demand gaps (>10 dwellings)\n")
    f.write("- High unemployment rates\n")
    f.write("- Low existing public housing supply\n\n")

    f.write("### Spatial Targeting\n\n")
    f.write("The analysis identifies specific SA1 areas for:\n")
    f.write("- New social housing construction\n")
    f.write("- Rental assistance programs\n")
    f.write("- Community housing partnerships\n")
    f.write("- Employment accessibility improvements\n\n")

    f.write("---\n\n")
    f.write("*Analysis generated using 2021 Australian Census data (SA1 level)*\n")
    f.write("*Australian Bureau of Statistics - General Community Profile (GCP)*\n")

print(f"✓ Summary report generated: {report_file}")
print()

print("=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print()
print(f"All outputs saved to: {OUTPUT_DIR}/")
print()
print("Next steps for spatial regression modeling:")
print("1. Load geographic boundary files for SA1 areas")
print("2. Build spatial weights matrix")
print("3. Run spatial lag/error models")
print("4. Generate predicted hotspot maps")
print("5. Validate with temporal trends")
print()
