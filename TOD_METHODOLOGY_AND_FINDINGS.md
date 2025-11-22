# Transit-Oriented Development (TOD) Analysis - Methodology & Findings

**Analysis Date:** November 22, 2025
**Dataset:** 2021 Australian Census - General Community Profile (Second Release)
**Geographic Coverage:** All 61,844 SA1 areas across Australia
**Analysis Focus:** Commuter Shed Optimization & Transit-Oriented Development Scoring

---

## Executive Summary

This comprehensive analysis identifies optimal locations for transit-oriented development (TOD) and transit infrastructure investment across Australia. Using 2021 Census data covering all 61,844 Statistical Area Level 1 (SA1) regions, we analyzed transportation methods, employment patterns, and housing density to create a sophisticated TOD scoring system.

### Key Findings

- **83.7% car dependency** across Australia (national average)
- **Only 6.4% public transit usage** (national average)
- **31,060 SA1 areas** (50.2%) have >90% car dependency
- **Identified 67 critical commute pain points** affecting 41,950 car-dependent commuters
- **Top 1,000 TOD opportunities** represent 264,984 commuters with 94.5% car dependency
- **Potential modal shift:** If 20% of car users in priority areas switch to transit: ~100,000 new transit users
- **Economic impact:** $47.9 million in annual time savings (top 1,000 areas only)

---

## Methodology

### Data Sources

**Census Tables Used:**
- **G62:** Method of Travel to Work (Transportation data - 109 columns)
- **G43:** Labour Force Status (Employment data)
- **G51A/B/C:** Occupation by Field (3 tables)
- **G54A/B/C/D:** Industry of Employment (4 tables)
- **G01:** Basic Demographics (Population)
- **G02:** Medians and Averages
- **G40:** Dwelling Structure (Housing stock)

**Geographic Levels:**
- **SA1:** 61,844 areas (finest granularity)
- **SA2:** 2,472 areas (employment centers)
- **SA3:** 358 areas (regional analysis)

### Analysis Pipeline

#### Step 1: Transportation Metrics Calculation

For each SA1 area, we calculated:

**Transportation Mode Totals:**
- Car (driver + passenger)
- Public Transit (train + bus + ferry + tram)
- Active Transport (bicycle + walking)
- Other (motorcycle, truck, etc.)

**Key Ratios:**
```
Car Dependency Ratio = Total Car Commuters / Total Commuters
Public Transit Ratio = Total Transit Commuters / Total Commuters
Active Transport Ratio = Total Active Commuters / Total Commuters
```

**Multimodal Adjustment:**
- Two-method combinations (e.g., Train+Bus, Car+Train) were allocated to both modes
- This captures transfer-based journeys and park-and-ride usage

#### Step 2: Employment Center Identification

**SA2 Level (2,472 areas):**
- Calculated total employed population
- Computed employment density (employed/total population)
- Identified top 100 employment centers

**SA3 Level (358 areas):**
- Regional employment aggregation
- Identified top 50 major employment regions

**Geographic Linkage:**
- Extracted SA2/SA3 codes from SA1 codes using hierarchical structure
- Linked each SA1 to its parent SA2 and SA3 employment data

#### Step 3: TOD Scoring Algorithm

**Four-Component Weighted Scoring System:**

```
TOD Score = (Car Dependency Score × 0.40) +
            (Commuter Volume Score × 0.30) +
            (Employment Proximity Score × 0.20) +
            (Transit Gap Score × 0.10)
```

**Component Details:**

1. **Car Dependency Score (40% weight)**
   - Direct measure: Car dependency ratio × 100
   - Rationale: High car dependency = high opportunity for modal shift
   - Range: 0-100

2. **Commuter Volume Score (30% weight)**
   - Percentile ranking of total commuters
   - Normalized to 0-100 scale
   - Rationale: More people = greater impact potential

3. **Employment Proximity Score (20% weight)**
   - Combined SA2 (50%) and SA3 (50%) employment density percentiles
   - Range: 0-100
   - Rationale: Proximity to jobs enables effective transit

4. **Transit Gap Score (10% weight)**
   - Formula: Car Dependency × (1 - Public Transit Usage) × 100
   - Range: 0-100
   - Rationale: Identifies underserved areas

**Final TOD Score Range:** 0-100 (higher = better TOD opportunity)

#### Step 4: Commute Pain Point Identification

**Criteria for Pain Points:**
- Car dependency > 75%
- Total commuters > 500
- Public transit usage < 10%

**Result:** 67 SA1 areas identified as critical intervention zones

#### Step 5: Network Analysis

**Transit Corridor Identification:**
- High commuter volume (top 25th percentile)
- High car dependency (>80%)
- Proximity to employment centers (top 25th percentile)

**Hub-and-Spoke Analysis:**
- Identified top 20 employment centers as potential hubs
- Analyzed surrounding SA1 "spokes" with high car dependency
- Calculated potential modal shift per hub network

**Travel Time Modeling:**
- Assumed average car commute: 35 minutes
- Assumed improved transit commute: 30 minutes
- Time savings: 5 minutes per trip × 2 trips/day = 10 min/day
- Economic value: $25/hour

#### Step 6: Investment Prioritization

**Three-Tier Priority System:**

**Priority 1:** High TOD Score + High Volume
- TOD score > 80
- Commuter volume > 90th percentile
- Result: 4,484 SA1 areas

**Priority 2:** Near Employment Centers + Low Transit
- SA2 employment density > 75th percentile
- Public transit usage < 10%
- Total commuters > 200
- Result: 1,496 SA1 areas

**Priority 3:** Multimodal Potential
- Public transit > 5%
- Active transport > 5%
- Car dependency > 70%
- Total commuters > 300
- Result: 60 SA1 areas

---

## Key Findings

### National Transportation Patterns

**Modal Split (7.88 million commuters):**
- Private Vehicle: 86.5% (6,811,913 commuters)
- Public Transit: 7.1% (556,689 commuters)
- Active Transport: 4.6% (360,948 commuters)

**Comparison to Global Cities:**
- Copenhagen: ~50% bike/transit
- Singapore: ~70% public transit
- Amsterdam: ~60% bike/transit
- **Australia: 11.7% sustainable transport** (transit + active)

### State/Territory Analysis

**Car Dependency Ranking (Highest to Lowest):**

| Rank | State | Car Dependency | Transit Usage | Commuters |
|------|-------|----------------|---------------|-----------|
| 1 | QLD | 85.9% | 4.4% | 1,770,425 |
| 2 | SA | 85.9% | 5.3% | 646,976 |
| 3 | TAS | 85.6% | 2.9% | 198,417 |
| 4 | VIC | 85.3% | 6.2% | 1,929,607 |
| 5 | NSW | 82.1% | 7.5% | 2,008,712 |
| 6 | WA | 80.8% | 9.1% | 1,042,707 |
| 7 | ACT | 79.4% | 5.9% | 190,331 |
| 8 | NT | 69.9% | 2.2% | 90,168 |

**TOD Opportunity Ranking (by Avg TOD Score):**

| Rank | State | Avg TOD Score | Car Dependency | SA1 Areas |
|------|-------|---------------|----------------|-----------|
| 1 | ACT | 74.4 | 79.4% | 1,229 |
| 2 | SA | 70.7 | 85.9% | 4,329 |
| 3 | WA | 70.8 | 80.8% | 6,352 |
| 4 | QLD | 69.5 | 85.9% | 12,549 |
| 5 | VIC | 68.0 | 85.3% | 15,482 |
| 6 | TAS | 66.4 | 85.6% | 1,482 |
| 7 | NT | 61.4 | 69.9% | 649 |
| 8 | NSW | 60.5 | 82.1% | 19,750 |

### Top 10 TOD Opportunities

| Rank | SA1 Code | TOD Score | Car Dep | Transit | Commuters | SA2 Employment |
|------|----------|-----------|---------|---------|-----------|----------------|
| 1 | 70101100901 | 97.1 | 95.9% | 1.0% | 292 | 1,856 |
| 2 | 10102101209 | 96.9 | 97.0% | 1.4% | 366 | 7,404 |
| 3 | 70101100903 | 96.5 | 93.8% | 1.1% | 368 | 1,856 |
| 4 | 10102101232 | 96.4 | 98.4% | 0.0% | 247 | 7,404 |
| 5 | 10102161109 | 96.4 | 100.0% | 0.0% | 239 | 9,026 |
| 6 | 70101100905 | 96.3 | 94.4% | 1.0% | 286 | 1,856 |
| 7 | 80104103604 | 96.2 | 97.2% | 0.0% | 252 | 3,770 |
| 8 | 10102101222 | 96.2 | 98.3% | 0.0% | 240 | 7,404 |
| 9 | 10102101224 | 95.9 | 97.6% | 1.2% | 248 | 7,404 |
| 10 | 10102101214 | 95.8 | 97.9% | 0.0% | 236 | 7,404 |

### Network Analysis Results

**Major Employment Hubs:**
- Identified 50 major centers
- Total employment: 617,827
- Average commuters per hub: 6,950

**Transit Corridors:**
- 3,074 SA1 areas identified
- Total corridor commuters: 673,389
- Average car dependency: 90.8%

**Hub-and-Spoke Opportunities:**
- 17 viable hub networks
- Potential modal shift (20%): 17,837 new transit users
- Top hub potential: 1,610 users

**Travel Time Savings (Top 1,000 areas):**
- Daily savings: 8,331 hours
- Annual savings: 1,916,076 hours (239,510 work-days)
- Economic value: **$47,901,908 per year**

---

## Investment Recommendations

### Short-Term (0-2 years)

1. **Quick Wins in Priority 1 Areas**
   - Focus on top 100 SA1s with TOD scores >85
   - Implement express bus services
   - Install bus priority lanes and signal priority

2. **Active Transport Infrastructure**
   - Improve bike lanes in multimodal opportunity areas
   - Create safe walking routes to transit stops
   - Install bike parking at key locations

3. **Pilot Programs**
   - Launch pilot TOD projects in top 10 opportunity areas
   - Measure ridership and modal shift
   - Refine methodology based on results

### Medium-Term (2-5 years)

4. **Bus Rapid Transit (BRT)**
   - Develop BRT corridors on highest-volume routes
   - Dedicated bus lanes
   - Enhanced stations with real-time information

5. **Hub-and-Spoke Networks**
   - Establish transit hubs at major employment centers
   - Create feeder bus routes
   - Integrate schedules and fares

6. **Zoning Reforms**
   - Allow higher density near transit stops
   - Implement minimum density requirements
   - Streamline approval processes for TOD

7. **Park-and-Ride Facilities**
   - Build at key interchange points
   - Enable multimodal journeys
   - Reduce car dependency for full trip

### Long-Term (5-15 years)

8. **Rail Transit Investment**
   - Build light rail or metro in highest-priority corridors
   - Connect major employment centers
   - Achieve 15-minute frequencies

9. **Comprehensive TOD Policies**
   - Mixed-use development requirements
   - Reduced parking minimums
   - Complete streets design standards

10. **Network Expansion**
    - Extend to Priority 2 employment center areas
    - Build comprehensive regional networks
    - Achieve 30% public transit mode share nationally

### Policy Enablers

**Essential Policies:**
- Transit-oriented zoning and land use reforms
- Parking pricing and management
- Complete streets and Vision Zero policies
- Dedicated bus lanes and transit signal priority
- Integrated fares and schedules across modes
- First/last-mile solutions (bike share, e-scooters, microtransit)

**Funding Mechanisms:**
- Value capture from increased property values
- Congestion pricing
- Parking revenue
- Federal/state infrastructure funds
- Public-private partnerships
- Carbon pricing mechanisms

---

## Data Files Generated

| File | Records | Description |
|------|---------|-------------|
| `tod_complete_sa1_analysis.csv` | 61,844 | Complete dataset for all SA1 areas |
| `tod_top_1000_opportunities.csv` | 1,000 | Highest TOD scoring areas |
| `tod_commute_pain_points.csv` | 67 | Critical intervention areas |
| `tod_high_car_dependency.csv` | 31,060 | Areas with >90% car dependency |
| `tod_multimodal_opportunities.csv` | 313 | Areas near employment with low transit |
| `tod_transit_corridors.csv` | 3,074 | Potential transit corridor routes |
| `tod_state_level_analysis.csv` | 9 | State/territory summary statistics |
| `tod_hub_spoke_analysis.csv` | 17 | Hub-and-spoke network analysis |
| `tod_travel_time_savings.csv` | 100 | Economic impact calculations |
| `tod_priority_1_high_score_volume.csv` | 500 | Priority 1 investment areas |
| `tod_priority_2_employment_centers.csv` | 500 | Priority 2 investment areas |
| `tod_priority_3_multimodal.csv` | 60 | Priority 3 investment areas |
| `tod_summary_statistics.csv` | Summary | Overall statistics |
| `tod_key_metrics_summary.csv` | Summary | Key metrics for reporting |
| `TOD_COMPREHENSIVE_REPORT.txt` | Report | Detailed text report |

---

## Python Scripts

1. **`tod_analysis_commuter_optimization.py`**
   - Main analysis script
   - Processes all 61,844 SA1 areas
   - Calculates TOD scores
   - Runtime: ~2-3 minutes

2. **`tod_network_analysis.py`**
   - Network and corridor analysis
   - Hub-and-spoke modeling
   - Travel time savings calculations
   - Runtime: ~30 seconds

3. **`tod_summary_report.py`**
   - Generates comprehensive reports
   - Creates summary statistics
   - Runtime: ~10 seconds

4. **`explore_census_tables.py`**
   - Initial data exploration
   - Table identification

---

## Limitations and Future Work

### Current Limitations

1. **Spatial Proximity**
   - Analysis does not include actual geographic distances
   - SA2/SA3 linkage is hierarchical, not spatial
   - Future: Add GIS shapefiles for precise distance calculations

2. **Place of Work Data**
   - Census does not provide destination SA1 for commuters
   - Cannot model actual origin-destination flows
   - Future: Integrate ABS Journey to Work data if available

3. **Travel Time Assumptions**
   - Generic travel time estimates used
   - Actual travel times vary by route and mode
   - Future: Integrate Google Maps API or transport modeling tools

4. **Cost-Benefit Analysis**
   - Economic analysis limited to time savings
   - Does not include infrastructure costs
   - Future: Full cost-benefit analysis with capital costs

5. **Temporal Coverage**
   - 2021 data (pre-COVID work patterns)
   - Does not account for remote work trends
   - Future: Compare with 2026 Census when available

### Future Enhancements

1. **GIS Integration**
   - Map visualizations
   - Spatial clustering analysis
   - Distance-based corridor identification

2. **Journey to Work Data**
   - Origin-destination matrices
   - Actual commute flows
   - Network flow optimization

3. **Real Estate Analysis**
   - Property values near transit
   - Value capture potential
   - Development feasibility

4. **Environmental Impact**
   - Carbon emissions reduction
   - Air quality improvements
   - Health benefits quantification

5. **Equity Analysis**
   - Income-based transit access
   - Social equity metrics
   - Disadvantaged area prioritization

---

## Acknowledgments

**Data Source:**
Australian Bureau of Statistics (ABS)
- 2021 Census of Population and Housing
- General Community Profile (Second Release)
- Creative Commons license

**Analysis Performed By:**
Claude Code (Anthropic)

**Date:**
November 22, 2025

---

## Contact

For questions about this analysis or to request custom analyses:
- Review the Python scripts included in this repository
- Check the comprehensive report (`TOD_COMPREHENSIVE_REPORT.txt`)
- Examine the data files for detailed results

---

**End of Methodology & Findings Documentation**
