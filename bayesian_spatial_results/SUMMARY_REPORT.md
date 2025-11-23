# Hierarchical Bayesian Spatial Model - Summary Report
Analysis Date: 2025-11-23 02:27:29

## Model Configuration
- Outcome variable: median_income
- Predictors: pct_yr12_complete, pct_working_age, employment_rate
- Sample size: 61,844 SA1 areas
- Hierarchical levels:
  - SA4: 107 areas
  - SA3: 358 areas
  - SA2: 2,472 areas
  - SA1: 61,844 areas
- MCMC: 2,000 samples × 2 chains

## Key Findings

### Fixed Effects
- **pct_yr12_complete**: increases median income (β = 0.1609, 95% CI [0.1523, 0.1695], P(β>0) = 1.000)
- **pct_working_age**: increases median income (β = 0.0303, 95% CI [0.0235, 0.0372], P(β>0) = 1.000)
- **employment_rate**: increases median income (β = 0.4494, 95% CI [0.4423, 0.4565], P(β>0) = 1.000)

### Spatial Autocorrelation
- ρ = 0.5075 (95% CI [0.0866, 0.9693])
- Interpretation: MODERATE spatial spillovers
