#!/usr/bin/env python3
"""
Generate Comprehensive Visualizations for Rental Stress Analysis
==================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = Path("rental_stress_outputs/rental_stress_analysis_full.csv")
PREDICTIONS_FILE = Path("rental_stress_outputs/spatial_models/spatial_predictions_all_sa1.csv")
OUTPUT_DIR = Path("rental_stress_outputs/visualizations")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

print("=" * 80)
print("GENERATING RENTAL STRESS VISUALIZATIONS")
print("=" * 80)
print()

# Load data
print("Loading data...")
df = pd.read_csv(INPUT_FILE)
df_pred = pd.read_csv(PREDICTIONS_FILE)
print(f"✓ Loaded {len(df):,} SA1 areas")
print()

# ============================================================================
# VISUALIZATION 1: Rental Stress Distribution
# ============================================================================
print("Creating visualization 1: Rental Stress Distribution...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Rent-to-Income Ratio Distribution
ax1 = axes[0, 0]
rent_ratios = df['rent_to_income_ratio'].replace([np.inf, -np.inf], np.nan).dropna()
rent_ratios_clean = rent_ratios[rent_ratios < 2]  # Remove extreme outliers
ax1.hist(rent_ratios_clean, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
ax1.axvline(0.30, color='orange', linestyle='--', linewidth=2, label='Stress Threshold (30%)')
ax1.axvline(0.50, color='red', linestyle='--', linewidth=2, label='Severe Stress (50%)')
ax1.set_xlabel('Rent-to-Income Ratio')
ax1.set_ylabel('Number of SA1 Areas')
ax1.set_title('Distribution of Rent-to-Income Ratios Across SA1 Areas')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Stress Category Distribution
ax2 = axes[0, 1]
stress_counts = df['stress_category'].value_counts()
colors = {'No Data': 'gray', 'Affordable (<30%)': 'green', 'Moderate Stress (30-50%)': 'orange', 'Severe Stress (50%+)': 'red'}
bars = ax2.bar(range(len(stress_counts)), stress_counts.values, color=[colors.get(x, 'blue') for x in stress_counts.index])
ax2.set_xticks(range(len(stress_counts)))
ax2.set_xticklabels(stress_counts.index, rotation=45, ha='right')
ax2.set_ylabel('Number of SA1 Areas')
ax2.set_title('Rental Stress Categories Distribution')
ax2.grid(True, axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, stress_counts.values)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
             f'{value:,}', ha='center', va='bottom', fontsize=9)

# Plot 3: Rental Stress Score Distribution
ax3 = axes[1, 0]
stress_scores = df['rental_stress_score'].replace([np.inf, -np.inf], np.nan).dropna()
ax3.hist(stress_scores, bins=50, color='coral', edgecolor='black', alpha=0.7)
ax3.axvline(stress_scores.mean(), color='darkred', linestyle='--', linewidth=2, label=f'Mean = {stress_scores.mean():.1f}')
ax3.axvline(stress_scores.median(), color='darkblue', linestyle='--', linewidth=2, label=f'Median = {stress_scores.median():.1f}')
ax3.set_xlabel('Rental Stress Score (0-100)')
ax3.set_ylabel('Number of SA1 Areas')
ax3.set_title('Distribution of Rental Stress Scores')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Low-Income Household Percentage
ax4 = axes[1, 1]
low_income_pct = df['low_income_pct'].replace([np.inf, -np.inf], np.nan).dropna()
low_income_pct_clean = low_income_pct[low_income_pct <= 100]
ax4.hist(low_income_pct_clean, bins=50, color='darkgreen', edgecolor='black', alpha=0.7)
ax4.axvline(50, color='red', linestyle='--', linewidth=2, label='High Concentration (50%)')
ax4.set_xlabel('Low-Income Household Percentage (%)')
ax4.set_ylabel('Number of SA1 Areas')
ax4.set_title('Distribution of Low-Income Household Concentrations')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'rental_stress_distributions.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'rental_stress_distributions.png'}")
plt.close()

# ============================================================================
# VISUALIZATION 2: Public Housing Analysis
# ============================================================================
print("Creating visualization 2: Public Housing Supply-Demand Analysis...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Public Housing Supply
ax1 = axes[0, 0]
public_housing = df['public_housing_dwellings'].replace([np.inf, -np.inf], np.nan).dropna()
public_housing_nonzero = public_housing[public_housing > 0]
ax1.hist(public_housing_nonzero, bins=50, color='navy', edgecolor='black', alpha=0.7)
ax1.set_xlabel('Public Housing Dwellings per SA1')
ax1.set_ylabel('Number of SA1 Areas')
ax1.set_title(f'Distribution of Public Housing Supply\n({len(public_housing_nonzero):,} SA1s with public housing)')
ax1.grid(True, alpha=0.3)

# Plot 2: Public Housing Rate
ax2 = axes[0, 1]
public_rate = df['public_housing_rate'].replace([np.inf, -np.inf], np.nan).dropna()
public_rate_clean = public_rate[public_rate <= 100]
ax2.hist(public_rate_clean, bins=50, color='darkblue', edgecolor='black', alpha=0.7)
ax2.axvline(public_rate_clean.mean(), color='red', linestyle='--', linewidth=2,
            label=f'Mean = {public_rate_clean.mean():.2f}%')
ax2.set_xlabel('Public Housing as % of Total Dwellings')
ax2.set_ylabel('Number of SA1 Areas')
ax2.set_title('Public Housing Rate Distribution')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Supply-Demand Gap
ax3 = axes[1, 0]
gap = df['public_housing_gap'].replace([np.inf, -np.inf], np.nan).dropna()
gap_range = gap[(gap >= -50) & (gap <= 200)]
ax3.hist(gap_range, bins=50, color='crimson', edgecolor='black', alpha=0.7)
ax3.axvline(0, color='green', linestyle='-', linewidth=2, label='Supply = Demand')
ax3.axvline(10, color='orange', linestyle='--', linewidth=2, label='Critical Gap (>10)')
ax3.set_xlabel('Supply-Demand Gap (Dwellings)')
ax3.set_ylabel('Number of SA1 Areas')
ax3.set_title('Public Housing Supply-Demand Gap Distribution')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Critical Gap Areas by State (if we had state data)
ax4 = axes[1, 1]
critical_gaps = df[df['critical_housing_gap'] == 1]
gap_summary = pd.DataFrame({
    'Metric': ['Total Public Housing', 'Estimated Demand', 'Supply Gap', 'Critical Gap Areas'],
    'Value': [
        df['public_housing_dwellings'].sum(),
        df['estimated_demand'].sum(),
        df['public_housing_gap'].sum(),
        len(critical_gaps)
    ]
})
bars = ax4.barh(gap_summary['Metric'], gap_summary['Value'], color=['navy', 'orange', 'red', 'darkred'])
ax4.set_xlabel('Count / Number of Dwellings')
ax4.set_title('Public Housing Summary Statistics')
ax4.grid(True, axis='x', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, gap_summary['Value'])):
    ax4.text(value + max(gap_summary['Value']) * 0.02, bar.get_y() + bar.get_height()/2,
             f'{value:,.0f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'public_housing_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'public_housing_analysis.png'}")
plt.close()

# ============================================================================
# VISUALIZATION 3: Risk Scores Comparison
# ============================================================================
print("Creating visualization 3: Risk Scores Comparison...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Rental Stress vs Displacement Risk
ax1 = axes[0, 0]
sample = df.sample(min(5000, len(df)))  # Sample for visualization
scatter = ax1.scatter(sample['rental_stress_score'], sample['displacement_risk_score'],
                     c=sample['investment_priority_score'], cmap='RdYlGn_r',
                     alpha=0.5, s=10)
ax1.set_xlabel('Rental Stress Score')
ax1.set_ylabel('Displacement Risk Score')
ax1.set_title('Rental Stress vs Displacement Risk\n(colored by Investment Priority)')
plt.colorbar(scatter, ax=ax1, label='Investment Priority Score')
ax1.grid(True, alpha=0.3)

# Plot 2: Investment Priority Distribution
ax2 = axes[0, 1]
investment_counts = df['investment_priority'].value_counts().sort_index()
colors_inv = {'No Priority': 'gray', 'Low Priority': 'lightblue', 'Moderate Priority': 'orange',
              'High Priority': 'darkorange', 'Critical Priority': 'red'}
bars = ax2.bar(range(len(investment_counts)), investment_counts.values,
              color=[colors_inv.get(x, 'blue') for x in investment_counts.index])
ax2.set_xticks(range(len(investment_counts)))
ax2.set_xticklabels(investment_counts.index, rotation=45, ha='right')
ax2.set_ylabel('Number of SA1 Areas')
ax2.set_title('Investment Priority Distribution')
ax2.grid(True, axis='y', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, investment_counts.values)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
             f'{value:,}', ha='center', va='bottom', fontsize=9)

# Plot 3: Income vs Rent Relationship
ax3 = axes[1, 0]
sample = df.sample(min(5000, len(df)))
sample_clean = sample[(sample['Median_rent_weekly'] > 0) &
                     (sample['Median_tot_hhd_inc_weekly'] > 0) &
                     (sample['Median_rent_weekly'] < 1000)]
scatter = ax3.scatter(sample_clean['Median_tot_hhd_inc_weekly'],
                     sample_clean['Median_rent_weekly'],
                     c=sample_clean['rental_stress_score'],
                     cmap='RdYlGn_r', alpha=0.6, s=20)
ax3.set_xlabel('Median Weekly Household Income ($)')
ax3.set_ylabel('Median Weekly Rent ($)')
ax3.set_title('Household Income vs Rent\n(colored by Rental Stress Score)')
plt.colorbar(scatter, ax=ax3, label='Rental Stress Score')
ax3.grid(True, alpha=0.3)

# Plot 4: Unemployment vs Rental Stress
ax4 = axes[1, 1]
unemployment_bins = pd.cut(df['unemployment_rate'], bins=[0, 3, 5, 7, 10, 100])
stress_by_unemployment = df.groupby(unemployment_bins)['rental_stress_score'].mean()
bars = ax4.bar(range(len(stress_by_unemployment)), stress_by_unemployment.values,
              color='steelblue', edgecolor='black')
ax4.set_xticks(range(len(stress_by_unemployment)))
ax4.set_xticklabels(['0-3%', '3-5%', '5-7%', '7-10%', '10%+'], rotation=45, ha='right')
ax4.set_xlabel('Unemployment Rate')
ax4.set_ylabel('Average Rental Stress Score')
ax4.set_title('Rental Stress by Unemployment Rate')
ax4.grid(True, axis='y', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, stress_by_unemployment.values)):
    if not np.isnan(value):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'risk_scores_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'risk_scores_analysis.png'}")
plt.close()

# ============================================================================
# VISUALIZATION 4: Model Performance
# ============================================================================
print("Creating visualization 4: Spatial Model Performance...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot model performance metrics
model_names = ['Linear\nRegression', 'Ridge\nRegression', 'Lasso\nRegression', 'Random\nForest', 'Gradient\nBoosting']
r2_scores = [0.8867, 0.8867, 0.8380, 0.8997, 0.9036]
rmse_scores = [0.3823, 0.3823, 0.4572, 0.3597, 0.3527]

# Plot 1: R² Scores
ax1 = axes[0, 0]
bars = ax1.bar(model_names, r2_scores, color=['lightblue', 'lightblue', 'lightcoral', 'lightgreen', 'darkgreen'])
ax1.set_ylabel('R² Score')
ax1.set_title('Model Performance: R² Scores (Rental Stress Prediction)')
ax1.set_ylim([0.8, 0.92])
ax1.grid(True, axis='y', alpha=0.3)
for i, (bar, value) in enumerate(zip(bars, r2_scores)):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
             f'{value:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 2: RMSE Scores
ax2 = axes[0, 1]
bars = ax2.bar(model_names, rmse_scores, color=['lightblue', 'lightblue', 'lightcoral', 'lightgreen', 'darkgreen'])
ax2.set_ylabel('RMSE')
ax2.set_title('Model Performance: RMSE (Rental Stress Prediction)')
ax2.grid(True, axis='y', alpha=0.3)
for i, (bar, value) in enumerate(zip(bars, rmse_scores)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{value:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 3: Feature Importance (top 10)
ax3 = axes[1, 0]
feature_names = ['Public Housing\nRate', 'Unemployment\nRate', 'Low Income\nHouseholds',
                'Median HH\nIncome', 'Labour Force\nParticipation', 'Public Housing\nDwellings',
                'Median Personal\nIncome', 'Total\nHouseholds', 'Low Income\n%', 'Median\nAge']
importance = [0.662099, 0.148300, 0.060646, 0.026647, 0.021728, 0.019217, 0.015814, 0.009512, 0.008869, 0.007798]
bars = ax3.barh(feature_names, importance, color='steelblue')
ax3.set_xlabel('Importance Score')
ax3.set_title('Top 10 Most Important Features (Random Forest)')
ax3.grid(True, axis='x', alpha=0.3)
for i, (bar, value) in enumerate(zip(bars, importance)):
    ax3.text(value + 0.01, bar.get_y() + bar.get_height()/2,
             f'{value:.3f}', va='center', fontsize=8)

# Plot 4: Prediction Accuracy Summary
ax4 = axes[1, 1]
metrics = ['Rental Stress\nPrediction', 'Displacement Risk\nPrediction', 'Investment Priority\nPrediction']
r2_values = [0.9036, 0.9992, 0.7306]
colors_metrics = ['darkgreen', 'navy', 'darkorange']
bars = ax4.bar(metrics, r2_values, color=colors_metrics)
ax4.set_ylabel('R² Score')
ax4.set_title('Model Accuracy Summary (Best Models)')
ax4.set_ylim([0, 1.1])
ax4.grid(True, axis='y', alpha=0.3)
for i, (bar, value) in enumerate(zip(bars, r2_values)):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f'{value:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'model_performance.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'model_performance.png'}")
plt.close()

print()
print("=" * 80)
print("VISUALIZATIONS COMPLETE!")
print("=" * 80)
print()
print(f"All visualizations saved to: {OUTPUT_DIR}/")
print()
print("Generated files:")
print("1. rental_stress_distributions.png")
print("2. public_housing_analysis.png")
print("3. risk_scores_analysis.png")
print("4. model_performance.png")
print()
