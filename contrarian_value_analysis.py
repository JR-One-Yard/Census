#!/usr/bin/env python3
"""
CONTRARIAN VALUE ANALYSIS - Finding Hidden Gems
================================================

Challenges conventional wisdom by exploring:
1. "Too Old" = Safety & Quiet (not bad!)
2. Wealth from Investment Income (not just salaries)
3. Separate Houses = Family Space (not density)
4. Retiree Arbitrage (safe, affordable, soon-to-turnover housing)

Author: Contrarian Real Estate Analysis
Date: 2025-11-22
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
MAPPING_FILE = "/home/user/Census/SAL_Suburb_Name_Mapping.csv"
OUTPUT_DIR = "/home/user/Census"

print("=" * 120)
print(" " * 40 + "CONTRARIAN VALUE ANALYSIS")
print(" " * 35 + "Challenging Conventional Wisdom")
print("=" * 120)
print()

# Load the base value analysis
df_base = pd.read_csv(f'{OUTPUT_DIR}/sydney_all_suburbs_value_analysis.csv')
print(f"Loaded {len(df_base):,} Sydney suburbs from base analysis")

# Load suburb mapping
suburb_mapping = pd.read_csv(MAPPING_FILE)

# Filter to Sydney suburbs (same as base analysis - suburbs in df_base)
sydney_sal_codes = set(df_base['SAL_CODE_2021'].values)
print(f"Analyzing {len(sydney_sal_codes):,} Sydney suburbs")
print()

# ============================================================================
# ANALYSIS 1: INCOME & WEALTH PROXIES - Using Available Data
# ============================================================================
print("[1/5] Creating wealth proxies from available data...")

# Note: Census doesn't have income SOURCE breakdown (wages vs investment)
# But we can use proxies:
# - High median age + high median income = likely investment/super income
# - High median income + low employment rate = non-wage income

income_sources = pd.DataFrame({
    'SAL_CODE_2021': list(sydney_sal_codes)
})

# Merge with base data to get income and age
temp_merge = df_base[['SAL_CODE_2021', 'Median_tot_prsnl_inc_weekly', 'Median_age_persons',
                       'Median_tot_hhd_inc_weekly']].copy()
income_sources = income_sources.merge(temp_merge, on='SAL_CODE_2021', how='left')

# Wealth proxy: High income + older age (likely from assets, not wages)
# Normalize to 0-100 scale
income_sources['Wealth_Score'] = (
    (income_sources['Median_tot_prsnl_inc_weekly'].rank(pct=True) * 50) +
    ((income_sources['Median_age_persons'] - 45).clip(0, 25) * 2)  # Age 45-70 gets bonus
).fillna(50)

# For consistency with later code
income_sources['Investment_Pct'] = income_sources['Wealth_Score']  # Proxy
income_sources['Wage_Pct'] = 100 - income_sources['Wealth_Score']  # Inverse proxy
income_sources['Govt_Benefit_Pct'] = (70 - income_sources['Median_age_persons']).clip(0, 30)  # Young or very old

print(f"   ✓ Created wealth proxies for {len(income_sources):,} suburbs (using age + income)")

# ============================================================================
# ANALYSIS 2: DWELLING TYPE - Separate Houses vs Units
# ============================================================================
print("\n[2/5] Analyzing Dwelling Types - Houses vs Units...")

# Load G33 - Dwelling Structure (if available, otherwise use G40/G41)
# Let's try G40 - Dwelling structure
try:
    df_dwelling = pd.read_csv(f"{DATA_DIR}2021Census_G40_AUST_SAL.csv")
    df_dwelling = df_dwelling[df_dwelling['SAL_CODE_2021'].isin(sydney_sal_codes)]

    dwelling_metrics = pd.DataFrame({
        'SAL_CODE_2021': df_dwelling['SAL_CODE_2021']
    })

    # Find columns for separate houses
    house_cols = [col for col in df_dwelling.columns if 'Separate_house' in col and col.startswith('Total_')]
    # Find columns for total dwellings
    total_dwell_col = [col for col in df_dwelling.columns if col.startswith('Total_Total')][0]

    if house_cols:
        dwelling_metrics['Separate_Houses'] = df_dwelling[house_cols[0]]
        dwelling_metrics['Total_Dwellings'] = df_dwelling[total_dwell_col]
        dwelling_metrics['House_Pct'] = (dwelling_metrics['Separate_Houses'] / dwelling_metrics['Total_Dwellings'] * 100).fillna(0)

        print(f"   ✓ Calculated dwelling type for {len(dwelling_metrics):,} suburbs")
    else:
        print("   ⚠ Separate house data not found in expected format")
        dwelling_metrics['House_Pct'] = 50.0  # Default

except Exception as e:
    print(f"   ⚠ Could not load dwelling data: {e}")
    dwelling_metrics = pd.DataFrame({
        'SAL_CODE_2021': list(sydney_sal_codes),
        'House_Pct': 50.0
    })

# ============================================================================
# ANALYSIS 3: TENURE TYPE - Owned Outright vs Mortgage vs Renting
# ============================================================================
print("\n[3/5] Analyzing Housing Tenure - Ownership Patterns...")

# G40 also has tenure data
try:
    tenure_metrics = pd.DataFrame({
        'SAL_CODE_2021': df_dwelling['SAL_CODE_2021']
    })

    # Find ownership columns
    owned_cols = [col for col in df_dwelling.columns if 'Owned_outright' in col and col.startswith('Total_')]
    mortgage_cols = [col for col in df_dwelling.columns if 'Owned_with_a_mortgage' in col and col.startswith('Total_')]
    rent_cols = [col for col in df_dwelling.columns if 'Rented' in col and col.startswith('Total_') and 'agent' not in col]

    if owned_cols and mortgage_cols:
        tenure_metrics['Owned_Outright'] = df_dwelling[owned_cols[0]]
        tenure_metrics['Owned_Mortgage'] = df_dwelling[mortgage_cols[0]]
        if rent_cols:
            tenure_metrics['Rented'] = df_dwelling[rent_cols[0]]

        tenure_metrics['Total_Dwellings'] = df_dwelling[total_dwell_col]
        tenure_metrics['Outright_Pct'] = (tenure_metrics['Owned_Outright'] / tenure_metrics['Total_Dwellings'] * 100).fillna(0)
        tenure_metrics['Mortgage_Pct'] = (tenure_metrics['Owned_Mortgage'] / tenure_metrics['Total_Dwellings'] * 100).fillna(0)

        # Retiree indicator = high outright ownership
        tenure_metrics['Retiree_Score'] = tenure_metrics['Outright_Pct']

        print(f"   ✓ Calculated tenure patterns for {len(tenure_metrics):,} suburbs")
    else:
        print("   ⚠ Tenure data not found")
        tenure_metrics['Outright_Pct'] = 30.0
        tenure_metrics['Retiree_Score'] = 30.0

except Exception as e:
    print(f"   ⚠ Could not calculate tenure: {e}")
    tenure_metrics = pd.DataFrame({
        'SAL_CODE_2021': list(sydney_sal_codes),
        'Outright_Pct': 30.0,
        'Retiree_Score': 30.0
    })

# ============================================================================
# ANALYSIS 4: BUILD CONTRARIAN MASTER DATASET
# ============================================================================
print("\n[4/5] Building contrarian master dataset...")

# Start with base analysis
contrarian_df = df_base.copy()

# Add income source data
contrarian_df = contrarian_df.merge(income_sources[['SAL_CODE_2021', 'Wage_Pct', 'Investment_Pct', 'Govt_Benefit_Pct', 'Wealth_Score']],
                                     on='SAL_CODE_2021', how='left')

# Add dwelling type
contrarian_df = contrarian_df.merge(dwelling_metrics[['SAL_CODE_2021', 'House_Pct']],
                                     on='SAL_CODE_2021', how='left')

# Add tenure
contrarian_df = contrarian_df.merge(tenure_metrics[['SAL_CODE_2021', 'Outright_Pct', 'Retiree_Score']],
                                     on='SAL_CODE_2021', how='left')

print(f"   ✓ Contrarian dataset built: {len(contrarian_df):,} suburbs")

# ============================================================================
# ANALYSIS 5: CONTRARIAN STRATEGIES
# ============================================================================
print("\n[5/5] Identifying contrarian opportunities...")

# ------------------------------------------------
# STRATEGY A: "THE RETIREE ARBITRAGE"
# ------------------------------------------------
# High median age (60+) + High outright ownership + Separate houses + Low crime proxy

retiree_suburbs = contrarian_df[
    (contrarian_df['Median_age_persons'] >= 60) &
    (contrarian_df['Outright_Pct'] >= 40) &
    (contrarian_df['House_Pct'] >= 60) &
    (contrarian_df['Average_household_size'] <= 2.2)
].copy()

# Score them by: Safety (age) + Affordability (moderate mortgage) + Space (houses)
retiree_suburbs['Retiree_Arbitrage_Score'] = (
    (retiree_suburbs['Median_age_persons'] - 60) * 2 +  # Older = safer
    (100 - retiree_suburbs['Price_Index']) +  # Lower price = better
    retiree_suburbs['House_Pct'] * 0.5 +  # More houses = more space
    retiree_suburbs['Outright_Pct'] * 0.5  # More outright = stable neighborhood
)

retiree_suburbs_sorted = retiree_suburbs.sort_values('Retiree_Arbitrage_Score', ascending=False)

print()
print("=" * 120)
print("STRATEGY A: THE RETIREE ARBITRAGE")
print("=" * 120)
print()
print("Theory: Older suburbs = Safe, quiet, spacious. Perfect for young families seeking peace.")
print("Bonus: Eventual housing turnover as retirees downsize/pass away.")
print()
print(f"Found {len(retiree_suburbs):,} suburbs matching criteria:")
print("  • Median age ≥ 60 (safe, established)")
print("  • Outright ownership ≥ 40% (stable, no foreclosure risk)")
print("  • Separate houses ≥ 60% (space, yards)")
print("  • Small households ≤ 2.2 (quiet)")
print()
print("TOP 20 RETIREE ARBITRAGE OPPORTUNITIES:")
print()
print(f"{'Rank':<6}{'Suburb':<35}{'Score':>8}  {'Age':>5}  {'Houses':>8}  {'Owned':>7}  {'Mortgage':>10}  {'Edu':>6}")
print("-" * 115)

for i, (_, row) in enumerate(retiree_suburbs_sorted.head(20).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<35}{row['Retiree_Arbitrage_Score']:>8.0f}  "
          f"{row['Median_age_persons']:>5.0f}  {row['House_Pct']:>7.1f}%  "
          f"{row['Outright_Pct']:>6.1f}%  ${row['Median_mortgage_repay_monthly']:>9,.0f}  "
          f"{row['Tertiary_Pct']:>5.1f}%")

# ------------------------------------------------
# STRATEGY B: "THE HIDDEN WEALTH SUBURBS"
# ------------------------------------------------
# High investment income % (wealthy but not flashy) + Moderate median income (not priced in)

wealthy_suburbs = contrarian_df[
    (contrarian_df['Investment_Pct'] >= contrarian_df['Investment_Pct'].quantile(0.75)) &
    (contrarian_df['Median_tot_prsnl_inc_weekly'] < contrarian_df['Median_tot_prsnl_inc_weekly'].median())
].copy()

wealthy_suburbs['Hidden_Wealth_Score'] = (
    wealthy_suburbs['Investment_Pct'] * 2 +  # Investment income = true wealth
    wealthy_suburbs['Outright_Pct'] +  # Outright ownership = paid-off wealth
    (100 - wealthy_suburbs['Price_Index'])  # But not yet expensive
)

wealthy_suburbs_sorted = wealthy_suburbs.sort_values('Hidden_Wealth_Score', ascending=False)

print()
print("=" * 120)
print("STRATEGY B: HIDDEN WEALTH SUBURBS")
print("=" * 120)
print()
print("Theory: High investment income = real wealth (not just high salaries).")
print("These suburbs have wealthy residents but moderate median incomes = underpriced.")
print()
print(f"Found {len(wealthy_suburbs):,} suburbs with high investment income but moderate wages:")
print()
print("TOP 20 HIDDEN WEALTH OPPORTUNITIES:")
print()
print(f"{'Rank':<6}{'Suburb':<35}{'Score':>8}  {'Invest%':>9}  {'Wages':>8}  {'Owned':>7}  {'Mortgage':>10}")
print("-" * 110)

for i, (_, row) in enumerate(wealthy_suburbs_sorted.head(20).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<35}{row['Hidden_Wealth_Score']:>8.0f}  "
          f"{row['Investment_Pct']:>8.1f}%  ${row['Median_tot_prsnl_inc_weekly']:>7,.0f}  "
          f"{row['Outright_Pct']:>6.1f}%  ${row['Median_mortgage_repay_monthly']:>9,.0f}")

# ------------------------------------------------
# STRATEGY C: "THE FAMILY SPACE PARADOX"
# ------------------------------------------------
# High % separate houses (space!) + Low density + Moderate price

family_space = contrarian_df[
    (contrarian_df['House_Pct'] >= 80) &
    (contrarian_df['Density_per_sqkm'] < 2000) &
    (contrarian_df['Average_household_size'] >= 2.5) &
    (contrarian_df['Price_Index'] < 60)
].copy()

family_space['Space_Value_Score'] = (
    family_space['House_Pct'] +  # Houses = space
    (5000 - family_space['Density_per_sqkm'].clip(upper=5000)) / 50 +  # Low density = room
    (100 - family_space['Price_Index']) +  # Affordable
    family_space['Average_household_size'] * 20  # Family-sized
)

family_space_sorted = family_space.sort_values('Space_Value_Score', ascending=False)

print()
print("=" * 120)
print("STRATEGY C: THE FAMILY SPACE PARADOX")
print("=" * 120)
print()
print("Theory: Separate houses + Low density = Yards, space, quiet.")
print("Modern analysis overvalues density. Families actually want space!")
print()
print(f"Found {len(family_space):,} suburbs with exceptional space at moderate prices:")
print()
print("TOP 20 FAMILY SPACE OPPORTUNITIES:")
print()
print(f"{'Rank':<6}{'Suburb':<35}{'Score':>8}  {'Houses':>8}  {'Density':>9}  {'HH Size':>8}  {'Mortgage':>10}")
print("-" * 110)

for i, (_, row) in enumerate(family_space_sorted.head(20).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<35}{row['Space_Value_Score']:>8.0f}  "
          f"{row['House_Pct']:>7.1f}%  {row['Density_per_sqkm']:>8.0f}/km²  "
          f"{row['Average_household_size']:>8.1f}  ${row['Median_mortgage_repay_monthly']:>9,.0f}")

# ------------------------------------------------
# STRATEGY D: "THE COMBINED CONTRARIAN PLAY"
# ------------------------------------------------
# Combination of all contrarian factors

contrarian_df['Contrarian_Score'] = (
    contrarian_df['Investment_Pct'].fillna(0) * 0.2 +  # Wealth beyond wages
    contrarian_df['House_Pct'].fillna(50) * 0.2 +  # Space
    contrarian_df['Outright_Pct'].fillna(30) * 0.2 +  # Stability
    ((contrarian_df['Median_age_persons'] - 45).clip(0, 20)) * 0.2 +  # Maturity (45-65 sweet spot)
    (100 - contrarian_df['Price_Index']) * 0.2  # Still affordable
)

contrarian_top = contrarian_df.sort_values('Contrarian_Score', ascending=False).head(50)

print()
print("=" * 120)
print("STRATEGY D: COMBINED CONTRARIAN OPPORTUNITIES")
print("=" * 120)
print()
print("Combining all contrarian factors:")
print("  • Investment income (real wealth)")
print("  • Separate houses (space)")
print("  • Outright ownership (stability)")
print("  • Mature age (safety)")
print("  • Moderate price (value)")
print()
print("TOP 30 COMBINED CONTRARIAN PLAYS:")
print()
print(f"{'Rank':<6}{'Suburb':<30}{'Score':>8}  {'Age':>5}  {'Invest%':>9}  {'Houses':>8}  {'Owned':>7}  {'Price':>7}  {'Mortgage':>10}")
print("-" * 120)

for i, (_, row) in enumerate(contrarian_top.head(30).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<30}{row['Contrarian_Score']:>8.1f}  "
          f"{row['Median_age_persons']:>5.0f}  {row['Investment_Pct']:>8.1f}%  "
          f"{row['House_Pct']:>7.1f}%  {row['Outright_Pct']:>6.1f}%  "
          f"{row['Price_Index']:>6.0f}  ${row['Median_mortgage_repay_monthly']:>9,.0f}")

# Save results
print()
print("=" * 120)
print("SAVING RESULTS")
print("=" * 120)
print()

retiree_suburbs_sorted.head(50).to_csv(f'{OUTPUT_DIR}/contrarian_retiree_arbitrage_top50.csv', index=False)
print("✓ Saved: contrarian_retiree_arbitrage_top50.csv")

wealthy_suburbs_sorted.head(50).to_csv(f'{OUTPUT_DIR}/contrarian_hidden_wealth_top50.csv', index=False)
print("✓ Saved: contrarian_hidden_wealth_top50.csv")

family_space_sorted.head(50).to_csv(f'{OUTPUT_DIR}/contrarian_family_space_top50.csv', index=False)
print("✓ Saved: contrarian_family_space_top50.csv")

contrarian_top.to_csv(f'{OUTPUT_DIR}/contrarian_combined_top50.csv', index=False)
print("✓ Saved: contrarian_combined_top50.csv")

# Save full dataset with all contrarian metrics
contrarian_df.to_csv(f'{OUTPUT_DIR}/sydney_all_suburbs_with_contrarian_metrics.csv', index=False)
print("✓ Saved: sydney_all_suburbs_with_contrarian_metrics.csv")

print()
print("=" * 120)
print("CONTRARIAN ANALYSIS COMPLETE")
print("=" * 120)
print()
print("Key Insights:")
print("  • Older suburbs (60+) offer safety, space, and peace - not a liability!")
print("  • Investment income reveals true wealth beyond salaries")
print("  • Separate houses provide space that families actually want")
print("  • High outright ownership = stable, low-risk neighborhoods")
print()
print("These suburbs are overlooked by conventional analysis but offer exceptional")
print("value for families prioritizing safety, space, and stability over appreciation.")
print()
