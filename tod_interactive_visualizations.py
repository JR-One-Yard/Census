#!/usr/bin/env python3
"""
TOD Analysis - Interactive Plotly Visualizations
================================================
Generates interactive HTML visualizations using Plotly

Visualizations:
1. Interactive state comparison dashboard
2. 3D TOD score explorer
3. Interactive modal split sunburst
4. Priority areas treemap
5. Economic impact visualization
6. Top opportunities interactive table

Author: Claude Code
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("TOD ANALYSIS - INTERACTIVE PLOTLY VISUALIZATIONS")
print("=" * 100)

# Load data
print("\nLoading datasets...")
df_complete = pd.read_csv('tod_complete_sa1_analysis.csv')
df_state = pd.read_csv('tod_state_level_analysis.csv')
df_top_1000 = pd.read_csv('tod_top_1000_opportunities.csv')
df_corridors = pd.read_csv('tod_transit_corridors.csv')

# Add state
def extract_state(sa1_code):
    state_map = {1: 'NSW', 2: 'VIC', 3: 'QLD', 4: 'SA', 5: 'WA',
                 6: 'TAS', 7: 'NT', 8: 'ACT', 9: 'Other'}
    return state_map.get(int(str(sa1_code)[0]), 'Unknown')

df_complete['state'] = df_complete['SA1_CODE_2021'].apply(extract_state)
df_top_1000['state'] = df_top_1000['SA1_CODE_2021'].apply(extract_state)

print("✓ Data loaded successfully\n")

# ============================================================================
# INTERACTIVE VIZ 1: State Comparison Dashboard
# ============================================================================

print("[1/6] Creating interactive state comparison dashboard...")

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Car Dependency by State', 'Public Transit Usage by State',
                   'Average TOD Score by State', 'Total Commuters by State'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'bar'}]]
)

# Sort states
df_state_sorted = df_state.sort_values('Avg_Car_Dependency', ascending=True)

# Car dependency
fig.add_trace(
    go.Bar(x=df_state_sorted['Avg_Car_Dependency']*100,
           y=df_state_sorted['state'],
           orientation='h',
           name='Car Dependency',
           marker=dict(color=df_state_sorted['Avg_Car_Dependency']*100,
                      colorscale='Reds',
                      showscale=False),
           text=[f"{v:.1f}%" for v in df_state_sorted['Avg_Car_Dependency']*100],
           textposition='outside',
           hovertemplate='<b>%{y}</b><br>Car Dependency: %{x:.1f}%<extra></extra>'),
    row=1, col=1
)

# Transit usage
df_state_transit = df_state.sort_values('Avg_Transit_Usage', ascending=True)
fig.add_trace(
    go.Bar(x=df_state_transit['Avg_Transit_Usage']*100,
           y=df_state_transit['state'],
           orientation='h',
           name='Transit Usage',
           marker=dict(color=df_state_transit['Avg_Transit_Usage']*100,
                      colorscale='Greens',
                      showscale=False),
           text=[f"{v:.1f}%" for v in df_state_transit['Avg_Transit_Usage']*100],
           textposition='outside',
           hovertemplate='<b>%{y}</b><br>Transit Usage: %{x:.1f}%<extra></extra>'),
    row=1, col=2
)

# TOD scores
df_state_tod = df_state.sort_values('Avg_TOD_Score', ascending=True)
fig.add_trace(
    go.Bar(x=df_state_tod['Avg_TOD_Score'],
           y=df_state_tod['state'],
           orientation='h',
           name='TOD Score',
           marker=dict(color=df_state_tod['Avg_TOD_Score'],
                      colorscale='Viridis',
                      showscale=False),
           text=[f"{v:.1f}" for v in df_state_tod['Avg_TOD_Score']],
           textposition='outside',
           hovertemplate='<b>%{y}</b><br>TOD Score: %{x:.1f}<extra></extra>'),
    row=2, col=1
)

# Total commuters
df_state_comm = df_state.sort_values('Total_Commuters', ascending=False)
fig.add_trace(
    go.Bar(x=df_state_comm['state'],
           y=df_state_comm['Total_Commuters'],
           name='Commuters',
           marker=dict(color=df_state_comm['Total_Commuters'],
                      colorscale='Blues',
                      showscale=False),
           text=[f"{v/1e6:.2f}M" for v in df_state_comm['Total_Commuters']],
           textposition='outside',
           hovertemplate='<b>%{x}</b><br>Commuters: %{y:,.0f}<extra></extra>'),
    row=2, col=2
)

fig.update_xaxes(title_text="Car Dependency (%)", row=1, col=1)
fig.update_xaxes(title_text="Transit Usage (%)", row=1, col=2)
fig.update_xaxes(title_text="TOD Score", row=2, col=1)
fig.update_xaxes(title_text="State/Territory", row=2, col=2)
fig.update_yaxes(title_text="Total Commuters", row=2, col=2)

fig.update_layout(
    title_text="<b>TOD Analysis - State/Territory Comparison Dashboard</b>",
    title_font_size=20,
    showlegend=False,
    height=800,
    template='plotly_white'
)

fig.write_html('visualizations/interactive_01_state_dashboard.html')
print("  ✓ Saved: visualizations/interactive_01_state_dashboard.html")

# ============================================================================
# INTERACTIVE VIZ 2: 3D TOD Score Explorer
# ============================================================================

print("[2/6] Creating 3D TOD score explorer...")

# Sample data for performance (every 10th SA1)
df_sample = df_complete.iloc[::10].copy()

fig = go.Figure(data=[go.Scatter3d(
    x=df_sample['total_commuters'],
    y=df_sample['car_dependency_ratio'] * 100,
    z=df_sample['tod_score'],
    mode='markers',
    marker=dict(
        size=4,
        color=df_sample['tod_score'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="TOD Score"),
        line=dict(width=0.5, color='white')
    ),
    text=df_sample['state'],
    hovertemplate='<b>SA1: %{customdata}</b><br>' +
                  'Commuters: %{x:,.0f}<br>' +
                  'Car Dependency: %{y:.1f}%<br>' +
                  'TOD Score: %{z:.1f}<br>' +
                  'State: %{text}<extra></extra>',
    customdata=df_sample['SA1_CODE_2021']
)])

fig.update_layout(
    title='<b>3D TOD Score Explorer</b><br><sub>Every 10th SA1 area (6,184 points)</sub>',
    scene=dict(
        xaxis=dict(title='Total Commuters', type='log'),
        yaxis=dict(title='Car Dependency (%)'),
        zaxis=dict(title='TOD Score'),
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
    ),
    height=700,
    template='plotly_white'
)

fig.write_html('visualizations/interactive_02_3d_explorer.html')
print("  ✓ Saved: visualizations/interactive_02_3d_explorer.html")

# ============================================================================
# INTERACTIVE VIZ 3: Modal Split Sunburst
# ============================================================================

print("[3/6] Creating interactive modal split sunburst...")

# Prepare hierarchical data
modal_data = []
for state in df_complete['state'].unique():
    if state != 'Unknown':
        state_data = df_complete[df_complete['state'] == state]
        total_car = state_data['total_car'].sum()
        total_transit = state_data['total_public_transit'].sum()
        total_active = state_data['total_active_transport'].sum()

        modal_data.extend([
            {'state': state, 'mode': 'Car', 'commuters': total_car},
            {'state': state, 'mode': 'Public Transit', 'commuters': total_transit},
            {'state': state, 'mode': 'Active Transport', 'commuters': total_active}
        ])

df_modal = pd.DataFrame(modal_data)

# Create sunburst
fig = px.sunburst(
    df_modal,
    path=['mode', 'state'],
    values='commuters',
    color='mode',
    color_discrete_map={'Car': '#ff6b6b', 'Public Transit': '#4ecdc4', 'Active Transport': '#95e1d3'},
    title='<b>National Modal Split by State/Territory</b><br><sub>Interactive Sunburst Chart</sub>'
)

fig.update_traces(
    textinfo="label+percent parent",
    hovertemplate='<b>%{label}</b><br>Commuters: %{value:,.0f}<br>Percentage: %{percentParent}<extra></extra>'
)

fig.update_layout(height=700, template='plotly_white')
fig.write_html('visualizations/interactive_03_modal_split_sunburst.html')
print("  ✓ Saved: visualizations/interactive_03_modal_split_sunburst.html")

# ============================================================================
# INTERACTIVE VIZ 4: Priority Areas Treemap
# ============================================================================

print("[4/6] Creating priority areas treemap...")

# Prepare priority data
priority_data = []

# Priority 1
for state in df_complete['state'].unique():
    if state != 'Unknown':
        p1_count = len(df_complete[
            (df_complete['state'] == state) &
            (df_complete['tod_score'] > 80) &
            (df_complete['total_commuters'] > df_complete['total_commuters'].quantile(0.9))
        ])
        if p1_count > 0:
            priority_data.append({
                'priority': 'Priority 1: High Score + Volume',
                'state': state,
                'count': p1_count
            })

# Priority 2
for state in df_complete['state'].unique():
    if state != 'Unknown':
        p2_count = len(df_complete[
            (df_complete['state'] == state) &
            (df_complete['sa2_employment_density'] > df_complete['sa2_employment_density'].quantile(0.75)) &
            (df_complete['public_transit_ratio'] < 0.10) &
            (df_complete['total_commuters'] > 200)
        ])
        if p2_count > 0:
            priority_data.append({
                'priority': 'Priority 2: Employment Centers',
                'state': state,
                'count': p2_count
            })

df_priority = pd.DataFrame(priority_data)

fig = px.treemap(
    df_priority,
    path=['priority', 'state'],
    values='count',
    color='priority',
    color_discrete_map={
        'Priority 1: High Score + Volume': '#e74c3c',
        'Priority 2: Employment Centers': '#f39c12'
    },
    title='<b>TOD Investment Priority Areas by State</b><br><sub>Interactive Treemap</sub>'
)

fig.update_traces(
    textinfo="label+value+percent parent",
    hovertemplate='<b>%{label}</b><br>SA1 Areas: %{value:,.0f}<br>Percentage: %{percentParent}<extra></extra>'
)

fig.update_layout(height=700, template='plotly_white')
fig.write_html('visualizations/interactive_04_priority_treemap.html')
print("  ✓ Saved: visualizations/interactive_04_priority_treemap.html")

# ============================================================================
# INTERACTIVE VIZ 5: Economic Impact Dashboard
# ============================================================================

print("[5/6] Creating economic impact dashboard...")

# Calculate cumulative impact
df_top_sorted = df_top_1000.sort_values('tod_score', ascending=False).copy()
df_top_sorted['cumulative_commuters'] = df_top_sorted['total_commuters'].cumsum()
df_top_sorted['potential_modal_shift'] = (df_top_sorted['total_car'] * 0.20).cumsum()
df_top_sorted['annual_time_savings_hours'] = (df_top_sorted['total_car'] * 0.20 * 10 * 230 / 60).cumsum()
df_top_sorted['economic_value'] = df_top_sorted['annual_time_savings_hours'] * 25

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Cumulative Modal Shift Potential', 'Annual Time Savings',
                   'Economic Value ($)', 'TOD Score vs. Impact'),
    specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
           [{'type': 'scatter'}, {'type': 'scatter'}]]
)

# Modal shift
fig.add_trace(
    go.Scatter(x=list(range(1, len(df_top_sorted)+1)),
               y=df_top_sorted['potential_modal_shift'],
               mode='lines',
               name='Potential New Transit Users',
               line=dict(color='#3498db', width=3),
               fill='tozeroy',
               hovertemplate='Top %{x} Areas<br>New Transit Users: %{y:,.0f}<extra></extra>'),
    row=1, col=1
)

# Time savings
fig.add_trace(
    go.Scatter(x=list(range(1, len(df_top_sorted)+1)),
               y=df_top_sorted['annual_time_savings_hours'],
               mode='lines',
               name='Annual Time Savings',
               line=dict(color='#e74c3c', width=3),
               fill='tozeroy',
               hovertemplate='Top %{x} Areas<br>Annual Hours Saved: %{y:,.0f}<extra></extra>'),
    row=1, col=2
)

# Economic value
fig.add_trace(
    go.Scatter(x=list(range(1, len(df_top_sorted)+1)),
               y=df_top_sorted['economic_value'],
               mode='lines',
               name='Economic Value',
               line=dict(color='#2ecc71', width=3),
               fill='tozeroy',
               hovertemplate='Top %{x} Areas<br>Economic Value: $%{y:,.0f}<extra></extra>'),
    row=2, col=1
)

# TOD score vs impact
fig.add_trace(
    go.Scatter(x=df_top_sorted['tod_score'],
               y=df_top_sorted['economic_value'] / len(df_top_sorted),
               mode='markers',
               name='TOD Score vs Value',
               marker=dict(size=8, color=df_top_sorted['tod_score'],
                          colorscale='Viridis', showscale=True),
               hovertemplate='TOD Score: %{x:.1f}<br>Avg Economic Value: $%{y:,.0f}<extra></extra>'),
    row=2, col=2
)

fig.update_xaxes(title_text="Number of Top SA1 Areas", row=1, col=1)
fig.update_xaxes(title_text="Number of Top SA1 Areas", row=1, col=2)
fig.update_xaxes(title_text="Number of Top SA1 Areas", row=2, col=1)
fig.update_xaxes(title_text="TOD Score", row=2, col=2)

fig.update_yaxes(title_text="New Transit Users", row=1, col=1)
fig.update_yaxes(title_text="Hours Saved", row=1, col=2)
fig.update_yaxes(title_text="Economic Value ($)", row=2, col=1)
fig.update_yaxes(title_text="Avg Economic Value ($)", row=2, col=2)

fig.update_layout(
    title_text="<b>Economic Impact Analysis - Top 1000 TOD Opportunities</b>",
    title_font_size=18,
    showlegend=False,
    height=800,
    template='plotly_white'
)

fig.write_html('visualizations/interactive_05_economic_impact.html')
print("  ✓ Saved: visualizations/interactive_05_economic_impact.html")

# ============================================================================
# INTERACTIVE VIZ 6: Top Opportunities Table
# ============================================================================

print("[6/6] Creating interactive top opportunities table...")

df_table = df_top_1000.head(100).copy()
df_table['rank'] = range(1, len(df_table)+1)

fig = go.Figure(data=[go.Table(
    header=dict(
        values=['<b>Rank</b>', '<b>SA1 Code</b>', '<b>State</b>', '<b>TOD Score</b>',
                '<b>Car Dep %</b>', '<b>Transit %</b>', '<b>Commuters</b>',
                '<b>SA2 Employment</b>'],
        fill_color='#3498db',
        align='center',
        font=dict(color='white', size=12)
    ),
    cells=dict(
        values=[
            df_table['rank'],
            df_table['SA1_CODE_2021'],
            df_table['state'],
            [f"{v:.1f}" for v in df_table['tod_score']],
            [f"{v:.1%}" for v in df_table['car_dependency_ratio']],
            [f"{v:.1%}" for v in df_table['public_transit_ratio']],
            [f"{v:,}" for v in df_table['total_commuters']],
            [f"{v:,}" for v in df_table['sa2_employment']]
        ],
        fill_color=[['white', '#ecf0f1'] * 50],
        align='center',
        font=dict(size=11)
    )
)])

fig.update_layout(
    title='<b>Top 100 TOD Opportunities - Detailed Table</b><br><sub>Interactive & Sortable</sub>',
    height=800,
    template='plotly_white'
)

fig.write_html('visualizations/interactive_06_top_opportunities_table.html')
print("  ✓ Saved: visualizations/interactive_06_top_opportunities_table.html")

print("\n" + "=" * 100)
print("INTERACTIVE VISUALIZATIONS COMPLETE!")
print("=" * 100)
print("\nGenerated 6 interactive HTML files:")
print("  1. State Dashboard (interactive_01_state_dashboard.html)")
print("  2. 3D TOD Explorer (interactive_02_3d_explorer.html)")
print("  3. Modal Split Sunburst (interactive_03_modal_split_sunburst.html)")
print("  4. Priority Treemap (interactive_04_priority_treemap.html)")
print("  5. Economic Impact Dashboard (interactive_05_economic_impact.html)")
print("  6. Top Opportunities Table (interactive_06_top_opportunities_table.html)")
print("\nAll files saved in: visualizations/")
print("Open any HTML file in a web browser for interactive exploration!")
print("=" * 100)
