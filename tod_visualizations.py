#!/usr/bin/env python3
"""
TOD Analysis - Comprehensive Visualization Suite
================================================
Generates static and interactive visualizations for TOD analysis results

Visualizations Created:
1. State-level comparison charts
2. TOD score distribution heatmaps
3. Modal split visualizations
4. Priority area maps
5. Corridor opportunity charts
6. Economic impact visualizations
7. Interactive Plotly charts

Author: Claude Code
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 100)
print("TOD ANALYSIS - COMPREHENSIVE VISUALIZATION SUITE")
print("=" * 100)

# Create output directory
import os
os.makedirs('visualizations', exist_ok=True)
print("\n✓ Created 'visualizations/' directory for output files\n")

# ============================================================================
# LOAD DATA
# ============================================================================

print("[1/10] Loading TOD analysis datasets...")
df_complete = pd.read_csv('tod_complete_sa1_analysis.csv')
df_state = pd.read_csv('tod_state_level_analysis.csv')
df_top_1000 = pd.read_csv('tod_top_1000_opportunities.csv')
df_corridors = pd.read_csv('tod_transit_corridors.csv')
df_hub_spoke = pd.read_csv('tod_hub_spoke_analysis.csv')
df_pain_points = pd.read_csv('tod_commute_pain_points.csv')

# Add state to complete dataset
def extract_state(sa1_code):
    state_map = {1: 'NSW', 2: 'VIC', 3: 'QLD', 4: 'SA', 5: 'WA',
                 6: 'TAS', 7: 'NT', 8: 'ACT', 9: 'Other'}
    return state_map.get(int(str(sa1_code)[0]), 'Unknown')

df_complete['state'] = df_complete['SA1_CODE_2021'].apply(extract_state)
df_top_1000['state'] = df_top_1000['SA1_CODE_2021'].apply(extract_state)
df_corridors['state'] = df_corridors['SA1_CODE_2021'].apply(extract_state)

print(f"  ✓ Loaded {len(df_complete):,} complete SA1 records")
print(f"  ✓ Loaded {len(df_state)} state records")
print(f"  ✓ Loaded {len(df_top_1000):,} top opportunities")

# ============================================================================
# VISUALIZATION 1: STATE-LEVEL COMPARISON DASHBOARD
# ============================================================================

print("\n[2/10] Creating state-level comparison dashboard...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('TOD Analysis - State/Territory Comparison', fontsize=20, fontweight='bold')

# Sort states by car dependency
df_state_sorted = df_state.sort_values('Avg_Car_Dependency', ascending=False)

# 1. Car Dependency by State
ax1 = axes[0, 0]
colors = plt.cm.RdYlGn_r(df_state_sorted['Avg_Car_Dependency'] / df_state_sorted['Avg_Car_Dependency'].max())
bars1 = ax1.barh(df_state_sorted['state'], df_state_sorted['Avg_Car_Dependency'] * 100, color=colors)
ax1.set_xlabel('Car Dependency (%)', fontsize=12, fontweight='bold')
ax1.set_title('Car Dependency by State/Territory', fontsize=14, fontweight='bold')
ax1.axvline(x=83.7, color='red', linestyle='--', linewidth=2, label='National Avg (83.7%)')
ax1.legend()
ax1.grid(axis='x', alpha=0.3)

# Add value labels
for i, (idx, row) in enumerate(df_state_sorted.iterrows()):
    ax1.text(row['Avg_Car_Dependency'] * 100 + 1, i, f"{row['Avg_Car_Dependency']*100:.1f}%",
             va='center', fontweight='bold')

# 2. Public Transit Usage by State
ax2 = axes[0, 1]
df_state_transit = df_state.sort_values('Avg_Transit_Usage', ascending=False)
colors2 = plt.cm.YlGn(df_state_transit['Avg_Transit_Usage'] / df_state_transit['Avg_Transit_Usage'].max())
bars2 = ax2.barh(df_state_transit['state'], df_state_transit['Avg_Transit_Usage'] * 100, color=colors2)
ax2.set_xlabel('Public Transit Usage (%)', fontsize=12, fontweight='bold')
ax2.set_title('Public Transit Usage by State/Territory', fontsize=14, fontweight='bold')
ax2.axvline(x=6.4, color='blue', linestyle='--', linewidth=2, label='National Avg (6.4%)')
ax2.legend()
ax2.grid(axis='x', alpha=0.3)

for i, (idx, row) in enumerate(df_state_transit.iterrows()):
    ax2.text(row['Avg_Transit_Usage'] * 100 + 0.3, i, f"{row['Avg_Transit_Usage']*100:.1f}%",
             va='center', fontweight='bold')

# 3. Average TOD Score by State
ax3 = axes[1, 0]
df_state_tod = df_state.sort_values('Avg_TOD_Score', ascending=False)
colors3 = plt.cm.plasma(df_state_tod['Avg_TOD_Score'] / df_state_tod['Avg_TOD_Score'].max())
bars3 = ax3.barh(df_state_tod['state'], df_state_tod['Avg_TOD_Score'], color=colors3)
ax3.set_xlabel('Average TOD Score', fontsize=12, fontweight='bold')
ax3.set_title('Average TOD Score by State/Territory', fontsize=14, fontweight='bold')
ax3.axvline(x=66.4, color='purple', linestyle='--', linewidth=2, label='National Avg (66.4)')
ax3.legend()
ax3.grid(axis='x', alpha=0.3)

for i, (idx, row) in enumerate(df_state_tod.iterrows()):
    ax3.text(row['Avg_TOD_Score'] + 1, i, f"{row['Avg_TOD_Score']:.1f}",
             va='center', fontweight='bold')

# 4. Total Commuters by State
ax4 = axes[1, 1]
df_state_commuters = df_state.sort_values('Total_Commuters', ascending=False)
colors4 = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_state_commuters)))
bars4 = ax4.bar(range(len(df_state_commuters)), df_state_commuters['Total_Commuters'], color=colors4)
ax4.set_xticks(range(len(df_state_commuters)))
ax4.set_xticklabels(df_state_commuters['state'], rotation=45, ha='right')
ax4.set_ylabel('Total Commuters', fontsize=12, fontweight='bold')
ax4.set_title('Total Commuters by State/Territory', fontsize=14, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

# Add value labels
for i, (idx, row) in enumerate(df_state_commuters.iterrows()):
    ax4.text(i, row['Total_Commuters'] + 50000, f"{row['Total_Commuters']/1e6:.2f}M",
             ha='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('visualizations/01_state_comparison_dashboard.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: visualizations/01_state_comparison_dashboard.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: NATIONAL MODAL SPLIT
# ============================================================================

print("\n[3/10] Creating national modal split visualization...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Australian Commuter Modal Split - 2021 Census', fontsize=18, fontweight='bold')

# Calculate totals
total_commuters = df_complete['total_commuters'].sum()
total_car = df_complete['total_car'].sum()
total_transit = df_complete['total_public_transit'].sum()
total_active = df_complete['total_active_transport'].sum()

# Pie chart
sizes = [total_car, total_transit, total_active]
labels = [f'Private Vehicle\n{total_car/total_commuters:.1%}\n({total_car/1e6:.2f}M)',
          f'Public Transit\n{total_transit/total_commuters:.1%}\n({total_transit/1e6:.2f}M)',
          f'Active Transport\n{total_active/total_commuters:.1%}\n({total_active/1e6:.2f}M)']
colors_pie = ['#ff6b6b', '#4ecdc4', '#95e1d3']
explode = (0.05, 0.05, 0.05)

wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='',
                                     colors=colors_pie, explode=explode,
                                     shadow=True, startangle=90,
                                     textprops={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('Current Modal Split\nTotal: 7.88M Commuters', fontsize=14, fontweight='bold', pad=20)

# Comparison bar chart
categories = ['Current\nAustralia', 'Target\n(Best Practice)', 'Copenhagen', 'Singapore', 'Amsterdam']
car_pct = [86.5, 40, 35, 30, 30]
transit_pct = [7.1, 35, 30, 70, 30]
active_pct = [4.6, 25, 35, 0, 40]

x = np.arange(len(categories))
width = 0.25

bars1 = ax2.bar(x - width, car_pct, width, label='Car', color='#ff6b6b')
bars2 = ax2.bar(x, transit_pct, width, label='Transit', color='#4ecdc4')
bars3 = ax2.bar(x + width, active_pct, width, label='Active', color='#95e1d3')

ax2.set_ylabel('Mode Share (%)', fontsize=12, fontweight='bold')
ax2.set_title('Australia vs. Global Best Practice', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(categories, fontsize=10)
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/02_modal_split_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: visualizations/02_modal_split_analysis.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: TOD SCORE DISTRIBUTION
# ============================================================================

print("\n[4/10] Creating TOD score distribution visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('TOD Score Distribution Analysis', fontsize=18, fontweight='bold')

# 1. Histogram of TOD Scores
ax1 = axes[0, 0]
ax1.hist(df_complete['tod_score'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
ax1.axvline(df_complete['tod_score'].mean(), color='red', linestyle='--',
            linewidth=2, label=f'Mean: {df_complete["tod_score"].mean():.1f}')
ax1.axvline(df_complete['tod_score'].median(), color='green', linestyle='--',
            linewidth=2, label=f'Median: {df_complete["tod_score"].median():.1f}')
ax1.set_xlabel('TOD Score', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of SA1 Areas', fontsize=12, fontweight='bold')
ax1.set_title('Distribution of TOD Scores (All 61,844 SA1s)', fontsize=13, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(alpha=0.3)

# 2. TOD Score by State (Box plot)
ax2 = axes[0, 1]
state_order = df_state.sort_values('Avg_TOD_Score', ascending=False)['state'].tolist()
df_plot = df_complete[df_complete['state'].isin(state_order)]
bp = ax2.boxplot([df_plot[df_plot['state'] == state]['tod_score'].values for state in state_order],
                  labels=state_order, patch_artist=True)
for patch, color in zip(bp['boxes'], plt.cm.Set3(np.linspace(0, 1, len(state_order)))):
    patch.set_facecolor(color)
ax2.set_ylabel('TOD Score', fontsize=12, fontweight='bold')
ax2.set_title('TOD Score Distribution by State', fontsize=13, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 3. Scatter: TOD Score vs. Commuters
ax3 = axes[1, 0]
scatter = ax3.scatter(df_complete['total_commuters'], df_complete['tod_score'],
                     c=df_complete['car_dependency_ratio'], cmap='RdYlGn_r',
                     alpha=0.5, s=10)
ax3.set_xlabel('Total Commuters', fontsize=12, fontweight='bold')
ax3.set_ylabel('TOD Score', fontsize=12, fontweight='bold')
ax3.set_title('TOD Score vs. Commuter Volume', fontsize=13, fontweight='bold')
ax3.set_xscale('log')
ax3.grid(alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax3)
cbar.set_label('Car Dependency Ratio', fontsize=10, fontweight='bold')

# 4. Top 1000 by State
ax4 = axes[1, 1]
top_by_state = df_top_1000.groupby('state').size().sort_values(ascending=False)
colors = plt.cm.viridis(np.linspace(0, 1, len(top_by_state)))
bars = ax4.bar(range(len(top_by_state)), top_by_state.values, color=colors)
ax4.set_xticks(range(len(top_by_state)))
ax4.set_xticklabels(top_by_state.index, rotation=45, ha='right')
ax4.set_ylabel('Number of Top 1000 SA1s', fontsize=12, fontweight='bold')
ax4.set_title('Top 1000 TOD Opportunities by State', fontsize=13, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

for i, v in enumerate(top_by_state.values):
    ax4.text(i, v + 5, str(v), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/03_tod_score_distribution.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: visualizations/03_tod_score_distribution.png")
plt.close()

# ============================================================================
# VISUALIZATION 4: CAR DEPENDENCY HEATMAP
# ============================================================================

print("\n[5/10] Creating car dependency heatmap...")

fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Car Dependency Analysis Across Australia', fontsize=18, fontweight='bold')

# 1. Car Dependency Categories
ax1 = axes[0]
df_complete['car_dep_category'] = pd.cut(
    df_complete['car_dependency_ratio'],
    bins=[0, 0.5, 0.7, 0.8, 0.9, 1.0],
    labels=['<50%\n(Low)', '50-70%\n(Moderate)', '70-80%\n(High)', '80-90%\n(Very High)', '>90%\n(Extreme)']
)
category_counts = df_complete['car_dep_category'].value_counts().sort_index()
colors_heat = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']
bars = ax1.bar(range(len(category_counts)), category_counts.values, color=colors_heat, edgecolor='black', linewidth=1.5)
ax1.set_xticks(range(len(category_counts)))
ax1.set_xticklabels(category_counts.index, fontsize=11)
ax1.set_ylabel('Number of SA1 Areas', fontsize=12, fontweight='bold')
ax1.set_title('SA1 Areas by Car Dependency Level', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

for i, (cat, count) in enumerate(category_counts.items()):
    percentage = count / len(df_complete) * 100
    ax1.text(i, count + 500, f'{count:,}\n({percentage:.1f}%)',
            ha='center', fontweight='bold', fontsize=10)

# 2. State-wise car dependency heatmap
ax2 = axes[1]
state_car_categories = pd.crosstab(df_complete['state'], df_complete['car_dep_category'])
state_car_pct = state_car_categories.div(state_car_categories.sum(axis=1), axis=0) * 100

# Sort by average car dependency
state_order = df_state.sort_values('Avg_Car_Dependency', ascending=False)['state'].tolist()
state_car_pct_sorted = state_car_pct.loc[state_order]

im = ax2.imshow(state_car_pct_sorted.T, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
ax2.set_xticks(range(len(state_order)))
ax2.set_xticklabels(state_order, rotation=45, ha='right')
ax2.set_yticks(range(len(state_car_pct_sorted.columns)))
ax2.set_yticklabels(state_car_pct_sorted.columns)
ax2.set_title('Car Dependency Distribution by State (%)', fontsize=14, fontweight='bold')

# Add text annotations
for i in range(len(state_order)):
    for j in range(len(state_car_pct_sorted.columns)):
        text = ax2.text(i, j, f'{state_car_pct_sorted.iloc[i, j]:.0f}%',
                       ha="center", va="center", color="black", fontsize=9, fontweight='bold')

cbar = plt.colorbar(im, ax=ax2)
cbar.set_label('Percentage of SA1 Areas', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/04_car_dependency_heatmap.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: visualizations/04_car_dependency_heatmap.png")
plt.close()

# ============================================================================
# VISUALIZATION 5: PRIORITY INVESTMENT DASHBOARD
# ============================================================================

print("\n[6/10] Creating priority investment dashboard...")

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

fig.suptitle('TOD Investment Priority Framework', fontsize=20, fontweight='bold')

# Top panel - Priority tiers
ax_top = fig.add_subplot(gs[0, :])
priorities = ['Priority 1\nHigh Score + Volume', 'Priority 2\nEmployment Centers', 'Priority 3\nMultimodal Potential']
counts = [4484, 1496, 60]
colors_priority = ['#e74c3c', '#f39c12', '#3498db']
bars = ax_top.bar(priorities, counts, color=colors_priority, edgecolor='black', linewidth=2)
ax_top.set_ylabel('Number of SA1 Areas', fontsize=13, fontweight='bold')
ax_top.set_title('Investment Priority Tiers', fontsize=15, fontweight='bold', pad=15)
ax_top.grid(axis='y', alpha=0.3)

for i, (p, c) in enumerate(zip(priorities, counts)):
    ax_top.text(i, c + 100, f'{c:,} SA1s', ha='center', fontweight='bold', fontsize=12)

# Middle left - Commuter pain points
ax_ml = fig.add_subplot(gs[1, 0])
pain_metrics = ['Pain Points\nIdentified', 'Affected\nCommuters', 'Avg Car\nDependency']
pain_values = [len(df_pain_points), df_pain_points['total_commuters'].sum()/1000,
               df_pain_points['car_dependency_ratio'].mean()*100]
pain_colors = ['#e74c3c', '#c0392b', '#a93226']
bars_pain = ax_ml.bar(pain_metrics, pain_values, color=pain_colors, edgecolor='black')
ax_ml.set_title('Commute Pain Points', fontsize=13, fontweight='bold')
ax_ml.grid(axis='y', alpha=0.3)

for i, v in enumerate(pain_values):
    if i == 0:
        ax_ml.text(i, v + 2, f'{int(v)}', ha='center', fontweight='bold')
    elif i == 1:
        ax_ml.text(i, v + 1, f'{v:.1f}K', ha='center', fontweight='bold')
    else:
        ax_ml.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')

# Middle center - Transit corridors
ax_mc = fig.add_subplot(gs[1, 1])
corridor_by_state = df_corridors.groupby('state').size().sort_values(ascending=False).head(6)
bars_corr = ax_mc.barh(range(len(corridor_by_state)), corridor_by_state.values,
                        color=plt.cm.viridis(np.linspace(0.2, 0.8, len(corridor_by_state))))
ax_mc.set_yticks(range(len(corridor_by_state)))
ax_mc.set_yticklabels(corridor_by_state.index)
ax_mc.set_xlabel('Number of Corridor SA1s', fontsize=11, fontweight='bold')
ax_mc.set_title('Transit Corridors by State (Top 6)', fontsize=13, fontweight='bold')
ax_mc.grid(axis='x', alpha=0.3)

for i, v in enumerate(corridor_by_state.values):
    ax_mc.text(v + 20, i, str(v), va='center', fontweight='bold')

# Middle right - Hub & spoke opportunities
ax_mr = fig.add_subplot(gs[1, 2])
top_hubs = df_hub_spoke.nlargest(8, 'Potential_Modal_Shift_20pct')
bars_hub = ax_mr.barh(range(len(top_hubs)), top_hubs['Potential_Modal_Shift_20pct'].values,
                       color=plt.cm.plasma(np.linspace(0.2, 0.8, len(top_hubs))))
ax_mr.set_yticks(range(len(top_hubs)))
ax_mr.set_yticklabels([f"Hub {i+1}" for i in range(len(top_hubs))], fontsize=9)
ax_mr.set_xlabel('Potential New Transit Users', fontsize=11, fontweight='bold')
ax_mr.set_title('Top Hub-and-Spoke Networks', fontsize=13, fontweight='bold')
ax_mr.grid(axis='x', alpha=0.3)

for i, v in enumerate(top_hubs['Potential_Modal_Shift_20pct'].values):
    ax_mr.text(v + 20, i, f'{v:,}', va='center', fontweight='bold', fontsize=9)

# Bottom panels - Key metrics
ax_bl = fig.add_subplot(gs[2, 0])
ax_bl.axis('off')
metrics_text = f"""
NATIONAL METRICS

Total SA1 Areas: 61,844
Total Commuters: 7.88M

Car Dependency: 83.7%
Transit Usage: 6.4%
Active Transport: 4.9%

High Car Dep Areas: 31,060
(>90% car usage)
"""
ax_bl.text(0.1, 0.5, metrics_text, fontsize=12, fontfamily='monospace',
          verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax_bc = fig.add_subplot(gs[2, 1])
ax_bc.axis('off')
impact_text = f"""
POTENTIAL IMPACT

20% Modal Shift:
~100,000 new transit users

Annual Time Savings:
1.9M hours

Economic Value:
$47.9 Million/year
"""
ax_bc.text(0.1, 0.5, impact_text, fontsize=12, fontfamily='monospace',
          verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

ax_br = fig.add_subplot(gs[2, 2])
ax_br.axis('off')
priority_text = f"""
TOP OPPORTUNITIES

Priority 1: 4,484 areas
Priority 2: 1,496 areas
Priority 3: 60 areas

Top SA1 TOD Score: 97.1
Avg Top 1000: 91.1
"""
ax_br.text(0.1, 0.5, priority_text, fontsize=12, fontfamily='monospace',
          verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.savefig('visualizations/05_priority_investment_dashboard.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: visualizations/05_priority_investment_dashboard.png")
plt.close()

print("\n[7/10] All static visualizations complete!")
print("\n" + "=" * 100)
print("STATIC VISUALIZATIONS GENERATED:")
print("=" * 100)
print("  1. State Comparison Dashboard")
print("  2. Modal Split Analysis")
print("  3. TOD Score Distribution")
print("  4. Car Dependency Heatmap")
print("  5. Priority Investment Dashboard")
print("\nAll files saved in: visualizations/")
print("=" * 100)
