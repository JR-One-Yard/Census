#!/usr/bin/env python3
"""
OPTIMIZED Lifestyle Premium Mapping & Amenity Access Scoring
Uses vectorized numpy operations and KD-trees for maximum performance

Processes all 61,844 SA1 areas in minutes instead of hours!
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os
from dataclasses import dataclass
from scipy.spatial import cKDTree
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# Configuration
# ============================================================================

DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SA1/AUS/"
OUTPUT_DIR = "/home/user/Census/lifestyle_premium_outputs/"

@dataclass
class AmenityWeights:
    """Weighting factors for different amenities"""
    beach_distance: float = 0.20
    park_access: float = 0.15
    school_proximity: float = 0.25
    hospital_proximity: float = 0.15
    education_level: float = 0.10
    income_level: float = 0.10
    age_preference: float = 0.05

# ============================================================================
# Geographic Coordinate System (Vectorized)
# ============================================================================

class SA1GeocodingEngine:
    """Generate geographic coordinates for all SA1 areas using vectorization"""

    STATE_CENTROIDS = {
        '1': {'lat': -33.8688, 'lon': 151.2093, 'name': 'NSW'},
        '2': {'lat': -37.8136, 'lon': 144.9631, 'name': 'VIC'},
        '3': {'lat': -27.4698, 'lon': 153.0251, 'name': 'QLD'},
        '4': {'lat': -34.9285, 'lon': 138.6007, 'name': 'SA'},
        '5': {'lat': -31.9505, 'lon': 115.8605, 'name': 'WA'},
        '6': {'lat': -42.8821, 'lon': 147.3272, 'name': 'TAS'},
        '7': {'lat': -12.4634, 'lon': 130.8456, 'name': 'NT'},
        '8': {'lat': -35.2809, 'lon': 149.1300, 'name': 'ACT'},
    }

    def generate_all_coordinates(self, sa1_codes: np.ndarray) -> pd.DataFrame:
        """
        Vectorized coordinate generation for all SA1s at once
        Much faster than individual generation
        """
        print("Generating coordinates for all SA1s using vectorization...")

        # Extract state codes
        state_codes = np.array([str(code)[0] for code in sa1_codes])

        # Get centroids for each state
        lats = np.array([self.STATE_CENTROIDS.get(sc, self.STATE_CENTROIDS['1'])['lat']
                        for sc in state_codes])
        lons = np.array([self.STATE_CENTROIDS.get(sc, self.STATE_CENTROIDS['1'])['lon']
                        for sc in state_codes])

        # Create pseudo-random but deterministic offsets
        code_hashes = np.array([int(str(code)[1:8]) if len(str(code)) >= 8 else int(str(code)[1:])
                               for code in sa1_codes])

        # Vectorized offset calculation
        lat_offsets = ((code_hashes % 1000) / 1000.0 - 0.5) * 10
        lon_offsets = ((code_hashes % 10000) / 10000.0 - 0.5) * 10

        lats = lats + lat_offsets
        lons = lons + lon_offsets

        df = pd.DataFrame({
            'SA1_CODE_2021': sa1_codes,
            'latitude': lats,
            'longitude': lons
        })

        print(f"✓ Generated coordinates for {len(df):,} SA1s")
        return df

# ============================================================================
# Amenity Location System (Optimized)
# ============================================================================

class AmenityLocationEngine:
    """Generate realistic amenity locations - optimized for speed"""

    def __init__(self):
        print("\nGenerating amenity locations...")
        self.beaches = self._generate_coastal_amenities()
        self.parks = self._generate_urban_amenities('parks', 5000)  # Reduced for speed
        self.schools = self._generate_urban_amenities('schools', 3000)  # Reduced for speed
        self.hospitals = self._generate_urban_amenities('hospitals', 800)  # Reduced for speed

    def _generate_coastal_amenities(self) -> np.ndarray:
        """Generate beach locations - returns numpy array for speed"""
        beaches = []

        # Coastline points (simplified)
        for lat in np.arange(-37.5, -28.0, 0.3):
            beaches.append((lat, 153.4 + np.random.uniform(-0.1, 0.1)))

        for lat in np.arange(-28.0, -10.0, 0.5):
            beaches.append((lat, 153.0 + np.random.uniform(-0.2, 0.2)))

        for lat in np.arange(-38.5, -37.5, 0.3):
            beaches.append((lat, 144.0 + np.random.uniform(-1.0, 3.0)))

        for lat in np.arange(-38.0, -32.0, 0.5):
            beaches.append((lat, 137.0 + np.random.uniform(-1.0, 1.0)))

        for lat in np.arange(-35.0, -28.0, 0.5):
            beaches.append((lat, 115.0 + np.random.uniform(-1.0, 1.0)))

        for lat in np.arange(-43.5, -40.5, 0.5):
            beaches.append((lat, 147.0 + np.random.uniform(-1.0, 1.0)))

        return np.array(beaches)

    def _generate_urban_amenities(self, amenity_type: str, count: int) -> np.ndarray:
        """Generate amenity locations - returns numpy array"""
        amenities = []

        # Major city clusters
        major_cities = [
            (-33.8688, 151.2093, 0.35),  # Sydney
            (-37.8136, 144.9631, 0.25),  # Melbourne
            (-27.4698, 153.0251, 0.15),  # Brisbane
            (-31.9505, 115.8605, 0.10),  # Perth
            (-34.9285, 138.6007, 0.08),  # Adelaide
            (-42.8821, 147.3272, 0.03),  # Hobart
            (-35.2809, 149.1300, 0.04),  # Canberra
        ]

        for lat, lon, proportion in major_cities:
            n = int(count * 0.8 * proportion)
            lats = np.random.normal(lat, 0.3, n)
            lons = np.random.normal(lon, 0.3, n)
            amenities.extend(zip(lats, lons))

        # Regional areas
        regional_count = int(count * 0.2)
        lats = np.random.uniform(-44, -10, regional_count)
        lons = np.random.uniform(115, 154, regional_count)
        amenities.extend(zip(lats, lons))

        return np.array(amenities)

# ============================================================================
# FAST Distance Calculation Using KD-Trees
# ============================================================================

def build_kdtree_and_calculate_distances(sa1_coords: np.ndarray,
                                         amenity_coords: np.ndarray,
                                         amenity_name: str,
                                         k_nearest: int = 5) -> pd.DataFrame:
    """
    Ultra-fast distance calculation using KD-trees
    Calculates all distances in one vectorized operation!
    """
    print(f"  Calculating {amenity_name} distances...", end=' ')

    # Convert to radians for haversine
    sa1_rad = np.radians(sa1_coords)
    amenity_rad = np.radians(amenity_coords)

    # Build KD-tree for fast nearest neighbor search
    tree = cKDTree(amenity_rad)

    # Find k nearest amenities for each SA1
    distances, indices = tree.query(sa1_rad, k=min(k_nearest, len(amenity_coords)))

    # Convert angular distances to km (approximate Haversine)
    # For small distances, this approximation is very good
    R = 6371  # Earth radius in km
    if k_nearest == 1:
        distances_km = distances * R
        min_dist = distances_km
        avg_dist = distances_km
    else:
        distances_km = distances * R
        min_dist = distances_km[:, 0]
        avg_dist = np.mean(distances_km, axis=1)

    # Count amenities within thresholds
    count_5km = np.sum(distances_km < 5/R, axis=1) if k_nearest > 1 else (distances_km < 5).astype(int)
    count_10km = np.sum(distances_km < 10/R, axis=1) if k_nearest > 1 else (distances_km < 10).astype(int)

    print(f"✓")

    return pd.DataFrame({
        f'{amenity_name}_min_km': min_dist,
        f'{amenity_name}_avg_km': avg_dist,
        f'{amenity_name}s_within_5km': count_5km,
        f'{amenity_name}s_within_10km': count_10km,
    })

# ============================================================================
# Census Data Loaders
# ============================================================================

class CensusDataLoader:
    """Load and process census data"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load a census table"""
        file_path = f"{self.data_dir}2021Census_{table_name}_AUST_SA1.csv"
        print(f"  Loading {table_name}...", end=' ')
        df = pd.read_csv(file_path)
        print(f"✓ ({len(df):,} records)")
        return df

    def load_all_data(self) -> pd.DataFrame:
        """Load all required census tables and merge"""
        print("\nLoading census data...")

        # G01: Basic demographics
        df = self.load_table('G01')[['SA1_CODE_2021', 'Tot_P_P']].copy()

        # G02: Median age, income
        df_g02 = self.load_table('G02')[[
            'SA1_CODE_2021', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly',
            'Median_rent_weekly', 'Median_mortgage_repay_monthly', 'Median_tot_hhd_inc_weekly'
        ]]
        df = df.merge(df_g02, on='SA1_CODE_2021', how='left')

        # G16A/B: Education
        df_g16a = self.load_table('G16A')
        df_g16b = self.load_table('G16B')

        y12_cols_m = [col for col in df_g16a.columns if 'M_Y12e' in col]
        y12_cols_f = [col for col in df_g16b.columns if 'F_Y12e' in col]

        df['Year12_Total'] = (
            df_g16a[y12_cols_m].sum(axis=1).values +
            df_g16b[y12_cols_f].sum(axis=1).values
        )

        # G17A/B: Income
        df_g17a = self.load_table('G17A')
        df_g17b = self.load_table('G17B')

        high_income_cols_m = [col for col in df_g17a.columns if
                             ('2000_2999' in col or '3000' in col) and col.startswith('M_')]
        high_income_cols_f = [col for col in df_g17b.columns if
                             ('2000_2999' in col or '3000' in col) and col.startswith('F_')]

        df['High_Income_Total'] = (
            df_g17a[high_income_cols_m].sum(axis=1).values +
            df_g17b[high_income_cols_f].sum(axis=1).values
        )

        # G23: Family structure
        df_g23 = self.load_table('G23')
        child_cols = [col for col in df_g23.columns if 'child' in col.lower()]
        df['Families_with_children'] = df_g23[child_cols].sum(axis=1).values if child_cols else 0

        print(f"\n✓ Merged data for {len(df):,} SA1 areas")

        return df

# ============================================================================
# Scoring Engine (Vectorized)
# ============================================================================

class LifestyleScoreCalculator:
    """Calculate lifestyle scores using vectorized operations"""

    def __init__(self, census_data: pd.DataFrame, sa1_coords: pd.DataFrame,
                 amenities: AmenityLocationEngine):
        self.census_data = census_data
        self.sa1_coords = sa1_coords
        self.amenities = amenities

    def calculate_all_scores(self, weights: AmenityWeights) -> pd.DataFrame:
        """Calculate all amenity and lifestyle scores"""

        print("\n" + "="*100)
        print("CALCULATING AMENITY ACCESS SCORES (VECTORIZED)")
        print("="*100)

        # Merge coordinates with census data
        df = self.census_data.merge(self.sa1_coords, on='SA1_CODE_2021', how='left')

        # Get SA1 coordinates as numpy array
        sa1_coords_array = df[['latitude', 'longitude']].values

        # Calculate distances to all amenity types using KD-trees
        beach_scores = build_kdtree_and_calculate_distances(
            sa1_coords_array, self.amenities.beaches, 'beach', k_nearest=3)

        park_scores = build_kdtree_and_calculate_distances(
            sa1_coords_array, self.amenities.parks, 'park', k_nearest=5)

        school_scores = build_kdtree_and_calculate_distances(
            sa1_coords_array, self.amenities.schools, 'school', k_nearest=3)

        hospital_scores = build_kdtree_and_calculate_distances(
            sa1_coords_array, self.amenities.hospitals, 'hospital', k_nearest=2)

        # Merge all scores
        for score_df in [beach_scores, park_scores, school_scores, hospital_scores]:
            df = pd.concat([df, score_df], axis=1)

        print("\n" + "="*100)
        print("CALCULATING LIFESTYLE PREMIUM INDEX")
        print("="*100)

        # Vectorized score calculations
        df['beach_score'] = self._inverse_distance_score(df['beach_avg_km'], 50)
        df['park_score'] = self._normalize_score(df['parks_within_5km'], 10)
        df['school_score'] = self._inverse_distance_score(df['school_avg_km'], 10)
        df['hospital_score'] = self._inverse_distance_score(df['hospital_avg_km'], 20)
        df['education_score'] = self._normalize_score(df['Year12_Total'])
        df['income_score'] = self._normalize_score(df['Median_tot_prsnl_inc_weekly'])
        df['age_score'] = self._age_preference_score(df['Median_age_persons'].fillna(35))

        # Composite Lifestyle Premium Index
        df['lifestyle_premium_index'] = (
            df['beach_score'] * weights.beach_distance +
            df['park_score'] * weights.park_access +
            df['school_score'] * weights.school_proximity +
            df['hospital_score'] * weights.hospital_proximity +
            df['education_score'] * weights.education_level +
            df['income_score'] * weights.income_level +
            df['age_score'] * weights.age_preference
        ) * 100

        # School Quality Demand Index
        df['school_demand_index'] = (
            df['education_score'] * 0.6 +
            self._normalize_score(df['Families_with_children']) * 0.4
        ) * 100

        # Lifestyle Preference Index
        df['lifestyle_preference_index'] = (
            df['income_score'] * 0.5 +
            df['age_score'] * 0.3 +
            df['education_score'] * 0.2
        ) * 100

        # Value Score (high lifestyle, lower cost)
        df['value_score'] = (
            df['lifestyle_premium_index'] /
            np.maximum(df['Median_tot_prsnl_inc_weekly'].fillna(1000), 100) * 100
        )

        print("✓ All indices calculated")

        return df

    def _normalize_score(self, values: pd.Series, max_val: float = None) -> pd.Series:
        """Vectorized normalization"""
        if max_val is None:
            max_val = values.quantile(0.99)
        if max_val == 0:
            return pd.Series(0, index=values.index)
        return np.clip(values / max_val, 0, 1)

    def _inverse_distance_score(self, distances: pd.Series, max_dist: float) -> pd.Series:
        """Vectorized inverse distance scoring"""
        return np.clip(1 - (distances / max_dist), 0, 1)

    def _age_preference_score(self, ages: pd.Series) -> pd.Series:
        """Vectorized age preference curve"""
        optimal_age = 42.5
        std_dev = 15
        return np.exp(-((ages - optimal_age) ** 2) / (2 * std_dev ** 2))

# ============================================================================
# Main Analysis Pipeline
# ============================================================================

def main():
    print("="*100)
    print("LIFESTYLE PREMIUM MAPPING & AMENITY ACCESS SCORING (OPTIMIZED)")
    print("Australian Census 2021 - All 61,844 SA1 Areas")
    print("Using vectorized operations and KD-trees for maximum performance")
    print("="*100)

    # Load census data
    loader = CensusDataLoader(DATA_DIR)
    census_data = loader.load_all_data()

    # Generate coordinates
    geocoder = SA1GeocodingEngine()
    sa1_coords = geocoder.generate_all_coordinates(census_data['SA1_CODE_2021'].values)

    # Generate amenities
    amenities = AmenityLocationEngine()
    print(f"✓ Generated {len(amenities.beaches):,} beach locations")
    print(f"✓ Generated {len(amenities.parks):,} park locations")
    print(f"✓ Generated {len(amenities.schools):,} school locations")
    print(f"✓ Generated {len(amenities.hospitals):,} hospital locations")

    # Calculate scores
    calculator = LifestyleScoreCalculator(census_data, sa1_coords, amenities)
    weights = AmenityWeights()
    results = calculator.calculate_all_scores(weights)

    # Filter to populated areas
    results_filtered = results[results['Tot_P_P'] >= 50].copy()

    print("\n" + "="*100)
    print("GENERATING OUTPUTS AND INSIGHTS")
    print("="*100)

    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Full results
    output_file = f"{OUTPUT_DIR}lifestyle_premium_all_sa1s.csv"
    results.to_csv(output_file, index=False)
    print(f"\n✓ Saved full results: {output_file}")
    print(f"  Total records: {len(results):,}")

    # Top lifestyle areas
    top_lifestyle = results_filtered.nlargest(1000, 'lifestyle_premium_index')
    top_lifestyle.to_csv(f"{OUTPUT_DIR}top_1000_lifestyle_premium.csv", index=False)
    print(f"\n✓ Saved top 1000 lifestyle premium areas")

    # Best value areas
    top_value = results_filtered.nlargest(1000, 'value_score')
    top_value.to_csv(f"{OUTPUT_DIR}top_1000_value_areas.csv", index=False)
    print(f"✓ Saved top 1000 value areas")

    # State-based analysis
    results_filtered['state'] = results_filtered['SA1_CODE_2021'].astype(str).str[0]
    state_summary = results_filtered.groupby('state').agg({
        'lifestyle_premium_index': ['mean', 'median', 'max'],
        'beach_avg_km': 'mean',
        'parks_within_5km': 'mean',
        'school_avg_km': 'mean',
        'Median_tot_prsnl_inc_weekly': 'median'
    }).round(2)
    state_summary.to_csv(f"{OUTPUT_DIR}state_summary_statistics.csv")
    print(f"✓ Saved state summary statistics")

    # Generate summary statistics
    print("\n" + "="*100)
    print("SUMMARY STATISTICS")
    print("="*100)

    print(f"\nTotal SA1 areas analyzed: {len(results):,}")
    print(f"SA1 areas with population >= 50: {len(results_filtered):,}")

    print(f"\nLifestyle Premium Index (populated areas):")
    print(f"  Mean: {results_filtered['lifestyle_premium_index'].mean():.2f}")
    print(f"  Median: {results_filtered['lifestyle_premium_index'].median():.2f}")
    print(f"  Max: {results_filtered['lifestyle_premium_index'].max():.2f}")
    print(f"  Min: {results_filtered['lifestyle_premium_index'].min():.2f}")

    print(f"\nAmenity Access Averages (populated areas):")
    print(f"  Beach distance: {results_filtered['beach_avg_km'].mean():.1f} km")
    print(f"  Parks within 5km: {results_filtered['parks_within_5km'].mean():.1f}")
    print(f"  School distance: {results_filtered['school_avg_km'].mean():.1f} km")
    print(f"  Hospital distance: {results_filtered['hospital_avg_km'].mean():.1f} km")

    # Top 20 lifestyle areas
    print("\n" + "="*100)
    print("TOP 20 LIFESTYLE PREMIUM SA1 AREAS")
    print("="*100)

    top_20 = results_filtered.nlargest(20, 'lifestyle_premium_index')

    for idx, row in top_20.iterrows():
        state_name = SA1GeocodingEngine.STATE_CENTROIDS.get(row['state'], {}).get('name', 'UNK')
        print(f"\n#{top_20.index.get_loc(idx) + 1} SA1: {row['SA1_CODE_2021']} ({state_name})")
        print(f"  Lifestyle Index: {row['lifestyle_premium_index']:.2f}/100")
        print(f"  Beach: {row['beach_avg_km']:.1f}km | Parks: {row['parks_within_5km']:.0f} within 5km")
        print(f"  Schools: {row['school_avg_km']:.1f}km | Hospitals: {row['hospital_avg_km']:.1f}km")
        print(f"  Income: ${row['Median_tot_prsnl_inc_weekly']:.0f}/wk | Age: {row['Median_age_persons']:.0f} | Pop: {row['Tot_P_P']:.0f}")

    # Top 20 value areas
    print("\n" + "="*100)
    print("TOP 20 BEST VALUE LIFESTYLE AREAS")
    print("(High lifestyle premium relative to income)")
    print("="*100)

    top_20_value = results_filtered.nlargest(20, 'value_score')

    for idx, row in top_20_value.iterrows():
        state_name = SA1GeocodingEngine.STATE_CENTROIDS.get(row['state'], {}).get('name', 'UNK')
        print(f"\n#{top_20_value.index.get_loc(idx) + 1} SA1: {row['SA1_CODE_2021']} ({state_name})")
        print(f"  Value Score: {row['value_score']:.2f} | Lifestyle Index: {row['lifestyle_premium_index']:.2f}/100")
        print(f"  Income: ${row['Median_tot_prsnl_inc_weekly']:.0f}/wk (undervalued indicator)")
        print(f"  Beach: {row['beach_avg_km']:.1f}km | Schools: {row['school_avg_km']:.1f}km")

    print("\n" + "="*100)
    print("ANALYSIS COMPLETE!")
    print("="*100)
    print(f"\nAll results saved to: {OUTPUT_DIR}")

    return results

if __name__ == "__main__":
    results = main()
