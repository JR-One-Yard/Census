#!/usr/bin/env python3
"""
Sydney/NSW Housing Affordability Crisis Deep Dive Analysis
Focuses on Greater Sydney metropolitan area
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("=" * 80)
print("SYDNEY/NSW HOUSING AFFORDABILITY CRISIS ANALYSIS")
print("2021 Australian Census Data")
print("=" * 80)
print()

# =============================================================================
# STEP 1: LOAD COMPREHENSIVE DATA
# =============================================================================
print("STEP 1: Loading comprehensive housing data...")

comprehensive = pd.read_csv('housing_affordability_comprehensive.csv')
crisis_areas = pd.read_csv('housing_crisis_areas.csv')
sweet_spots = pd.read_csv('housing_affordability_sweet_spots.csv')

print(f"✓ Loaded {len(comprehensive):,} total suburbs")
print()

# =============================================================================
# STEP 2: IDENTIFY NSW AND SYDNEY SUBURBS
# =============================================================================
print("STEP 2: Identifying NSW and Sydney suburbs...")

# NSW SAL codes start with "1" (SAL1xxxx)
# Sydney metro is a subset of NSW - we'll use multiple methods to identify

# Method 1: SAL code patterns for NSW (codes starting with 1)
comprehensive['is_nsw'] = comprehensive['SAL_CODE_2021'].astype(str).str.startswith('SAL1')

# For Sydney, we'll use common Sydney suburb name patterns
# Greater Sydney roughly includes SAL codes 10000-14999
comprehensive['is_sydney_metro'] = (
    comprehensive['SAL_CODE_2021'].astype(str).str.startswith('SAL1') &
    (comprehensive['SAL_CODE_2021'].astype(str).str.extract('(\d+)')[0].astype(int) >= 10000) &
    (comprehensive['SAL_CODE_2021'].astype(str).str.extract('(\d+)')[0].astype(int) <= 14999)
)

# Filter datasets
nsw_data = comprehensive[comprehensive['is_nsw']].copy()
sydney_data = comprehensive[comprehensive['is_sydney_metro']].copy()

print(f"✓ Identified {len(nsw_data):,} NSW suburbs")
print(f"✓ Identified {len(sydney_data):,} Greater Sydney suburbs")
print()

# Also filter crisis and sweet spot data for Sydney
sydney_crisis = crisis_areas[crisis_areas['SAL_CODE_2021'].astype(str).str.startswith('SAL1')].copy()
sydney_crisis['is_sydney_metro'] = (
    (sydney_crisis['SAL_CODE_2021'].astype(str).str.extract('(\d+)')[0].astype(int) >= 10000) &
    (sydney_crisis['SAL_CODE_2021'].astype(str).str.extract('(\d+)')[0].astype(int) <= 14999)
)
sydney_crisis_metro = sydney_crisis[sydney_crisis['is_sydney_metro']].copy()

sydney_sweet = sweet_spots[sweet_spots['SAL_CODE_2021'].astype(str).str.startswith('SAL1')].copy()
sydney_sweet['is_sydney_metro'] = (
    (sydney_sweet['SAL_CODE_2021'].astype(str).str.extract('(\d+)')[0].astype(int) >= 10000) &
    (sydney_sweet['SAL_CODE_2021'].astype(str).str.extract('(\d+)')[0].astype(int) <= 14999)
)
sydney_sweet_metro = sydney_sweet[sydney_sweet['is_sydney_metro']].copy()

print(f"✓ Sydney metro crisis areas: {len(sydney_crisis_metro):,}")
print(f"✓ Sydney metro sweet spots: {len(sydney_sweet_metro):,}")
print()

# =============================================================================
# STEP 3: SYDNEY vs AUSTRALIA COMPARISON
# =============================================================================
print("STEP 3: Comparing Sydney to National Averages...")
print("-" * 80)

comparison = {
    'Metric': [],
    'Australia': [],
    'NSW': [],
    'Sydney Metro': [],
    'Sydney vs Australia': []
}

metrics = {
    'Median Age': ('Median_age_persons', 'years'),
    'Median Household Income': ('Median_tot_hhd_inc_weekly', '$/week'),
    'Median Rent': ('Median_rent_weekly', '$/week'),
    'Median Mortgage': ('Median_mortgage_repay_monthly', '$/month'),
    'Mortgage Stress Ratio': ('mortgage_stress_ratio', '%'),
    'Rent Stress Ratio': ('rent_stress_ratio', '%'),
    '% Owned Outright': ('pct_owned_outright', '%'),
    '% Owned with Mortgage': ('pct_owned_mortgage', '%'),
    '% Renting': ('pct_renting', '%'),
    '% Apartments': ('pct_apartments', '%'),
    '% Young Adults': ('pct_young_adults', '%'),
    '% Low Income': ('pct_low_income', '%'),
}

for metric_name, (col, unit) in metrics.items():
    aus_val = comprehensive[col].mean()
    nsw_val = nsw_data[col].mean()
    syd_val = sydney_data[col].mean()
    diff = ((syd_val - aus_val) / aus_val * 100) if aus_val != 0 else 0

    comparison['Metric'].append(metric_name)
    comparison['Australia'].append(f"{aus_val:.1f}{unit}")
    comparison['NSW'].append(f"{nsw_val:.1f}{unit}")
    comparison['Sydney Metro'].append(f"{syd_val:.1f}{unit}")
    comparison['Sydney vs Australia'].append(f"{diff:+.1f}%")

comparison_df = pd.DataFrame(comparison)
print(comparison_df.to_string(index=False))
print()

# =============================================================================
# STEP 4: TOP SYDNEY CRISIS AREAS
# =============================================================================
print("\nSTEP 4: Top Sydney Metro Crisis Areas...")
print("-" * 80)

# Sort by crisis score
sydney_crisis_sorted = sydney_crisis_metro.sort_values('crisis_score', ascending=False)

print(f"\nTop 30 Sydney Crisis Areas by Crisis Score:")
print()
top_sydney_crisis = sydney_crisis_sorted.head(30)[
    ['Suburb', 'mortgage_stress_ratio', 'rent_stress_ratio',
     'Median_tot_hhd_inc_weekly', 'Median_rent_weekly',
     'pct_renting', 'crisis_score']
]
print(top_sydney_crisis.to_string(index=False))
print()

# =============================================================================
# STEP 5: SYDNEY AFFORDABILITY SWEET SPOTS
# =============================================================================
print("\nSTEP 5: Sydney Metro Affordability Sweet Spots...")
print("-" * 80)

sydney_sweet_sorted = sydney_sweet_metro.sort_values('affordability_score', ascending=False)

print(f"\nTop 30 Sydney Sweet Spots by Affordability Score:")
print()
top_sydney_sweet = sydney_sweet_sorted.head(30)[
    ['Suburb', 'Median_tot_hhd_inc_weekly', 'Median_rent_weekly',
     'Median_mortgage_repay_monthly', 'mortgage_stress_ratio',
     'rent_stress_ratio', 'affordability_score']
]
print(top_sydney_sweet.to_string(index=False))
print()

# =============================================================================
# STEP 6: SYDNEY DEMOGRAPHICS LOCKED OUT
# =============================================================================
print("\nSTEP 6: Sydney Demographics Most Locked Out...")
print("-" * 80)

# Young adults
sydney_young_lockout = sydney_data.nlargest(20, 'homeownership_lockout_score')[
    ['Suburb', 'pct_young_adults', 'pct_renting', 'rent_stress_ratio',
     'Median_rent_weekly', 'homeownership_lockout_score']
]
print("\nTop 20 Sydney Suburbs Locking Out Young Adults:")
print(sydney_young_lockout.to_string(index=False))
print()

# Families
sydney_family_lockout = sydney_data.nlargest(20, 'family_lockout_score')[
    ['Suburb', 'single_parent_families', 'pct_small_dwellings',
     'Average_num_psns_per_bedroom', 'rent_stress_ratio', 'family_lockout_score']
]
print("\nTop 20 Sydney Suburbs Locking Out Families:")
print(sydney_family_lockout.to_string(index=False))
print()

# =============================================================================
# STEP 7: SYDNEY STRESS DISTRIBUTION
# =============================================================================
print("\nSTEP 7: Sydney Housing Stress Distribution...")
print("-" * 80)

# Mortgage stress categories
mort_stress_bins = pd.cut(sydney_data['mortgage_stress_ratio'],
                          bins=[0, 30, 40, 50, 100],
                          labels=['Manageable (<30%)', 'Moderate (30-40%)',
                                 'Severe (40-50%)', 'Extreme (>50%)'])

print("\nSydney Mortgage Stress Distribution:")
print(mort_stress_bins.value_counts().sort_index())
print()

# Rent stress categories
rent_stress_bins = pd.cut(sydney_data['rent_stress_ratio'],
                          bins=[0, 30, 40, 50, 100],
                          labels=['Manageable (<30%)', 'Moderate (30-40%)',
                                 'Severe (40-50%)', 'Extreme (>50%)'])

print("Sydney Rent Stress Distribution:")
print(rent_stress_bins.value_counts().sort_index())
print()

# =============================================================================
# STEP 8: SYDNEY INCOME vs HOUSING COST ANALYSIS
# =============================================================================
print("\nSTEP 8: Sydney Income vs Housing Cost Analysis...")
print("-" * 80)

# Create income quartiles for Sydney
sydney_data['income_quartile'] = pd.qcut(sydney_data['Median_tot_hhd_inc_weekly'],
                                          q=4, labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])

# Average stress by income quartile
stress_by_income = sydney_data.groupby('income_quartile')[
    ['mortgage_stress_ratio', 'rent_stress_ratio', 'Median_tot_hhd_inc_weekly']
].mean()

print("\nStress Ratios by Income Quartile (Sydney):")
print(stress_by_income.round(1))
print()

# =============================================================================
# STEP 9: SYDNEY DWELLING TYPE ANALYSIS
# =============================================================================
print("\nSTEP 9: Sydney Dwelling Type Analysis...")
print("-" * 80)

# Categorize by apartment concentration
sydney_data['apartment_category'] = pd.cut(sydney_data['pct_apartments'],
                                           bins=[0, 10, 30, 50, 100],
                                           labels=['Low (<10%)', 'Medium (10-30%)',
                                                  'High (30-50%)', 'Very High (>50%)'])

dwelling_analysis = sydney_data.groupby('apartment_category')[
    ['mortgage_stress_ratio', 'rent_stress_ratio', 'Median_rent_weekly',
     'pct_renting', 'pct_owned_outright']
].mean()

print("\nHousing Metrics by Apartment Concentration (Sydney):")
print(dwelling_analysis.round(1))
print()

# =============================================================================
# STEP 10: SAVE SYDNEY-SPECIFIC RESULTS
# =============================================================================
print("\nSTEP 10: Saving Sydney-Specific Results...")
print("-" * 80)

# Save comprehensive Sydney data
sydney_data.to_csv('sydney_housing_comprehensive.csv', index=False)
print("✓ Saved: sydney_housing_comprehensive.csv")

# Save Sydney crisis areas
sydney_crisis_metro.to_csv('sydney_crisis_areas.csv', index=False)
print("✓ Saved: sydney_crisis_areas.csv")

# Save Sydney sweet spots
sydney_sweet_metro.to_csv('sydney_sweet_spots.csv', index=False)
print("✓ Saved: sydney_sweet_spots.csv")

# Save comparison
comparison_df.to_csv('sydney_vs_australia_comparison.csv', index=False)
print("✓ Saved: sydney_vs_australia_comparison.csv")

# Save lockout analyses
sydney_young_lockout.to_csv('sydney_young_adult_lockout.csv', index=False)
print("✓ Saved: sydney_young_adult_lockout.csv")

sydney_family_lockout.to_csv('sydney_family_lockout.csv', index=False)
print("✓ Saved: sydney_family_lockout.csv")

# =============================================================================
# STEP 11: CREATE SYDNEY VISUALIZATIONS
# =============================================================================
print("\nSTEP 11: Creating Sydney-Specific Visualizations...")
print("-" * 80)

import os
os.makedirs('sydney_analysis_plots', exist_ok=True)

# Visualization 1: Sydney vs Australia Comparison
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Sydney vs Australia - Housing Affordability Comparison',
             fontsize=16, fontweight='bold')

# Stress comparison
stress_comparison = {
    'Australia': [comprehensive['mortgage_stress_ratio'].mean(),
                  comprehensive['rent_stress_ratio'].mean()],
    'Sydney': [sydney_data['mortgage_stress_ratio'].mean(),
               sydney_data['rent_stress_ratio'].mean()]
}
x = np.arange(2)
width = 0.35
bars1 = axes[0, 0].bar(x - width/2, stress_comparison['Australia'], width,
                       label='Australia', color='lightblue', alpha=0.8)
bars2 = axes[0, 0].bar(x + width/2, stress_comparison['Sydney'], width,
                       label='Sydney', color='darkred', alpha=0.8)
axes[0, 0].axhline(y=30, color='red', linestyle='--', linewidth=2, label='30% Threshold')
axes[0, 0].set_ylabel('Stress Ratio (%)', fontsize=11)
axes[0, 0].set_title('Average Housing Stress: Sydney vs Australia', fontsize=12, fontweight='bold')
axes[0, 0].set_xticks(x)
axes[0, 0].set_xticklabels(['Mortgage Stress', 'Rent Stress'])
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3, axis='y')

# Income comparison
income_comparison = {
    'Median Income\n($/week)': [comprehensive['Median_tot_hhd_inc_weekly'].median(),
                                sydney_data['Median_tot_hhd_inc_weekly'].median()],
    'Median Rent\n($/week)': [comprehensive['Median_rent_weekly'].median(),
                              sydney_data['Median_rent_weekly'].median()],
    'Median Mortgage\n($/week)': [comprehensive['Median_mortgage_repay_monthly'].median() / 4.33,
                                  sydney_data['Median_mortgage_repay_monthly'].median() / 4.33]
}
x = np.arange(len(income_comparison))
bars1 = axes[0, 1].bar(x - width/2, [v[0] for v in income_comparison.values()],
                       width, label='Australia', color='lightblue', alpha=0.8)
bars2 = axes[0, 1].bar(x + width/2, [v[1] for v in income_comparison.values()],
                       width, label='Sydney', color='darkred', alpha=0.8)
axes[0, 1].set_ylabel('Weekly Amount ($)', fontsize=11)
axes[0, 1].set_title('Income and Housing Costs: Sydney vs Australia', fontsize=12, fontweight='bold')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(income_comparison.keys())
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Tenure comparison
tenure_comparison = {
    'Owned\nOutright': [comprehensive['pct_owned_outright'].mean(),
                        sydney_data['pct_owned_outright'].mean()],
    'Owned with\nMortgage': [comprehensive['pct_owned_mortgage'].mean(),
                             sydney_data['pct_owned_mortgage'].mean()],
    'Renting': [comprehensive['pct_renting'].mean(),
                sydney_data['pct_renting'].mean()]
}
x = np.arange(len(tenure_comparison))
bars1 = axes[1, 0].bar(x - width/2, [v[0] for v in tenure_comparison.values()],
                       width, label='Australia', color='lightblue', alpha=0.8)
bars2 = axes[1, 0].bar(x + width/2, [v[1] for v in tenure_comparison.values()],
                       width, label='Sydney', color='darkred', alpha=0.8)
axes[1, 0].set_ylabel('Percentage', fontsize=11)
axes[1, 0].set_title('Housing Tenure: Sydney vs Australia', fontsize=12, fontweight='bold')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(tenure_comparison.keys())
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Demographics comparison
demo_comparison = {
    'Young Adults\n(15-34)': [comprehensive['pct_young_adults'].mean(),
                              sydney_data['pct_young_adults'].mean()],
    'Low Income\nHouseholds': [comprehensive['pct_low_income'].mean(),
                               sydney_data['pct_low_income'].mean()],
    'Apartments': [comprehensive['pct_apartments'].mean(),
                   sydney_data['pct_apartments'].mean()]
}
x = np.arange(len(demo_comparison))
bars1 = axes[1, 1].bar(x - width/2, [v[0] for v in demo_comparison.values()],
                       width, label='Australia', color='lightblue', alpha=0.8)
bars2 = axes[1, 1].bar(x + width/2, [v[1] for v in demo_comparison.values()],
                       width, label='Sydney', color='darkred', alpha=0.8)
axes[1, 1].set_ylabel('Percentage', fontsize=11)
axes[1, 1].set_title('Demographics: Sydney vs Australia', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(demo_comparison.keys())
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('sydney_analysis_plots/sydney_vs_australia_comparison.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: sydney_vs_australia_comparison.png")

# Visualization 2: Sydney Crisis Areas
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Sydney Housing Crisis Areas - Detailed Analysis', fontsize=16, fontweight='bold')

# Top crisis areas
top_15_crisis = sydney_crisis_sorted.head(15)
y_pos = np.arange(len(top_15_crisis))
axes[0, 0].barh(y_pos, top_15_crisis['crisis_score'], color='darkred', alpha=0.7)
axes[0, 0].set_yticks(y_pos)
axes[0, 0].set_yticklabels(top_15_crisis['Suburb'].str[:40], fontsize=9)
axes[0, 0].set_xlabel('Crisis Score', fontsize=11)
axes[0, 0].set_title('Top 15 Sydney Crisis Areas', fontsize=12, fontweight='bold')
axes[0, 0].grid(True, alpha=0.3, axis='x')

# Crisis score distribution
axes[0, 1].hist(sydney_data['crisis_score'].dropna(), bins=40,
                color='darkred', edgecolor='black', alpha=0.7)
crisis_threshold = sydney_data['crisis_score'].quantile(0.90)
axes[0, 1].axvline(x=crisis_threshold, color='orange', linestyle='--',
                   linewidth=2, label=f'Top 10% ({crisis_threshold:.1f})')
axes[0, 1].set_xlabel('Crisis Score', fontsize=11)
axes[0, 1].set_ylabel('Number of Suburbs', fontsize=11)
axes[0, 1].set_title('Sydney Crisis Score Distribution', fontsize=12, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Stress by income quartile
stress_by_income_plot = sydney_data.groupby('income_quartile')[
    ['mortgage_stress_ratio', 'rent_stress_ratio']
].mean()
x = np.arange(len(stress_by_income_plot))
width = 0.35
bars1 = axes[1, 0].bar(x - width/2, stress_by_income_plot['mortgage_stress_ratio'],
                       width, label='Mortgage Stress', color='steelblue', alpha=0.7)
bars2 = axes[1, 0].bar(x + width/2, stress_by_income_plot['rent_stress_ratio'],
                       width, label='Rent Stress', color='coral', alpha=0.7)
axes[1, 0].axhline(y=30, color='red', linestyle='--', linewidth=2, label='30% Threshold')
axes[1, 0].set_ylabel('Stress Ratio (%)', fontsize=11)
axes[1, 0].set_title('Sydney: Stress by Income Quartile', fontsize=12, fontweight='bold')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(stress_by_income_plot.index, rotation=15)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Stress by apartment concentration
dwelling_stress = sydney_data.groupby('apartment_category')[
    ['mortgage_stress_ratio', 'rent_stress_ratio']
].mean()
x = np.arange(len(dwelling_stress))
bars1 = axes[1, 1].bar(x - width/2, dwelling_stress['mortgage_stress_ratio'],
                       width, label='Mortgage Stress', color='steelblue', alpha=0.7)
bars2 = axes[1, 1].bar(x + width/2, dwelling_stress['rent_stress_ratio'],
                       width, label='Rent Stress', color='coral', alpha=0.7)
axes[1, 1].axhline(y=30, color='red', linestyle='--', linewidth=2, label='30% Threshold')
axes[1, 1].set_ylabel('Stress Ratio (%)', fontsize=11)
axes[1, 1].set_title('Sydney: Stress by Apartment Concentration', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(dwelling_stress.index, rotation=15)
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('sydney_analysis_plots/sydney_crisis_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: sydney_crisis_analysis.png")

print()
print("=" * 80)
print("SYDNEY ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📊 Sydney Key Statistics:")
print(f"  Total Sydney suburbs analyzed: {len(sydney_data):,}")
print(f"  Crisis areas: {len(sydney_crisis_metro):,}")
print(f"  Sweet spots: {len(sydney_sweet_metro):,}")
print(f"  Average mortgage stress: {sydney_data['mortgage_stress_ratio'].mean():.1f}%")
print(f"  Average rent stress: {sydney_data['rent_stress_ratio'].mean():.1f}%")
print(f"  Median household income: ${sydney_data['Median_tot_hhd_inc_weekly'].median():.0f}/week")
print(f"  Median rent: ${sydney_data['Median_rent_weekly'].median():.0f}/week")
print()
