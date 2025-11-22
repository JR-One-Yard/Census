#!/usr/bin/env python3
"""
BONUS: Advanced Pattern Mining & Statistical Analysis
Extract maximum insights from the data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from sklearn.preprocessing import StandardScaler
from itertools import combinations
import json

print("="*100)
print("🎁 BONUS: ADVANCED PATTERN MINING")
print("="*100)

OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")

# Load data
master_profile = pd.read_csv(OUTPUT_DIR / 'master_demographic_profile.csv')
clustering = pd.read_csv(OUTPUT_DIR / 'clustering_results.csv')
coords = pd.read_csv(OUTPUT_DIR / 'dimensionality_reduction_coords.csv')

full_data = master_profile.merge(clustering[['SAL_CODE_2021', 'KMeans_10']], on='SAL_CODE_2021')

# ============================================================================
# 1. CORRELATION MATRIX - Find strongest relationships
# ============================================================================
print("\n📊 Computing correlation matrix...")

key_features = [
    'Median_age_persons',
    'Median_tot_prsnl_inc_weekly',
    'Median_tot_hhd_inc_weekly',
    'Average_household_size',
    'Tot_P_P'
]

available_features = [f for f in key_features if f in full_data.columns]

if len(available_features) >= 2:
    corr_matrix = full_data[available_features].corr()

    print("\n🔍 Strongest Correlations:")
    # Get upper triangle of correlation matrix
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    corr_pairs = []

    for i in range(len(corr_matrix)):
        for j in range(i+1, len(corr_matrix)):
            corr_pairs.append({
                'feature1': corr_matrix.columns[i],
                'feature2': corr_matrix.columns[j],
                'correlation': float(corr_matrix.iloc[i, j])
            })

    corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)

    for pair in corr_pairs[:10]:
        print(f"  {pair['feature1']:35} <-> {pair['feature2']:35} | r = {pair['correlation']:.3f}")

# ============================================================================
# 2. STATISTICAL TESTS - Compare clusters
# ============================================================================
print("\n" + "="*100)
print("📊 STATISTICAL TESTS: Comparing Clusters")
print("="*100)

if 'Median_tot_prsnl_inc_weekly' in full_data.columns and 'KMeans_10' in full_data.columns:
    # ANOVA: Test if income differs significantly between clusters
    cluster_groups = [
        full_data[full_data['KMeans_10'] == i]['Median_tot_prsnl_inc_weekly'].dropna().values
        for i in range(10)
        if len(full_data[full_data['KMeans_10'] == i]) > 0
    ]

    # Remove empty groups
    cluster_groups = [g for g in cluster_groups if len(g) > 0]

    if len(cluster_groups) >= 2:
        f_stat, p_value = stats.f_oneway(*cluster_groups)
        print(f"\n🔬 ANOVA: Income across clusters")
        print(f"  F-statistic: {f_stat:.2f}")
        print(f"  P-value: {p_value:.2e}")
        print(f"  Result: {'Clusters have SIGNIFICANTLY different incomes' if p_value < 0.001 else 'No significant difference'}")

# ============================================================================
# 3. PERCENTILE RANKINGS - Where does each suburb rank?
# ============================================================================
print("\n" + "="*100)
print("📊 PERCENTILE RANKINGS")
print("="*100)

percentile_features = {}

for feature in ['Median_age_persons', 'Median_tot_prsnl_inc_weekly']:
    if feature in full_data.columns:
        full_data[f'{feature}_percentile'] = full_data[feature].rank(pct=True) * 100
        percentile_features[feature] = f'{feature}_percentile'

# Find suburbs in the 99th percentile for multiple metrics
if len(percentile_features) >= 2:
    print("\n🏆 Elite Suburbs (Top 1% in multiple categories):")

    elite_mask = True
    for col in percentile_features.values():
        elite_mask &= (full_data[col] >= 99)

    elite_suburbs = full_data[elite_mask]

    if len(elite_suburbs) > 0:
        print(f"\nFound {len(elite_suburbs)} elite suburbs:")
        for idx, row in elite_suburbs.head(10).iterrows():
            print(f"  {row['Suburb_Name']:40} | ", end='')
            for feature, pct_col in percentile_features.items():
                val = row[feature]
                pct = row[pct_col]
                print(f"{feature.split('_')[1][:3].title()}: {val:.0f} ({pct:.1f}%ile) ", end='')
            print()
    else:
        print("  No suburbs in top 1% for all metrics")

# ============================================================================
# 4. DIVERSITY INDEX - Calculate demographic diversity
# ============================================================================
print("\n" + "="*100)
print("📊 DEMOGRAPHIC DIVERSITY INDEX")
print("="*100)

# Calculate diversity as distance from cluster center
diversity_scores = []

for idx, row in full_data.iterrows():
    cluster = row['KMeans_10']
    cluster_data = full_data[full_data['KMeans_10'] == cluster]

    # Calculate how different this suburb is from its cluster average
    numeric_cols = full_data.select_dtypes(include=[np.number]).columns
    numeric_cols = [c for c in numeric_cols if c not in ['SAL_CODE_2021', 'KMeans_10']]

    if len(numeric_cols) > 0 and len(cluster_data) > 1:
        suburb_vals = row[numeric_cols].fillna(0).values
        cluster_mean = cluster_data[numeric_cols].fillna(0).mean().values

        # Euclidean distance from cluster center
        distance = np.linalg.norm(suburb_vals - cluster_mean)
        diversity_scores.append({
            'suburb_name': row['Suburb_Name'],
            'cluster': cluster,
            'diversity_score': float(distance)
        })

diversity_scores.sort(key=lambda x: x['diversity_score'], reverse=True)

print("\n🌈 Most Diverse Suburbs (furthest from their cluster average):")
for i, suburb in enumerate(diversity_scores[:15], 1):
    print(f"{i:2}. {suburb['suburb_name']:40} | Cluster {suburb['cluster']} | "
          f"Diversity: {suburb['diversity_score']:.2f}")

# ============================================================================
# 5. OUTLIER DETECTION - Extreme values
# ============================================================================
print("\n" + "="*100)
print("📊 EXTREME VALUE DETECTION")
print("="*100)

extremes = {}

for feature in ['Median_age_persons', 'Median_tot_prsnl_inc_weekly', 'Median_tot_hhd_inc_weekly']:
    if feature in full_data.columns:
        data = full_data[full_data[feature] > 0]

        if len(data) > 0:
            q1 = data[feature].quantile(0.25)
            q3 = data[feature].quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 3 * iqr
            upper_bound = q3 + 3 * iqr

            extreme_high = data[data[feature] > upper_bound].nlargest(5, feature)
            extreme_low = data[data[feature] < lower_bound].nsmallest(5, feature)

            extremes[feature] = {
                'high': extreme_high[['Suburb_Name', feature]].to_dict('records'),
                'low': extreme_low[['Suburb_Name', feature]].to_dict('records')
            }

            print(f"\n📈 {feature}:")
            print(f"  Extreme HIGH:")
            for suburb in extremes[feature]['high'][:3]:
                print(f"    {suburb['Suburb_Name']:40} | {suburb[feature]:.0f}")

# ============================================================================
# 6. CLUSTER STABILITY ANALYSIS
# ============================================================================
print("\n" + "="*100)
print("📊 CLUSTER STABILITY ANALYSIS")
print("="*100)

# Compare different clustering methods
cluster_methods = ['KMeans_10', 'KMeans_15', 'KMeans_20', 'Hierarchical_10']
available_methods = [m for m in cluster_methods if m in clustering.columns]

if len(available_methods) >= 2:
    print(f"\nComparing {len(available_methods)} clustering methods...")

    # Calculate agreement between methods
    agreements = []
    for method1, method2 in combinations(available_methods, 2):
        # Adjusted Rand Index would be better, but let's use simple agreement
        merge_data = clustering[[method1, method2]].copy()

        # For each suburb, see if it's clustered with the same suburbs
        # This is simplified - just checking cluster sizes
        print(f"\n  {method1} vs {method2}:")
        method1_counts = merge_data[method1].value_counts()
        method2_counts = merge_data[method2].value_counts()
        print(f"    {method1} cluster sizes: {sorted(method1_counts.values, reverse=True)[:5]}")
        print(f"    {method2} cluster sizes: {sorted(method2_counts.values, reverse=True)[:5]}")

# ============================================================================
# SAVE BONUS RESULTS
# ============================================================================
print("\n💾 Saving bonus analysis results...")

bonus_results = {
    'correlation_pairs': corr_pairs[:20] if 'corr_pairs' in locals() else [],
    'diversity_scores': diversity_scores[:50] if diversity_scores else [],
    'extremes': extremes if extremes else {},
}

with open(OUTPUT_DIR / 'bonus_advanced_analysis.json', 'w') as f:
    json.dump(bonus_results, f, indent=2)

# Create summary statistics file
summary_stats = {}

for feature in ['Median_age_persons', 'Median_tot_prsnl_inc_weekly', 'Tot_P_P']:
    if feature in full_data.columns:
        data = full_data[full_data[feature] > 0][feature]
        summary_stats[feature] = {
            'count': int(len(data)),
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'q25': float(data.quantile(0.25)),
            'q75': float(data.quantile(0.75)),
        }

with open(OUTPUT_DIR / 'summary_statistics.json', 'w') as f:
    json.dump(summary_stats, f, indent=2)

print("\n" + "="*100)
print("✓ BONUS ANALYSIS COMPLETE!")
print("="*100)

print("\n📊 Results:")
print(f"  ✓ Correlation analysis: {len(corr_pairs) if 'corr_pairs' in locals() else 0} pairs analyzed")
print(f"  ✓ Diversity scores: {len(diversity_scores)} suburbs ranked")
print(f"  ✓ Extreme values identified for {len(extremes)} features")
print(f"  ✓ Summary statistics for {len(summary_stats)} key metrics")

print("\n🎉 ALL ANALYSIS COMPLETE!")
