#!/usr/bin/env python3
"""
Phase 10: Create Visualizations
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

print("="*100)
print("📊 PHASE 10: CREATING VISUALIZATIONS")
print("="*100)

OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")
VIZ_DIR = OUTPUT_DIR / "visualizations"
VIZ_DIR.mkdir(exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

# Load data
master_profile = pd.read_csv(OUTPUT_DIR / 'master_demographic_profile.csv')
coords = pd.read_csv(OUTPUT_DIR / 'dimensionality_reduction_coords.csv')
clustering = pd.read_csv(OUTPUT_DIR / 'clustering_results.csv')

# Merge everything
full_data = master_profile.merge(coords, on=['SAL_CODE_2021', 'Suburb_Name'])
full_data = full_data.merge(
    clustering[['SAL_CODE_2021', 'KMeans_10', 'HDBSCAN']],
    on='SAL_CODE_2021'
)

# ============================================================================
# VIZ 1: UMAP Clustering Visualization
# ============================================================================
print("\n📊 Creating UMAP clustering visualization...")

fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# K-Means clusters
scatter1 = axes[0].scatter(
    full_data['UMAP_X'],
    full_data['UMAP_Y'],
    c=full_data['KMeans_10'],
    cmap='tab10',
    alpha=0.6,
    s=10
)
axes[0].set_title('UMAP Projection - K-Means Clusters (k=10)', fontsize=16, fontweight='bold')
axes[0].set_xlabel('UMAP Dimension 1', fontsize=12)
axes[0].set_ylabel('UMAP Dimension 2', fontsize=12)
plt.colorbar(scatter1, ax=axes[0], label='Cluster')

# Income heatmap
if 'Median_tot_prsnl_inc_weekly' in full_data.columns:
    scatter2 = axes[1].scatter(
        full_data['UMAP_X'],
        full_data['UMAP_Y'],
        c=full_data['Median_tot_prsnl_inc_weekly'],
        cmap='RdYlGn',
        alpha=0.6,
        s=10,
        vmin=0,
        vmax=2000
    )
    axes[1].set_title('UMAP Projection - Median Income Heatmap', fontsize=16, fontweight='bold')
    axes[1].set_xlabel('UMAP Dimension 1', fontsize=12)
    axes[1].set_ylabel('UMAP Dimension 2', fontsize=12)
    plt.colorbar(scatter2, ax=axes[1], label='Weekly Income ($)')

plt.tight_layout()
plt.savefig(VIZ_DIR / '01_umap_clustering.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {VIZ_DIR / '01_umap_clustering.png'}")
plt.close()

# ============================================================================
# VIZ 2: Age vs Income Distribution
# ============================================================================
print("\n📊 Creating age vs income distribution...")

if 'Median_age_persons' in full_data.columns and 'Median_tot_prsnl_inc_weekly' in full_data.columns:
    fig, ax = plt.subplots(figsize=(14, 10))

    # Filter out zero values
    plot_data = full_data[
        (full_data['Median_age_persons'] > 0) &
        (full_data['Median_tot_prsnl_inc_weekly'] > 0)
    ]

    scatter = ax.scatter(
        plot_data['Median_age_persons'],
        plot_data['Median_tot_prsnl_inc_weekly'],
        c=plot_data['KMeans_10'],
        cmap='tab10',
        alpha=0.5,
        s=20
    )

    ax.set_xlabel('Median Age (years)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Median Personal Income ($/week)', fontsize=14, fontweight='bold')
    ax.set_title('Suburb Demographics: Age vs Income', fontsize=18, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.colorbar(scatter, label='Cluster')

    plt.tight_layout()
    plt.savefig(VIZ_DIR / '02_age_vs_income.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {VIZ_DIR / '02_age_vs_income.png'}")
    plt.close()

# ============================================================================
# VIZ 3: Cluster Size Distribution
# ============================================================================
print("\n📊 Creating cluster size distribution...")

fig, ax = plt.subplots(figsize=(12, 8))

cluster_counts = full_data['KMeans_10'].value_counts().sort_index()
bars = ax.bar(cluster_counts.index, cluster_counts.values, color='steelblue', alpha=0.7)

ax.set_xlabel('Cluster ID', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Suburbs', fontsize=14, fontweight='bold')
ax.set_title('Cluster Size Distribution (K-Means, k=10)', fontsize=18, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}',
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(VIZ_DIR / '03_cluster_distribution.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {VIZ_DIR / '03_cluster_distribution.png'}")
plt.close()

# ============================================================================
# VIZ 4: Income Distribution
# ============================================================================
print("\n📊 Creating income distribution...")

if 'Median_tot_prsnl_inc_weekly' in full_data.columns:
    fig, ax = plt.subplots(figsize=(12, 8))

    income_data = full_data[full_data['Median_tot_prsnl_inc_weekly'] > 0]['Median_tot_prsnl_inc_weekly']

    ax.hist(income_data, bins=50, color='darkgreen', alpha=0.7, edgecolor='black')
    ax.axvline(income_data.median(), color='red', linestyle='--', linewidth=2, label=f'Median: ${income_data.median():.0f}')
    ax.axvline(income_data.mean(), color='blue', linestyle='--', linewidth=2, label=f'Mean: ${income_data.mean():.0f}')

    ax.set_xlabel('Median Personal Income ($/week)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Suburbs', fontsize=14, fontweight='bold')
    ax.set_title('Distribution of Median Personal Income Across Australian Suburbs', fontsize=18, fontweight='bold')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(VIZ_DIR / '04_income_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {VIZ_DIR / '04_income_distribution.png'}")
    plt.close()

# ============================================================================
# VIZ 5: Age Distribution
# ============================================================================
print("\n📊 Creating age distribution...")

if 'Median_age_persons' in full_data.columns:
    fig, ax = plt.subplots(figsize=(12, 8))

    age_data = full_data[full_data['Median_age_persons'] > 0]['Median_age_persons']

    ax.hist(age_data, bins=40, color='darkblue', alpha=0.7, edgecolor='black')
    ax.axvline(age_data.median(), color='red', linestyle='--', linewidth=2, label=f'Median: {age_data.median():.0f} years')
    ax.axvline(age_data.mean(), color='orange', linestyle='--', linewidth=2, label=f'Mean: {age_data.mean():.0f} years')

    ax.set_xlabel('Median Age (years)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Suburbs', fontsize=14, fontweight='bold')
    ax.set_title('Distribution of Median Age Across Australian Suburbs', fontsize=18, fontweight='bold')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(VIZ_DIR / '05_age_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {VIZ_DIR / '05_age_distribution.png'}")
    plt.close()

# ============================================================================
# VIZ 6: t-SNE Visualization
# ============================================================================
print("\n📊 Creating t-SNE visualization...")

fig, ax = plt.subplots(figsize=(14, 10))

scatter = ax.scatter(
    full_data['tSNE_X'],
    full_data['tSNE_Y'],
    c=full_data['KMeans_10'],
    cmap='tab10',
    alpha=0.6,
    s=15
)

ax.set_title('t-SNE Projection - Demographic Clusters', fontsize=18, fontweight='bold')
ax.set_xlabel('t-SNE Dimension 1', fontsize=14)
ax.set_ylabel('t-SNE Dimension 2', fontsize=14)
plt.colorbar(scatter, label='Cluster')

plt.tight_layout()
plt.savefig(VIZ_DIR / '06_tsne_clustering.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {VIZ_DIR / '06_tsne_clustering.png'}")
plt.close()

print("\n✓ PHASE 10 COMPLETE!")
print(f"✓ All visualizations saved to: {VIZ_DIR}")
