#!/usr/bin/env python3
"""
Enhance housing affordability results with suburb names and create visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

print("=" * 80)
print("ENHANCING RESULTS WITH SUBURB NAMES AND CREATING VISUALIZATIONS")
print("=" * 80)
print()

# =============================================================================
# STEP 1: EXTRACT SUBURB NAMES FROM METADATA
# =============================================================================
print("STEP 1: Extracting suburb names from metadata...")

try:
    # Try to read the Excel metadata file
    metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"

    # Read the SAL sheet
    sal_metadata = pd.read_excel(metadata_file, sheet_name='SAL')

    # Extract SAL code and name columns
    sal_mapping = sal_metadata[['SAL_CODE_2021', 'SAL_NAME_2021']].copy()
    sal_mapping = sal_mapping.drop_duplicates()

    print(f"✓ Extracted {len(sal_mapping):,} suburb names from metadata")

    # Save for future use
    sal_mapping.to_csv('SAL_Suburb_Name_Mapping.csv', index=False)
    print("✓ Saved suburb mapping to SAL_Suburb_Name_Mapping.csv")

except Exception as e:
    print(f"⚠ Could not read Excel metadata: {e}")
    print("  Will use SAL codes as suburb names")
    sal_mapping = None

# =============================================================================
# STEP 2: UPDATE RESULT FILES WITH SUBURB NAMES
# =============================================================================
print("\nSTEP 2: Updating result files with suburb names...")

if sal_mapping is not None:
    result_files = [
        'housing_affordability_comprehensive.csv',
        'housing_lockout_young_adults.csv',
        'housing_lockout_families.csv',
        'housing_crisis_areas.csv',
        'housing_affordability_sweet_spots.csv'
    ]

    for filename in result_files:
        try:
            df = pd.read_csv(filename)

            # Replace Suburb column with actual names
            df = df.drop('Suburb', axis=1, errors='ignore')
            df = df.merge(sal_mapping, on='SAL_CODE_2021', how='left')
            df = df.rename(columns={'SAL_NAME_2021': 'Suburb'})

            # Reorder columns to put Suburb first
            cols = ['SAL_CODE_2021', 'Suburb'] + [col for col in df.columns if col not in ['SAL_CODE_2021', 'Suburb']]
            df = df[cols]

            # Save updated file
            df.to_csv(filename, index=False)
            print(f"✓ Updated {filename}")
        except Exception as e:
            print(f"⚠ Could not update {filename}: {e}")

# =============================================================================
# STEP 3: LOAD DATA FOR VISUALIZATIONS
# =============================================================================
print("\nSTEP 3: Loading data for visualizations...")

comprehensive = pd.read_csv('housing_affordability_comprehensive.csv')
crisis_areas = pd.read_csv('housing_crisis_areas.csv')
sweet_spots = pd.read_csv('housing_affordability_sweet_spots.csv')
locked_young = pd.read_csv('housing_lockout_young_adults.csv')
locked_families = pd.read_csv('housing_lockout_families.csv')

print(f"✓ Data loaded successfully")

# =============================================================================
# STEP 4: CREATE VISUALIZATIONS
# =============================================================================
print("\nSTEP 4: Creating visualizations...")

# Create output directory for plots
import os
os.makedirs('housing_analysis_plots', exist_ok=True)

# ---------------------------------------------------------------------------
# Visualization 1: Housing Stress Distribution
# ---------------------------------------------------------------------------
print("  Creating housing stress distribution plots...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Housing Affordability Stress Analysis - Australia 2021', fontsize=16, fontweight='bold')

# Mortgage stress distribution
axes[0, 0].hist(comprehensive['mortgage_stress_ratio'].dropna(), bins=50,
                color='steelblue', edgecolor='black', alpha=0.7)
axes[0, 0].axvline(x=30, color='red', linestyle='--', linewidth=2, label='30% Threshold')
axes[0, 0].axvline(x=comprehensive['mortgage_stress_ratio'].median(),
                   color='green', linestyle='--', linewidth=2, label='Median')
axes[0, 0].set_xlabel('Mortgage Stress Ratio (%)', fontsize=11)
axes[0, 0].set_ylabel('Number of Suburbs', fontsize=11)
axes[0, 0].set_title('Mortgage Stress Distribution', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Rent stress distribution
axes[0, 1].hist(comprehensive['rent_stress_ratio'].dropna(), bins=50,
                color='coral', edgecolor='black', alpha=0.7)
axes[0, 1].axvline(x=30, color='red', linestyle='--', linewidth=2, label='30% Threshold')
axes[0, 1].axvline(x=comprehensive['rent_stress_ratio'].median(),
                   color='green', linestyle='--', linewidth=2, label='Median')
axes[0, 1].set_xlabel('Rent Stress Ratio (%)', fontsize=11)
axes[0, 1].set_ylabel('Number of Suburbs', fontsize=11)
axes[0, 1].set_title('Rent Stress Distribution', fontsize=12, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Tenure type distribution
tenure_data = {
    'Owned Outright': comprehensive['pct_owned_outright'].mean(),
    'Owned with\nMortgage': comprehensive['pct_owned_mortgage'].mean(),
    'Renting\n(Private)': (comprehensive['pct_renting'] - comprehensive['pct_renting_social']).mean(),
    'Social\nHousing': comprehensive['pct_renting_social'].mean()
}
colors_pie = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
axes[1, 0].pie(tenure_data.values(), labels=tenure_data.keys(), autopct='%1.1f%%',
               startangle=90, colors=colors_pie)
axes[1, 0].set_title('Average Housing Tenure Distribution', fontsize=12, fontweight='bold')

# Income vs stress scatter
sample_data = comprehensive.sample(min(1000, len(comprehensive)))
scatter = axes[1, 1].scatter(sample_data['Median_tot_hhd_inc_weekly'],
                             sample_data['rent_stress_ratio'],
                             c=sample_data['pct_young_adults'],
                             cmap='viridis', alpha=0.6, s=30)
axes[1, 1].axhline(y=30, color='red', linestyle='--', linewidth=2, label='30% Stress Threshold')
axes[1, 1].set_xlabel('Median Household Income ($/week)', fontsize=11)
axes[1, 1].set_ylabel('Rent Stress Ratio (%)', fontsize=11)
axes[1, 1].set_title('Income vs Rent Stress (colored by % Young Adults)', fontsize=12, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
plt.colorbar(scatter, ax=axes[1, 1], label='% Young Adults')

plt.tight_layout()
plt.savefig('housing_analysis_plots/01_housing_stress_overview.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: 01_housing_stress_overview.png")

# ---------------------------------------------------------------------------
# Visualization 2: Crisis Areas Analysis
# ---------------------------------------------------------------------------
print("  Creating crisis areas analysis plots...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Housing Crisis Areas - Detailed Analysis', fontsize=16, fontweight='bold')

# Crisis score distribution
axes[0, 0].hist(comprehensive['crisis_score'].dropna(), bins=50,
                color='darkred', edgecolor='black', alpha=0.7)
crisis_threshold = comprehensive['crisis_score'].quantile(0.90)
axes[0, 0].axvline(x=crisis_threshold, color='orange', linestyle='--',
                   linewidth=2, label=f'Top 10% Threshold ({crisis_threshold:.1f})')
axes[0, 0].set_xlabel('Crisis Score', fontsize=11)
axes[0, 0].set_ylabel('Number of Suburbs', fontsize=11)
axes[0, 0].set_title('Crisis Score Distribution', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Top 15 crisis areas
top_crisis = crisis_areas.nlargest(15, 'crisis_score')
y_pos = np.arange(len(top_crisis))
axes[0, 1].barh(y_pos, top_crisis['crisis_score'], color='darkred', alpha=0.7)
axes[0, 1].set_yticks(y_pos)
axes[0, 1].set_yticklabels(top_crisis['Suburb'].str[:30], fontsize=9)
axes[0, 1].set_xlabel('Crisis Score', fontsize=11)
axes[0, 1].set_title('Top 15 Crisis Areas by Score', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='x')

# Crisis factors breakdown
crisis_factors = {
    'Mortgage\nStress': crisis_areas['mortgage_stress_ratio'].mean(),
    'Rent\nStress': crisis_areas['rent_stress_ratio'].mean(),
    'High %\nRenting': crisis_areas['pct_renting'].mean(),
    'Low Income\nHouseholds': crisis_areas['pct_low_income'].mean(),
    'Overcrowding': crisis_areas['Average_num_psns_per_bedroom'].mean() * 50
}
bars = axes[1, 0].bar(crisis_factors.keys(), crisis_factors.values(),
                      color=['#d62828', '#f77f00', '#fcbf49', '#eae2b7', '#003049'], alpha=0.8)
axes[1, 0].set_ylabel('Score/Percentage', fontsize=11)
axes[1, 0].set_title('Average Crisis Indicators in High-Risk Areas', fontsize=12, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3, axis='y')
for bar in bars:
    height = bar.get_height()
    axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Income distribution in crisis vs non-crisis
crisis_income = crisis_areas['Median_tot_hhd_inc_weekly'].dropna()
non_crisis = comprehensive[~comprehensive['SAL_CODE_2021'].isin(crisis_areas['SAL_CODE_2021'])]
non_crisis_income = non_crisis['Median_tot_hhd_inc_weekly'].dropna()

axes[1, 1].hist([non_crisis_income, crisis_income], bins=30,
                label=['Non-Crisis Areas', 'Crisis Areas'],
                color=['lightblue', 'darkred'], alpha=0.7, edgecolor='black')
axes[1, 1].set_xlabel('Median Household Income ($/week)', fontsize=11)
axes[1, 1].set_ylabel('Number of Suburbs', fontsize=11)
axes[1, 1].set_title('Income Distribution: Crisis vs Non-Crisis Areas', fontsize=12, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('housing_analysis_plots/02_crisis_areas_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: 02_crisis_areas_analysis.png")

# ---------------------------------------------------------------------------
# Visualization 3: Locked Out Demographics
# ---------------------------------------------------------------------------
print("  Creating locked-out demographics plots...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Demographics Locked Out of Housing', fontsize=16, fontweight='bold')

# Young adults lockout score distribution
axes[0, 0].hist(comprehensive['homeownership_lockout_score'].dropna(), bins=50,
                color='purple', edgecolor='black', alpha=0.7)
axes[0, 0].axvline(x=comprehensive['homeownership_lockout_score'].quantile(0.90),
                   color='red', linestyle='--', linewidth=2, label='Top 10%')
axes[0, 0].set_xlabel('Homeownership Lockout Score', fontsize=11)
axes[0, 0].set_ylabel('Number of Suburbs', fontsize=11)
axes[0, 0].set_title('Young Adult Homeownership Lockout Distribution', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Top 15 areas locking out young adults
top_young_lockout = locked_young.nlargest(15, 'homeownership_lockout_score')
y_pos = np.arange(len(top_young_lockout))
axes[0, 1].barh(y_pos, top_young_lockout['homeownership_lockout_score'], color='purple', alpha=0.7)
axes[0, 1].set_yticks(y_pos)
axes[0, 1].set_yticklabels(top_young_lockout['Suburb'].str[:30], fontsize=9)
axes[0, 1].set_xlabel('Lockout Score', fontsize=11)
axes[0, 1].set_title('Top 15 Areas Locking Out Young Adults', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='x')

# Family lockout score distribution
axes[1, 0].hist(comprehensive['family_lockout_score'].dropna(), bins=50,
                color='darkorange', edgecolor='black', alpha=0.7)
axes[1, 0].axvline(x=comprehensive['family_lockout_score'].quantile(0.90),
                   color='red', linestyle='--', linewidth=2, label='Top 10%')
axes[1, 0].set_xlabel('Family Lockout Score', fontsize=11)
axes[1, 0].set_ylabel('Number of Suburbs', fontsize=11)
axes[1, 0].set_title('Family Housing Lockout Distribution', fontsize=12, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Top 15 areas locking out families
top_family_lockout = locked_families.nlargest(15, 'family_lockout_score')
y_pos = np.arange(len(top_family_lockout))
axes[1, 1].barh(y_pos, top_family_lockout['family_lockout_score'], color='darkorange', alpha=0.7)
axes[1, 1].set_yticks(y_pos)
axes[1, 1].set_yticklabels(top_family_lockout['Suburb'].str[:30], fontsize=9)
axes[1, 1].set_xlabel('Lockout Score', fontsize=11)
axes[1, 1].set_title('Top 15 Areas Locking Out Families', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('housing_analysis_plots/03_locked_out_demographics.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: 03_locked_out_demographics.png")

# ---------------------------------------------------------------------------
# Visualization 4: Affordability Sweet Spots
# ---------------------------------------------------------------------------
print("  Creating affordability sweet spots plots...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Housing Affordability Sweet Spots Analysis', fontsize=16, fontweight='bold')

# Affordability score distribution
axes[0, 0].hist(sweet_spots['affordability_score'].dropna(), bins=50,
                color='green', edgecolor='black', alpha=0.7)
axes[0, 0].axvline(x=sweet_spots['affordability_score'].median(),
                   color='blue', linestyle='--', linewidth=2, label='Median')
axes[0, 0].set_xlabel('Affordability Score', fontsize=11)
axes[0, 0].set_ylabel('Number of Suburbs', fontsize=11)
axes[0, 0].set_title('Affordability Score Distribution (Sweet Spots)', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Top 15 sweet spots
top_sweet = sweet_spots.nlargest(15, 'affordability_score')
y_pos = np.arange(len(top_sweet))
axes[0, 1].barh(y_pos, top_sweet['affordability_score'], color='green', alpha=0.7)
axes[0, 1].set_yticks(y_pos)
axes[0, 1].set_yticklabels(top_sweet['Suburb'].str[:30], fontsize=9)
axes[0, 1].set_xlabel('Affordability Score', fontsize=11)
axes[0, 1].set_title('Top 15 Affordability Sweet Spots', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='x')

# Sweet spot characteristics
sweet_characteristics = {
    'Avg Mortgage\nStress (%)': sweet_spots['mortgage_stress_ratio'].mean(),
    'Avg Rent\nStress (%)': sweet_spots['rent_stress_ratio'].mean(),
    'Avg % Houses': sweet_spots['pct_houses'].mean(),
    'Avg Median\nIncome ($100s)': sweet_spots['Median_tot_hhd_inc_weekly'].mean() / 100
}
bars = axes[1, 0].bar(sweet_characteristics.keys(), sweet_characteristics.values(),
                      color=['#06d6a0', '#118ab2', '#073b4c', '#ef476f'], alpha=0.8)
axes[1, 0].set_ylabel('Value', fontsize=11)
axes[1, 0].set_title('Average Characteristics of Sweet Spots', fontsize=12, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3, axis='y')
for bar in bars:
    height = bar.get_height()
    axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Price comparison: Sweet spots vs Crisis areas
comparison_data = {
    'Median\nRent': [sweet_spots['Median_rent_weekly'].median(),
                     crisis_areas['Median_rent_weekly'].median()],
    'Median\nMortgage': [sweet_spots['Median_mortgage_repay_monthly'].median() / 4.33,
                         crisis_areas['Median_mortgage_repay_monthly'].median() / 4.33],
    'Median\nIncome': [sweet_spots['Median_tot_hhd_inc_weekly'].median(),
                       crisis_areas['Median_tot_hhd_inc_weekly'].median()]
}

x = np.arange(len(comparison_data))
width = 0.35

bars1 = axes[1, 1].bar(x - width/2, [v[0] for v in comparison_data.values()],
                       width, label='Sweet Spots', color='green', alpha=0.7)
bars2 = axes[1, 1].bar(x + width/2, [v[1] for v in comparison_data.values()],
                       width, label='Crisis Areas', color='darkred', alpha=0.7)

axes[1, 1].set_ylabel('Weekly Amount ($)', fontsize=11)
axes[1, 1].set_title('Cost Comparison: Sweet Spots vs Crisis Areas', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(comparison_data.keys())
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('housing_analysis_plots/04_affordability_sweet_spots.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: 04_affordability_sweet_spots.png")

# ---------------------------------------------------------------------------
# Visualization 5: Dwelling Types and Stress
# ---------------------------------------------------------------------------
print("  Creating dwelling types analysis plots...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Dwelling Types and Housing Stress Patterns', fontsize=16, fontweight='bold')

# Dwelling type vs rent stress
sample_data = comprehensive.sample(min(1000, len(comprehensive)))
scatter1 = axes[0, 0].scatter(sample_data['pct_apartments'],
                              sample_data['rent_stress_ratio'],
                              c=sample_data['Median_rent_weekly'],
                              cmap='Reds', alpha=0.6, s=40)
axes[0, 0].axhline(y=30, color='blue', linestyle='--', linewidth=2, label='30% Threshold')
axes[0, 0].set_xlabel('% Apartments', fontsize=11)
axes[0, 0].set_ylabel('Rent Stress Ratio (%)', fontsize=11)
axes[0, 0].set_title('Apartment Concentration vs Rent Stress', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
plt.colorbar(scatter1, ax=axes[0, 0], label='Median Rent ($/week)')

# Small dwellings vs overcrowding
scatter2 = axes[0, 1].scatter(sample_data['pct_small_dwellings'],
                              sample_data['Average_num_psns_per_bedroom'],
                              c=sample_data['pct_low_income'],
                              cmap='YlOrRd', alpha=0.6, s=40)
axes[0, 1].set_xlabel('% Small Dwellings (0-1 bedroom)', fontsize=11)
axes[0, 1].set_ylabel('Avg Persons per Bedroom', fontsize=11)
axes[0, 1].set_title('Small Dwellings vs Overcrowding', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)
plt.colorbar(scatter2, ax=axes[0, 1], label='% Low Income')

# Stress by dwelling type (binned)
bins_apartments = [0, 10, 30, 50, 100]
comprehensive['apartment_bin'] = pd.cut(comprehensive['pct_apartments'], bins=bins_apartments,
                                         labels=['<10%', '10-30%', '30-50%', '>50%'])
stress_by_dwelling = comprehensive.groupby('apartment_bin')[['mortgage_stress_ratio', 'rent_stress_ratio']].mean()

x = np.arange(len(stress_by_dwelling))
width = 0.35
bars1 = axes[1, 0].bar(x - width/2, stress_by_dwelling['mortgage_stress_ratio'],
                       width, label='Mortgage Stress', color='steelblue', alpha=0.7)
bars2 = axes[1, 0].bar(x + width/2, stress_by_dwelling['rent_stress_ratio'],
                       width, label='Rent Stress', color='coral', alpha=0.7)
axes[1, 0].axhline(y=30, color='red', linestyle='--', linewidth=2, label='30% Threshold')
axes[1, 0].set_ylabel('Average Stress Ratio (%)', fontsize=11)
axes[1, 0].set_title('Housing Stress by Apartment Concentration', fontsize=12, fontweight='bold')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(stress_by_dwelling.index)
axes[1, 0].set_xlabel('% Apartments in Area', fontsize=11)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Tenure distribution in high vs low apartment areas
high_apartment = comprehensive[comprehensive['pct_apartments'] > 30]
low_apartment = comprehensive[comprehensive['pct_apartments'] <= 10]

tenure_comparison = {
    'Owned\nOutright': [low_apartment['pct_owned_outright'].mean(),
                        high_apartment['pct_owned_outright'].mean()],
    'Owned with\nMortgage': [low_apartment['pct_owned_mortgage'].mean(),
                             high_apartment['pct_owned_mortgage'].mean()],
    'Renting': [low_apartment['pct_renting'].mean(),
                high_apartment['pct_renting'].mean()]
}

x = np.arange(len(tenure_comparison))
width = 0.35
bars1 = axes[1, 1].bar(x - width/2, [v[0] for v in tenure_comparison.values()],
                       width, label='Low Apartments (<10%)', color='lightblue', alpha=0.7)
bars2 = axes[1, 1].bar(x + width/2, [v[1] for v in tenure_comparison.values()],
                       width, label='High Apartments (>30%)', color='navy', alpha=0.7)
axes[1, 1].set_ylabel('Average Percentage', fontsize=11)
axes[1, 1].set_title('Tenure Type by Apartment Concentration', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(tenure_comparison.keys())
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('housing_analysis_plots/05_dwelling_types_stress.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: 05_dwelling_types_stress.png")

print("\n" + "=" * 80)
print("VISUALIZATION COMPLETE!")
print("=" * 80)
print(f"\nCreated 5 comprehensive visualization plots in 'housing_analysis_plots/' directory:")
print("  1. 01_housing_stress_overview.png")
print("  2. 02_crisis_areas_analysis.png")
print("  3. 03_locked_out_demographics.png")
print("  4. 04_affordability_sweet_spots.png")
print("  5. 05_dwelling_types_stress.png")
print()
