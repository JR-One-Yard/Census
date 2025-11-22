"""
Core migration analysis module
Identifies cultural clusters, anchor points, and migration patterns
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import config
from data_loader import CensusDataLoader, aggregate_country_total, get_country_columns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationAnalyzer:
    """
    Analyzes migration patterns and identifies cultural communities
    """

    def __init__(self, geo_level: str = 'SA1'):
        self.geo_level = geo_level
        self.loader = CensusDataLoader(geo_level=geo_level)
        self.data = None
        self.results = {}

    def load_data(self, use_cache: bool = True):
        """Load all required census data"""
        self.data = self.loader.load_all_data(use_cache=use_cache)
        logger.info("Data loaded successfully")

    def identify_cultural_clusters(self, country: str,
                                   min_population: int = None,
                                   min_concentration: float = None) -> pd.DataFrame:
        """
        Identify areas with significant populations from a specific country

        Args:
            country: Country of birth to analyze
            min_population: Minimum population threshold
            min_concentration: Minimum concentration ratio (0-1)

        Returns:
            DataFrame with identified clusters
        """
        if min_population is None:
            min_population = config.CLUSTER_THRESHOLDS['min_population']
        if min_concentration is None:
            min_concentration = config.CLUSTER_THRESHOLDS['concentration_ratio']

        logger.info(f"Identifying {country} clusters (min_pop={min_population}, min_conc={min_concentration})")

        birthplace_df = self.data['birthplace']
        geo_col = birthplace_df.columns[0]

        # Calculate country-specific population
        country_pop = aggregate_country_total(birthplace_df, country)

        # Get total population (sum all birthplace columns for males and females)
        # Get all columns that end with '_Tot' to get totals
        total_cols = [col for col in birthplace_df.columns if col.endswith('_Tot')]
        if total_cols:
            # Sum male and female totals
            male_total_cols = [col for col in total_cols if col.startswith('M_')]
            female_total_cols = [col for col in total_cols if col.startswith('F_')]

            if male_total_cols and female_total_cols:
                total_pop = birthplace_df[male_total_cols].sum(axis=1) + birthplace_df[female_total_cols].sum(axis=1)
            else:
                # Fallback: use first total column found
                total_pop = birthplace_df[total_cols[0]]
        else:
            # Estimate total from all numeric columns
            numeric_cols = birthplace_df.select_dtypes(include=[np.number]).columns
            total_pop = birthplace_df[numeric_cols].sum(axis=1)

        # Calculate concentration ratio
        concentration = country_pop / total_pop.replace(0, np.nan)
        concentration = concentration.fillna(0)

        # Filter based on thresholds
        mask = (country_pop >= min_population) & (concentration >= min_concentration)

        # Create results DataFrame
        results = pd.DataFrame({
            geo_col: birthplace_df[geo_col],
            f'{country}_population': country_pop,
            'total_population': total_pop,
            'concentration_ratio': concentration,
            'is_cluster': mask
        })

        clusters = results[results['is_cluster']].copy()
        clusters = clusters.sort_values(f'{country}_population', ascending=False)

        logger.info(f"Found {len(clusters)} {country} clusters")
        return clusters

    def identify_anchor_points(self, country: str) -> pd.DataFrame:
        """
        Identify "anchor points" - areas with very high concentration of specific community

        Args:
            country: Country of birth to analyze

        Returns:
            DataFrame with anchor points
        """
        min_pop = config.CLUSTER_THRESHOLDS['anchor_point_min']
        min_conc = config.CLUSTER_THRESHOLDS['anchor_concentration']

        logger.info(f"Identifying {country} anchor points")

        anchor_points = self.identify_cultural_clusters(
            country=country,
            min_population=min_pop,
            min_concentration=min_conc
        )

        anchor_points['anchor_strength'] = (
            anchor_points['concentration_ratio'] *
            np.log1p(anchor_points[f'{country}_population'])
        )

        anchor_points = anchor_points.sort_values('anchor_strength', ascending=False)

        logger.info(f"Found {len(anchor_points)} {country} anchor points")
        return anchor_points

    def analyze_all_countries(self) -> Dict[str, pd.DataFrame]:
        """
        Analyze clusters and anchor points for all countries of interest

        Returns:
            Dictionary mapping country to cluster/anchor data
        """
        logger.info("=" * 80)
        logger.info("ANALYZING ALL COUNTRIES")
        logger.info("=" * 80)

        results = {}

        for country in config.COUNTRIES_OF_INTEREST:
            try:
                logger.info(f"Analyzing {country}...")

                # Get clusters
                clusters = self.identify_cultural_clusters(country)

                # Get anchor points
                anchors = self.identify_anchor_points(country)

                results[country] = {
                    'clusters': clusters,
                    'anchor_points': anchors,
                    'total_clusters': len(clusters),
                    'total_anchors': len(anchors),
                    'total_population': clusters[f'{country}_population'].sum() if len(clusters) > 0 else 0
                }

            except Exception as e:
                logger.error(f"Error analyzing {country}: {e}")
                continue

        logger.info("=" * 80)
        logger.info("COUNTRY ANALYSIS COMPLETE")
        logger.info("=" * 80)

        self.results['country_analysis'] = results
        return results

    def analyze_migration_timing(self, country: str) -> pd.DataFrame:
        """
        Analyze year of arrival patterns for a specific country

        Args:
            country: Country to analyze

        Returns:
            DataFrame with arrival timing analysis
        """
        logger.info(f"Analyzing migration timing for {country}")

        arrival_df = self.data['year_arrival']
        geo_col = arrival_df.columns[0]

        # Get columns related to this country and year of arrival
        # G12 tables contain year of arrival by country
        country_arrival_cols = [col for col in arrival_df.columns if country in col]

        if not country_arrival_cols:
            logger.warning(f"No arrival data found for {country}")
            return pd.DataFrame()

        # Aggregate by time period
        # Column names typically include year ranges like 'Before_1981', '1981_1990', etc.
        results = pd.DataFrame()
        results[geo_col] = arrival_df[geo_col]

        # Sum across all columns for this country
        for col in country_arrival_cols:
            # Try to extract time period from column name
            if 'Before' in col:
                period = 'Before_1981'
            elif '1981' in col or '1980' in col:
                period = '1981_1990'
            elif '1991' in col or '1990' in col:
                period = '1991_2000'
            elif '2001' in col or '2000' in col:
                period = '2001_2010'
            elif '2011' in col or '2010' in col:
                period = '2011_2015'
            elif '2016' in col or '2015' in col:
                period = '2016_2020'
            elif '2021' in col or '2020' in col:
                period = '2021'
            else:
                period = 'Unknown'

            if period not in results.columns:
                results[period] = 0

            results[period] += arrival_df[col].fillna(0)

        return results

    def cross_reference_housing(self, clusters: pd.DataFrame) -> pd.DataFrame:
        """
        Cross-reference cultural clusters with housing affordability data

        Args:
            clusters: DataFrame with identified clusters

        Returns:
            DataFrame with housing metrics added
        """
        logger.info("Cross-referencing with housing data...")

        geo_col = clusters.columns[0]

        # Load housing/income data
        housing_income = self.data['housing_income']

        # Get G02 (median incomes and housing costs)
        g02 = housing_income.get('G02')
        if g02 is None:
            logger.warning("G02 data not available")
            return clusters

        # Merge housing data
        clusters_with_housing = clusters.merge(
            g02[[geo_col, 'Median_rent_weekly', 'Median_mortgage_repay_monthly',
                 'Median_tot_hhd_inc_weekly', 'Average_household_size']],
            on=geo_col,
            how='left'
        )

        # Calculate affordability metrics
        clusters_with_housing['rent_to_income_ratio'] = (
            clusters_with_housing['Median_rent_weekly'] * 52 /
            (clusters_with_housing['Median_tot_hhd_inc_weekly'] * 52)
        )

        clusters_with_housing['mortgage_to_income_ratio'] = (
            clusters_with_housing['Median_mortgage_repay_monthly'] * 12 /
            (clusters_with_housing['Median_tot_hhd_inc_weekly'] * 52)
        )

        # Classify affordability
        def classify_affordability(ratio):
            if pd.isna(ratio):
                return 'Unknown'
            elif ratio < 0.3:
                return 'Affordable'
            elif ratio < 0.4:
                return 'Moderately_Affordable'
            elif ratio < 0.5:
                return 'Expensive'
            else:
                return 'Very_Expensive'

        clusters_with_housing['rent_affordability'] = clusters_with_housing['rent_to_income_ratio'].apply(
            classify_affordability
        )

        clusters_with_housing['mortgage_affordability'] = clusters_with_housing['mortgage_to_income_ratio'].apply(
            classify_affordability
        )

        return clusters_with_housing

    def calculate_growth_trajectories(self, country: str) -> Dict:
        """
        Calculate growth trajectories for a community based on recent arrival patterns

        Args:
            country: Country to analyze

        Returns:
            Dictionary with growth projections
        """
        logger.info(f"Calculating growth trajectory for {country}")

        # Get year of arrival data
        arrival_timing = self.analyze_migration_timing(country)

        if arrival_timing.empty:
            return {}

        # Focus on recent periods (2011-2021)
        recent_periods = ['2011_2015', '2016_2020', '2021']
        recent_cols = [col for col in arrival_timing.columns if col in recent_periods]

        if not recent_cols:
            logger.warning(f"No recent arrival data for {country}")
            return {}

        # Calculate total recent arrivals by area
        geo_col = arrival_timing.columns[0]
        arrival_timing['recent_arrivals'] = arrival_timing[recent_cols].sum(axis=1)

        # Get current population from clusters
        clusters = self.identify_cultural_clusters(country)

        # Merge
        growth_data = clusters.merge(
            arrival_timing[[geo_col, 'recent_arrivals']],
            on=geo_col,
            how='left'
        )

        # Calculate growth rate
        growth_data['growth_rate'] = (
            growth_data['recent_arrivals'] /
            growth_data[f'{country}_population'].replace(0, np.nan)
        )

        # Project future demand
        years_to_project = config.ANALYSIS_PARAMS['growth_trajectory_years']
        growth_data['projected_population'] = (
            growth_data[f'{country}_population'] *
            (1 + growth_data['growth_rate']) ** years_to_project
        )

        growth_data['projected_additional_demand'] = (
            growth_data['projected_population'] - growth_data[f'{country}_population']
        )

        # Sort by projected demand
        growth_data = growth_data.sort_values('projected_additional_demand', ascending=False)

        logger.info(f"Growth trajectory calculated for {len(growth_data)} areas")

        return {
            'data': growth_data,
            'total_current_population': growth_data[f'{country}_population'].sum(),
            'total_projected_population': growth_data['projected_population'].sum(),
            'total_projected_growth': growth_data['projected_additional_demand'].sum(),
        }

    def generate_comprehensive_report(self) -> Dict:
        """
        Generate comprehensive analysis report for all communities

        Returns:
            Dictionary with complete analysis results
        """
        logger.info("=" * 80)
        logger.info("GENERATING COMPREHENSIVE MIGRATION ANALYSIS REPORT")
        logger.info("=" * 80)

        # Analyze all countries
        country_analysis = self.analyze_all_countries()

        # For top countries, do detailed analysis
        top_countries = sorted(
            country_analysis.items(),
            key=lambda x: x[1]['total_population'],
            reverse=True
        )[:10]  # Top 10 countries by population

        detailed_analysis = {}

        for country, data in top_countries:
            logger.info(f"Detailed analysis for {country}...")

            # Get clusters with housing data
            clusters_with_housing = self.cross_reference_housing(data['clusters'])

            # Calculate growth trajectories
            growth = self.calculate_growth_trajectories(country)

            detailed_analysis[country] = {
                'clusters': data['clusters'],
                'anchor_points': data['anchor_points'],
                'clusters_with_housing': clusters_with_housing,
                'growth_projections': growth,
                'summary': {
                    'total_population': data['total_population'],
                    'num_clusters': data['total_clusters'],
                    'num_anchor_points': data['total_anchors'],
                    'projected_growth': growth.get('total_projected_growth', 0) if growth else 0,
                }
            }

        report = {
            'overview': country_analysis,
            'detailed_analysis': detailed_analysis,
            'top_countries': [c for c, _ in top_countries],
            'metadata': {
                'geo_level': self.geo_level,
                'analysis_date': pd.Timestamp.now().isoformat(),
                'parameters': config.CLUSTER_THRESHOLDS,
            }
        }

        self.results['comprehensive_report'] = report

        logger.info("=" * 80)
        logger.info("COMPREHENSIVE REPORT COMPLETE")
        logger.info("=" * 80)

        return report
