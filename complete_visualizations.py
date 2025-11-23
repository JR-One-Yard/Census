"""
Complete visualization generation for Bayesian model results
"""
import arviz as az
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

print("Loading saved MCMC trace...")
trace = az.from_netcdf('bayesian_spatial_results/mcmc_trace.nc')
print("✓ Trace loaded")

output_path = Path('bayesian_spatial_results')

# Generate trace plots
print("\nGenerating trace plots...")
axes = az.plot_trace(
    trace,
    var_names=['β', 'ρ', 'σ_sa4', 'σ_sa3', 'σ_sa2', 'σ_spatial', 'σ'],
    figsize=(15, 10)
)
plt.savefig(output_path / 'trace_plots.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved: trace_plots.png")

# Generate posterior plots
print("\nGenerating posterior plots...")
axes = az.plot_posterior(
    trace,
    var_names=['β', 'ρ', 'σ_sa4', 'σ_sa3', 'σ_sa2', 'σ_spatial'],
    figsize=(15, 10)
)
plt.savefig(output_path / 'posterior_plots.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved: posterior_plots.png")

# Generate summary statistics
print("\nGenerating parameter summary...")
summary = az.summary(
    trace,
    var_names=['β', 'ρ', 'σ_sa4', 'σ_sa3', 'σ_sa2', 'σ_spatial', 'σ']
)
summary.to_csv(output_path / 'parameter_summary.csv')
print("✓ Saved: parameter_summary.csv")

print("\n" + "="*60)
print("VISUALIZATION COMPLETE!")
print("="*60)
print("\nGenerated files:")
print("  - trace_plots.png")
print("  - posterior_plots.png")
print("  - parameter_summary.csv")
