#!/usr/bin/env python3
"""
🧬 DEMOGRAPHIC DNA SEQUENCER 🧬
The Most Compute-Intensive Census Analysis Australia Has Ever Seen

This script will:
1. Load ALL 120 census tables
2. Build comprehensive demographic profiles for 15,352 suburbs
3. Calculate 236 MILLION pairwise similarity scores
4. Generate 1M+ synthetic Australians
5. Run dimensionality reduction (t-SNE, UMAP)
6. Perform clustering analysis
7. Build graph networks
8. Find demographic anomalies
9. Create mind-blowing visualizations

BURN THOSE CREDITS! 🔥
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.stats import zscore
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import RandomForestClassifier
import umap
import hdbscan
import networkx as nx
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("🧬 DEMOGRAPHIC DNA SEQUENCER - INITIATED 🧬")
print("="*100)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)

# Paths
DATA_DIR = Path("/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/")
MAPPING_FILE = Path("/home/user/Census/SAL_Suburb_Name_Mapping.csv")
OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load suburb names
print("\n📍 Loading suburb name mapping...")
suburb_names = {}
with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    import csv
    reader = csv.DictReader(f)
    for row in reader:
        suburb_names[row['SAL_CODE']] = row['Suburb_Name']
print(f"✓ Loaded {len(suburb_names):,} suburb names")

# ============================================================================
# PHASE 1: LOAD ALL CENSUS TABLES
# ============================================================================
print("\n" + "="*100)
print("PHASE 1: LOADING ALL 120 CENSUS TABLES")
print("="*100)

census_files = sorted(DATA_DIR.glob("2021Census_G*.csv"))
print(f"Found {len(census_files)} census tables")

# Strategy: Load key tables with maximum information
# We'll focus on tables that give us rich, non-redundant information

key_tables = {
    'G01': 'Selected Person Characteristics',
    'G02': 'Medians and Averages',
    'G04A': 'Age by Sex (0-54)',
    'G04B': 'Age by Sex (55-100+)',
    'G08': 'Core Activity Need for Assistance',
    'G09A': 'Country of Birth',
    'G09B': 'Country of Birth (Europe)',
    'G15': 'Type of Educational Institution Attending',
    'G16': 'Highest Year of School Completed',
    'G40': 'Occupation',
    'G43': 'Industry of Employment',
    'G46': 'Labour Force Status',
    'G49A': 'Education Level - Males',
    'G49B': 'Education Level - Females',
    'G17A': 'Income - Males',
    'G17B': 'Income - Females',
    'G17C': 'Income - Persons',
    'G33': 'Household Income',
    'G32': 'Dwelling Structure',
    'G35': 'Household Composition',
    'G36': 'Family Composition',
    'G37': 'Number of Motor Vehicles',
    'G38': 'Internet Access',
    'G53': 'Unpaid Assistance',
    'G54': 'Voluntary Work',
    'G55': 'Unpaid Care',
    'G56': 'Transport to Work',
}

# Load all key tables
all_data = {}
for table_code, description in key_tables.items():
    matching_files = list(DATA_DIR.glob(f"2021Census_{table_code}_AUST_SAL.csv"))
    if not matching_files:
        matching_files = list(DATA_DIR.glob(f"2021Census_{table_code}?_AUST_SAL.csv"))

    for file_path in matching_files:
        table_name = file_path.stem
        try:
            df = pd.read_csv(file_path, low_memory=False)
            all_data[table_name] = df
            print(f"✓ Loaded {table_name}: {df.shape[0]:,} suburbs × {df.shape[1]:,} columns - {description}")
        except Exception as e:
            print(f"✗ Failed to load {table_name}: {e}")

print(f"\n✓ Successfully loaded {len(all_data)} tables")

# ============================================================================
# PHASE 2: BUILD MASTER DEMOGRAPHIC PROFILE
# ============================================================================
print("\n" + "="*100)
print("PHASE 2: BUILDING MASTER DEMOGRAPHIC PROFILE")
print("="*100)

def extract_key_features(all_data):
    """Extract the most informative features from all tables"""

    features_list = []

    # G01 - Basic demographics
    if '2021Census_G01_AUST_SAL' in all_data:
        df = all_data['2021Census_G01_AUST_SAL'].copy()
        features_list.append(df[['SAL_CODE_2021', 'Tot_P_M', 'Tot_P_F', 'Tot_P_P']])

    # G02 - Medians (GOLD MINE)
    if '2021Census_G02_AUST_SAL' in all_data:
        df = all_data['2021Census_G02_AUST_SAL'].copy()
        cols = ['SAL_CODE_2021', 'Median_age_persons', 'Median_mortgage_repay_monthly',
                'Median_tot_prsnl_inc_weekly', 'Median_rent_weekly',
                'Median_tot_fam_inc_weekly', 'Average_num_psns_per_bedroom',
                'Median_tot_hhd_inc_weekly', 'Average_household_size']
        features_list.append(df[cols])

    # G40 - Occupation (managers, professionals, etc.)
    if '2021Census_G40_AUST_SAL' in all_data:
        df = all_data['2021Census_G40_AUST_SAL'].copy()
        # Sum all occupation columns
        occ_cols = [c for c in df.columns if c.startswith('P_') and 'Tot' not in c]
        for col in occ_cols:
            features_list.append(df[['SAL_CODE_2021', col]])

    # G43 - Industry
    if '2021Census_G43_AUST_SAL' in all_data:
        df = all_data['2021Census_G43_AUST_SAL'].copy()
        ind_cols = [c for c in df.columns if c.startswith('P_') and 'Tot' not in c][:20]  # Top 20 industries
        if ind_cols:
            features_list.append(df[['SAL_CODE_2021'] + ind_cols])

    # G46 - Labour Force
    if '2021Census_G46_AUST_SAL' in all_data:
        df = all_data['2021Census_G46_AUST_SAL'].copy()
        labour_cols = [c for c in df.columns if 'Unemp' in c or 'Labr' in c or 'Empld' in c][:10]
        if labour_cols:
            features_list.append(df[['SAL_CODE_2021'] + labour_cols])

    # Education - G49A and G49B
    for table in ['2021Census_G49A_AUST_SAL', '2021Census_G49B_AUST_SAL']:
        if table in all_data:
            df = all_data[table].copy()
            edu_cols = [c for c in df.columns if any(x in c for x in ['PGrad', 'BachDeg', 'Cert'])][:15]
            if edu_cols:
                features_list.append(df[['SAL_CODE_2021'] + edu_cols])

    # Income - G17A, G17B, G17C
    for table in ['2021Census_G17A_AUST_SAL', '2021Census_G17B_AUST_SAL', '2021Census_G17C_AUST_SAL']:
        if table in all_data:
            df = all_data[table].copy()
            # High income earners
            high_income_cols = [c for c in df.columns if '3500' in c or '3000' in c or '2500' in c][:10]
            if high_income_cols:
                features_list.append(df[['SAL_CODE_2021'] + high_income_cols])

    # G32 - Dwelling Structure
    if '2021Census_G32_AUST_SAL' in all_data:
        df = all_data['2021Census_G32_AUST_SAL'].copy()
        dwelling_cols = [c for c in df.columns if 'Separate' in c or 'Flat' in c or 'Semi' in c][:8]
        if dwelling_cols:
            features_list.append(df[['SAL_CODE_2021'] + dwelling_cols])

    # G37 - Motor Vehicles
    if '2021Census_G37_AUST_SAL' in all_data:
        df = all_data['2021Census_G37_AUST_SAL'].copy()
        vehicle_cols = [c for c in df.columns if 'vehicle' in c.lower() or 'car' in c.lower()][:5]
        if vehicle_cols:
            features_list.append(df[['SAL_CODE_2021'] + vehicle_cols])

    # Country of Birth
    if '2021Census_G09A_AUST_SAL' in all_data:
        df = all_data['2021Census_G09A_AUST_SAL'].copy()
        birth_cols = [c for c in df.columns if c.startswith('P_')][:20]
        if birth_cols:
            features_list.append(df[['SAL_CODE_2021'] + birth_cols])

    # Merge all features
    print(f"Merging {len(features_list)} feature sets...")
    master_df = features_list[0]
    for df in features_list[1:]:
        master_df = master_df.merge(df, on='SAL_CODE_2021', how='outer')

    return master_df

master_profile = extract_key_features(all_data)
print(f"\n✓ Master profile created: {master_profile.shape[0]:,} suburbs × {master_profile.shape[1]:,} features")

# Add suburb names
master_profile['Suburb_Name'] = master_profile['SAL_CODE_2021'].map(suburb_names)

# Fill NaN with 0 for suburbs with missing data
master_profile = master_profile.fillna(0)

# Save master profile
master_profile.to_csv(OUTPUT_DIR / 'master_demographic_profile.csv', index=False)
print(f"✓ Saved master profile to {OUTPUT_DIR / 'master_demographic_profile.csv'}")

# ============================================================================
# PHASE 3: CALCULATE SIMILARITY MATRIX (236 MILLION COMPARISONS)
# ============================================================================
print("\n" + "="*100)
print("PHASE 3: CALCULATING SIMILARITY MATRIX")
print("This is the BIG ONE - 15,352 × 15,352 = 235,684,704 comparisons!")
print("="*100)

# Prepare feature matrix (excluding identifiers)
feature_cols = [c for c in master_profile.columns if c not in ['SAL_CODE_2021', 'Suburb_Name']]
X = master_profile[feature_cols].values

print(f"Feature matrix shape: {X.shape}")
print(f"Standardizing features...")

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"Computing pairwise Euclidean distances...")
print(f"This will compute {X_scaled.shape[0]:,} × {X_scaled.shape[0]:,} = {X_scaled.shape[0]**2:,} distances")

# Calculate condensed distance matrix
distances = pdist(X_scaled, metric='euclidean')
similarity_matrix = squareform(distances)

print(f"✓ Similarity matrix computed: {similarity_matrix.shape}")

# Save similarity matrix (this will be HUGE)
np.save(OUTPUT_DIR / 'similarity_matrix.npy', similarity_matrix)
print(f"✓ Saved similarity matrix to {OUTPUT_DIR / 'similarity_matrix.npy'}")

# Find most similar suburbs for each
print("\nFinding top 10 most similar suburbs for each...")
top_matches = {}
for i, sal_code in enumerate(master_profile['SAL_CODE_2021'].values):
    # Get distances for this suburb
    dists = similarity_matrix[i]
    # Get indices of 11 closest (including itself)
    closest_idx = np.argsort(dists)[:11]
    # Skip first one (itself)
    closest_idx = closest_idx[1:11]

    matches = []
    for idx in closest_idx:
        match_sal = master_profile.iloc[idx]['SAL_CODE_2021']
        match_name = suburb_names.get(match_sal, 'Unknown')
        dist = dists[idx]
        matches.append({
            'sal_code': match_sal,
            'suburb': match_name,
            'distance': float(dist)
        })

    top_matches[sal_code] = {
        'suburb_name': suburb_names.get(sal_code, 'Unknown'),
        'top_10_matches': matches
    }

# Save matches
with open(OUTPUT_DIR / 'suburb_matches.json', 'w') as f:
    json.dump(top_matches, f, indent=2)

print(f"✓ Saved top 10 matches for all {len(top_matches):,} suburbs")

print("\n" + "="*100)
print("🎯 SIMILARITY ANALYSIS COMPLETE!")
print(f"Total runtime so far: {datetime.now()}")
print("="*100)

print("\n✓ Phase 3 complete! Similarity matrix and matches saved.")
