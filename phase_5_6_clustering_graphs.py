#!/usr/bin/env python3
"""
Phase 5: Clustering (safer version)
Phase 6: Graph Analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
import hdbscan
import networkx as nx
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("PHASE 5-6: CLUSTERING & GRAPH ANALYSIS")
print("="*100)

OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")

# Load data
master_profile = pd.read_csv(OUTPUT_DIR / 'master_demographic_profile.csv')
coords_df = pd.read_csv(OUTPUT_DIR / 'dimensionality_reduction_coords.csv')

feature_cols = [c for c in master_profile.columns if c not in ['SAL_CODE_2021', 'Suburb_Name']]
X = master_profile[feature_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================================
# CLUSTERING (Safe version - skip problematic DBSCAN)
# ============================================================================
print("\n🔬 Running clustering...")

clustering_results = coords_df[['SAL_CODE_2021', 'Suburb_Name']].copy()

# K-Means only
for k in [5, 10, 15, 20]:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    clustering_results[f'KMeans_{k}'] = labels
    print(f"✓ K-Means with k={k}")

# Hierarchical
for k in [10, 20]:
    hier = AgglomerativeClustering(n_clusters=k)
    labels = hier.fit_predict(X_scaled)
    clustering_results[f'Hierarchical_{k}'] = labels
    print(f"✓ Hierarchical with k={k}")

# HDBSCAN (more stable than DBSCAN)
print("Running HDBSCAN...")
clusterer = hdbscan.HDBSCAN(min_cluster_size=50, min_samples=10)
labels = clusterer.fit_predict(X_scaled)
clustering_results['HDBSCAN'] = labels
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print(f"✓ HDBSCAN: {n_clusters} clusters")

clustering_results.to_csv(OUTPUT_DIR / 'clustering_results.csv', index=False)
print(f"✓ Saved clustering results")

# Analyze K-Means 10
master_with_clusters = master_profile.copy()
master_with_clusters['Cluster'] = clustering_results['KMeans_10']

cluster_profiles = []
print("\n📊 Cluster Profiles (K-Means 10):")
for cluster_id in range(10):
    cluster_data = master_with_clusters[master_with_clusters['Cluster'] == cluster_id]

    profile = {
        'cluster_id': cluster_id,
        'size': len(cluster_data),
        'avg_age': float(cluster_data['Median_age_persons'].mean()) if 'Median_age_persons' in cluster_data.columns else None,
        'avg_income': float(cluster_data['Median_tot_prsnl_inc_weekly'].mean()) if 'Median_tot_prsnl_inc_weekly' in cluster_data.columns else None,
        'example_suburbs': cluster_data['Suburb_Name'].head(10).tolist()
    }
    cluster_profiles.append(profile)

    print(f"  Cluster {cluster_id}: {profile['size']:,} suburbs | "
          f"Age: {profile['avg_age']:.0f} | Income: ${profile['avg_income']:.0f}/wk")

with open(OUTPUT_DIR / 'cluster_profiles.json', 'w') as f:
    json.dump(cluster_profiles, f, indent=2)

# ============================================================================
# GRAPH NETWORK ANALYSIS
# ============================================================================
print("\n" + "="*100)
print("PHASE 6: GRAPH NETWORK")
print("="*100)

print("Building graph...")
G = nx.Graph()

# Add nodes
for idx, row in master_profile.iterrows():
    G.add_node(row['SAL_CODE_2021'], suburb_name=row['Suburb_Name'])

# Add edges from top matches
with open(OUTPUT_DIR / 'suburb_matches.json', 'r') as f:
    matches = json.load(f)

for sal_code, data in list(matches.items())[:5000]:  # Limit to avoid memory issues
    for match in data['top_10_matches'][:5]:
        weight = 1.0 / (match['distance'] + 0.0001)
        G.add_edge(sal_code, match['sal_code'], weight=weight)

print(f"✓ Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

# Centrality (sample for speed)
print("Calculating centrality...")
sample_nodes = list(G.nodes())[:2000]
degree_cent = {node: G.degree(node) for node in sample_nodes}

top_central = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:20]
print("\n🌟 Most Connected Suburbs:")
for i, (sal_code, degree) in enumerate(top_central[:10], 1):
    suburb = G.nodes[sal_code]['suburb_name']
    print(f"{i}. {suburb:40} | Connections: {degree}")

# Communities
print("\nDetecting communities...")
communities = nx.community.louvain_communities(G, seed=42)
print(f"✓ Found {len(communities)} communities")

sorted_communities = sorted(communities, key=len, reverse=True)
print("\nLargest communities:")
for i, community in enumerate(sorted_communities[:5], 1):
    suburb_names = [G.nodes[node]['suburb_name'] for node in list(community)[:3]]
    print(f"{i}. Size: {len(community):,} | {', '.join(suburb_names)}")

# Save
network_stats = {
    'num_nodes': G.number_of_nodes(),
    'num_edges': G.number_of_edges(),
    'num_communities': len(communities),
    'top_connected': [(sal, degree, G.nodes[sal]['suburb_name'])
                       for sal, degree in top_central[:20]],
}

with open(OUTPUT_DIR / 'network_analysis.json', 'w') as f:
    json.dump(network_stats, f, indent=2)

print("\n✓ Phases 5-6 complete!")
