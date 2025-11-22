# Rental Stress & Social Housing Demand Forecasting Analysis
## 2021 Australian Census - SA1 Level Analysis

---

## Executive Summary

This analysis processed **61,844 SA1 statistical areas** across Australia to identify:
1. Rental affordability stress hotspots
2. Low-income household concentrations
3. Public housing supply-demand gaps
4. Areas at risk of displacement
5. Optimal social housing investment locations

---

## Key Findings

### Rental Affordability Crisis

- **5,676 SA1 areas (9.2%)** experiencing rental stress (rent ≥30% of income)
- **296 SA1 areas (0.5%)** in severe rental stress (rent ≥50% of income)
- Average rent-to-income ratio: **inf%**
- Median weekly rent: **$380**
- Median weekly household income: **$1,781**

### Low-Income Household Vulnerability

- Total households analyzed: **9,275,075**
- Low-income households (<$800/week): **3,378,554** (36.4%)
- SA1s with >50% low-income households: **13,225**
- Average low-income percentage: **inf%**

### Public Housing Supply Crisis

- Total public housing dwellings: **447,895**
- Total rental dwellings: **5,638,948**
- Public housing as % of rentals: **7.94%**
- Estimated demand (low-income in stress): **564,228**
- **Supply-demand gap: 116,333 dwellings**
- SA1s with critical gaps (>10 dwellings): **5,234**

### Risk Assessment

- SA1s with critical rental stress (score ≥75): **0**
- SA1s with high displacement risk (score ≥75): **0**
- SA1s requiring critical investment priority: **0**
- Average rental stress score: **21.15/100**
- Average displacement risk score: **20.33/100**

---

## Methodology

### Data Sources
- **G02**: Median rent & household income
- **G33**: Household income distributions
- **G37**: Tenure type (owned/rented/public housing)
- **G40**: Rental by landlord type
- **G43**: Labour force status

### Key Metrics

1. **Rent-to-Income Ratio**: Weekly rent / Weekly household income
   - Stress threshold: ≥30%
   - Severe stress threshold: ≥50%

2. **Low-Income Households**: Households earning <$800/week

3. **Public Housing Gap**: Estimated demand - Current supply
   - Demand = Low-income households in rental stress

4. **Rental Stress Score** (0-100):
   - Rent-to-income ratio: 35%
   - Low-income concentration: 25%
   - Public housing gap: 20%
   - Unemployment rate: 10%
   - Public housing supply: 10%

5. **Displacement Risk Score** (0-100):
   - Affordability pressure: 30%
   - Vulnerable population: 30%
   - Low social housing: 20%
   - Economic vulnerability: 20%

6. **Investment Priority Score** (0-100):
   - Rental stress: 40%
   - Supply-demand gap: 30%
   - Vulnerable population: 20%
   - Unemployment: 10%

---

## Output Files

1. `rental_stress_analysis_full.csv` - Complete analysis for all SA1 areas
2. `top_1000_rental_stress_hotspots.csv` - Highest rental stress areas
3. `top_1000_displacement_risk_areas.csv` - Areas most at risk of displacement
4. `top_500_investment_priorities.csv` - Optimal social housing investment locations
5. `critical_public_housing_gaps.csv` - Areas with critical supply-demand gaps

---

## Policy Implications

### Immediate Action Required

1. **Address Critical Supply Gap**: 116,333 additional public housing dwellings needed
2. **Target High-Risk Areas**: 0 SA1s require immediate intervention
3. **Prevent Displacement**: 0 areas at critical risk

### Investment Priorities

Focus social housing investment on:
- Areas with high rental stress scores (≥75)
- High concentrations of low-income households (>50%)
- Large supply-demand gaps (>10 dwellings)
- High unemployment rates
- Low existing public housing supply

### Spatial Targeting

The analysis identifies specific SA1 areas for:
- New social housing construction
- Rental assistance programs
- Community housing partnerships
- Employment accessibility improvements

---

*Analysis generated using 2021 Australian Census data (SA1 level)*
*Australian Bureau of Statistics - General Community Profile (GCP)*
