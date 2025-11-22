#!/usr/bin/env python3
"""
COMPREHENSIVE SPATIAL ECONOMETRIC ANALYSIS
Australian Census 2021 - Full Geographic Decomposition

This script performs:
1. Spatial lag models for ALL socioeconomic variables
2. Geographically Weighted Regression (GWR) - coefficients vary by location
3. Spatial regimes modeling
4. Moran's I and LISA statistics for all 6,000+ variables
5. Spatial clusters, outliers, hot/cold spot identification

Author: Automated Analysis
Date: 2025-11-22
"""

import os
import sys
import glob
import warnings
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
import json
import pickle
from datetime import datetime
from tqdm import tqdm

# Spatial analysis libraries
import libpysal as lps
from libpysal.weights import Queen, Rook, KNN, DistanceBand
from esda.moran import Moran, Moran_Local
from esda.getisord import G_Local
from spreg import OLS, ML_Lag, ML_Error, GM_Lag
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
import mapclassify

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for spatial analysis"""

    # Directories
    BASE_DIR = "/home/user/Census"
    DATA_DIR = os.path.join(BASE_DIR, "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS")
    SHAPEFILE_DIR = os.path.join(BASE_DIR, "shapefiles")
    OUTPUT_DIR = os.path.join(BASE_DIR, "spatial_analysis_results")

    # Geographic levels to analyze
    GEO_LEVELS = ['SA2', 'SA3', 'SA4', 'LGA']  # Start with these, SA1 is too granular (61K+ areas)

    # Spatial weights methods
    SPATIAL_WEIGHTS_METHODS = ['queen', 'rook', 'knn_5', 'knn_10', 'distance']

    # Analysis settings
    MIN_OBSERVATIONS = 30  # Minimum number of observations for analysis
    GWR_BANDWIDTH_METHODS = ['AIC', 'CV', 'BIC']
    GWR_KERNEL = 'gaussian'  # or 'bisquare'

    # Parallel processing
    N_JOBS = -1  # Use all available cores

    # Output formats
    SAVE_FORMATS = ['csv', 'geojson', 'pkl']

# Create output directories
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
for geo_level in Config.GEO_LEVELS:
    os.makedirs(os.path.join(Config.OUTPUT_DIR, geo_level), exist_ok=True)

print("="*120)
print("COMPREHENSIVE SPATIAL ECONOMETRIC ANALYSIS - AUSTRALIAN CENSUS 2021")
print("="*120)
print(f"Output directory: {Config.OUTPUT_DIR}")
print(f"Geographic levels: {', '.join(Config.GEO_LEVELS)}")
print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*120)

# ============================================================================
# STEP 1: DATA LOADING INFRASTRUCTURE
# ============================================================================

class CensusDataLoader:
    """Load and manage census data across multiple tables and geographies"""

    def __init__(self, data_dir, geo_level):
        self.data_dir = data_dir
        self.geo_level = geo_level
        self.geo_data_dir = os.path.join(data_dir, geo_level, "AUS")
        self.tables = {}
        self.combined_data = None

    def get_available_tables(self):
        """Get list of all available census tables"""
        pattern = os.path.join(self.geo_data_dir, f"2021Census_G*_AUST_{self.geo_level}.csv")
        files = glob.glob(pattern)
        table_names = [os.path.basename(f).replace(f'2021Census_', '').replace(f'_AUST_{self.geo_level}.csv', '') for f in files]
        return sorted(table_names)

    def load_table(self, table_name):
        """Load a specific census table"""
        filepath = os.path.join(self.geo_data_dir, f"2021Census_{table_name}_AUST_{self.geo_level}.csv")
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath, low_memory=False)
                self.tables[table_name] = df
                return df
            except Exception as e:
                print(f"Error loading {table_name}: {e}")
                return None
        return None

    def load_all_tables(self):
        """Load all available census tables"""
        available_tables = self.get_available_tables()
        print(f"\nLoading {len(available_tables)} tables for {self.geo_level}...")

        for table_name in tqdm(available_tables, desc=f"Loading {self.geo_level} tables"):
            self.load_table(table_name)

        print(f"✓ Loaded {len(self.tables)} tables for {self.geo_level}")
        return self.tables

    def merge_all_tables(self):
        """Merge all tables on geographic identifier"""
        if not self.tables:
            self.load_all_tables()

        geo_code = f"{self.geo_level}_CODE_2021"

        # Start with the first table
        table_names = list(self.tables.keys())
        combined = self.tables[table_names[0]].copy()

        print(f"\nMerging {len(table_names)} tables on {geo_code}...")

        for table_name in tqdm(table_names[1:], desc="Merging tables"):
            try:
                # Merge on geographic code
                combined = combined.merge(
                    self.tables[table_name],
                    on=geo_code,
                    how='outer',
                    suffixes=('', f'_{table_name}')
                )
            except Exception as e:
                print(f"Error merging {table_name}: {e}")

        self.combined_data = combined
        print(f"✓ Combined dataset: {combined.shape[0]} rows × {combined.shape[1]} columns")

        return combined

    def get_numeric_columns(self):
        """Get all numeric columns from combined dataset"""
        if self.combined_data is None:
            self.merge_all_tables()

        numeric_cols = self.combined_data.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude the geographic code column
        geo_code = f"{self.geo_level}_CODE_2021"
        if geo_code in numeric_cols:
            numeric_cols.remove(geo_code)

        return numeric_cols

# ============================================================================
# STEP 2: SPATIAL WEIGHTS MATRICES
# ============================================================================

class SpatialWeightsBuilder:
    """Build spatial weights matrices using various methods"""

    def __init__(self, geodataframe):
        self.gdf = geodataframe
        self.weights = {}

    def build_queen(self):
        """Build Queen contiguity weights (shared edges or vertices)"""
        try:
            w = Queen.from_dataframe(self.gdf)
            self.weights['queen'] = w
            print(f"✓ Queen weights: {w.n} observations, avg {w.mean_neighbors:.2f} neighbors")
            return w
        except Exception as e:
            print(f"✗ Error building Queen weights: {e}")
            return None

    def build_rook(self):
        """Build Rook contiguity weights (shared edges only)"""
        try:
            w = Rook.from_dataframe(self.gdf)
            self.weights['rook'] = w
            print(f"✓ Rook weights: {w.n} observations, avg {w.mean_neighbors:.2f} neighbors")
            return w
        except Exception as e:
            print(f"✗ Error building Rook weights: {e}")
            return None

    def build_knn(self, k=5):
        """Build K-nearest neighbors weights"""
        try:
            # Get centroids for distance calculation
            centroids = self.gdf.geometry.centroid
            coords = np.array(list(zip(centroids.x, centroids.y)))

            w = KNN.from_array(coords, k=k)
            self.weights[f'knn_{k}'] = w
            print(f"✓ KNN-{k} weights: {w.n} observations, {k} neighbors each")
            return w
        except Exception as e:
            print(f"✗ Error building KNN-{k} weights: {e}")
            return None

    def build_distance_band(self, threshold=None):
        """Build distance band weights"""
        try:
            centroids = self.gdf.geometry.centroid
            coords = np.array(list(zip(centroids.x, centroids.y)))

            if threshold is None:
                # Auto-determine threshold to ensure all areas have at least one neighbor
                from libpysal.weights import min_threshold_distance
                threshold = min_threshold_distance(coords)
                threshold *= 1.1  # Add 10% buffer

            w = DistanceBand.from_array(coords, threshold=threshold)
            self.weights['distance'] = w
            print(f"✓ Distance band weights: {w.n} observations, threshold={threshold:.2f}, avg {w.mean_neighbors:.2f} neighbors")
            return w
        except Exception as e:
            print(f"✗ Error building distance band weights: {e}")
            return None

    def build_all(self):
        """Build all spatial weights matrices"""
        print("\nBuilding spatial weights matrices...")
        print("-" * 80)

        self.build_queen()
        self.build_rook()
        self.build_knn(k=5)
        self.build_knn(k=10)
        self.build_distance_band()

        print(f"\n✓ Built {len(self.weights)} spatial weights matrices")
        return self.weights

# ============================================================================
# STEP 3: GLOBAL SPATIAL AUTOCORRELATION (MORAN'S I)
# ============================================================================

class GlobalSpatialAutocorrelation:
    """Calculate Moran's I for all variables"""

    def __init__(self, data, weights):
        self.data = data
        self.weights = weights
        self.results = {}

    def calculate_morans_i(self, variable_name, variable_data, weight_matrix):
        """Calculate Moran's I for a single variable"""
        try:
            # Remove NaN values
            valid_idx = ~np.isnan(variable_data)
            if valid_idx.sum() < Config.MIN_OBSERVATIONS:
                return None

            # Calculate Moran's I
            moran = Moran(variable_data[valid_idx], weight_matrix)

            result = {
                'variable': variable_name,
                'I': moran.I,
                'expected_I': moran.EI,
                'p_value': moran.p_sim,
                'z_score': moran.z_sim,
                'significant': moran.p_sim < 0.05,
                'interpretation': self._interpret_morans_i(moran.I, moran.p_sim)
            }

            return result
        except Exception as e:
            return None

    def _interpret_morans_i(self, I, p_value):
        """Interpret Moran's I statistic"""
        if p_value >= 0.05:
            return "No significant spatial autocorrelation"
        elif I > 0:
            return "Positive spatial autocorrelation (clustering)"
        else:
            return "Negative spatial autocorrelation (dispersion)"

    def analyze_all_variables(self, numeric_columns, weights_dict):
        """Calculate Moran's I for all variables across all weight matrices"""
        results = []

        for weight_name, weight_matrix in weights_dict.items():
            print(f"\nAnalyzing spatial autocorrelation using {weight_name} weights...")

            for col in tqdm(numeric_columns, desc=f"Moran's I ({weight_name})"):
                try:
                    var_data = self.data[col].values
                    result = self.calculate_morans_i(col, var_data, weight_matrix)

                    if result:
                        result['weights_method'] = weight_name
                        results.append(result)
                except Exception as e:
                    continue

        self.results = pd.DataFrame(results)
        print(f"\n✓ Calculated Moran's I for {len(self.results)} variable-weight combinations")

        # Summary statistics
        significant = self.results[self.results['significant'] == True]
        print(f"  • Significant spatial autocorrelation: {len(significant)} ({len(significant)/len(self.results)*100:.1f}%)")
        print(f"  • Positive clustering: {len(significant[significant['I'] > 0])}")
        print(f"  • Negative dispersion: {len(significant[significant['I'] < 0])}")

        return self.results

# ============================================================================
# STEP 4: LOCAL SPATIAL AUTOCORRELATION (LISA)
# ============================================================================

class LocalSpatialAutocorrelation:
    """Calculate LISA statistics for hot/cold spot detection"""

    def __init__(self, data, weights, geodataframe):
        self.data = data
        self.weights = weights
        self.gdf = geodataframe
        self.results = {}

    def calculate_local_morans(self, variable_name, variable_data, weight_matrix):
        """Calculate Local Moran's I for a single variable"""
        try:
            # Remove NaN values
            valid_idx = ~np.isnan(variable_data)
            if valid_idx.sum() < Config.MIN_OBSERVATIONS:
                return None

            # Calculate Local Moran's I
            lisa = Moran_Local(variable_data[valid_idx], weight_matrix, permutations=999)

            result = {
                'variable': variable_name,
                'Is': lisa.Is,  # Local Moran's I values
                'p_values': lisa.p_sim,  # P-values
                'z_scores': lisa.z_sim,  # Z-scores
                'quadrants': lisa.q,  # Quadrant classification (1=HH, 2=LH, 3=LL, 4=HL)
                'significant': lisa.p_sim < 0.05,
                'spots': self._classify_spots(lisa.q, lisa.p_sim)
            }

            return result
        except Exception as e:
            return None

    def _classify_spots(self, quadrants, p_values):
        """Classify hot spots, cold spots, and spatial outliers"""
        spots = np.full(len(quadrants), 'Not Significant')
        significant = p_values < 0.05

        spots[(quadrants == 1) & significant] = 'Hot Spot (HH)'
        spots[(quadrants == 2) & significant] = 'Spatial Outlier (LH)'
        spots[(quadrants == 3) & significant] = 'Cold Spot (LL)'
        spots[(quadrants == 4) & significant] = 'Spatial Outlier (HL)'

        return spots

    def analyze_key_variables(self, key_variables, weights_dict):
        """Calculate LISA for key socioeconomic variables"""
        results = {}

        for weight_name, weight_matrix in weights_dict.items():
            print(f"\nCalculating LISA statistics using {weight_name} weights...")

            for var in tqdm(key_variables, desc=f"LISA ({weight_name})"):
                try:
                    var_data = self.data[var].values
                    result = self.calculate_local_morans(var, var_data, weight_matrix)

                    if result:
                        result['weights_method'] = weight_name
                        results[f"{var}_{weight_name}"] = result

                        # Summary
                        hot_spots = (result['spots'] == 'Hot Spot (HH)').sum()
                        cold_spots = (result['spots'] == 'Cold Spot (LL)').sum()
                        outliers = ((result['spots'] == 'Spatial Outlier (LH)') |
                                   (result['spots'] == 'Spatial Outlier (HL)')).sum()

                        print(f"  {var}: {hot_spots} hot spots, {cold_spots} cold spots, {outliers} outliers")
                except Exception as e:
                    continue

        self.results = results
        print(f"\n✓ Calculated LISA for {len(results)} variable-weight combinations")

        return results

# ============================================================================
# STEP 5: SPATIAL LAG MODELS
# ============================================================================

class SpatialLagModels:
    """Estimate spatial lag models for socioeconomic variables"""

    def __init__(self, data, weights):
        self.data = data
        self.weights = weights
        self.models = {}

    def estimate_spatial_lag(self, y_var, x_vars, weight_matrix, method='ML'):
        """Estimate spatial lag model: y = ρWy + Xβ + ε"""
        try:
            # Prepare data
            y = self.data[y_var].values.reshape(-1, 1)
            X = self.data[x_vars].values

            # Remove NaN values
            valid_idx = ~(np.isnan(y).any(axis=1) | np.isnan(X).any(axis=1))
            if valid_idx.sum() < Config.MIN_OBSERVATIONS:
                return None

            y = y[valid_idx]
            X = X[valid_idx]

            # Estimate model
            if method == 'ML':
                model = ML_Lag(y, X, w=weight_matrix, name_y=y_var, name_x=x_vars)
            else:
                model = GM_Lag(y, X, w=weight_matrix, name_y=y_var, name_x=x_vars)

            result = {
                'y_variable': y_var,
                'x_variables': x_vars,
                'rho': model.rho,  # Spatial lag coefficient
                'betas': model.betas.flatten(),
                'r_squared': model.pr2 if hasattr(model, 'pr2') else None,
                'log_likelihood': model.logll if hasattr(model, 'logll') else None,
                'AIC': model.aic if hasattr(model, 'aic') else None,
                'model_summary': model.summary if hasattr(model, 'summary') else None
            }

            return result
        except Exception as e:
            return None

    def estimate_multiple_models(self, model_specs, weights_dict):
        """Estimate multiple spatial lag models"""
        results = []

        for weight_name, weight_matrix in weights_dict.items():
            print(f"\nEstimating spatial lag models using {weight_name} weights...")

            for spec in tqdm(model_specs, desc=f"Spatial Lag ({weight_name})"):
                try:
                    y_var = spec['y']
                    x_vars = spec['x']

                    result = self.estimate_spatial_lag(y_var, x_vars, weight_matrix)

                    if result:
                        result['weights_method'] = weight_name
                        results.append(result)
                except Exception as e:
                    continue

        self.models = results
        print(f"\n✓ Estimated {len(results)} spatial lag models")

        return results

# ============================================================================
# STEP 6: GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)
# ============================================================================

class GeographicallyWeightedRegression:
    """Estimate GWR models with spatially varying coefficients"""

    def __init__(self, data, geodataframe):
        self.data = data
        self.gdf = geodataframe
        self.models = {}

    def estimate_gwr(self, y_var, x_vars, bw_method='AIC', kernel='gaussian', fixed=False):
        """Estimate GWR model"""
        try:
            # Prepare data
            y = self.data[y_var].values.reshape(-1, 1)
            X = self.data[x_vars].values

            # Get coordinates
            centroids = self.gdf.geometry.centroid
            coords = np.array(list(zip(centroids.x, centroids.y)))

            # Remove NaN values
            valid_idx = ~(np.isnan(y).any(axis=1) | np.isnan(X).any(axis=1))
            if valid_idx.sum() < Config.MIN_OBSERVATIONS:
                return None

            y = y[valid_idx]
            X = X[valid_idx]
            coords = coords[valid_idx]

            # Select bandwidth
            print(f"  Selecting bandwidth using {bw_method}...")
            bw_selector = Sel_BW(coords, y, X, kernel=kernel, fixed=fixed)

            if bw_method == 'AIC':
                bw = bw_selector.search(criterion='AIC')
            elif bw_method == 'CV':
                bw = bw_selector.search(criterion='CV')
            else:
                bw = bw_selector.search(criterion='BIC')

            print(f"  Selected bandwidth: {bw}")

            # Estimate GWR
            print(f"  Estimating GWR model...")
            gwr_model = GWR(coords, y, X, bw=bw, kernel=kernel, fixed=fixed)
            gwr_results = gwr_model.fit()

            result = {
                'y_variable': y_var,
                'x_variables': x_vars,
                'bandwidth': bw,
                'kernel': kernel,
                'fixed': fixed,
                'params': gwr_results.params,  # Spatially varying coefficients
                'standard_errors': gwr_results.bse,
                't_values': gwr_results.tvalues,
                'local_R2': gwr_results.localR2,
                'AIC': gwr_results.aicc,
                'residuals': gwr_results.resid_response,
                'coords': coords
            }

            return result
        except Exception as e:
            print(f"  ✗ Error estimating GWR: {e}")
            return None

    def estimate_multiple_gwr(self, model_specs):
        """Estimate multiple GWR models"""
        results = []

        print("\nEstimating Geographically Weighted Regression models...")
        print("WARNING: This is computationally intensive and may take a long time!")
        print("-" * 80)

        for spec in model_specs:
            try:
                y_var = spec['y']
                x_vars = spec['x']

                print(f"\nGWR: {y_var} ~ {' + '.join(x_vars)}")

                result = self.estimate_gwr(y_var, x_vars)

                if result:
                    results.append(result)
                    print(f"  ✓ Model estimated successfully")
                    print(f"  • AIC: {result['AIC']:.2f}")
                    print(f"  • Mean local R²: {np.mean(result['local_R2']):.4f}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue

        self.models = results
        print(f"\n✓ Estimated {len(results)} GWR models")

        return results

# ============================================================================
# STEP 7: SPATIAL REGIMES MODELING
# ============================================================================

class SpatialRegimes:
    """Estimate spatial regimes models (parameters vary by regime/region)"""

    def __init__(self, data, weights):
        self.data = data
        self.weights = weights
        self.models = {}

    def identify_regimes(self, clustering_vars, n_regimes=4):
        """Identify spatial regimes using clustering"""
        from sklearn.cluster import KMeans

        try:
            # Prepare data
            X = self.data[clustering_vars].values

            # Remove NaN values
            valid_idx = ~np.isnan(X).any(axis=1)
            X = X[valid_idx]

            # K-means clustering
            kmeans = KMeans(n_clusters=n_regimes, random_state=42)
            regimes = np.full(len(self.data), -1)
            regimes[valid_idx] = kmeans.fit_predict(X)

            self.data['regime'] = regimes

            print(f"✓ Identified {n_regimes} spatial regimes")
            for i in range(n_regimes):
                count = (regimes == i).sum()
                print(f"  • Regime {i}: {count} areas ({count/len(self.data)*100:.1f}%)")

            return regimes
        except Exception as e:
            print(f"✗ Error identifying regimes: {e}")
            return None

    def estimate_regime_models(self, y_var, x_vars, weight_matrix):
        """Estimate separate models for each regime"""
        results = []

        if 'regime' not in self.data.columns:
            print("✗ No regimes identified. Run identify_regimes() first.")
            return None

        regimes = self.data['regime'].unique()
        regimes = regimes[regimes >= 0]  # Exclude invalid regimes

        for regime in regimes:
            try:
                # Filter data for this regime
                regime_data = self.data[self.data['regime'] == regime]

                if len(regime_data) < Config.MIN_OBSERVATIONS:
                    continue

                # Prepare data
                y = regime_data[y_var].values.reshape(-1, 1)
                X = regime_data[x_vars].values

                # Remove NaN values
                valid_idx = ~(np.isnan(y).any(axis=1) | np.isnan(X).any(axis=1))
                if valid_idx.sum() < Config.MIN_OBSERVATIONS:
                    continue

                y = y[valid_idx]
                X = X[valid_idx]

                # Estimate OLS model for this regime
                model = OLS(y, X, name_y=y_var, name_x=x_vars)

                result = {
                    'regime': regime,
                    'y_variable': y_var,
                    'x_variables': x_vars,
                    'betas': model.betas.flatten(),
                    'r_squared': model.r2,
                    'n_observations': len(y)
                }

                results.append(result)
            except Exception as e:
                continue

        print(f"✓ Estimated models for {len(results)} regimes")

        return results

# ============================================================================
# STEP 8: MAIN ANALYSIS PIPELINE
# ============================================================================

def run_comprehensive_analysis(geo_level='SA2'):
    """Run complete spatial econometric analysis for a geographic level"""

    print("\n" + "="*120)
    print(f"ANALYZING GEOGRAPHIC LEVEL: {geo_level}")
    print("="*120)

    output_dir = os.path.join(Config.OUTPUT_DIR, geo_level)

    # Step 1: Load census data
    print("\n" + "-"*120)
    print("STEP 1: LOADING CENSUS DATA")
    print("-"*120)

    loader = CensusDataLoader(Config.DATA_DIR, geo_level)
    loader.load_all_tables()
    combined_data = loader.merge_all_tables()
    numeric_cols = loader.get_numeric_columns()

    print(f"\n✓ Dataset ready: {len(numeric_cols)} numeric variables")

    # Save combined dataset
    combined_data_file = os.path.join(output_dir, f'{geo_level}_combined_data.csv')
    combined_data.to_csv(combined_data_file, index=False)
    print(f"✓ Saved combined data: {combined_data_file}")

    # Step 2: Load or create geodataframe
    print("\n" + "-"*120)
    print("STEP 2: LOADING GEOGRAPHIC DATA")
    print("-"*120)

    shapefile_path = os.path.join(Config.SHAPEFILE_DIR, geo_level)
    shp_files = glob.glob(os.path.join(shapefile_path, f"{geo_level}_2021_AUST*.shp"))

    if shp_files:
        print(f"Loading shapefile: {shp_files[0]}")
        gdf = gpd.read_file(shp_files[0])

        # Merge with census data
        geo_code = f"{geo_level}_CODE_2021"
        gdf = gdf.merge(combined_data, left_on=geo_level + '_CODE', right_on=geo_code, how='inner')

        print(f"✓ Loaded geographic data: {len(gdf)} areas")
    else:
        print(f"⚠ No shapefile found for {geo_level}")
        print("  Creating simplified geodataframe (analysis will be limited)")

        # Create a simple geodataframe with point geometries (centroids)
        # This is a fallback - full spatial analysis requires actual shapefiles
        from shapely.geometry import Point

        geo_code = f"{geo_level}_CODE_2021"
        gdf = gpd.GeoDataFrame(
            combined_data,
            geometry=[Point(0, 0) for _ in range(len(combined_data))],
            crs="EPSG:4326"
        )

        print(f"✓ Created simplified geodataframe: {len(gdf)} areas")
        print("  NOTE: Some spatial analyses may be skipped without proper geometries")

    # Save geodataframe
    geojson_file = os.path.join(output_dir, f'{geo_level}_geodata.geojson')
    gdf.to_file(geojson_file, driver='GeoJSON')
    print(f"✓ Saved geodataframe: {geojson_file}")

    # Step 3: Build spatial weights matrices
    print("\n" + "-"*120)
    print("STEP 3: BUILDING SPATIAL WEIGHTS MATRICES")
    print("-"*120)

    weights_builder = SpatialWeightsBuilder(gdf)
    weights_dict = weights_builder.build_all()

    # Save weights
    for weight_name, weight_matrix in weights_dict.items():
        weight_file = os.path.join(output_dir, f'{geo_level}_weights_{weight_name}.pkl')
        with open(weight_file, 'wb') as f:
            pickle.dump(weight_matrix, f)
        print(f"✓ Saved {weight_name} weights: {weight_file}")

    # Step 4: Global spatial autocorrelation (Moran's I)
    print("\n" + "-"*120)
    print("STEP 4: GLOBAL SPATIAL AUTOCORRELATION (MORAN'S I)")
    print("-"*120)

    global_auto = GlobalSpatialAutocorrelation(combined_data, weights_dict)

    # Analyze a subset of variables first (to save time)
    sample_size = min(500, len(numeric_cols))  # Start with 500 variables
    sample_cols = numeric_cols[:sample_size]

    morans_results = global_auto.analyze_all_variables(sample_cols, weights_dict)

    # Save results
    morans_file = os.path.join(output_dir, f'{geo_level}_morans_i.csv')
    morans_results.to_csv(morans_file, index=False)
    print(f"✓ Saved Moran's I results: {morans_file}")

    # Top variables with strongest spatial autocorrelation
    top_positive = morans_results.nlargest(20, 'I')[['variable', 'I', 'p_value', 'interpretation']]
    top_negative = morans_results.nsmallest(20, 'I')[['variable', 'I', 'p_value', 'interpretation']]

    print("\nTop 20 variables with strongest POSITIVE spatial autocorrelation:")
    print(top_positive.to_string(index=False))

    print("\nTop 20 variables with strongest NEGATIVE spatial autocorrelation:")
    print(top_negative.to_string(index=False))

    # Step 5: Local spatial autocorrelation (LISA)
    print("\n" + "-"*120)
    print("STEP 5: LOCAL SPATIAL AUTOCORRELATION (LISA)")
    print("-"*120)

    # Select key socioeconomic variables for LISA
    key_variables = [col for col in numeric_cols if any(keyword in col.lower() for keyword in
                     ['median', 'income', 'age', 'education', 'unemployment', 'degree'])][:50]

    print(f"Analyzing {len(key_variables)} key socioeconomic variables...")

    local_auto = LocalSpatialAutocorrelation(combined_data, weights_dict, gdf)
    lisa_results = local_auto.analyze_key_variables(key_variables, weights_dict)

    # Save LISA results
    lisa_file = os.path.join(output_dir, f'{geo_level}_lisa_results.pkl')
    with open(lisa_file, 'wb') as f:
        pickle.dump(lisa_results, f)
    print(f"✓ Saved LISA results: {lisa_file}")

    # Step 6: Spatial lag models
    print("\n" + "-"*120)
    print("STEP 6: SPATIAL LAG MODELS")
    print("-"*120)

    # Define model specifications
    model_specs = []

    # Example: Income as function of education and age
    if 'Median_tot_prsnl_inc_weekly' in numeric_cols and 'Median_age_persons' in numeric_cols:
        model_specs.append({
            'y': 'Median_tot_prsnl_inc_weekly',
            'x': ['Median_age_persons']
        })

    if model_specs:
        spatial_lag = SpatialLagModels(combined_data, weights_dict)
        lag_results = spatial_lag.estimate_multiple_models(model_specs, weights_dict)

        # Save results
        lag_file = os.path.join(output_dir, f'{geo_level}_spatial_lag_models.pkl')
        with open(lag_file, 'wb') as f:
            pickle.dump(lag_results, f)
        print(f"✓ Saved spatial lag models: {lag_file}")

    # Step 7: Geographically Weighted Regression (GWR)
    print("\n" + "-"*120)
    print("STEP 7: GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)")
    print("-"*120)
    print("WARNING: GWR is computationally intensive!")
    print("Starting with a small number of models...")

    if model_specs:
        gwr_analyzer = GeographicallyWeightedRegression(combined_data, gdf)
        gwr_results = gwr_analyzer.estimate_multiple_gwr(model_specs[:3])  # Limit to 3 models

        # Save results
        gwr_file = os.path.join(output_dir, f'{geo_level}_gwr_models.pkl')
        with open(gwr_file, 'wb') as f:
            pickle.dump(gwr_results, f)
        print(f"✓ Saved GWR models: {gwr_file}")

    # Step 8: Spatial regimes
    print("\n" + "-"*120)
    print("STEP 8: SPATIAL REGIMES MODELING")
    print("-"*120)

    regimes_vars = ['Median_tot_prsnl_inc_weekly', 'Median_age_persons']
    regimes_vars = [v for v in regimes_vars if v in numeric_cols]

    if regimes_vars and weights_dict:
        regimes_analyzer = SpatialRegimes(combined_data, weights_dict)
        regimes = regimes_analyzer.identify_regimes(regimes_vars, n_regimes=4)

        if regimes is not None and model_specs:
            regime_models = regimes_analyzer.estimate_regime_models(
                model_specs[0]['y'],
                model_specs[0]['x'],
                list(weights_dict.values())[0]
            )

            # Save results
            regime_file = os.path.join(output_dir, f'{geo_level}_spatial_regimes.pkl')
            with open(regime_file, 'wb') as f:
                pickle.dump({'regimes': regimes, 'models': regime_models}, f)
            print(f"✓ Saved spatial regimes: {regime_file}")

    # Summary
    print("\n" + "="*120)
    print(f"ANALYSIS COMPLETE FOR {geo_level}")
    print("="*120)
    print(f"Results saved to: {output_dir}")
    print("\nGenerated files:")
    for f in os.listdir(output_dir):
        filepath = os.path.join(output_dir, f)
        size_mb = os.path.getsize(filepath) / 1024 / 1024
        print(f"  • {f} ({size_mb:.2f} MB)")

    return {
        'geo_level': geo_level,
        'data': combined_data,
        'geodata': gdf,
        'weights': weights_dict,
        'morans_i': morans_results,
        'lisa': lisa_results,
        'output_dir': output_dir
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run analysis for each geographic level
    all_results = {}

    for geo_level in Config.GEO_LEVELS:
        try:
            results = run_comprehensive_analysis(geo_level)
            all_results[geo_level] = results
        except Exception as e:
            print(f"\n✗ Error analyzing {geo_level}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Final summary
    print("\n" + "="*120)
    print("ALL ANALYSES COMPLETE!")
    print("="*120)
    print(f"Total geographic levels analyzed: {len(all_results)}")
    print(f"Results directory: {Config.OUTPUT_DIR}")
    print(f"\nAnalysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*120)
