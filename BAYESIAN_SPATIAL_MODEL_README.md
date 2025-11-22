# Hierarchical Bayesian Spatial Model - Australian Census 2021

## Overview

This analysis implements a **full-scale Hierarchical Bayesian Spatial Model** on the 2021 Australian Census data, analyzing all **61,844 Statistical Areas Level 1 (SA1)** - the finest geographic granularity available.

## Model Specification

### Hierarchical Structure

The model implements a 4-level geographic hierarchy:

```
Level 4 (National): SA4 regions (107 areas)
    ↓
Level 3 (Regional): SA3 areas (358 areas)
    ↓
Level 2 (District): SA2 areas (2,472 areas)
    ↓
Level 1 (Neighborhood): SA1 areas (61,844 areas)
```

### Mathematical Formulation

**Level 1 - SA1 (Observation Level):**
```
Y_i ~ Normal(μ_i, σ²)
```

**Level 2 - SA2 (District Random Effects):**
```
μ_i = α_SA2[j(i)] + β₁X₁ᵢ + β₂X₂ᵢ + β₃X₃ᵢ + ρφᵢ
```

Where:
- `Y_i` = Median income in SA1 area i
- `α_SA2[j(i)]` = Random intercept for SA2 district j containing area i
- `β₁, β₂, β₃` = Fixed effects coefficients for predictors
- `ρ` = Spatial autocorrelation parameter (0 ≤ ρ ≤ 1)
- `φᵢ` = Spatial random effect for area i

**Level 3 - SA3 (Regional Random Effects):**
```
α_SA2[j] ~ Normal(γ_SA3[k(j)], τ²_SA2)
```

**Level 4 - SA4 (National Random Effects):**
```
γ_SA3[k] ~ Normal(δ_SA4[m(k)], τ²_SA3)
δ_SA4[m] ~ Normal(0, τ²_SA4)
```

**Spatial Component (CAR Prior):**
```
φ ~ Normal(0, σ²_spatial)
```

### Variables

**Outcome Variable:**
- `median_income`: Median total personal income (weekly), standardized

**Predictor Variables:**
- `pct_yr12_complete`: Percentage of population with Year 12 completion
- `pct_working_age`: Percentage of population aged 25-44 (prime working age)
- `employment_rate`: Labor force employment rate (full-time + part-time)

**Spatial Structure:**
- K-nearest neighbors (k=8) spatial weights matrix
- 539,242 non-zero spatial connections
- 99.99% sparse (efficient computation)

## Computational Specifications

### MCMC Configuration

- **Sampler**: NUTS (No-U-Turn Sampler)
- **Chains**: 2 independent chains
- **Tuning iterations**: 1,000 per chain (burn-in)
- **Sampling iterations**: 2,000 per chain
- **Total samples**: 4,000 posterior samples
- **Parameters estimated**: 67,681 total
  - Fixed effects: 3 (β coefficients)
  - Hierarchical effects: 2,937 (SA2 + SA3 + SA4 random intercepts)
  - Spatial effects: 61,844 (φ for each SA1)
  - Variance components: 5 (σ², τ²_SA4, τ²_SA3, τ²_SA2, σ²_spatial)
  - Spatial correlation: 1 (ρ)

### Data Processing

1. **Data Loading**: 3 Census tables merged (G01, G02, G43)
2. **Spatial Weights**: K-D tree algorithm for efficient neighbor search
3. **Hierarchy Extraction**: Derived from 11-digit SA1 codes
4. **Missing Data**: Median imputation for numeric variables
5. **Standardization**: Z-score normalization for all continuous variables

## Spatial Spillover Effects

The model accounts for spatial autocorrelation through:

1. **Direct Effects**: Impact of predictors on the area itself (β coefficients)
2. **Indirect Effects**: Spillover impacts from neighboring areas (ρφ term)
3. **Total Effects**: Combined direct + indirect impacts

The spatial autocorrelation parameter `ρ` quantifies the strength of spatial spillovers:
- ρ = 0: No spatial autocorrelation (independent areas)
- ρ = 1: Maximum spatial autocorrelation (perfect spillover)

## Model Outputs

### Files Generated

1. **mcmc_trace.nc** - Full MCMC trace (NetCDF format)
   - Contains all posterior samples for all parameters
   - Can be loaded with `arviz.from_netcdf()`

2. **model_metadata.json** - Model configuration
   - Variables used
   - Sample sizes
   - Hierarchy structure

3. **spatial_weights.npz** - Sparse spatial weights matrix
   - 61,844 × 61,844 adjacency matrix
   - scipy sparse format

4. **hierarchy.csv** - Geographic hierarchy mapping
   - SA1 → SA2 → SA3 → SA4 relationships

5. **trace_plots.png** - MCMC convergence diagnostics
   - Trace plots for key parameters
   - Visual assessment of chain mixing

6. **posterior_plots.png** - Posterior distributions
   - Marginal posteriors for all parameters
   - Credible intervals (95% HPD)

7. **parameter_summary.csv** - Parameter estimates
   - Posterior means
   - Standard deviations
   - 95% credible intervals
   - R-hat convergence diagnostics
   - Effective sample sizes

### Diagnostic Metrics

**Convergence Diagnostics:**
- **R-hat**: Should be < 1.01 for convergence
- **Effective Sample Size (ESS)**: Should be > 400 for reliable inference
- **Trace plots**: Should show good mixing with no trends

**Model Fit:**
- **Posterior predictive checks**: Compare observed vs predicted distributions
- **LOO-CV**: Leave-one-out cross-validation for out-of-sample fit
- **WAIC**: Widely Applicable Information Criterion

## Interpretation Guide

### Fixed Effects (β)

- **Positive β**: Predictor increases median income
- **Negative β**: Predictor decreases median income
- **Magnitude**: Effect size in standard deviations

### Spatial Autocorrelation (ρ)

- **Low ρ (< 0.3)**: Weak spatial clustering
- **Moderate ρ (0.3-0.7)**: Moderate spatial spillovers
- **High ρ (> 0.7)**: Strong spatial dependence

### Variance Components

- **τ²_SA4**: Between-region (national level) variance
- **τ²_SA3**: Between-area (regional level) variance
- **τ²_SA2**: Between-district variance
- **σ²_spatial**: Spatial random effect variance
- **σ²**: Residual (unexplained) variance

**Variance Partitioning Coefficient (VPC):**
```
VPC_SA2 = τ²_SA2 / (τ²_SA4 + τ²_SA3 + τ²_SA2 + σ²_spatial + σ²)
```
Indicates proportion of variance explained by SA2-level clustering.

## Technical Stack

### Software Dependencies

```python
numpy>=1.24.0          # Numerical computing
pandas>=2.0.0          # Data manipulation
scipy>=1.10.0          # Sparse matrices, spatial operations
pymc>=5.10.0           # Bayesian modeling framework
arviz>=0.17.0          # Bayesian diagnostics and visualization
matplotlib>=3.7.0      # Plotting
```

### Computational Resources

- **Memory**: ~16-32 GB RAM recommended
- **CPU**: Multi-core (2 chains run in parallel)
- **Runtime**: ~30-120 minutes (depending on hardware)
- **Storage**: ~2-5 GB for outputs

## Usage

### Running the Model

```bash
python3 hierarchical_bayesian_spatial_model.py
```

### Loading Results

```python
import arviz as az
import pandas as pd
from scipy import sparse

# Load MCMC trace
trace = az.from_netcdf('bayesian_spatial_results/mcmc_trace.nc')

# Load parameter estimates
params = pd.read_csv('bayesian_spatial_results/parameter_summary.csv')

# Load spatial weights
W = sparse.load_npz('bayesian_spatial_results/spatial_weights.npz')

# Examine posterior summaries
print(az.summary(trace, var_names=['β', 'ρ', 'σ_sa4', 'σ_sa3', 'σ_sa2']))
```

### Visualization

```python
import arviz as az

# Posterior plots
az.plot_posterior(trace, var_names=['β', 'ρ'])

# Forest plot of fixed effects
az.plot_forest(trace, var_names=['β'], combined=True)

# Trace plots for convergence
az.plot_trace(trace, var_names=['β', 'ρ'])

# Posterior predictive checks
az.plot_ppc(trace)
```

## Scientific Applications

This model enables analysis of:

1. **Spatial Inequality**: How income varies across geographic scales
2. **Education Returns**: Impact of education on income, accounting for spatial clustering
3. **Spillover Effects**: How neighboring areas affect each other
4. **Policy Targeting**: Identify areas with unexplained low/high outcomes
5. **Regional Variation**: Decompose variance across hierarchical levels

## References

**Spatial Statistics:**
- Besag, J. (1974). "Spatial Interaction and the Statistical Analysis of Lattice Systems"
- Banerjee, S., Carlin, B. P., & Gelfand, A. E. (2014). "Hierarchical Modeling and Analysis for Spatial Data"

**Bayesian Methods:**
- Gelman, A. et al. (2013). "Bayesian Data Analysis" (3rd ed.)
- McElreath, R. (2020). "Statistical Rethinking: A Bayesian Course"

**Australian Census:**
- Australian Bureau of Statistics (2022). "2021 Census of Population and Housing"

## License

Data: Creative Commons (Australian Bureau of Statistics)
Code: MIT License

## Contact

For questions or issues, please refer to the main repository documentation.

---

**Generated**: 2025-11-22
**Analysis Scale**: 61,844 SA1 areas (full national coverage)
**Model Type**: Hierarchical Bayesian CAR (Conditional Autoregressive)
**Framework**: PyMC v5.26+
