"""
Configuration file for National Migration Pattern & Property Demand Flow Analysis
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "2021_GCP_all_for_AUS_short-header", "2021 Census GCP All Geographies for AUS")
OUTPUT_DIR = os.path.join(BASE_DIR, "migration_analysis", "outputs")
CACHE_DIR = os.path.join(BASE_DIR, "migration_analysis", "cache")

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Geographic levels to analyze
GEO_LEVELS = {
    'SA1': 'SA1',      # Finest granularity - ~61,844 areas
    'SA2': 'SA2',      # Suburbs and communities
    'SA3': 'SA3',      # Regional areas
    'SA4': 'SA4',      # Labour markets
    'LGA': 'LGA',      # Local Government Areas
    'POA': 'POA',      # Postcodes
    'STE': 'STE',      # States and Territories
}

# Primary geographic level for detailed analysis
PRIMARY_GEO = 'SA1'

# Census tables to load
TABLES = {
    # Birthplace data (by age and sex for major countries)
    'birthplace': [
        'G09A', 'G09B', 'G09C', 'G09D', 'G09E', 'G09F', 'G09G', 'G09H'
    ],

    # Year of arrival
    'year_arrival': [
        'G12A', 'G12B'
    ],

    # Languages spoken (indicator of cultural communities)
    'language': [
        'G13A', 'G13B', 'G13C', 'G13D', 'G13E'
    ],

    # Housing and income
    'housing_income': [
        'G02',   # Median incomes and housing costs
        'G32',   # Family income
        'G33',   # Household income
        'G40',   # Personal income
    ],

    # Dwelling types and tenure
    'dwelling': [
        'G30', 'G31', 'G34', 'G35', 'G36', 'G37'
    ],
}

# Countries/regions of interest for detailed analysis
COUNTRIES_OF_INTEREST = [
    'China', 'India', 'England', 'Philippines', 'Vietnam', 'Italy',
    'New_Zealand', 'Greece', 'Germany', 'South_Africa', 'Malaysia',
    'Lebanon', 'Sri_Lanka', 'Hong_Kong', 'Indonesia', 'Thailand',
    'Korea', 'Japan', 'Afghanistan', 'Iran', 'Iraq', 'Pakistan',
    'Bangladesh', 'Nepal', 'Myanmar', 'Singapore', 'Cambodia',
    'Sudan', 'South_Sudan', 'Somalia', 'Ethiopia', 'Egypt',
    'Croatia', 'Serbia', 'Bosnia', 'Macedonia', 'Poland', 'Russia',
    'Ukraine', 'Turkey', 'Brazil', 'Chile', 'Argentina', 'Colombia'
]

# Thresholds for identifying cultural clusters
CLUSTER_THRESHOLDS = {
    'min_population': 50,           # Minimum population from a country in an SA1 to be considered
    'concentration_ratio': 0.1,      # Minimum 10% of area population from same country
    'anchor_point_min': 200,         # Minimum population for "anchor point" designation
    'anchor_concentration': 0.2,     # Minimum 20% concentration for anchor point
}

# Income brackets for affordability analysis (weekly household income)
INCOME_BRACKETS = {
    'very_low': (0, 649),
    'low': (650, 1249),
    'moderate': (1250, 1999),
    'high': (2000, 2999),
    'very_high': (3000, 10000),
}

# Housing tenure types
TENURE_TYPES = [
    'owned_outright',
    'owned_with_mortgage',
    'rented',
    'social_housing',
    'other'
]

# Analysis parameters
ANALYSIS_PARAMS = {
    'min_data_quality_threshold': 0.7,  # Minimum data completeness
    'growth_trajectory_years': 5,         # Years to project growth
    'confidence_interval': 0.95,          # Statistical confidence level
    'spatial_radius_km': 5,               # Radius for spatial clustering analysis
}

# Visualization settings
VIZ_SETTINGS = {
    'figure_size': (16, 10),
    'dpi': 300,
    'color_palette': 'viridis',
    'map_style': 'darkgrid',
}
