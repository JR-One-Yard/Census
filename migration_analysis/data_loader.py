"""
Data loading and preprocessing module for Census data
Handles efficient loading of large CSV files with caching
"""

import pandas as pd
import numpy as np
import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from tqdm import tqdm
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CensusDataLoader:
    """Efficient loader for Australian Census 2021 data"""

    def __init__(self, geo_level: str = 'SA1'):
        self.geo_level = geo_level
        self.data_path = os.path.join(config.DATA_DIR, geo_level, 'AUS')
        self.cache_path = os.path.join(config.CACHE_DIR, geo_level)
        os.makedirs(self.cache_path, exist_ok=True)

        logger.info(f"Initialized CensusDataLoader for {geo_level}")
        logger.info(f"Data path: {self.data_path}")

    def _get_cache_filename(self, table_id: str) -> str:
        """Generate cache filename for a table"""
        return os.path.join(self.cache_path, f"{table_id}_cached.pkl")

    def _is_cached(self, table_id: str) -> bool:
        """Check if table data is cached"""
        cache_file = self._get_cache_filename(table_id)
        return os.path.exists(cache_file)

    def _save_cache(self, table_id: str, data: pd.DataFrame):
        """Save DataFrame to cache"""
        cache_file = self._get_cache_filename(table_id)
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"Cached {table_id}: {len(data)} rows")

    def _load_cache(self, table_id: str) -> pd.DataFrame:
        """Load DataFrame from cache"""
        cache_file = self._get_cache_filename(table_id)
        with open(cache_file, 'rb') as f:
            data = pickle.load(f)
        logger.info(f"Loaded {table_id} from cache: {len(data)} rows")
        return data

    def load_table(self, table_id: str, use_cache: bool = True) -> pd.DataFrame:
        """
        Load a single census table

        Args:
            table_id: Table identifier (e.g., 'G09A', 'G12A')
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with census data
        """
        # Check cache first
        if use_cache and self._is_cached(table_id):
            return self._load_cache(table_id)

        # Find the CSV file
        csv_pattern = f"2021Census_{table_id}_AUST_{self.geo_level}.csv"
        csv_path = os.path.join(self.data_path, csv_pattern)

        if not os.path.exists(csv_path):
            logger.error(f"File not found: {csv_path}")
            raise FileNotFoundError(f"Census table {table_id} not found")

        logger.info(f"Loading {table_id} from CSV...")
        df = pd.read_csv(csv_path, low_memory=False)

        # Replace '..' with NaN for missing/confidential data
        df = df.replace('..', np.nan)

        # Convert numeric columns (skip first column which is geo code)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        # Cache the data
        if use_cache:
            self._save_cache(table_id, df)

        logger.info(f"Loaded {table_id}: {len(df)} rows, {len(df.columns)} columns")
        return df

    def load_table_group(self, table_ids: List[str], use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Load multiple census tables

        Args:
            table_ids: List of table identifiers
            use_cache: Whether to use cached data

        Returns:
            Dictionary mapping table_id to DataFrame
        """
        tables = {}
        for table_id in tqdm(table_ids, desc=f"Loading {self.geo_level} tables"):
            try:
                tables[table_id] = self.load_table(table_id, use_cache=use_cache)
            except Exception as e:
                logger.error(f"Failed to load {table_id}: {e}")

        return tables

    def load_birthplace_data(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load and combine all birthplace tables (G09A-G09H)

        Returns:
            Combined DataFrame with birthplace data
        """
        logger.info("Loading birthplace data...")
        tables = self.load_table_group(config.TABLES['birthplace'], use_cache=use_cache)

        # Combine all birthplace tables
        # All tables should have the same SA1 codes as first column
        combined = None
        for table_id, df in tables.items():
            if combined is None:
                combined = df
            else:
                # Merge on SA1 code
                geo_col = df.columns[0]
                combined = combined.merge(df, on=geo_col, how='outer')

        logger.info(f"Combined birthplace data: {len(combined)} areas, {len(combined.columns)} columns")
        return combined

    def load_year_arrival_data(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load and combine year of arrival tables (G12A, G12B)

        Returns:
            Combined DataFrame with year of arrival data
        """
        logger.info("Loading year of arrival data...")
        tables = self.load_table_group(config.TABLES['year_arrival'], use_cache=use_cache)

        combined = None
        for table_id, df in tables.items():
            if combined is None:
                combined = df
            else:
                geo_col = df.columns[0]
                combined = combined.merge(df, on=geo_col, how='outer')

        logger.info(f"Combined year of arrival data: {len(combined)} areas, {len(combined.columns)} columns")
        return combined

    def load_language_data(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load and combine language spoken tables (G13A-G13E)

        Returns:
            Combined DataFrame with language data
        """
        logger.info("Loading language data...")
        tables = self.load_table_group(config.TABLES['language'], use_cache=use_cache)

        combined = None
        for table_id, df in tables.items():
            if combined is None:
                combined = df
            else:
                geo_col = df.columns[0]
                combined = combined.merge(df, on=geo_col, how='outer')

        logger.info(f"Combined language data: {len(combined)} areas, {len(combined.columns)} columns")
        return combined

    def load_housing_income_data(self, use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Load housing and income tables

        Returns:
            Dictionary of DataFrames with housing/income data
        """
        logger.info("Loading housing and income data...")
        tables = self.load_table_group(config.TABLES['housing_income'], use_cache=use_cache)
        return tables

    def load_dwelling_data(self, use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Load dwelling type and tenure tables

        Returns:
            Dictionary of DataFrames with dwelling data
        """
        logger.info("Loading dwelling data...")
        tables = self.load_table_group(config.TABLES['dwelling'], use_cache=use_cache)
        return tables

    def load_all_data(self, use_cache: bool = True) -> Dict[str, any]:
        """
        Load all required data for migration analysis

        Returns:
            Dictionary containing all loaded datasets
        """
        logger.info("=" * 80)
        logger.info("LOADING ALL CENSUS DATA FOR MIGRATION ANALYSIS")
        logger.info("=" * 80)

        data = {
            'birthplace': self.load_birthplace_data(use_cache=use_cache),
            'year_arrival': self.load_year_arrival_data(use_cache=use_cache),
            'language': self.load_language_data(use_cache=use_cache),
            'housing_income': self.load_housing_income_data(use_cache=use_cache),
            'dwelling': self.load_dwelling_data(use_cache=use_cache),
        }

        logger.info("=" * 80)
        logger.info("DATA LOADING COMPLETE")
        logger.info("=" * 80)

        return data


def get_country_columns(df: pd.DataFrame, country: str) -> List[str]:
    """
    Get all columns related to a specific country

    Args:
        df: DataFrame with birthplace/demographic data
        country: Country name (e.g., 'China', 'India')

    Returns:
        List of column names
    """
    # Match columns containing the country name
    # Handle variations like 'M_China_', 'F_China_', etc.
    cols = [col for col in df.columns if country in col]
    return cols


def aggregate_country_total(df: pd.DataFrame, country: str) -> pd.Series:
    """
    Calculate total population from a country for each geographic area

    Args:
        df: DataFrame with birthplace data
        country: Country name

    Returns:
        Series with total population by area
    """
    cols = get_country_columns(df, country)
    if not cols:
        return pd.Series(0, index=df.index)

    # Sum across all columns for this country (handles M/F, age groups, etc.)
    return df[cols].sum(axis=1)


def calculate_concentration_ratio(df: pd.DataFrame, country: str, total_pop_col: str) -> pd.Series:
    """
    Calculate concentration ratio for a country in each area

    Args:
        df: DataFrame with birthplace data
        country: Country name
        total_pop_col: Column name containing total population

    Returns:
        Series with concentration ratios (0-1)
    """
    country_pop = aggregate_country_total(df, country)
    total_pop = df[total_pop_col]

    # Avoid division by zero
    ratio = country_pop / total_pop.replace(0, np.nan)
    return ratio.fillna(0)
