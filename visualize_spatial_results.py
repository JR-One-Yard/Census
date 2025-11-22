#!/usr/bin/env python3
"""
Visualization Script for Spatial Econometric Analysis Results
Creates maps, charts, and summary reports from analysis output
"""

import os
import pickle
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (15, 10)

RESULTS_DIR = "/home/user/Census/spatial_analysis_results"
VIZ_DIR = "/home/user/Census/spatial_visualizations"

os.makedirs(VIZ_DIR, exist_ok=True)

print("="*120)
print("SPATIAL ANALYSIS VISUALIZATION")
print("="*120)

def visualize_morans_i(geo_level):
    """Create visualizations for Moran's I results"""
    print(f"\nVisualizing Moran's I results for {geo_level}...")

    morans_file = os.path.join(RESULTS_DIR, geo_level, f'{geo_level}_morans_i.csv')

    if not os.path.exists(morans_file):
        print(f"  ✗ File not found: {morans_file}")
        return

    df = pd.read_csv(morans_file)

    # Create output directory
    output_dir = os.path.join(VIZ_DIR, geo_level, 'morans_i')
    os.makedirs(output_dir, exist_ok=True)

    # 1. Distribution of Moran's I values
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Histogram
    axes[0, 0].hist(df['I'], bins=50, edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(df['I'].mean(), color='red', linestyle='--', label=f'Mean: {df["I"].mean():.3f}')
    axes[0, 0].set_xlabel("Moran's I")
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title(f'Distribution of Moran\'s I ({geo_level})')
    axes[0, 0].legend()

    # Scatter: I vs p-value
    significant = df[df['significant'] == True]
    not_significant = df[df['significant'] == False]

    axes[0, 1].scatter(not_significant['I'], not_significant['p_value'],
                      alpha=0.3, label='Not Significant', s=10)
    axes[0, 1].scatter(significant['I'], significant['p_value'],
                      alpha=0.7, label='Significant (p<0.05)', s=10, color='red')
    axes[0, 1].axhline(0.05, color='black', linestyle='--', label='p=0.05')
    axes[0, 1].set_xlabel("Moran's I")
    axes[0, 1].set_ylabel('P-value')
    axes[0, 1].set_title('Moran\'s I vs P-value')
    axes[0, 1].legend()

    # Top positive spatial autocorrelation
    top_positive = df.nlargest(20, 'I')
    axes[1, 0].barh(range(20), top_positive['I'].values)
    axes[1, 0].set_yticks(range(20))
    axes[1, 0].set_yticklabels([v[:30] for v in top_positive['variable'].values], fontsize=8)
    axes[1, 0].set_xlabel("Moran's I")
    axes[1, 0].set_title('Top 20 Variables with Strongest Positive Clustering')
    axes[1, 0].invert_yaxis()

    # Top negative spatial autocorrelation
    top_negative = df.nsmallest(20, 'I')
    axes[1, 1].barh(range(20), top_negative['I'].values)
    axes[1, 1].set_yticks(range(20))
    axes[1, 1].set_yticklabels([v[:30] for v in top_negative['variable'].values], fontsize=8)
    axes[1, 1].set_xlabel("Moran's I")
    axes[1, 1].set_title('Top 20 Variables with Strongest Negative Dispersion')
    axes[1, 1].invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'morans_i_overview.png'), dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: morans_i_overview.png")

    # 2. Summary statistics by weights method
    fig, ax = plt.subplots(figsize=(12, 6))

    weights_methods = df['weights_method'].unique()
    mean_I = df.groupby('weights_method')['I'].mean()
    sig_pct = df.groupby('weights_method')['significant'].apply(lambda x: (x == True).sum() / len(x) * 100)

    x = np.arange(len(weights_methods))
    width = 0.35

    ax.bar(x - width/2, mean_I.values, width, label='Mean Moran\'s I', alpha=0.8)
    ax2 = ax.twinx()
    ax2.bar(x + width/2, sig_pct.values, width, label='% Significant', alpha=0.8, color='orange')

    ax.set_xlabel('Spatial Weights Method')
    ax.set_ylabel('Mean Moran\'s I', color='blue')
    ax2.set_ylabel('% Significant Variables', color='orange')
    ax.set_xticks(x)
    ax.set_xticklabels(weights_methods, rotation=45)
    ax.set_title(f'Moran\'s I by Spatial Weights Method ({geo_level})')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'morans_i_by_weights.png'), dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: morans_i_by_weights.png")

    plt.close('all')

    # 3. Export top results to CSV
    top_results = pd.concat([
        df.nlargest(50, 'I'),
        df.nsmallest(50, 'I')
    ]).drop_duplicates()

    top_results.to_csv(os.path.join(output_dir, 'top_spatial_autocorrelation.csv'), index=False)
    print(f"  ✓ Saved: top_spatial_autocorrelation.csv")

def create_summary_report(geo_level):
    """Create comprehensive summary report"""
    print(f"\nCreating summary report for {geo_level}...")

    geo_dir = os.path.join(RESULTS_DIR, geo_level)

    if not os.path.exists(geo_dir):
        print(f"  ✗ Results directory not found: {geo_dir}")
        return

    report = []
    report.append("="*120)
    report.append(f"SPATIAL ECONOMETRIC ANALYSIS SUMMARY: {geo_level}")
    report.append("="*120)
    report.append("")

    # Moran's I summary
    morans_file = os.path.join(geo_dir, f'{geo_level}_morans_i.csv')
    if os.path.exists(morans_file):
        df = pd.read_csv(morans_file)
        report.append("GLOBAL SPATIAL AUTOCORRELATION (MORAN'S I)")
        report.append("-" * 120)
        report.append(f"Total variable-weight combinations analyzed: {len(df):,}")
        report.append(f"Significant spatial autocorrelation (p<0.05): {(df['significant']==True).sum():,} ({(df['significant']==True).sum()/len(df)*100:.1f}%)")
        report.append(f"Positive clustering: {((df['significant']==True) & (df['I']>0)).sum():,}")
        report.append(f"Negative dispersion: {((df['significant']==True) & (df['I']<0)).sum():,}")
        report.append(f"Mean Moran's I: {df['I'].mean():.4f}")
        report.append(f"Median Moran's I: {df['I'].median():.4f}")
        report.append(f"Range: [{df['I'].min():.4f}, {df['I'].max():.4f}]")
        report.append("")

        report.append("TOP 10 VARIABLES WITH STRONGEST POSITIVE CLUSTERING:")
        top_pos = df.nlargest(10, 'I')[['variable', 'I', 'p_value', 'weights_method']]
        for idx, row in top_pos.iterrows():
            report.append(f"  {row['variable'][:60]:60} | I={row['I']:.4f}, p={row['p_value']:.4f} ({row['weights_method']})")
        report.append("")

        report.append("TOP 10 VARIABLES WITH STRONGEST NEGATIVE DISPERSION:")
        top_neg = df.nsmallest(10, 'I')[['variable', 'I', 'p_value', 'weights_method']]
        for idx, row in top_neg.iterrows():
            report.append(f"  {row['variable'][:60]:60} | I={row['I']:.4f}, p={row['p_value']:.4f} ({row['weights_method']})")
        report.append("")

    # LISA summary
    lisa_file = os.path.join(geo_dir, f'{geo_level}_lisa_results.pkl')
    if os.path.exists(lisa_file):
        with open(lisa_file, 'rb') as f:
            lisa_results = pickle.load(f)

        report.append("LOCAL SPATIAL AUTOCORRELATION (LISA)")
        report.append("-" * 120)
        report.append(f"Variables analyzed: {len(lisa_results)}")

        # Count hot/cold spots across all variables
        total_hotspots = 0
        total_coldspots = 0
        total_outliers = 0

        for key, result in lisa_results.items():
            total_hotspots += (result['spots'] == 'Hot Spot (HH)').sum()
            total_coldspots += (result['spots'] == 'Cold Spot (LL)').sum()
            total_outliers += ((result['spots'] == 'Spatial Outlier (LH)') |
                              (result['spots'] == 'Spatial Outlier (HL)')).sum()

        report.append(f"Total hot spots identified: {total_hotspots:,}")
        report.append(f"Total cold spots identified: {total_coldspots:,}")
        report.append(f"Total spatial outliers identified: {total_outliers:,}")
        report.append("")

    # Spatial lag models summary
    lag_file = os.path.join(geo_dir, f'{geo_level}_spatial_lag_models.pkl')
    if os.path.exists(lag_file):
        with open(lag_file, 'rb') as f:
            lag_results = pickle.load(f)

        report.append("SPATIAL LAG MODELS")
        report.append("-" * 120)
        report.append(f"Models estimated: {len(lag_results)}")

        for model in lag_results:
            report.append(f"\nModel: {model['y_variable']} ~ {' + '.join(model['x_variables'])}")
            report.append(f"  Spatial lag coefficient (ρ): {model['rho']:.4f}")
            if model['r_squared'] is not None:
                report.append(f"  Pseudo R²: {model['r_squared']:.4f}")
            if model['AIC'] is not None:
                report.append(f"  AIC: {model['AIC']:.2f}")

        report.append("")

    # GWR summary
    gwr_file = os.path.join(geo_dir, f'{geo_level}_gwr_models.pkl')
    if os.path.exists(gwr_file):
        with open(gwr_file, 'rb') as f:
            gwr_results = pickle.load(f)

        report.append("GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)")
        report.append("-" * 120)
        report.append(f"Models estimated: {len(gwr_results)}")

        for model in gwr_results:
            report.append(f"\nModel: {model['y_variable']} ~ {' + '.join(model['x_variables'])}")
            report.append(f"  Bandwidth: {model['bandwidth']:.4f}")
            report.append(f"  Kernel: {model['kernel']}")
            report.append(f"  AIC: {model['AIC']:.2f}")
            report.append(f"  Mean local R²: {np.mean(model['local_R2']):.4f}")
            report.append(f"  Local R² range: [{np.min(model['local_R2']):.4f}, {np.max(model['local_R2']):.4f}]")

        report.append("")

    # File inventory
    report.append("OUTPUT FILES")
    report.append("-" * 120)
    for filename in sorted(os.listdir(geo_dir)):
        filepath = os.path.join(geo_dir, filename)
        size_mb = os.path.getsize(filepath) / 1024 / 1024
        report.append(f"  {filename:50} {size_mb:10.2f} MB")

    report.append("")
    report.append("="*120)

    # Save report
    report_text = "\n".join(report)
    report_file = os.path.join(VIZ_DIR, f'{geo_level}_analysis_summary.txt')
    with open(report_file, 'w') as f:
        f.write(report_text)

    print(f"  ✓ Saved: {report_file}")

    # Also print to console
    print("\n" + report_text)

def main():
    """Main visualization pipeline"""

    # Get all geographic levels that have been analyzed
    if not os.path.exists(RESULTS_DIR):
        print(f"✗ Results directory not found: {RESULTS_DIR}")
        print("  Run spatial_econometric_analysis.py first")
        return

    geo_levels = [d for d in os.listdir(RESULTS_DIR)
                  if os.path.isdir(os.path.join(RESULTS_DIR, d))]

    if not geo_levels:
        print("✗ No analysis results found")
        return

    print(f"\nFound results for {len(geo_levels)} geographic levels: {', '.join(geo_levels)}")

    for geo_level in geo_levels:
        print(f"\n{'='*120}")
        print(f"Processing {geo_level}")
        print(f"{'='*120}")

        try:
            visualize_morans_i(geo_level)
            create_summary_report(geo_level)
        except Exception as e:
            print(f"✗ Error processing {geo_level}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*120)
    print("VISUALIZATION COMPLETE!")
    print("="*120)
    print(f"Visualizations saved to: {VIZ_DIR}")

if __name__ == "__main__":
    main()
