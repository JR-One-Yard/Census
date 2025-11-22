# Computational Details - Hierarchical Bayesian Spatial Model

## Current Status

The MCMC sampler is actively running on the full Census dataset.

## Scale of Computation

### Data Dimensions
- **SA1 Areas**: 61,844 (finest geographic level)
- **SA2 Districts**: 2,472
- **SA3 Regions**: 358
- **SA4 Sectors**: 107
- **Total Observations**: 61,844
- **Predictor Variables**: 3 (standardized)

### Model Parameters

Total parameters being estimated: **67,786**

Breakdown:
1. **Fixed Effects (β)**: 3 parameters
   - Coefficient for `pct_yr12_complete`
   - Coefficient for `pct_working_age`
   - Coefficient for `employment_rate`

2. **Hierarchical Random Effects**: 2,937 parameters
   - SA4 random intercepts (α_SA4): 107 parameters
   - SA3 random intercepts (α_SA3): 358 parameters
   - SA2 random intercepts (α_SA2): 2,472 parameters

3. **Spatial Random Effects (φ)**: 61,844 parameters
   - One spatial effect per SA1 area
   - Captures local spatial variation not explained by predictors

4. **Variance Components**: 5 parameters
   - σ_SA4: Between-region variance
   - σ_SA3: Between-area variance
   - σ_SA2: Between-district variance
   - σ_spatial: Spatial random effect variance
   - σ: Residual variance

5. **Spatial Autocorrelation (ρ)**: 1 parameter
   - Measures strength of spatial spillovers

### MCMC Sampling Configuration

- **Algorithm**: NUTS (No-U-Turn Sampler)
  - Auto-tuning step size
  - Auto-adapting mass matrix
  - Efficient exploration of posterior

- **Chains**: 2 independent chains
  - Run in parallel on separate cores
  - Enables convergence diagnostics (R-hat)

- **Iterations per Chain**:
  - Tuning: 1,000 iterations (discarded)
  - Sampling: 2,000 iterations (kept)
  - Total: 3,000 iterations per chain

- **Total Posterior Samples**: 4,000
  - Chain 1: 2,000 samples
  - Chain 2: 2,000 samples

### Computational Requirements

**Memory Usage (Estimated)**:
- Data: ~500 MB (3 merged Census tables)
- Spatial Weights Matrix: ~4.3 MB (sparse: 539,242 non-zero entries)
- MCMC Trace: ~10-15 GB (67,786 parameters × 4,000 samples × 8 bytes/float)
- Total: ~16-20 GB RAM

**CPU Usage**:
- 2 cores actively sampling (parallel chains)
- Additional cores for matrix operations

**Storage**:
- Output files: ~2-5 GB
  - MCMC trace (NetCDF): ~1-3 GB
  - Diagnostic plots: ~20-50 MB
  - CSV outputs: ~100-500 MB

**Runtime (Estimated)**:
- Depends heavily on hardware
- Conservative estimate: 30-120 minutes
- With fast CPUs: Potentially 15-30 minutes
- Current stage: Initialization and early sampling

## Why Is This Expensive?

### 1. High Dimensionality
- 67,786 parameters require evaluating complex joint distributions
- Each MCMC iteration requires gradient computation for all parameters

### 2. Spatial Dependencies
- Spatial weights matrix creates dependencies between all neighboring areas
- Each area's likelihood depends on its neighbors (not independent)

### 3. Hierarchical Structure
- 4-level nesting requires computing conditional distributions at each level
- SA1 depends on SA2, which depends on SA3, which depends on SA4

### 4. NUTS Sampler Complexity
- NUTS builds a binary tree to explore the posterior
- Tree depth auto-adapts based on geometry
- Requires multiple likelihood evaluations per iteration

### 5. Matrix Operations
- Large sparse matrix multiplications for spatial component
- Cholesky decompositions for covariance matrices
- Gradient computations via automatic differentiation

## Progress Indicators

The NUTS sampler outputs progress bars showing:
- Current iteration number
- Acceptance rate (target: ~65-95%)
- Step size
- Tree depth
- Iterations per second

Example output (when visible):
```
Sampling: 100%|██████████| 3000/3000 [25:30<00:00,  1.96it/s]
```

## What Happens After Sampling?

Once MCMC completes, the script automatically:

1. **Computes Posterior Summaries**
   - Parameter means, SDs, quantiles
   - Spatial autocorrelation statistics
   - Variance decomposition

2. **Generates Diagnostics**
   - R-hat (convergence check)
   - Effective sample size
   - Divergence detection
   - Trace plots

3. **Creates Visualizations**
   - Posterior distributions
   - Forest plots
   - Spatial effects maps

4. **Saves Results**
   - MCMC trace (NetCDF)
   - Parameter summaries (CSV)
   - Diagnostic plots (PNG)
   - Spatial effects (CSV)

## Monitoring Progress

To check current status:

```bash
# View last 50 lines of output
tail -50 bayesian_model_output.log

# Continuously monitor (updates every 2 seconds)
watch -n 2 tail -30 bayesian_model_output.log

# Check if still running
pgrep -f hierarchical_bayesian_spatial_model.py
```

## Next Steps After Completion

1. **Analyze Results**:
   ```bash
   python3 analyze_bayesian_results.py
   ```

2. **Inspect Outputs**:
   ```bash
   ls -lh bayesian_spatial_results/
   ```

3. **Load Trace for Custom Analysis**:
   ```python
   import arviz as az
   trace = az.from_netcdf('bayesian_spatial_results/mcmc_trace.nc')
   az.summary(trace)
   ```

## Expected Outcomes

Upon successful completion, you will have:

✅ **Complete posterior distributions** for all 67,786 parameters
✅ **Spatial spillover quantification** (ρ parameter)
✅ **Variance decomposition** across geographic hierarchy
✅ **Fixed effects estimates** with credible intervals
✅ **Spatial random effects** for each of 61,844 SA1 areas
✅ **Convergence diagnostics** (R-hat, ESS)
✅ **Rich visualizations** of results

This enables answering questions like:
- How much does education increase income, accounting for spatial clustering?
- What percentage of income variation is due to regional vs local factors?
- Which SA1 areas have unexpectedly high/low incomes given their characteristics?
- How strong are spatial spillovers between neighboring areas?

---

**Status**: Currently sampling in progress...
**Timestamp**: 2025-11-22
