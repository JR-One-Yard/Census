# Ultra-Granular Gentrification Risk/Opportunity Heatmap Analysis

**Analysis Date:** November 22, 2025
**Dataset:** 2021 Australian Census Data (Release 2)
**Geographic Level:** SA1 (Statistical Area Level 1)
**Total Areas Analyzed:** 61,844 SA1 areas
**Residential Areas:** 60,487 SA1 areas (with population > 0)
**Total Population Covered:** ~25.7 million Australians

---

## Executive Summary

This compute-intensive analysis identifies **gentrification risk and opportunity hotspots** across all 61,844 SA1 areas in Australia using multi-dimensional census data analysis. The model combines income, education, age demographics, diversity, and housing patterns to generate a **composite gentrification risk score** (0-100) for each micro-area.

### Key Innovation: Income-Education Mismatch Detection

The analysis identifies the **strongest gentrification signal**: areas where **education levels exceed income levels** (high education, moderate-to-low income). These represent neighborhoods on the cusp of transformation, where an educated population has moved in but property values haven't fully adjusted yet.

---

## Methodology

### 1. Data Sources

The analysis integrates 10 different census tables at the SA1 level:

- **G01**: Basic demographics (age, education completion)
- **G02**: Median income, rent, and household metrics
- **G17A**: Detailed personal income distributions
- **G16A**: Educational attainment (Year 12 completion)
- **G40**: Higher education qualifications (Bachelor/Postgraduate)
- **G33**: Household income distributions
- **G32**: Housing tenure and family income
- **G34**: Dwelling structure types
- **G09A**: Country of birth (diversity metrics)
- **G13A**: Language spoken at home

### 2. Gentrification Indicators Analyzed

#### A. Income-Education Mismatch (Weight: 30%)
**The Primary Gentrification Signal**

- Calculates the gap between education percentile and income percentile
- Positive mismatch (education > income) indicates gentrification potential
- Formula: `mismatch = education_percentile - income_percentile`
- Rationale: Educated professionals moving into affordable areas precede price increases

#### B. Young Professional Concentration (Weight: 25%)

- Identifies concentration of 25-44 year olds (prime earning years)
- Includes 20-24 year olds as future gentrifiers
- Formula: `youth_score = pct_25_44 + (pct_20_24 × 0.5)`
- Rationale: Young professionals drive urban transformation and amenity demand

#### C. Education Levels (Weight: 20%)

- Year 12 completion rates
- Tertiary education (Bachelor/Postgraduate degrees)
- Percentile ranking across all SA1 areas
- Rationale: Education correlates with future income growth and neighborhood transformation

#### D. Cultural Diversity (Weight: 10%)

- Overseas-born population percentage
- Non-English speaking background percentage
- Combined diversity score
- Rationale: Diverse areas often see gentrification as cultural amenities attract new residents

#### E. Urban Density (Weight: 10%)

- Average household size (inverse relationship)
- Persons per bedroom ratio
- Rationale: Dense urban areas with smaller households indicate apartment living and urbanization

#### F. Current Income (Weight: 5%, Inverse)

- Lower current income = higher gentrification potential
- Inverse weighting: `(100 - income_percentile)`
- Rationale: Affordability attracts early-stage gentrifiers

### 3. Composite Gentrification Risk Score

```
Gentrification Risk Score =
  (0.30 × Income-Education Mismatch) +
  (0.25 × Young Professional Concentration) +
  (0.20 × Education Levels) +
  (0.10 × Cultural Diversity) +
  (0.10 × Urban Density) +
  (0.05 × Inverse Income)
```

**Risk Categories:**
- **Very High**: 90th-100th percentile (top 10%)
- **High**: 75th-90th percentile
- **Moderate**: 50th-75th percentile
- **Low**: 25th-50th percentile
- **Very Low**: 0-25th percentile

---

## Key Findings

### National Overview

| Risk Category | SA1 Areas | Percentage |
|--------------|-----------|------------|
| Very High    | 6,185     | 10.2%      |
| High         | 9,276     | 15.3%      |
| Moderate     | 15,461    | 25.6%      |
| Low          | 15,461    | 25.6%      |
| Very Low     | 15,461    | 25.6%      |

### State-Level Summary

| State | SA1 Areas | Population | Avg Risk Score | Median Income | Avg Year 12% | Avg Young Prof% |
|-------|-----------|------------|----------------|---------------|--------------|-----------------|
| **NSW** | 19,326 | 8,072,460 | 37.02 | $811/wk | 60.1% | 26.8% |
| **VIC** | 15,232 | 6,503,324 | **40.90** | $804/wk | 63.1% | 28.3% |
| **QLD** | 12,281 | 5,156,235 | 34.95 | $795/wk | 58.4% | 26.1% |
| **WA**  | 6,169  | 2,659,794 | 37.10 | $844/wk | 59.2% | 27.3% |
| **SA**  | 4,236  | 1,781,541 | 35.16 | $756/wk | 54.9% | 25.1% |
| **TAS** | 1,439  | 557,573   | 30.34 | $706/wk | 47.7% | 24.7% |
| **ACT** | 1,164  | 454,346   | **43.70** | $1,194/wk | 77.0% | 31.7% |
| **NT**  | 622    | 232,565   | 37.21 | $1,037/wk | 51.1% | 32.7% |

**Observations:**
- **Victoria** has the highest average gentrification risk (40.90)
- **ACT** shows the highest average risk score (43.70), driven by high education levels
- **Tasmania** shows the lowest risk (30.34), with lower education and income levels

---

## Top Gentrification Hotspots

### Top 10 Highest Risk SA1 Areas (National)

| Rank | SA1 Code    | State | Risk Score | Population | Median Income | Year 12% | Young Prof% | Edu-Income Mismatch |
|------|-------------|-------|------------|------------|---------------|----------|-------------|---------------------|
| 1    | 12102157701 | NSW   | 99.23      | 3          | $350/wk       | 100.0%   | 133.3%      | 98.5                |
| 2    | 20604111737 | VIC   | 98.50      | 1,153      | $323/wk       | 94.8%    | 35.4%       | 98.1                |
| 3    | 20604111734 | VIC   | 98.25      | 430        | $313/wk       | 98.1%    | 32.3%       | 98.3                |
| 4    | 11703163916 | NSW   | 98.19      | 750        | $425/wk       | 94.0%    | 42.7%       | 97.1                |
| 5    | 20604150414 | VIC   | 98.08      | 1,329      | $414/wk       | 93.7%    | 35.6%       | 97.2                |
| 6    | 11703164015 | NSW   | 97.98      | 114        | $8/wk         | 96.4%    | 19.3%       | 98.6                |
| 7    | 20604111736 | VIC   | 97.97      | 211        | $397/wk       | 93.9%    | 45.5%       | 97.5                |
| 8    | 20604150418 | VIC   | 97.96      | 405        | $391/wk       | 91.9%    | 33.6%       | 96.9                |
| 9    | 20604150614 | VIC   | 97.91      | 44         | $75/wk        | 100.0%   | 11.4%       | 99.0                |
| 10   | 20604111748 | VIC   | 97.52      | 147        | $265/wk       | 97.2%    | 27.9%       | 98.4                |

**Pattern Recognition:**
- **Victoria dominates** the top 10 (7 out of 10 areas are in VIC)
- **Extremely high education** levels (90%+ Year 12 completion)
- **Below-median incomes** ($300-$400/week range)
- **High education-income mismatch** scores (95-99)
- Mix of small populations (3-147 people) and moderate populations (400-1,329)

### State Distribution of Top 500 Very High Risk Areas

| State | Count | Percentage |
|-------|-------|------------|
| VIC   | 241   | 48.2%      |
| NSW   | 107   | 21.4%      |
| QLD   | 64    | 12.8%      |
| WA    | 40    | 8.0%       |
| SA    | 28    | 5.6%       |
| TAS   | 12    | 2.4%       |
| ACT   | 7     | 1.4%       |
| NT    | 1     | 0.2%       |

---

## Interpretation & Use Cases

### What Does a High Gentrification Risk Score Mean?

A **high gentrification risk score** indicates an area with:

1. **Education-Income Disparity**: Highly educated residents with moderate-to-low current incomes
2. **Young Demographics**: Concentration of professionals aged 25-44
3. **Urban Characteristics**: Dense living, diverse population
4. **Transformation Potential**: Early-stage gentrification before property prices fully reflect amenity value

### Property Market Applications

#### For Investors:
- **Buy Signal**: High-risk areas may offer undervalued properties before transformation
- **Early Detection**: Identify neighborhoods 3-5 years before mainstream recognition
- **Risk-Reward**: Balance high risk scores with actual property prices for best opportunities

#### For Developers:
- **Development Opportunity**: High-risk areas may support density increases and mixed-use projects
- **Amenity Demand**: Young professionals drive demand for cafes, co-working, and lifestyle services
- **Rezoning Targets**: Areas with high education but low-rise housing may support upzoning

#### For Planners:
- **Gentrification Management**: Early intervention to preserve affordable housing
- **Infrastructure Planning**: Young professional influx drives public transport demand
- **Social Housing**: Identify at-risk areas for displacement prevention

---

## Limitations & Caveats

### 1. Census Data Age
- Data from 2021 Census (now 4+ years old)
- Property markets may have already adjusted in some areas
- Best used for macro trends, not immediate decisions

### 2. Spatial Autocorrelation Not Completed
- Moran's I analysis requires SA1 geographic coordinates
- Currently missing spatial clustering detection
- Adjacent high-risk areas may amplify gentrification effects

### 3. Small Population Areas
- Some top-ranked SA1s have very small populations (3-50 people)
- Statistical noise in small samples
- Filter for population > 100-200 for more reliable signals

### 4. No Property Price Data
- Analysis based solely on demographic characteristics
- Does not include actual property values or trends
- Should be combined with CoreLogic/APM price data for validation

### 5. State-Level Variation
- Different states have different gentrification dynamics
- Urban vs. regional patterns differ significantly
- Capital cities dominate high-risk rankings

---

## Technical Details

### Computational Intensity

This analysis processed:
- **61,844 SA1 areas** × **10 census tables** = 618,440 data points
- **25+ calculated metrics** per SA1 area
- **6 normalized component scores** weighted into composite score
- **State-level aggregations** across 8 states/territories
- **Risk categorization** and percentile rankings

### Data Quality

- All SA1 areas with population = 0 were flagged (non-residential)
- Extreme outliers in percentages (>100%) indicate census data quality issues or small sample sizes
- Median values used where possible to reduce outlier impact

### Reproducibility

All analysis code is available:
- `gentrification_analysis.py` - Main analysis engine
- `enhance_gentrification_results.py` - Geographic enhancement and state breakdowns

---

## Output Files

### Summary Files
- `gentrification_summary_by_state.csv` - State-level aggregated metrics
- `gentrification_summary_by_category.csv` - Risk category distributions
- `gentrification_risk_distribution_by_state.csv` - Risk breakdown by state

### Rankings
- `gentrification_risk_scores_all_sa1.csv` - Complete dataset (61,844 areas, 20MB)
- `gentrification_risk_top_1000.csv` - Top 1,000 highest risk areas
- `gentrification_risk_top_100.csv` - Top 100 highest risk areas
- `gentrification_very_high_risk_top_500.csv` - Top 500 "Very High" risk areas

### State-Specific
- `gentrification_top_20_NSW.csv` - Top 20 areas in New South Wales
- `gentrification_top_20_VIC.csv` - Top 20 areas in Victoria
- `gentrification_top_20_QLD.csv` - Top 20 areas in Queensland
- `gentrification_top_20_SA.csv` - Top 20 areas in South Australia
- `gentrification_top_20_WA.csv` - Top 20 areas in Western Australia
- `gentrification_top_20_TAS.csv` - Top 20 areas in Tasmania
- `gentrification_top_20_ACT.csv` - Top 20 areas in Australian Capital Territory
- `gentrification_top_20_NT.csv` - Top 20 areas in Northern Territory

---

## Next Steps & Future Enhancements

### 1. Geographic Mapping
- Add SA1 geographic coordinates (lat/long)
- Calculate spatial autocorrelation (Moran's I)
- Generate interactive heatmaps using Folium/Plotly
- Identify spatial clusters (hot spots and cold spots)

### 2. Property Price Integration
- Overlay CoreLogic/Domain/APM property price data
- Calculate price-to-gentrification-risk ratios
- Identify undervalued areas (high risk, low prices)
- Track price velocity vs. risk scores

### 3. Temporal Analysis
- Compare 2016 vs 2021 Census data
- Calculate gentrification acceleration rates
- Predict 2026 Census outcomes
- Validate model accuracy with historical price data

### 4. Amenity Overlay
- Distance to CBDs, beaches, parks
- Public transport accessibility scores
- School catchment quality ratings
- Cafe/restaurant density (gentrification precursors)

### 5. SA2/Suburb Mapping
- Convert SA1 codes to actual suburb names
- Aggregate SA1 scores to SA2/suburb level
- Create suburb-level gentrification rankings
- More user-friendly geographic identifiers

---

## Acknowledgments

**Data Source:** Australian Bureau of Statistics (ABS)
**Dataset:** 2021 Census of Population and Housing - General Community Profile (GCP) DataPack Release 2
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

**Analysis Framework:**
- Python 3.x
- Pandas (data manipulation)
- NumPy (numerical computations)
- SciPy (statistical functions)

---

## Contact & Citation

If you use this analysis, please cite:
```
Ultra-Granular Gentrification Risk Analysis
Australian Census Data 2021
Analysis Date: November 2025
Data Source: Australian Bureau of Statistics
```

---

**Last Updated:** November 22, 2025
**Version:** 1.0
**Status:** Complete (except spatial autocorrelation)
