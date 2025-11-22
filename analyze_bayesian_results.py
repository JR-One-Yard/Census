"""
Analysis Script for Hierarchical Bayesian Spatial Model Results

This script loads and analyzes the results from the Bayesian spatial model,
generating additional insights and visualizations.
"""

import pandas as pd
import numpy as np
import arviz as az
from scipy import sparse
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_results(results_dir='bayesian_spatial_results'):
    """Load all model results"""
    results_path = Path(results_dir)

    print("Loading results...")

    # Load MCMC trace
    trace = az.from_netcdf(results_path / 'mcmc_trace.nc')

    # Load metadata
    with open(results_path / 'model_metadata.json', 'r') as f:
        metadata = json.load(f)

    # Load spatial weights
    W = sparse.load_npz(results_path / 'spatial_weights.npz')

    # Load hierarchy
    hierarchy = pd.read_csv(results_path / 'hierarchy.csv')

    # Load parameter summary
    param_summary = pd.read_csv(results_path / 'parameter_summary.csv', index_col=0)

    print(f"✓ Loaded trace with {trace.posterior.dims['draw']} draws × {trace.posterior.dims['chain']} chains")

    return {
        'trace': trace,
        'metadata': metadata,
        'spatial_weights': W,
        'hierarchy': hierarchy,
        'param_summary': param_summary
    }


def analyze_fixed_effects(results):
    """Analyze fixed effects (β coefficients)"""
    print("\n" + "="*80)
    print("FIXED EFFECTS ANALYSIS")
    print("="*80)

    trace = results['trace']
    metadata = results['metadata']
    predictor_names = metadata['predictors']

    # Extract posterior samples
    β_samples = trace.posterior['β'].values  # shape: (chains, draws, n_predictors)

    # Compute summary statistics
    print("\nPosterior summaries:")
    print("-" * 80)
    print(f"{'Variable':<30} {'Mean':>10} {'SD':>10} {'95% CI':>25} {'Prob>0':>10}")
    print("-" * 80)

    for i, var_name in enumerate(predictor_names):
        samples = β_samples[:, :, i].flatten()
        mean = np.mean(samples)
        std = np.std(samples)
        ci_lower, ci_upper = np.percentile(samples, [2.5, 97.5])
        prob_positive = np.mean(samples > 0)

        print(f"{var_name:<30} {mean:>10.4f} {std:>10.4f} [{ci_lower:>7.4f}, {ci_upper:>7.4f}] {prob_positive:>10.3f}")

    # Create forest plot
    fig, ax = plt.subplots(figsize=(10, 6))
    az.plot_forest(
        trace,
        var_names=['β'],
        combined=True,
        figsize=(10, 6),
        ax=ax
    )

    # Update y-axis labels with predictor names
    ax.set_yticklabels(predictor_names)
    ax.set_xlabel('Effect Size (standardized)', fontsize=12)
    ax.set_title('Fixed Effects Posterior Distributions', fontsize=14, fontweight='bold')
    ax.axvline(0, color='red', linestyle='--', alpha=0.5, linewidth=1)

    plt.tight_layout()
    plt.savefig('bayesian_spatial_results/fixed_effects_forest.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n✓ Forest plot saved: fixed_effects_forest.png")


def analyze_spatial_autocorrelation(results):
    """Analyze spatial autocorrelation parameter"""
    print("\n" + "="*80)
    print("SPATIAL AUTOCORRELATION ANALYSIS")
    print("="*80)

    trace = results['trace']

    # Extract ρ samples
    ρ_samples = trace.posterior['ρ'].values.flatten()

    print(f"\nSpatial autocorrelation parameter (ρ):")
    print(f"  Mean: {np.mean(ρ_samples):.4f}")
    print(f"  Median: {np.median(ρ_samples):.4f}")
    print(f"  SD: {np.std(ρ_samples):.4f}")
    print(f"  95% CI: [{np.percentile(ρ_samples, 2.5):.4f}, {np.percentile(ρ_samples, 97.5):.4f}]")

    # Interpret
    mean_ρ = np.mean(ρ_samples)
    if mean_ρ < 0.3:
        interpretation = "WEAK spatial spillovers"
    elif mean_ρ < 0.7:
        interpretation = "MODERATE spatial spillovers"
    else:
        interpretation = "STRONG spatial spillovers"

    print(f"\n  Interpretation: {interpretation}")

    # Plot posterior distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    az.plot_posterior(
        trace,
        var_names=['ρ'],
        point_estimate='mean',
        hdi_prob=0.95,
        ax=ax
    )
    ax.set_title('Spatial Autocorrelation Parameter (ρ)', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('bayesian_spatial_results/spatial_autocorrelation.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✓ Plot saved: spatial_autocorrelation.png")


def variance_decomposition(results):
    """Decompose variance across hierarchical levels"""
    print("\n" + "="*80)
    print("VARIANCE DECOMPOSITION")
    print("="*80)

    trace = results['trace']

    # Extract variance components
    σ_sa4_samples = trace.posterior['σ_sa4'].values.flatten() ** 2
    σ_sa3_samples = trace.posterior['σ_sa3'].values.flatten() ** 2
    σ_sa2_samples = trace.posterior['σ_sa2'].values.flatten() ** 2
    σ_spatial_samples = trace.posterior['σ_spatial'].values.flatten() ** 2
    σ_samples = trace.posterior['σ'].values.flatten() ** 2

    # Total variance
    total_var = σ_sa4_samples + σ_sa3_samples + σ_sa2_samples + σ_spatial_samples + σ_samples

    # Variance partition coefficients
    vpc_sa4 = σ_sa4_samples / total_var * 100
    vpc_sa3 = σ_sa3_samples / total_var * 100
    vpc_sa2 = σ_sa2_samples / total_var * 100
    vpc_spatial = σ_spatial_samples / total_var * 100
    vpc_residual = σ_samples / total_var * 100

    print("\nVariance Partition Coefficients (% of total variance):")
    print("-" * 60)
    print(f"{'Level':<20} {'Mean %':>15} {'95% CI':>25}")
    print("-" * 60)

    components = [
        ('SA4 (National)', vpc_sa4),
        ('SA3 (Regional)', vpc_sa3),
        ('SA2 (District)', vpc_sa2),
        ('Spatial', vpc_spatial),
        ('Residual', vpc_residual)
    ]

    for name, vpc in components:
        mean_vpc = np.mean(vpc)
        ci_lower, ci_upper = np.percentile(vpc, [2.5, 97.5])
        print(f"{name:<20} {mean_vpc:>15.2f}% [{ci_lower:>7.2f}%, {ci_upper:>7.2f}%]")

    # Create pie chart
    mean_vpcs = [np.mean(vpc) for _, vpc in components]
    labels = [name for name, _ in components]

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = sns.color_palette("Set3", len(components))

    wedges, texts, autotexts = ax.pie(
        mean_vpcs,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 11}
    )

    ax.set_title('Variance Decomposition Across Hierarchical Levels',
                 fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('bayesian_spatial_results/variance_decomposition.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n✓ Plot saved: variance_decomposition.png")


def convergence_diagnostics(results):
    """Check MCMC convergence"""
    print("\n" + "="*80)
    print("CONVERGENCE DIAGNOSTICS")
    print("="*80)

    trace = results['trace']

    # R-hat
    rhat = az.rhat(trace)

    print("\nR-hat statistics (should be < 1.01):")
    print("-" * 60)

    for var in ['β', 'ρ', 'σ_sa4', 'σ_sa3', 'σ_sa2', 'σ_spatial', 'σ']:
        if var in rhat:
            rhat_vals = rhat[var].values
            if rhat_vals.size > 1:
                max_rhat = np.max(rhat_vals)
                mean_rhat = np.mean(rhat_vals)
                print(f"  {var:<15} max={max_rhat:.4f}, mean={mean_rhat:.4f}")
            else:
                print(f"  {var:<15} {float(rhat_vals):.4f}")

    # Effective sample size
    ess_bulk = az.ess(trace, method='bulk')
    ess_tail = az.ess(trace, method='tail')

    print("\nEffective Sample Size (should be > 400):")
    print("-" * 60)
    print(f"{'Variable':<15} {'Bulk ESS':>15} {'Tail ESS':>15}")
    print("-" * 60)

    for var in ['β', 'ρ', 'σ_sa4', 'σ_sa3', 'σ_sa2', 'σ_spatial', 'σ']:
        if var in ess_bulk:
            bulk_vals = ess_bulk[var].values
            tail_vals = ess_tail[var].values

            if bulk_vals.size > 1:
                bulk_min = np.min(bulk_vals)
                tail_min = np.min(tail_vals)
            else:
                bulk_min = float(bulk_vals)
                tail_min = float(tail_vals)

            print(f"{var:<15} {bulk_min:>15.0f} {tail_min:>15.0f}")

    # Check for divergences
    divergences = trace.sample_stats.diverging.sum().values
    print(f"\nNumber of divergent transitions: {divergences}")

    if divergences == 0:
        print("✓ No divergences detected - excellent!")
    else:
        print("⚠ Divergences detected - consider increasing target_accept or reparameterizing")


def spatial_random_effects_map(results):
    """Analyze spatial random effects"""
    print("\n" + "="*80)
    print("SPATIAL RANDOM EFFECTS ANALYSIS")
    print("="*80)

    trace = results['trace']
    hierarchy = results['hierarchy']

    # Extract spatial random effects (φ)
    φ_samples = trace.posterior['φ'].values  # (chains, draws, n_sa1)
    φ_mean = φ_samples.mean(axis=(0, 1))  # Mean across chains and draws
    φ_sd = φ_samples.std(axis=(0, 1))

    # Create summary DataFrame
    spatial_effects = pd.DataFrame({
        'sa1_code': hierarchy['sa1_code'].values,
        'sa2_code': hierarchy['sa2_code'].values,
        'sa3_code': hierarchy['sa3_code'].values,
        'sa4_code': hierarchy['sa4_code'].values,
        'spatial_effect_mean': φ_mean,
        'spatial_effect_sd': φ_sd
    })

    # Sort by spatial effect
    spatial_effects = spatial_effects.sort_values('spatial_effect_mean', ascending=False)

    print("\nTop 10 SA1 areas with highest positive spatial effects:")
    print(spatial_effects.head(10)[['sa1_code', 'sa2_code', 'spatial_effect_mean', 'spatial_effect_sd']])

    print("\nTop 10 SA1 areas with highest negative spatial effects:")
    print(spatial_effects.tail(10)[['sa1_code', 'sa2_code', 'spatial_effect_mean', 'spatial_effect_sd']])

    # Save full results
    spatial_effects.to_csv('bayesian_spatial_results/spatial_effects_sa1.csv', index=False)
    print("\n✓ Saved: spatial_effects_sa1.csv")

    # Plot distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(φ_mean, bins=100, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero effect')
    ax.set_xlabel('Spatial Random Effect (φ)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Spatial Random Effects Across 61,844 SA1 Areas',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('bayesian_spatial_results/spatial_effects_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✓ Plot saved: spatial_effects_distribution.png")


def generate_summary_report(results):
    """Generate comprehensive summary report"""
    print("\n" + "="*80)
    print("GENERATING SUMMARY REPORT")
    print("="*80)

    trace = results['trace']
    metadata = results['metadata']

    report = []
    report.append("# Hierarchical Bayesian Spatial Model - Summary Report\n")
    report.append(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # Model configuration
    report.append("## Model Configuration\n")
    report.append(f"- Outcome variable: {metadata['outcome_var']}\n")
    report.append(f"- Predictors: {', '.join(metadata['predictors'])}\n")
    report.append(f"- Sample size: {metadata['n_sa1']:,} SA1 areas\n")
    report.append(f"- Hierarchical levels:\n")
    report.append(f"  - SA4: {metadata['n_sa4']:,} areas\n")
    report.append(f"  - SA3: {metadata['n_sa3']:,} areas\n")
    report.append(f"  - SA2: {metadata['n_sa2']:,} areas\n")
    report.append(f"  - SA1: {metadata['n_sa1']:,} areas\n")
    report.append(f"- MCMC: {metadata['n_samples']:,} samples × {metadata['n_chains']} chains\n\n")

    # Key findings
    report.append("## Key Findings\n\n")

    # Fixed effects
    β_samples = trace.posterior['β'].values
    report.append("### Fixed Effects\n")
    for i, var in enumerate(metadata['predictors']):
        samples = β_samples[:, :, i].flatten()
        mean = np.mean(samples)
        ci_lower, ci_upper = np.percentile(samples, [2.5, 97.5])
        prob_pos = np.mean(samples > 0)

        direction = "increases" if mean > 0 else "decreases"
        report.append(f"- **{var}**: {direction} median income "
                     f"(β = {mean:.4f}, 95% CI [{ci_lower:.4f}, {ci_upper:.4f}], "
                     f"P(β>0) = {prob_pos:.3f})\n")

    # Spatial autocorrelation
    ρ_samples = trace.posterior['ρ'].values.flatten()
    ρ_mean = np.mean(ρ_samples)
    ρ_ci = np.percentile(ρ_samples, [2.5, 97.5])
    report.append(f"\n### Spatial Autocorrelation\n")
    report.append(f"- ρ = {ρ_mean:.4f} (95% CI [{ρ_ci[0]:.4f}, {ρ_ci[1]:.4f}])\n")

    if ρ_mean < 0.3:
        report.append("- Interpretation: WEAK spatial spillovers\n")
    elif ρ_mean < 0.7:
        report.append("- Interpretation: MODERATE spatial spillovers\n")
    else:
        report.append("- Interpretation: STRONG spatial spillovers\n")

    # Save report
    with open('bayesian_spatial_results/SUMMARY_REPORT.md', 'w') as f:
        f.writelines(report)

    print("✓ Summary report saved: SUMMARY_REPORT.md")


def main():
    """Main analysis pipeline"""
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "HIERARCHICAL BAYESIAN SPATIAL MODEL - RESULTS ANALYSIS".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80 + "\n")

    # Load results
    results = load_results()

    # Run analyses
    analyze_fixed_effects(results)
    analyze_spatial_autocorrelation(results)
    variance_decomposition(results)
    convergence_diagnostics(results)
    spatial_random_effects_map(results)
    generate_summary_report(results)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nAll results saved to: bayesian_spatial_results/")
    print("\nGenerated files:")
    print("  1. fixed_effects_forest.png - Forest plot of predictor effects")
    print("  2. spatial_autocorrelation.png - Spatial autocorrelation posterior")
    print("  3. variance_decomposition.png - Variance across hierarchy levels")
    print("  4. spatial_effects_sa1.csv - Spatial random effects for each SA1")
    print("  5. spatial_effects_distribution.png - Distribution of spatial effects")
    print("  6. SUMMARY_REPORT.md - Executive summary of findings")
    print()


if __name__ == '__main__':
    main()
