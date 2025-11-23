"""
Create infographics for social media post about Bayesian Spatial Model
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['figure.facecolor'] = 'white'

output_dir = Path('social_media_graphics')
output_dir.mkdir(exist_ok=True)

# Color palette
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'accent': '#F18F01',       # Orange
    'success': '#06A77D',      # Green
    'warning': '#C73E1D',      # Red
    'neutral': '#6C757D'       # Gray
}

def create_title_card():
    """Create main title card"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Background gradient
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(gradient, extent=[0, 1, 0, 1], aspect='auto', cmap='Blues', alpha=0.3)

    # Title
    ax.text(0.5, 0.75, '🇦🇺 What Drives Income',
            ha='center', va='center', fontsize=48, fontweight='bold',
            color=COLORS['primary'])
    ax.text(0.5, 0.65, 'Inequality in Australia?',
            ha='center', va='center', fontsize=48, fontweight='bold',
            color=COLORS['primary'])

    # Subtitle
    ax.text(0.5, 0.50, 'A Bayesian Spatial Analysis of 61,844 Neighborhoods',
            ha='center', va='center', fontsize=20, style='italic',
            color=COLORS['neutral'])

    # Key stats
    stats_y = 0.35
    ax.text(0.25, stats_y, '61,844', ha='center', fontsize=32, fontweight='bold',
            color=COLORS['accent'])
    ax.text(0.25, stats_y-0.08, 'Neighborhoods\nAnalyzed', ha='center', fontsize=14,
            color=COLORS['neutral'])

    ax.text(0.5, stats_y, '67,786', ha='center', fontsize=32, fontweight='bold',
            color=COLORS['accent'])
    ax.text(0.5, stats_y-0.08, 'Parameters\nEstimated', ha='center', fontsize=14,
            color=COLORS['neutral'])

    ax.text(0.75, stats_y, '100%', ha='center', fontsize=32, fontweight='bold',
            color=COLORS['success'])
    ax.text(0.75, stats_y-0.08, 'Coverage of\nAustralia', ha='center', fontsize=14,
            color=COLORS['neutral'])

    # Footer
    ax.text(0.5, 0.08, '2021 Australian Census • PyMC Bayesian Modeling',
            ha='center', va='center', fontsize=12,
            color=COLORS['neutral'], style='italic')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / '1_title_card.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created title card")


def create_top_findings():
    """Create top 3 findings infographic"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, '🔍 Three Major Findings',
            ha='center', va='top', fontsize=36, fontweight='bold',
            color=COLORS['primary'])

    # Finding 1
    y1 = 0.80
    circle1 = plt.Circle((0.1, y1), 0.04, color=COLORS['accent'], zorder=10)
    ax.add_patch(circle1)
    ax.text(0.1, y1, '1', ha='center', va='center', fontsize=24,
            fontweight='bold', color='white', zorder=11)

    ax.text(0.18, y1+0.02, 'Employment Dominates',
            ha='left', va='center', fontsize=24, fontweight='bold',
            color=COLORS['primary'])
    ax.text(0.18, y1-0.04, 'β = +0.449 (3× stronger than education)',
            ha='left', va='center', fontsize=16,
            color=COLORS['neutral'])
    ax.text(0.18, y1-0.08, 'Having a job available matters more than qualifications alone',
            ha='left', va='center', fontsize=14, style='italic',
            color=COLORS['neutral'])

    # Bar for visual emphasis
    bar1 = mpatches.FancyBboxPatch((0.15, y1-0.12), 0.449, 0.015,
                                    boxstyle="round,pad=0.005",
                                    facecolor=COLORS['accent'],
                                    edgecolor='none', alpha=0.8)
    ax.add_patch(bar1)

    # Finding 2
    y2 = 0.55
    circle2 = plt.Circle((0.1, y2), 0.04, color=COLORS['secondary'], zorder=10)
    ax.add_patch(circle2)
    ax.text(0.1, y2, '2', ha='center', va='center', fontsize=24,
            fontweight='bold', color='white', zorder=11)

    ax.text(0.18, y2+0.02, 'Regional Location Matters Most',
            ha='left', va='center', fontsize=24, fontweight='bold',
            color=COLORS['primary'])
    ax.text(0.18, y2-0.04, '51% of variation at regional level (only 10% at neighborhood level)',
            ha='left', va='center', fontsize=16,
            color=COLORS['neutral'])
    ax.text(0.18, y2-0.08, 'Living in Sydney vs regional QLD matters more than Bondi vs Parramatta',
            ha='left', va='center', fontsize=14, style='italic',
            color=COLORS['neutral'])

    # Pie chart mini visualization
    sizes = [51, 10, 39]
    colors_pie = [COLORS['secondary'], COLORS['neutral'], '#E0E0E0']
    wedges, texts = ax.pie(sizes, colors=colors_pie, startangle=90,
                           center=(0.85, y2), radius=0.08,
                           wedgeprops=dict(width=0.04))
    ax.text(0.85, y2-0.15, '51% Regional\n10% Local',
            ha='center', va='top', fontsize=11, color=COLORS['neutral'])

    # Finding 3
    y3 = 0.30
    circle3 = plt.Circle((0.1, y3), 0.04, color=COLORS['success'], zorder=10)
    ax.add_patch(circle3)
    ax.text(0.1, y3, '3', ha='center', va='center', fontsize=24,
            fontweight='bold', color='white', zorder=11)

    ax.text(0.18, y3+0.02, 'Geographic Spillovers Are Real',
            ha='left', va='center', fontsize=24, fontweight='bold',
            color=COLORS['primary'])
    ax.text(0.18, y3-0.04, 'ρ = 0.507 (moderate spatial autocorrelation)',
            ha='left', va='center', fontsize=16,
            color=COLORS['neutral'])
    ax.text(0.18, y3-0.08, 'High-income areas cluster near other high-income areas',
            ha='left', va='center', fontsize=14, style='italic',
            color=COLORS['neutral'])

    # Gradient bar showing correlation
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(gradient, extent=[0.15, 0.65, y3-0.14, y3-0.12],
              aspect='auto', cmap='Greens', alpha=0.8)
    ax.text(0.15 + 0.507*(0.65-0.15), y3-0.17, '↑\n50.7%',
            ha='center', va='top', fontsize=11, fontweight='bold',
            color=COLORS['success'])

    # Bottom note
    ax.text(0.5, 0.08, 'All findings have >99% posterior probability',
            ha='center', va='center', fontsize=14,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['success'],
                     alpha=0.2, edgecolor=COLORS['success']),
            color=COLORS['success'], fontweight='bold')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / '2_top_findings.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created top findings")


def create_variance_breakdown():
    """Create variance decomposition infographic"""
    fig, ax = plt.subplots(figsize=(12, 10))

    # Data
    categories = ['Regional\n(SA4)', 'Residual\n(Individual)', 'District\n(SA2)',
                  'Sub-regional\n(SA3)', 'Spatial\nSpillovers']
    values = [51.0, 30.3, 9.9, 6.8, 2.0]
    colors = [COLORS['primary'], COLORS['neutral'], COLORS['secondary'],
              COLORS['accent'], COLORS['success']]

    # Create horizontal bar chart
    y_pos = np.arange(len(categories))
    bars = ax.barh(y_pos, values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(val + 1.5, bar.get_y() + bar.get_height()/2,
                f'{val}%', va='center', fontsize=18, fontweight='bold',
                color=colors[i])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=16, fontweight='bold')
    ax.set_xlabel('% of Total Income Variation', fontsize=18, fontweight='bold')
    ax.set_title('🎯 Where Does Income Inequality Come From?\n',
                 fontsize=28, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add insight box
    ax.text(0.5, 0.95, 'Key Insight: Over 50% of inequality happens at regional scale!',
            transform=ax.transAxes, ha='center', va='top', fontsize=16,
            bbox=dict(boxstyle='round,pad=0.8', facecolor=COLORS['primary'],
                     alpha=0.2, edgecolor=COLORS['primary'], linewidth=2),
            color=COLORS['primary'], fontweight='bold')

    ax.set_xlim(0, 60)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / '3_variance_breakdown.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created variance breakdown")


def create_predictor_comparison():
    """Create predictor effects comparison"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Data
    predictors = ['Employment\nRate', 'Education\n(Year 12)', 'Working Age\nPopulation %']
    effects = [0.449, 0.161, 0.030]
    ci_lower = [0.442, 0.153, 0.024]
    ci_upper = [0.456, 0.169, 0.037]
    colors = [COLORS['accent'], COLORS['primary'], COLORS['secondary']]

    y_pos = np.arange(len(predictors))

    # Create bars
    bars = ax.barh(y_pos, effects, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

    # Add error bars (credible intervals)
    errors = [[effects[i] - ci_lower[i] for i in range(len(effects))],
              [ci_upper[i] - effects[i] for i in range(len(effects))]]
    ax.errorbar(effects, y_pos, xerr=errors, fmt='none', ecolor='black',
                capsize=8, capthick=2, linewidth=2, alpha=0.6)

    # Add value labels with magnitude
    for i, (bar, val) in enumerate(zip(bars, effects)):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                f'β = {val:.3f}', va='center', fontsize=16, fontweight='bold',
                color=colors[i])

        # Add relative strength indicator
        if i == 0:
            ax.text(val + 0.08, bar.get_y() + bar.get_height()/2,
                   '← STRONGEST', va='center', fontsize=14,
                   color=colors[i], style='italic', fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(predictors, fontsize=18, fontweight='bold')
    ax.set_xlabel('Effect Size (Standardized β)', fontsize=18, fontweight='bold')
    ax.set_title('📊 What Predicts Higher Income?\n(with 95% Credible Intervals)',
                 fontsize=26, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add zero reference line
    ax.axvline(0, color='black', linestyle='--', alpha=0.3, linewidth=2)

    # Add note
    ax.text(0.5, -0.15, 'All effects are positive with >99.9% probability',
            transform=ax.transAxes, ha='center', va='top', fontsize=14,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['success'],
                     alpha=0.2, edgecolor=COLORS['success']),
            color=COLORS['success'], fontweight='bold')

    ax.set_xlim(-0.05, 0.55)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / '4_predictor_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created predictor comparison")


def create_spatial_clustering():
    """Create spatial clustering visualization"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create a conceptual network visualization
    np.random.seed(42)

    # Generate example network
    n_nodes = 30
    angles = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)

    # Color nodes based on "income" (example)
    node_values = np.random.beta(2, 2, n_nodes)  # Simulated income distribution

    # Draw connections (moderate clustering)
    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            dist = np.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
            if dist < 0.6:  # Connect nearby nodes
                # Color edge based on similarity
                similarity = 1 - abs(node_values[i] - node_values[j])
                ax.plot([x[i], x[j]], [y[i], y[j]],
                       color=COLORS['neutral'], alpha=similarity*0.3,
                       linewidth=1, zorder=1)

    # Draw nodes
    scatter = ax.scatter(x, y, c=node_values, s=400,
                        cmap='RdYlGn', vmin=0, vmax=1,
                        edgecolor='white', linewidth=2, zorder=10)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Income Level', fontsize=14, fontweight='bold')
    cbar.ax.set_yticklabels(['Low', '', '', '', 'High'], fontsize=12)

    # Title and labels
    ax.set_title('🗺️ Spatial Autocorrelation: ρ = 0.507\n"Moderate Geographic Clustering"',
                fontsize=26, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add annotations
    ax.text(0.02, 0.98, '✓ High-income areas cluster together',
            transform=ax.transAxes, ha='left', va='top', fontsize=14,
            color=COLORS['success'], fontweight='bold')
    ax.text(0.02, 0.93, '✓ But significant individual variation exists',
            transform=ax.transAxes, ha='left', va='top', fontsize=14,
            color=COLORS['success'], fontweight='bold')
    ax.text(0.02, 0.88, '✓ Improving one area helps neighbors',
            transform=ax.transAxes, ha='left', va='top', fontsize=14,
            color=COLORS['success'], fontweight='bold')

    # Add interpretation box
    ax.text(0.5, 0.05, 'Each area is connected to ~9 neighbors on average\nSpatial correlation is moderate, not deterministic',
            transform=ax.transAxes, ha='center', va='bottom', fontsize=12,
            bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                     alpha=0.9, edgecolor=COLORS['primary'], linewidth=2),
            color=COLORS['neutral'])

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis('off')
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(output_dir / '5_spatial_clustering.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created spatial clustering visualization")


def create_methodology_overview():
    """Create methodology overview"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, '🔬 Methodology: State-of-the-Art Bayesian Modeling',
            ha='center', va='top', fontsize=28, fontweight='bold',
            color=COLORS['primary'])

    # Model specs
    y = 0.85
    specs = [
        ('Scale', '61,844 SA1 neighborhoods', COLORS['accent']),
        ('Parameters', '67,786 estimated simultaneously', COLORS['primary']),
        ('Method', 'Hierarchical Bayesian CAR Model', COLORS['secondary']),
        ('Sampler', 'NUTS (No-U-Turn Sampler)', COLORS['success']),
        ('Samples', '4,000 MCMC posterior samples', COLORS['accent']),
        ('Runtime', '8.5 minutes', COLORS['primary']),
        ('Framework', 'PyMC5 + ArviZ + NumPy', COLORS['secondary']),
        ('Data', '2021 Australian Census (ABS)', COLORS['success']),
    ]

    for i, (label, value, color) in enumerate(specs):
        y_pos = y - i * 0.09
        ax.text(0.15, y_pos, f'• {label}:',
                ha='left', va='center', fontsize=16, fontweight='bold',
                color=COLORS['neutral'])
        ax.text(0.4, y_pos, value,
                ha='left', va='center', fontsize=16,
                color=color, fontweight='bold')

    # Why Bayesian box
    box_y = 0.15
    ax.text(0.5, box_y + 0.08, 'Why Bayesian?',
            ha='center', va='top', fontsize=20, fontweight='bold',
            color=COLORS['primary'])

    benefits = [
        '✓ Full uncertainty quantification',
        '✓ Probability statements about effects',
        '✓ Natural handling of spatial dependencies',
        '✓ Hierarchical modeling across 4 levels',
        '✓ No p-value hacking or multiple testing issues'
    ]

    for i, benefit in enumerate(benefits):
        ax.text(0.5, box_y - i * 0.04, benefit,
                ha='center', va='top', fontsize=13,
                color=COLORS['neutral'])

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / '6_methodology.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created methodology overview")


def create_key_stats_grid():
    """Create grid of key statistics"""
    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    stats = [
        ('61,844', 'Neighborhoods\nAnalyzed', COLORS['accent']),
        ('67,786', 'Parameters\nEstimated', COLORS['primary']),
        ('51%', 'Regional\nVariation', COLORS['secondary']),
        ('+0.449', 'Employment\nEffect', COLORS['success']),
        ('0.507', 'Spatial\nCorrelation', COLORS['accent']),
        ('100%', 'Coverage of\nAustralia', COLORS['primary']),
        ('8.5 min', 'Model\nRuntime', COLORS['secondary']),
        ('99.9%', 'Confidence\nin Results', COLORS['success']),
        ('4,000', 'MCMC\nSamples', COLORS['accent']),
    ]

    for idx, (value, label, color) in enumerate(stats):
        row = idx // 3
        col = idx % 3
        ax = fig.add_subplot(gs[row, col])
        ax.axis('off')

        # Background
        rect = mpatches.FancyBboxPatch((0.1, 0.2), 0.8, 0.6,
                                        boxstyle="round,pad=0.05",
                                        facecolor=color, alpha=0.15,
                                        edgecolor=color, linewidth=3)
        ax.add_patch(rect)

        # Value
        ax.text(0.5, 0.6, value,
                ha='center', va='center', fontsize=40, fontweight='bold',
                color=color)

        # Label
        ax.text(0.5, 0.35, label,
                ha='center', va='center', fontsize=14,
                color=COLORS['neutral'], style='italic')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    fig.suptitle('📈 Key Statistics at a Glance',
                 fontsize=32, fontweight='bold', color=COLORS['primary'], y=0.98)

    plt.savefig(output_dir / '7_key_stats.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created key stats grid")


def create_policy_implications():
    """Create policy implications infographic"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, '💡 Policy Implications',
            ha='center', va='top', fontsize=32, fontweight='bold',
            color=COLORS['primary'])

    implications = [
        ('🎯', 'Focus on Regional Development',
         '51% of variation is regional → interventions should target\nbroad economic development, not just individual suburbs'),
        ('💼', 'Employment Over Everything',
         'Job creation is the strongest lever for improving incomes.\nTraining without jobs has limited impact.'),
        ('🎓', 'Education + Opportunity',
         'Education matters, but needs to be coupled with job availability.\nSkills without jobs won\'t move the needle.'),
        ('🌐', 'Leverage Spatial Spillovers',
         'ρ = 0.507 means improving one area helps neighbors.\nEconomic development isn\'t zero-sum.'),
        ('📍', 'Context Matters',
         '30% unexplained variation shows heterogeneity.\nOne-size-fits-all policies won\'t work everywhere.'),
    ]

    y_start = 0.85
    for i, (emoji, title, desc) in enumerate(implications):
        y = y_start - i * 0.17

        # Emoji
        ax.text(0.08, y, emoji, ha='center', va='center', fontsize=40)

        # Title
        ax.text(0.18, y+0.03, title,
                ha='left', va='center', fontsize=18, fontweight='bold',
                color=COLORS['primary'])

        # Description
        ax.text(0.18, y-0.03, desc,
                ha='left', va='top', fontsize=13,
                color=COLORS['neutral'], linespacing=1.5)

        # Separator line
        if i < len(implications) - 1:
            ax.plot([0.1, 0.9], [y-0.08, y-0.08],
                   color=COLORS['neutral'], alpha=0.3, linewidth=1)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / '8_policy_implications.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created policy implications")


def create_summary_card():
    """Create final summary card"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.92, '🎯 The Bottom Line',
            ha='center', va='top', fontsize=36, fontweight='bold',
            color=COLORS['primary'])

    # Main message box
    message = """Income inequality in Australia is fundamentally a
REGIONAL phenomenon driven primarily by
EMPLOYMENT opportunities.

Education matters and spatial spillovers exist,
but 51% of variation happens at the regional scale.

This suggests federal/state policy matters more
than local interventions for income outcomes."""

    ax.text(0.5, 0.70, message,
            ha='center', va='top', fontsize=18, linespacing=2,
            bbox=dict(boxstyle='round,pad=1.5', facecolor=COLORS['primary'],
                     alpha=0.1, edgecolor=COLORS['primary'], linewidth=3),
            color=COLORS['neutral'])

    # The good news
    ax.text(0.5, 0.35, '✅ The Good News',
            ha='center', va='top', fontsize=24, fontweight='bold',
            color=COLORS['success'])

    ax.text(0.5, 0.28, 'Geographic spillovers (ρ = 0.507) mean improving\none area helps its neighbors.',
            ha='center', va='top', fontsize=16,
            color=COLORS['neutral'])

    ax.text(0.5, 0.22, 'Economic development isn\'t zero-sum!',
            ha='center', va='top', fontsize=16, style='italic',
            color=COLORS['success'], fontweight='bold')

    # The challenge
    ax.text(0.5, 0.12, '⚠️ The Challenge',
            ha='center', va='top', fontsize=24, fontweight='bold',
            color=COLORS['warning'])

    ax.text(0.5, 0.05, 'Addressing inequality requires coordinated policy at scale,\nnot just local interventions.',
            ha='center', va='top', fontsize=16, linespacing=1.5,
            color=COLORS['neutral'])

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / '9_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created summary card")


def main():
    """Generate all infographics"""
    print("\n" + "="*60)
    print("Creating Social Media Infographics")
    print("="*60 + "\n")

    create_title_card()
    create_top_findings()
    create_variance_breakdown()
    create_predictor_comparison()
    create_spatial_clustering()
    create_methodology_overview()
    create_key_stats_grid()
    create_policy_implications()
    create_summary_card()

    print("\n" + "="*60)
    print("✓ ALL INFOGRAPHICS CREATED!")
    print("="*60)
    print(f"\nOutput directory: {output_dir}/")
    print("\nGenerated 9 infographics:")
    print("  1. Title card")
    print("  2. Top 3 findings")
    print("  3. Variance breakdown")
    print("  4. Predictor comparison")
    print("  5. Spatial clustering")
    print("  6. Methodology overview")
    print("  7. Key stats grid")
    print("  8. Policy implications")
    print("  9. Summary card")
    print()


if __name__ == '__main__':
    main()
