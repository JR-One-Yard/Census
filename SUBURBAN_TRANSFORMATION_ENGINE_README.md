# 🏗️ Suburban Transformation Prediction Engine

## Overview

A comprehensive, compute-intensive analysis of **62,409 Australian geographic areas** (565 LGAs + 61,844 SA1s) to identify suburbs ripe for redevelopment and rezoning opportunities using 2021 Census data.

**Analysis Completed:** November 22, 2025
**Total Areas Analyzed:** 62,409
**Data Source:** Australian Bureau of Statistics 2021 Census (GCP DataPack R2)
**Geographic Levels:** LGA (Local Government Areas), SA1 (Statistical Area Level 1)

---

## 🎯 What This Engine Analyzes

This engine identifies three major redevelopment opportunities:

### 1. 🏘️ Subdivision Potential
**High detached house % near urban centers**
- Areas with >70% separate/detached houses
- High urban proximity (population density proxy)
- Population base >5,000
- **Perfect for:** Subdividing large blocks into townhouses or duplexes

### 2. 🏢 Luxury Apartment Demand
**Low density but affluent demographics**
- Current apartment stock <20%
- High household income (top 30%)
- High tertiary education (top 30%)
- **Perfect for:** Premium apartment developments in leafy suburbs

### 3. 👴 Downsizing Wave
**Aging population in large houses**
- >30% of population aged 55+
- >60% living in detached houses
- Above-median household income
- **Perfect for:** Age-appropriate housing, retirement villages, smaller dwellings

---

## 📊 Key Findings

### LGA Level (565 areas)

**Redevelopment Readiness:**
- Very High: 171 areas (30.3%)
- High: 172 areas (30.4%)
- Medium: 173 areas (30.6%)
- Low: 34 areas (6.0%)

**Opportunity Breakdown:**
- **127 high subdivision potential areas**
- **72 high luxury apartment demand areas**
- **121 high downsizing wave areas**

**Time-Decay Projections:**
- 40% average transformation probability in 5 years
- 64% average transformation probability in 10 years
- 78% average transformation probability in 15 years

### SA1 Level (61,844 areas - finest granularity)

**Redevelopment Readiness:**
- Very High: 7,236 areas (11.7%)
- High: 22,091 areas (35.7%)
- Medium: 25,585 areas (41.4%)
- Low: 5,089 areas (8.2%)

**Opportunity Breakdown:**
- **8,605 high luxury apartment demand areas**
- **8,963 high downsizing wave areas**

**Top SA1 Areas by Score:**
1. SA1 50301103533: Score 92.84 - 79% detached, $3,524/week income, 38% aged 55+
2. SA1 80109110401: Score 92.12 - 92% detached, $3,524/week income, 40% aged 55+
3. SA1 80109110702: Score 91.27 - 91% detached, $4,700/week income, 39% aged 55+

---

## 📁 Generated Files

### LGA Analysis Files

| File | Records | Description |
|------|---------|-------------|
| `transformation_analysis_lga_full.csv` | 565 | Complete analysis for all LGAs |
| `transformation_analysis_lga_top100.csv` | 100 | Top 100 redevelopment opportunities |
| `subdivision_potential_lga.csv` | 127 | High subdivision potential areas |
| `luxury_apartment_demand_lga.csv` | 72 | High luxury apartment demand areas |
| `downsizing_wave_lga.csv` | 121 | High downsizing potential areas |

### SA1 Analysis Files

| File | Records | Description |
|------|---------|-------------|
| `transformation_analysis_sa1_full.csv` | 61,844 | Complete analysis for all SA1s (11 MB!) |
| `transformation_analysis_sa1_top500.csv` | 500 | Top 500 redevelopment opportunities |
| `subdivision_potential_sa1.csv` | 0 | High subdivision potential areas |
| `luxury_apartment_demand_sa1.csv` | 8,605 | High luxury apartment demand areas |
| `downsizing_wave_sa1.csv` | 8,963 | High downsizing potential areas |

---

## 📐 Methodology

### Data Sources

The engine combines data from multiple census tables:

| Table | Description | Used For |
|-------|-------------|----------|
| **G36** | Dwelling structure by type | Separate houses, apartments, semi-detached ratios |
| **G02** | Medians and averages | Median age, household income, family income |
| **G04B** | Age distribution (55+ years) | Aging population analysis, downsizing potential |
| **G49A/B** | Tertiary education qualifications | Education levels, affluence indicators |
| **GCCSA** | Greater capital city areas | Urban center identification |

### Scoring Algorithms

#### 1. Subdivision Potential Score (0-100)
```
Score = (Detached % Score × 0.40) + (Urban Proximity × 0.40) + (Population Size × 0.20)

Where:
- Detached % Score = min(pct_separate_houses / 70 × 40, 40)
- Urban Proximity = population_percentile × 40
- Population Size = min(population / 10000 × 20, 20)
```

**Flags high potential when:**
- Detached houses ≥70%
- Urban proximity ≥60th percentile
- Population ≥5,000

#### 2. Luxury Apartment Demand Score (0-100)
```
Score = (Low Density Bonus × 0.30) + (Income Percentile × 0.35) + (Education Percentile × 0.35)

Where:
- Low Density Bonus = max(0, (30 - apartment%) / 30 × 30)
- Income Percentile = household_income_rank × 35
- Education Percentile = tertiary_education_rank × 35
```

**Flags high demand when:**
- Current apartment stock <20%
- Income ≥70th percentile
- Education ≥70th percentile

#### 3. Downsizing Wave Score (0-100)
```
Score = (Aging Population × 0.40) + (Large Houses × 0.30) + (Income × 0.30)

Where:
- Aging Population = min(pct_aged_55+ / 40 × 40, 40)
- Large Houses = min(pct_separate / 70 × 30, 30)
- Income = income_percentile × 30
```

**Flags high potential when:**
- Population aged 55+ ≥30%
- Detached houses ≥60%
- Household income ≥median

#### 4. Redevelopment Readiness Score (0-100)
```
Overall Score = (Subdivision × 0.30) + (Luxury Demand × 0.25) +
                (Downsizing × 0.25) + (Urban Proximity × 0.20)
```

**Categories:**
- Very High: 75-100
- High: 60-75
- Medium: 40-60
- Low: 0-40

### Time-Decay Transformation Model

Probability of housing stock transformation over time using exponential growth:

```
P(t) = 1 - e^(-λt)

Where:
- λ = base_transformation_rate × 0.15
- t = time in years (5, 10, or 15)
- base_rate = weighted average of all three scores
```

**Example Interpretation:**
- Area with 70/100 readiness score:
  - 5 years: ~40% probability of significant change
  - 10 years: ~64% probability of significant change
  - 15 years: ~78% probability of significant change

---

## 🔍 How to Use the Results

### For Property Developers

1. **Start with the top 100 files:**
   - `transformation_analysis_lga_top100.csv` for broad market overview
   - `transformation_analysis_sa1_top500.csv` for specific locations

2. **Filter by opportunity type:**
   - Subdivision: Use `subdivision_potential_*.csv`
   - Luxury apartments: Use `luxury_apartment_demand_*.csv`
   - Retirement/downsizer: Use `downsizing_wave_*.csv`

3. **Key columns to examine:**
   - `redevelopment_readiness_score`: Overall opportunity (higher = better)
   - `pct_separate`: How much detached housing exists
   - `median_household_income`: Affluence level
   - `pct_age_55_plus`: Aging population percentage
   - `transform_prob_5yr/10yr/15yr`: Likelihood of change over time

### For Urban Planners

1. **Identify rezoning priorities:**
   - High subdivision potential = consider upzoning to medium density
   - High luxury demand = approve quality apartment developments
   - High downsizing wave = plan age-appropriate housing

2. **Infrastructure planning:**
   - Areas with high transformation probability need infrastructure upgrades
   - Monitor areas in "Very High" category for development applications

### For Researchers

1. **Full datasets available:**
   - `transformation_analysis_sa1_full.csv` (11 MB, 61,844 records)
   - `transformation_analysis_lga_full.csv` (103 KB, 565 records)

2. **All calculated metrics included:**
   - Dwelling type percentages
   - Demographics (age, income, education)
   - All component scores
   - Time-decay probabilities
   - Readiness categories

---

## 📈 Top 10 LGA Redevelopment Opportunities

| Rank | LGA Code | Score | Detached % | Income ($/week) | Age 55+ % | Category |
|------|----------|-------|------------|-----------------|-----------|----------|
| 1 | LGA54170 | 92.07 | 83.8% | $2,165 | 31.5% | Very High |
| 2 | LGA17420 | 91.48 | 77.3% | $2,831 | 25.8% | Very High |
| 3 | LGA10750 | 90.55 | 77.1% | $2,107 | 20.6% | Very High |
| 4 | LGA55320 | 90.31 | 69.9% | $2,096 | 33.6% | Very High |
| 5 | LGA23670 | 90.26 | 79.2% | $1,884 | 30.8% | Very High |
| 6 | LGA21610 | 90.23 | 86.6% | $1,918 | 20.8% | Very High |
| 7 | LGA27450 | 89.83 | 88.0% | $1,881 | 30.7% | Very High |
| 8 | LGA22750 | 89.54 | 77.2% | $1,592 | 31.5% | Very High |
| 9 | LGA20660 | 89.48 | 70.2% | $2,027 | 30.6% | Very High |
| 10 | LGA27260 | 89.40 | 82.6% | $2,023 | 15.2% | Very High |

---

## 💻 Technical Details

### Requirements
- Python 3.11+
- pandas 2.3.3+
- numpy 2.3.5+

### Running the Analysis

```bash
# Install dependencies
pip install pandas numpy

# Run the engine
python3 suburban_transformation_engine.py
```

**Runtime:** ~2-3 minutes for full analysis of 62,409 areas
**Memory:** ~2-3 GB RAM (processing 61,844 SA1 areas)
**Output:** 10 CSV files + detailed console report

### Source Code

Main script: `suburban_transformation_engine.py`

**Key Classes:**
- `SuburbanTransformationEngine`: Main analysis engine
  - Data loading methods (dwelling, age, income, education)
  - Scoring algorithms (subdivision, luxury, downsizing)
  - Time-decay modeling
  - Export and reporting functions

---

## 🎓 Data Quality & Limitations

### Data Protections
- ABS applies small random adjustments to protect confidentiality
- Row/column sums may differ slightly from totals
- Some small areas may have suppressed data

### Geographic Considerations
- **SA1** is the finest granularity (~400 people per area on average)
- **LGA** represents local government boundaries (variable population)
- Urban proximity uses population density as a proxy (actual distance to CBDs not calculated)

### Temporal Considerations
- Analysis based on 2021 Census (snapshot in time)
- Time-decay models are probabilistic, not deterministic
- External factors (rezoning, infrastructure, policy changes) not modeled

### Scoring Caveats
- Scores are **relative rankings** within the dataset
- High scores indicate opportunity, not certainty
- Always verify with local market research and feasibility studies

---

## 📚 Related Files

- `DATA_ANALYSIS_GUIDE.md` - Guide to census tables and data structure
- `DOCUMENTATION_SUMMARY.md` - Summary of census data coverage
- `transformation_engine_output.log` - Full execution log with detailed progress

---

## 🙏 Acknowledgments

**Data Source:** Australian Bureau of Statistics
**Dataset:** 2021 Census of Population and Housing - General Community Profile (GCP) DataPack, Release 2
**License:** Creative Commons
**Contact:** Australian Census Data: Client.services@abs.gov.au or 1300 135 070

---

## 📧 Questions or Issues?

For technical questions about this analysis, refer to:
1. The execution log: `transformation_engine_output.log`
2. The source code: `suburban_transformation_engine.py`
3. ABS documentation in `/2021_GCP_all_for_AUS_short-header/Readme/`

---

**Generated:** November 22, 2025
**Engine Version:** 1.0
**Total Compute:** Processing 62,409 areas across 5 dimensions (dwelling types, age, income, education, proximity)
**Free credits well spent! 💰**
