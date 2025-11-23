#!/usr/bin/env python3
"""
Advanced Step 4: Investment Scenario Modeling & Impact Simulation
===================================================================
Simulates the impact of different social housing investment allocations:

1. Baseline Scenario: No additional investment
2. Budget-Constrained Scenario: $2B investment (targeted)
3. Moderate Investment: $5B investment (mixed strategy)
4. Major Investment: $13B investment (comprehensive)
5. Custom Geographic Strategy: State-focused allocations

Measures impact on:
- Rental stress reduction
- Households assisted
- Cost per household
- Geographic coverage
- ROI metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ADVANCED ANALYSIS STEP 4: INVESTMENT SCENARIO MODELING")
print("=" * 80)
print()

# Configuration
INPUT_FILE = Path("rental_stress_outputs/transport_accessibility/sa1_with_transport_accessibility.csv")
OUTPUT_DIR = Path("rental_stress_outputs/scenario_modeling")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 12)

# Investment parameters
DWELLING_COST = 56000  # Average cost per social housing dwelling (simplified)
HOUSEHOLDS_PER_DWELLING = 1  # Assuming 1:1 ratio

# Load data
print("Step 1: Loading comprehensive SA1 dataset...")
df = pd.read_csv(INPUT_FILE)
print(f"✓ Loaded {len(df):,} SA1 areas with full metrics")
print()

# ============================================================================
# Define Investment Scenarios
# ============================================================================
print("Step 2: Defining investment scenarios...")

scenarios = {
    'Scenario 1: Baseline (No Investment)': {
        'budget': 0,
        'dwellings': 0,
        'strategy': 'none',
        'description': 'Current state, no new construction'
    },

    'Scenario 2: Budget-Constrained ($2B)': {
        'budget': 2_000_000_000,
        'dwellings': 35_714,  # $2B / $56k
        'strategy': 'highest_priority',
        'description': 'Target highest priority areas only'
    },

    'Scenario 3: Moderate Investment ($5B)': {
        'budget': 5_000_000_000,
        'dwellings': 89_286,  # $5B / $56k
        'strategy': 'mixed',
        'description': 'Mix of high priority + emerging hotspots'
    },

    'Scenario 4: Major Investment ($13B)': {
        'budget': 13_000_000_000,
        'dwellings': 232_143,  # $13B / $56k
        'strategy': 'comprehensive',
        'description': 'Address full supply-demand gap'
    },

    'Scenario 5: Accessibility-Focused ($5B)': {
        'budget': 5_000_000_000,
        'dwellings': 89_286,
        'strategy': 'accessibility',
        'description': 'Prioritize areas near employment centers'
    },

    'Scenario 6: Equity-Focused ($5B)': {
        'budget': 5_000_000_000,
        'dwellings': 89_286,
        'strategy': 'equity',
        'description': 'Prioritize highest low-income concentration'
    },
}

print("Investment Scenarios Defined:")
for scenario_name, params in scenarios.items():
    print(f"  {scenario_name}")
    print(f"    Budget: ${params['budget']:,.0f}")
    print(f"    Dwellings: {params['dwellings']:,}")
    print(f"    Strategy: {params['strategy']}")
    print()

# ============================================================================
# Simulate Investment Allocation
# ============================================================================
print("Step 3: Simulating investment allocations...")

def allocate_investment(df, dwellings, strategy):
    """
    Allocate dwellings to SA1 areas based on strategy.
    Returns dataframe with allocation amounts.
    """
    df_scenario = df.copy()
    df_scenario['new_dwellings'] = 0

    if dwellings == 0:
        return df_scenario

    remaining_dwellings = dwellings

    if strategy == 'highest_priority':
        # Allocate to highest priority areas first
        # Prioritize by investment_priority_score
        df_sorted = df_scenario.sort_values('investment_priority_score', ascending=False)

        for idx, row in df_sorted.iterrows():
            # Allocate up to the gap (or max 50 per SA1 to avoid over-concentration)
            gap = max(0, row['public_housing_gap'])
            allocation = min(gap, 50, remaining_dwellings)

            df_scenario.at[idx, 'new_dwellings'] = allocation
            remaining_dwellings -= allocation

            if remaining_dwellings <= 0:
                break

    elif strategy == 'mixed':
        # 60% to high priority, 40% to emerging hotspots
        high_priority_dwellings = int(dwellings * 0.6)
        emerging_dwellings = dwellings - high_priority_dwellings

        # High priority allocation
        df_sorted = df_scenario[
            df_scenario['investment_priority_score'] >= 40
        ].sort_values('investment_priority_score', ascending=False)

        for idx, row in df_sorted.head(1000).iterrows():
            gap = max(0, row['public_housing_gap'])
            allocation = min(gap, 40, high_priority_dwellings)
            df_scenario.at[idx, 'new_dwellings'] = allocation
            high_priority_dwellings -= allocation

        # Emerging hotspots allocation
        df_emerging = df_scenario[
            (df_scenario['new_dwellings'] == 0) &
            (df_scenario['rental_stress_score'] >= 25) &
            (df_scenario['rental_stress_score'] < 50)
        ].sort_values('rental_stress_score', ascending=False)

        for idx, row in df_emerging.head(500).iterrows():
            allocation = min(20, emerging_dwellings)
            df_scenario.at[idx, 'new_dwellings'] = allocation
            emerging_dwellings -= allocation

    elif strategy == 'comprehensive':
        # Allocate proportionally to gap across all stressed areas
        stressed = df_scenario[df_scenario['public_housing_gap'] > 0].copy()
        total_gap = stressed['public_housing_gap'].sum()

        if total_gap > 0:
            stressed['allocation_pct'] = stressed['public_housing_gap'] / total_gap
            stressed['new_dwellings'] = (stressed['allocation_pct'] * dwellings).round().astype(int)

            # Update main dataframe
            for idx, row in stressed.iterrows():
                df_scenario.at[idx, 'new_dwellings'] = row['new_dwellings']

    elif strategy == 'accessibility':
        # Prioritize areas with good employment access + rental stress
        df_sorted = df_scenario[
            (df_scenario['employment_accessibility_score'] >= 40) &
            (df_scenario['rental_stress_score'] >= 25)
        ].sort_values('optimal_location_score', ascending=False)

        for idx, row in df_sorted.head(2000).iterrows():
            allocation = min(50, remaining_dwellings)
            df_scenario.at[idx, 'new_dwellings'] = allocation
            remaining_dwellings -= allocation

            if remaining_dwellings <= 0:
                break

    elif strategy == 'equity':
        # Prioritize highest low-income concentration + stress
        df_sorted = df_scenario[
            (df_scenario['low_income_pct'] >= 40) &
            (df_scenario['rental_stress_score'] >= 25)
        ].sort_values(['low_income_pct', 'rental_stress_score'], ascending=False)

        for idx, row in df_sorted.head(2000).iterrows():
            allocation = min(50, remaining_dwellings)
            df_scenario.at[idx, 'new_dwellings'] = allocation
            remaining_dwellings -= allocation

            if remaining_dwellings <= 0:
                break

    return df_scenario

# Simulate each scenario
results = {}

for scenario_name, params in scenarios.items():
    print(f"\n  Simulating: {scenario_name}...")

    # Allocate dwellings
    df_scenario = allocate_investment(df, params['dwellings'], params['strategy'])

    # Calculate post-investment metrics
    df_scenario['new_total_public_housing'] = (
        df_scenario['public_housing_dwellings'] + df_scenario['new_dwellings']
    )

    df_scenario['new_public_housing_rate'] = (
        df_scenario['new_total_public_housing'] / df_scenario['total_dwellings'] * 100
    )

    df_scenario['new_public_housing_gap'] = (
        df_scenario['estimated_demand'] - df_scenario['new_total_public_housing']
    )

    # Calculate impact metrics
    sa1s_receiving_investment = (df_scenario['new_dwellings'] > 0).sum()
    total_allocated = df_scenario['new_dwellings'].sum()
    households_assisted = total_allocated  # 1:1 ratio assumption

    # Estimate stress reduction
    # Simple model: each dwelling reduces stress for low-income households
    stress_reduction_factor = min(1.0, total_allocated / df['estimated_demand'].sum())
    initial_stressed = df['rental_stress'].sum()
    projected_stressed = int(initial_stressed * (1 - stress_reduction_factor * 0.15))  # 15% max reduction
    stress_reduction = initial_stressed - projected_stressed

    # Store results
    results[scenario_name] = {
        'dataframe': df_scenario,
        'dwellings_allocated': total_allocated,
        'sa1s_receiving': sa1s_receiving_investment,
        'households_assisted': households_assisted,
        'cost': params['budget'],
        'cost_per_household': params['budget'] / households_assisted if households_assisted > 0 else 0,
        'stress_reduction': stress_reduction,
        'stressed_sa1s_before': initial_stressed,
        'stressed_sa1s_after': projected_stressed,
        'gap_closed_pct': (total_allocated / df['public_housing_gap'].sum() * 100) if df['public_housing_gap'].sum() > 0 else 0
    }

    print(f"    → {sa1s_receiving_investment:,} SA1s receive investment")
    print(f"    → {households_assisted:,} households assisted")
    print(f"    → {stress_reduction:,} SA1s exit stress (projected)")
    print(f"    → {results[scenario_name]['gap_closed_pct']:.1f}% of gap closed")

print()

# ============================================================================
# Create Comparative Visualizations
# ============================================================================
print("Step 4: Creating scenario comparison visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Investment Scenario Comparison & Impact Analysis', fontsize=16, fontweight='bold')

# Plot 1: Budget allocation
ax1 = axes[0, 0]
budgets = [params['budget'] / 1_000_000_000 for params in scenarios.values()]
scenario_labels = [f"S{i+1}" for i in range(len(scenarios))]
bars = ax1.bar(scenario_labels, budgets, color='steelblue', edgecolor='black')
ax1.set_ylabel('Budget ($ Billions)')
ax1.set_title('Investment Budget by Scenario')
ax1.grid(True, axis='y', alpha=0.3)

for i, (bar, value) in enumerate(zip(bars, budgets)):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'${value:.1f}B', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 2: Dwellings delivered
ax2 = axes[0, 1]
dwellings = [results[name]['dwellings_allocated'] for name in results.keys()]
bars = ax2.bar(scenario_labels, dwellings, color='darkgreen', edgecolor='black')
ax2.set_ylabel('Dwellings Delivered')
ax2.set_title('New Social Housing Dwellings')
ax2.grid(True, axis='y', alpha=0.3)

for i, (bar, value) in enumerate(zip(bars, dwellings)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f'{value:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 3: Households assisted
ax3 = axes[0, 2]
households = [results[name]['households_assisted'] for name in results.keys()]
bars = ax3.bar(scenario_labels, households, color='purple', edgecolor='black')
ax3.set_ylabel('Households Assisted')
ax3.set_title('Households Receiving Housing')
ax3.grid(True, axis='y', alpha=0.3)

for i, (bar, value) in enumerate(zip(bars, households)):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f'{value:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 4: Stress reduction
ax4 = axes[1, 0]
stress_before = [results[name]['stressed_sa1s_before'] for name in results.keys()]
stress_after = [results[name]['stressed_sa1s_after'] for name in results.keys()]

x = np.arange(len(scenario_labels))
width = 0.35

bars1 = ax4.bar(x - width/2, stress_before, width, label='Before', color='red', alpha=0.7)
bars2 = ax4.bar(x + width/2, stress_after, width, label='After', color='green', alpha=0.7)

ax4.set_ylabel('Stressed SA1 Areas')
ax4.set_title('Rental Stress Reduction Impact')
ax4.set_xticks(x)
ax4.set_xticklabels(scenario_labels)
ax4.legend()
ax4.grid(True, axis='y', alpha=0.3)

# Plot 5: Cost per household
ax5 = axes[1, 1]
cost_per_hh = [results[name]['cost_per_household'] / 1000 for name in results.keys()]
cost_per_hh_clean = [c if c > 0 else 0 for c in cost_per_hh]
bars = ax5.bar(scenario_labels, cost_per_hh_clean, color='orange', edgecolor='black')
ax5.set_ylabel('Cost per Household ($1000s)')
ax5.set_title('Cost Efficiency')
ax5.grid(True, axis='y', alpha=0.3)

for i, (bar, value) in enumerate(zip(bars, cost_per_hh_clean)):
    if value > 0:
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${value:.0f}k', ha='center', va='bottom', fontsize=9)

# Plot 6: Gap closure percentage
ax6 = axes[1, 2]
gap_closed = [results[name]['gap_closed_pct'] for name in results.keys()]
bars = ax6.bar(scenario_labels, gap_closed, color='darkblue', edgecolor='black')
ax6.set_ylabel('Gap Closure (%)')
ax6.set_title('Supply-Demand Gap Closed')
ax6.axhline(100, color='red', linestyle='--', linewidth=2, label='Full Gap')
ax6.legend()
ax6.grid(True, axis='y', alpha=0.3)

for i, (bar, value) in enumerate(zip(bars, gap_closed)):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            f'{value:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
viz_file = OUTPUT_DIR / 'scenario_comparison_analysis.png'
plt.savefig(viz_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {viz_file}")
plt.close()

# ============================================================================
# Export Scenario Results
# ============================================================================
print("\nStep 5: Exporting scenario modeling results...")

# Export each scenario's allocation
for scenario_name, result in results.items():
    scenario_key = scenario_name.split(':')[0].replace(' ', '_').lower()
    scenario_file = OUTPUT_DIR / f"{scenario_key}_allocation.csv"

    # Export SA1s receiving investment
    invested_sa1s = result['dataframe'][result['dataframe']['new_dwellings'] > 0]
    invested_sa1s.to_csv(scenario_file, index=False)
    print(f"✓ Saved: {scenario_file} ({len(invested_sa1s):,} SA1s)")

# Summary comparison table
summary_df = pd.DataFrame({
    'Scenario': list(results.keys()),
    'Budget ($B)': [r['cost'] / 1_000_000_000 for r in results.values()],
    'Dwellings': [r['dwellings_allocated'] for r in results.values()],
    'SA1s Receiving': [r['sa1s_receiving'] for r in results.values()],
    'Households Assisted': [r['households_assisted'] for r in results.values()],
    'Cost per HH ($)': [r['cost_per_household'] for r in results.values()],
    'Stress Reduction (SA1s)': [r['stress_reduction'] for r in results.values()],
    'Gap Closed (%)': [r['gap_closed_pct'] for r in results.values()]
})

summary_file = OUTPUT_DIR / "scenario_comparison_summary.csv"
summary_df.to_csv(summary_file, index=False)
print(f"✓ Saved: {summary_file}")

# ============================================================================
# Generate Scenario Modeling Report
# ============================================================================
print("\nStep 6: Generating scenario modeling report...")

report_file = OUTPUT_DIR / "SCENARIO_MODELING_REPORT.md"
with open(report_file, 'w') as f:
    f.write("# Investment Scenario Modeling & Impact Simulation\n\n")
    f.write("---\n\n")

    f.write("## Executive Summary\n\n")
    f.write("Modeled 6 investment scenarios ranging from $0 (baseline) to $13B (comprehensive) ")
    f.write("to assess impact on rental stress and housing affordability.\n\n")

    f.write("---\n\n")
    f.write("## Scenario Comparison\n\n")

    for scenario_name, params in scenarios.items():
        result = results[scenario_name]

        f.write(f"### {scenario_name}\n")
        f.write(f"*{params['description']}*\n\n")
        f.write(f"**Budget**: ${result['cost']:,.0f} (${result['cost']/1e9:.1f}B)\n")
        f.write(f"**Strategy**: {params['strategy']}\n\n")

        f.write("**Impact Metrics**:\n")
        f.write(f"- Dwellings Delivered: **{result['dwellings_allocated']:,}**\n")
        f.write(f"- SA1 Areas Receiving Investment: **{result['sa1s_receiving']:,}**\n")
        f.write(f"- Households Directly Assisted: **{result['households_assisted']:,}**\n")
        f.write(f"- Cost per Household: **${result['cost_per_household']:,.0f}**\n")
        f.write(f"- Projected Stress Reduction: **{result['stress_reduction']:,} SA1s**\n")
        f.write(f"- Supply Gap Closed: **{result['gap_closed_pct']:.1f}%**\n\n")

        f.write("---\n\n")

    f.write("## Key Findings\n\n")

    best_roi = min(results.items(), key=lambda x: x[1]['cost_per_household'] if x[1]['cost_per_household'] > 0 else float('inf'))
    most_impact = max(results.items(), key=lambda x: x[1]['stress_reduction'])

    f.write(f"### Best Cost Efficiency\n")
    f.write(f"**{best_roi[0]}** achieves lowest cost per household at ${best_roi[1]['cost_per_household']:,.0f}\n\n")

    f.write(f"### Greatest Impact\n")
    f.write(f"**{most_impact[0]}** reduces stress in {most_impact[1]['stress_reduction']:,} SA1s\n\n")

    f.write("### Required Investment for Full Gap Closure\n")
    total_gap = df['public_housing_gap'].sum()
    required_budget = total_gap * DWELLING_COST
    f.write(f"To fully close the supply-demand gap:\n")
    f.write(f"- **{total_gap:,.0f} dwellings** needed\n")
    f.write(f"- **${required_budget:,.0f}** (${required_budget/1e9:.1f}B) total investment required\n\n")

    f.write("---\n\n")
    f.write("## Policy Recommendations\n\n")

    f.write("### Short-Term (2-3 years)\n")
    f.write("- Implement **Scenario 2 or 3** ($2-5B)\n")
    f.write("- Focus on highest priority areas\n")
    f.write("- Quick wins to demonstrate effectiveness\n\n")

    f.write("### Medium-Term (3-5 years)\n")
    f.write("- Scale up to **Scenario 4** ($13B)\n")
    f.write("- Comprehensive gap closure\n")
    f.write("- Sustainable funding mechanism\n\n")

    f.write("### Strategy Optimization\n")
    f.write("- **Accessibility-focused** strategy maximizes resident outcomes\n")
    f.write("- Locations near employment reduce transport costs\n")
    f.write("- **Equity-focused** strategy addresses most vulnerable communities\n")
    f.write("- Mixed strategy balances efficiency and equity\n\n")

print(f"✓ Saved: {report_file}")
print()

print("=" * 80)
print("SCENARIO MODELING COMPLETE!")
print("=" * 80)
print()

print("📊 Outputs Generated:")
print("  1. scenario_comparison_analysis.png - Visual comparison of all scenarios")
print("  2. scenario_1_baseline_(no_investment)_allocation.csv")
print("  3. scenario_2_budget-constrained_($2b)_allocation.csv")
print("  4. scenario_3_moderate_investment_($5b)_allocation.csv")
print("  5. scenario_4_major_investment_($13b)_allocation.csv")
print("  6. scenario_5_accessibility-focused_($5b)_allocation.csv")
print("  7. scenario_6_equity-focused_($5b)_allocation.csv")
print("  8. scenario_comparison_summary.csv - Summary table")
print("  9. SCENARIO_MODELING_REPORT.md - Full report")
print()

print(f"All files saved to: {OUTPUT_DIR}/")
print()

print("💡 Key Insights:")
best_scenario = max(results.items(), key=lambda x: x[1]['gap_closed_pct'] if x[1]['cost'] > 0 else 0)
print(f"  • Best scenario: {best_scenario[0]}")
print(f"  • Closes {best_scenario[1]['gap_closed_pct']:.1f}% of supply gap")
print(f"  • Assists {best_scenario[1]['households_assisted']:,} households")
print(f"  • Reduces stress in {best_scenario[1]['stress_reduction']:,} SA1s")
print()
