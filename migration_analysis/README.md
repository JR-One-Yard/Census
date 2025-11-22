# National Migration Pattern & Property Demand Flow Analysis

**Compute Load: ⭐⭐⭐⭐⭐**

A comprehensive analysis of Australian Census 2021 data to identify migration patterns, cultural clusters, and predict future property demand.

## Overview

This analysis examines birthplace and year of arrival data across all Australian geographic levels to:

- **Map migration flows** to specific SA1 areas (finest granularity)
- **Identify cultural/ethnic community clusters** and expansion patterns
- **Calculate "Cultural Anchor Points"** where specific communities concentrate
- **Cross-reference with housing affordability**, rental vs. ownership, dwelling types
- **Predict future demand** based on community growth trajectories

## Features

### 1. Cultural Cluster Identification
- Identifies areas with significant populations from specific countries
- Calculates concentration ratios and community strength
- Distinguishes between established and emerging communities

### 2. Anchor Point Analysis
- Pinpoints areas with very high concentration of specific communities
- Calculates "anchor strength" based on both concentration and absolute population
- Identifies cultural hubs and community centers

### 3. Migration Timing Analysis
- Analyzes year of arrival patterns by country
- Identifies recent vs. historical migration waves
- Tracks community establishment and growth phases

### 4. Housing Affordability Cross-Reference
- Links cultural clusters with housing metrics
- Calculates rent-to-income and mortgage-to-income ratios
- Classifies areas by affordability for different communities

### 5. Growth Trajectory Modeling
- Projects future population growth for each community
- Identifies areas of emerging demand
- Predicts housing demand hotspots

### 6. Comprehensive Visualizations
- Summary dashboards with key metrics
- Country-specific housing affordability analysis
- Growth projection charts
- Cultural anchor point heatmaps
- Population distribution visualizations

## Project Structure

```
migration_analysis/
├── config.py                 # Configuration and parameters
├── data_loader.py           # Efficient data loading with caching
├── migration_analyzer.py    # Core analysis logic
├── visualizer.py            # Visualization generation
├── report_generator.py      # Text reports and CSV exports
├── main.py                  # Main execution script
├── requirements.txt         # Python dependencies
├── outputs/                 # Generated reports and visualizations
│   ├── *.png               # Visualizations
│   ├── *.csv               # Exported datasets
│   └── *.txt               # Text reports
└── cache/                   # Cached processed data
    └── SA1/                 # Cached SA1 level data
```

## Installation

1. Ensure you have Python 3.8+ installed

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the complete analysis:

```bash
python main.py
```

The analysis will:
1. Load census data (uses caching for efficiency)
2. Analyze migration patterns for 40+ countries
3. Identify clusters and anchor points
4. Cross-reference with housing data
5. Generate growth projections
6. Create comprehensive visualizations
7. Export results to CSV and text reports

## Output Files

### Visualizations
- `summary_dashboard.png` - Overall analysis summary
- `country_distribution.png` - Population by country
- `anchor_points_heatmap.png` - Cultural anchor concentrations
- `housing_affordability_{country}.png` - Housing analysis per country
- `growth_projections_{country}.png` - Growth projections per country

### Reports
- `comprehensive_report.txt` - Full detailed analysis
- `executive_summary.txt` - Key findings and recommendations
- `analysis.log` - Processing log

### Data Exports
- `overview_by_country.csv` - Summary statistics by country
- `clusters_{country}.csv` - Cluster details per country
- `anchor_points_{country}.csv` - Anchor point data per country
- `housing_analysis_{country}.csv` - Housing metrics per country
- `growth_projections_{country}.csv` - Growth forecasts per country

## Configuration

Edit `config.py` to customize:

- **Geographic levels** to analyze (default: SA1)
- **Countries of interest** (default: 40+ major source countries)
- **Cluster thresholds** (minimum population, concentration ratios)
- **Income brackets** for affordability analysis
- **Projection parameters** (years to project, confidence intervals)
- **Visualization settings** (figure size, DPI, color schemes)

## Key Parameters

### Cluster Thresholds
- `min_population`: 50 people (minimum to identify a cluster)
- `concentration_ratio`: 10% (minimum % of area population)
- `anchor_point_min`: 200 people (minimum for anchor designation)
- `anchor_concentration`: 20% (minimum % for anchor point)

### Analysis Parameters
- `growth_trajectory_years`: 5 years projection
- `confidence_interval`: 95% statistical confidence
- `spatial_radius_km`: 5km for spatial clustering

## Data Sources

**Australian Bureau of Statistics (ABS)**
- Dataset: 2021 Census General Community Profile (GCP)
- Release: Second Release (R2) - December 2022
- Size: 3.2 GB, 2,023 CSV files
- Geographic Levels: 17 levels from SA1 to National
- License: Creative Commons

## Performance

- **Data loading**: Uses intelligent caching for 10-100x speedup on subsequent runs
- **Memory efficient**: Processes data in chunks, handles 60,000+ geographic areas
- **Parallel processing**: Analyzes multiple countries concurrently where possible
- **Estimated runtime**:
  - First run (no cache): 30-60 minutes depending on hardware
  - Subsequent runs (with cache): 5-15 minutes

## Insights Generated

### For Property Investors
- Stable anchor points for long-term investment
- High-growth emerging clusters for capital appreciation
- Community-specific demand patterns
- Affordability sweet spots

### For Developers
- Areas with projected population growth
- Community preferences for housing types
- Multi-generational housing demand
- Culturally appropriate design opportunities

### For Urban Planners
- Infrastructure needs for growing communities
- Cultural amenity requirements
- Housing affordability challenges
- Community integration patterns

## Technical Notes

- Handles census data protection (random adjustments for confidentiality)
- Manages missing/suppressed data appropriately
- Uses robust statistical methods for projections
- Validates data quality throughout pipeline

## Future Enhancements

Potential additions:
- Geographic mapping with geopandas/folium
- Time series analysis across multiple census years
- Integration with property price data
- Machine learning models for demand prediction
- Interactive dashboards with Plotly/Dash
- API for real-time queries

## License

Analysis code: MIT License
Census data: Creative Commons (see ABS licensing)

## Contact

For questions or issues, refer to the project repository.

---

**Analysis Date**: Generated from 2021 Australian Census Data
**Last Updated**: 2025
**Version**: 1.0
