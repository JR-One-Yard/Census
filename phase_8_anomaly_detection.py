#!/usr/bin/env python3
"""
Phase 8: Anomaly Detection & Demographic Unicorns
Find the weirdest, most unusual suburbs in Australia
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy.stats import zscore
import json

print("="*100)
print("🦄 PHASE 8: ANOMALY DETECTION - FINDING DEMOGRAPHIC UNICORNS")
print("="*100)

OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")

# Load data
master_profile = pd.read_csv(OUTPUT_DIR / 'master_demographic_profile.csv')
clustering = pd.read_csv(OUTPUT_DIR / 'clustering_results.csv')

master_with_clusters = master_profile.merge(
    clustering[['SAL_CODE_2021', 'KMeans_10']],
    on='SAL_CODE_2021'
)

feature_cols = [c for c in master_profile.columns if c not in ['SAL_CODE_2021', 'Suburb_Name']]
X = master_profile[feature_cols].values

# ============================================================================
# 1. ISOLATION FOREST - Find global anomalies
# ============================================================================
print("\n🌲 Running Isolation Forest...")
iso_forest = IsolationForest(contamination=0.05, random_state=42)
anomaly_labels = iso_forest.fit_predict(X)
anomaly_scores = iso_forest.score_samples(X)

master_with_clusters['anomaly_score'] = anomaly_scores
master_with_clusters['is_anomaly'] = anomaly_labels == -1

n_anomalies = (anomaly_labels == -1).sum()
print(f"✓ Found {n_anomalies:,} anomalous suburbs")

# ============================================================================
# 2. Z-SCORE ANOMALIES - Find extreme values
# ============================================================================
print("\n📊 Finding Z-score anomalies...")

# Calculate z-scores for key metrics
if 'Median_age_persons' in master_with_clusters.columns:
    master_with_clusters['age_zscore'] = zscore(
        master_with_clusters['Median_age_persons'].fillna(0)
    )

if 'Median_tot_prsnl_inc_weekly' in master_with_clusters.columns:
    master_with_clusters['income_zscore'] = zscore(
        master_with_clusters['Median_tot_prsnl_inc_weekly'].fillna(0)
    )

if 'Tot_P_P' in master_with_clusters.columns:
    master_with_clusters['population_zscore'] = zscore(
        master_with_clusters['Tot_P_P'].fillna(0)
    )

# Find extreme suburbs
extreme_age = master_with_clusters.nlargest(20, 'age_zscore') if 'age_zscore' in master_with_clusters.columns else None
extreme_income = master_with_clusters.nlargest(20, 'income_zscore') if 'income_zscore' in master_with_clusters.columns else None

# ============================================================================
# 3. CLUSTER OUTLIERS - Suburbs that don't fit their cluster
# ============================================================================
print("\n🎯 Finding cluster outliers...")

cluster_outliers = []

for cluster_id in range(10):
    cluster_data = master_with_clusters[master_with_clusters['KMeans_10'] == cluster_id]

    if len(cluster_data) < 5:
        continue

    # Calculate distance from cluster center
    cluster_X = cluster_data[feature_cols].values
    cluster_center = cluster_X.mean(axis=0)

    distances = np.linalg.norm(cluster_X - cluster_center, axis=1)

    # Find most distant suburbs in cluster
    cluster_data_copy = cluster_data.copy()
    cluster_data_copy['cluster_distance'] = distances

    outliers = cluster_data_copy.nlargest(5, 'cluster_distance')

    for idx, row in outliers.iterrows():
        cluster_outliers.append({
            'suburb_name': row['Suburb_Name'],
            'sal_code': row['SAL_CODE_2021'],
            'cluster': cluster_id,
            'distance_from_center': float(row['cluster_distance']),
            'age': float(row['Median_age_persons']) if 'Median_age_persons' in row else None,
            'income': float(row['Median_tot_prsnl_inc_weekly']) if 'Median_tot_prsnl_inc_weekly' in row else None,
        })

cluster_outliers.sort(key=lambda x: x['distance_from_center'], reverse=True)

# ============================================================================
# 4. DEMOGRAPHIC UNICORNS - Unusual combinations
# ============================================================================
print("\n🦄 Finding demographic unicorns...")

unicorns = []

# Very young + very wealthy
if 'Median_age_persons' in master_with_clusters.columns and 'Median_tot_prsnl_inc_weekly' in master_with_clusters.columns:
    young_wealthy = master_with_clusters[
        (master_with_clusters['Median_age_persons'] < 30) &
        (master_with_clusters['Median_tot_prsnl_inc_weekly'] > 2000)
    ]
    print(f"  Young & Wealthy (age<30, income>$2k): {len(young_wealthy)} suburbs")

    for idx, row in young_wealthy.head(10).iterrows():
        unicorns.append({
            'type': 'Young & Wealthy',
            'suburb': row['Suburb_Name'],
            'age': float(row['Median_age_persons']),
            'income': float(row['Median_tot_prsnl_inc_weekly']),
            'population': float(row['Tot_P_P']) if 'Tot_P_P' in row else None
        })

# Very old + very wealthy
if 'Median_age_persons' in master_with_clusters.columns and 'Median_tot_prsnl_inc_weekly' in master_with_clusters.columns:
    old_wealthy = master_with_clusters[
        (master_with_clusters['Median_age_persons'] > 60) &
        (master_with_clusters['Median_tot_prsnl_inc_weekly'] > 1500)
    ]
    print(f"  Old & Wealthy (age>60, income>$1.5k): {len(old_wealthy)} suburbs")

    for idx, row in old_wealthy.head(10).iterrows():
        unicorns.append({
            'type': 'Old & Wealthy',
            'suburb': row['Suburb_Name'],
            'age': float(row['Median_age_persons']),
            'income': float(row['Median_tot_prsnl_inc_weekly']),
            'population': float(row['Tot_P_P']) if 'Tot_P_P' in row else None
        })

# Young + poor (university towns?)
if 'Median_age_persons' in master_with_clusters.columns and 'Median_tot_prsnl_inc_weekly' in master_with_clusters.columns:
    young_poor = master_with_clusters[
        (master_with_clusters['Median_age_persons'] < 25) &
        (master_with_clusters['Median_tot_prsnl_inc_weekly'] < 500) &
        (master_with_clusters['Tot_P_P'] > 100 if 'Tot_P_P' in master_with_clusters.columns else True)
    ]
    print(f"  Young & Poor (age<25, income<$500): {len(young_poor)} suburbs")

    for idx, row in young_poor.head(10).iterrows():
        unicorns.append({
            'type': 'Young & Poor (Student areas?)',
            'suburb': row['Suburb_Name'],
            'age': float(row['Median_age_persons']),
            'income': float(row['Median_tot_prsnl_inc_weekly']),
            'population': float(row['Tot_P_P']) if 'Tot_P_P' in row else None
        })

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n💾 Saving anomaly results...")

# Save top anomalies
top_anomalies = master_with_clusters.nsmallest(50, 'anomaly_score')
top_anomalies.to_csv(OUTPUT_DIR / 'top_anomalous_suburbs.csv', index=False)

# Save unicorns
with open(OUTPUT_DIR / 'demographic_unicorns.json', 'w') as f:
    json.dump({
        'cluster_outliers': cluster_outliers[:50],
        'unusual_combinations': unicorns,
    }, f, indent=2)

print("\n" + "="*100)
print("📊 ANOMALY DETECTION SUMMARY")
print("="*100)

print(f"\n✓ Global anomalies (Isolation Forest): {n_anomalies:,}")
print(f"✓ Cluster outliers identified: {len(cluster_outliers)}")
print(f"✓ Demographic unicorns found: {len(unicorns)}")

print("\n🏆 Top 10 Most Anomalous Suburbs:")
for i, (idx, row) in enumerate(top_anomalies.head(10).iterrows(), 1):
    print(f"{i}. {row['Suburb_Name']:40} | "
          f"Anomaly Score: {row['anomaly_score']:.3f} | "
          f"Age: {row['Median_age_persons']:.0f} | "
          f"Income: ${row['Median_tot_prsnl_inc_weekly']:.0f}")

print("\n✓ PHASE 8 COMPLETE!")
