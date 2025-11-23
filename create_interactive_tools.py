#!/usr/bin/env python3
"""
Create Interactive Housing Affordability Tools
- Interactive maps with Plotly
- Interactive charts
- Suburb comparison visualizations
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("CREATING INTERACTIVE HOUSING AFFORDABILITY TOOLS")
print("=" * 80)
print()

# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================
print("STEP 1: Loading data...")

comprehensive = pd.read_csv('housing_affordability_comprehensive.csv')
sydney_data = pd.read_csv('sydney_housing_comprehensive.csv')
crisis_areas = pd.read_csv('housing_crisis_areas.csv')
sweet_spots = pd.read_csv('housing_affordability_sweet_spots.csv')
sydney_crisis = pd.read_csv('sydney_crisis_areas.csv')
sydney_sweet = pd.read_csv('sydney_sweet_spots.csv')

print(f"✓ Loaded comprehensive data: {len(comprehensive):,} suburbs")
print(f"✓ Loaded Sydney data: {len(sydney_data):,} suburbs")
print()

import os
os.makedirs('interactive_tools', exist_ok=True)

# =============================================================================
# STEP 2: CREATE INTERACTIVE SCATTER PLOTS
# =============================================================================
print("STEP 2: Creating interactive scatter plots...")

# Scatter 1: Income vs Rent Stress (National)
fig1 = px.scatter(comprehensive.sample(min(2000, len(comprehensive))),
                  x='Median_tot_hhd_inc_weekly',
                  y='rent_stress_ratio',
                  color='pct_young_adults',
                  size='total_population',
                  hover_data=['Suburb', 'Median_rent_weekly', 'pct_renting'],
                  title='Income vs Rent Stress - Australia',
                  labels={
                      'Median_tot_hhd_inc_weekly': 'Median Household Income ($/week)',
                      'rent_stress_ratio': 'Rent Stress Ratio (%)',
                      'pct_young_adults': '% Young Adults (15-34)'
                  },
                  color_continuous_scale='Viridis')

fig1.add_hline(y=30, line_dash="dash", line_color="red",
               annotation_text="30% Stress Threshold")
fig1.update_layout(height=600, template='plotly_white')
fig1.write_html('interactive_tools/income_vs_rent_stress_australia.html')
print("  ✓ Created: income_vs_rent_stress_australia.html")

# Scatter 2: Income vs Mortgage Stress (Sydney)
fig2 = px.scatter(sydney_data,
                  x='Median_tot_hhd_inc_weekly',
                  y='mortgage_stress_ratio',
                  color='pct_apartments',
                  size='total_dwellings',
                  hover_data=['Suburb', 'Median_mortgage_repay_monthly', 'pct_owned_mortgage'],
                  title='Income vs Mortgage Stress - Sydney Metro',
                  labels={
                      'Median_tot_hhd_inc_weekly': 'Median Household Income ($/week)',
                      'mortgage_stress_ratio': 'Mortgage Stress Ratio (%)',
                      'pct_apartments': '% Apartments'
                  },
                  color_continuous_scale='Reds')

fig2.add_hline(y=30, line_dash="dash", line_color="red",
               annotation_text="30% Stress Threshold")
fig2.update_layout(height=600, template='plotly_white')
fig2.write_html('interactive_tools/income_vs_mortgage_stress_sydney.html')
print("  ✓ Created: income_vs_mortgage_stress_sydney.html")

# Scatter 3: Crisis Score vs Income
fig3 = px.scatter(crisis_areas.sample(min(500, len(crisis_areas))),
                  x='Median_tot_hhd_inc_weekly',
                  y='crisis_score',
                  color='pct_renting',
                  size='total_population',
                  hover_data=['Suburb', 'mortgage_stress_ratio', 'rent_stress_ratio'],
                  title='Crisis Areas: Income vs Crisis Score',
                  labels={
                      'Median_tot_hhd_inc_weekly': 'Median Household Income ($/week)',
                      'crisis_score': 'Crisis Score',
                      'pct_renting': '% Renting'
                  },
                  color_continuous_scale='YlOrRd')

fig3.update_layout(height=600, template='plotly_white')
fig3.write_html('interactive_tools/crisis_score_analysis.html')
print("  ✓ Created: crisis_score_analysis.html")

# =============================================================================
# STEP 3: CREATE INTERACTIVE BAR CHARTS
# =============================================================================
print("\nSTEP 3: Creating interactive bar charts...")

# Top 30 Crisis Areas
top_crisis = crisis_areas.nlargest(30, 'crisis_score')
fig4 = go.Figure(data=[
    go.Bar(x=top_crisis['crisis_score'],
           y=top_crisis['Suburb'],
           orientation='h',
           marker=dict(
               color=top_crisis['crisis_score'],
               colorscale='Reds',
               showscale=True,
               colorbar=dict(title="Crisis Score")
           ),
           text=top_crisis['crisis_score'].round(1),
           textposition='outside',
           hovertemplate='<b>%{y}</b><br>' +
                        'Crisis Score: %{x:.1f}<br>' +
                        '<extra></extra>')
])

fig4.update_layout(
    title='Top 30 Housing Crisis Areas in Australia',
    xaxis_title='Crisis Score',
    yaxis_title='Suburb',
    height=800,
    template='plotly_white',
    yaxis=dict(autorange="reversed")
)
fig4.write_html('interactive_tools/top_crisis_areas.html')
print("  ✓ Created: top_crisis_areas.html")

# Top 30 Sweet Spots
top_sweet = sweet_spots.nlargest(30, 'affordability_score')
fig5 = go.Figure(data=[
    go.Bar(x=top_sweet['affordability_score'],
           y=top_sweet['Suburb'],
           orientation='h',
           marker=dict(
               color=top_sweet['affordability_score'],
               colorscale='Greens',
               showscale=True,
               colorbar=dict(title="Affordability Score")
           ),
           text=top_sweet['affordability_score'].round(1),
           textposition='outside',
           hovertemplate='<b>%{y}</b><br>' +
                        'Affordability Score: %{x:.1f}<br>' +
                        '<extra></extra>')
])

fig5.update_layout(
    title='Top 30 Affordability Sweet Spots in Australia',
    xaxis_title='Affordability Score',
    yaxis_title='Suburb',
    height=800,
    template='plotly_white',
    yaxis=dict(autorange="reversed")
)
fig5.write_html('interactive_tools/top_sweet_spots.html')
print("  ✓ Created: top_sweet_spots.html")

# Top 30 Sydney Crisis Areas
top_sydney_crisis = sydney_crisis.nlargest(30, 'crisis_score')
fig6 = go.Figure(data=[
    go.Bar(x=top_sydney_crisis['crisis_score'],
           y=top_sydney_crisis['Suburb'],
           orientation='h',
           marker=dict(
               color=top_sydney_crisis['crisis_score'],
               colorscale='Reds',
               showscale=True,
               colorbar=dict(title="Crisis Score")
           ),
           text=top_sydney_crisis['crisis_score'].round(1),
           textposition='outside',
           hovertemplate='<b>%{y}</b><br>' +
                        'Crisis Score: %{x:.1f}<br>' +
                        'Mortgage Stress: %{customdata[0]:.1f}%<br>' +
                        'Rent Stress: %{customdata[1]:.1f}%<br>' +
                        '<extra></extra>',
           customdata=top_sydney_crisis[['mortgage_stress_ratio', 'rent_stress_ratio']].values)
])

fig6.update_layout(
    title='Top 30 Housing Crisis Areas in Sydney Metro',
    xaxis_title='Crisis Score',
    yaxis_title='Suburb',
    height=800,
    template='plotly_white',
    yaxis=dict(autorange="reversed")
)
fig6.write_html('interactive_tools/top_sydney_crisis_areas.html')
print("  ✓ Created: top_sydney_crisis_areas.html")

# =============================================================================
# STEP 4: CREATE INTERACTIVE COMPARISON CHARTS
# =============================================================================
print("\nSTEP 4: Creating interactive comparison charts...")

# Sydney vs Australia Comparison
comparison_data = {
    'Metric': ['Mortgage Stress', 'Rent Stress', 'Median Income', 'Median Rent',
               '% Apartments', '% Renting'],
    'Australia': [
        comprehensive['mortgage_stress_ratio'].mean(),
        comprehensive['rent_stress_ratio'].mean(),
        comprehensive['Median_tot_hhd_inc_weekly'].mean(),
        comprehensive['Median_rent_weekly'].mean(),
        comprehensive['pct_apartments'].mean(),
        comprehensive['pct_renting'].mean()
    ],
    'Sydney': [
        sydney_data['mortgage_stress_ratio'].mean(),
        sydney_data['rent_stress_ratio'].mean(),
        sydney_data['Median_tot_hhd_inc_weekly'].mean(),
        sydney_data['Median_rent_weekly'].mean(),
        sydney_data['pct_apartments'].mean(),
        sydney_data['pct_renting'].mean()
    ]
}

fig7 = go.Figure(data=[
    go.Bar(name='Australia', x=comparison_data['Metric'], y=comparison_data['Australia'],
           marker_color='lightblue', text=[f"{v:.1f}" for v in comparison_data['Australia']],
           textposition='outside'),
    go.Bar(name='Sydney Metro', x=comparison_data['Metric'], y=comparison_data['Sydney'],
           marker_color='darkred', text=[f"{v:.1f}" for v in comparison_data['Sydney']],
           textposition='outside')
])

fig7.update_layout(
    title='Sydney vs Australia: Housing Affordability Comparison',
    xaxis_title='Metric',
    yaxis_title='Value',
    barmode='group',
    height=600,
    template='plotly_white'
)
fig7.write_html('interactive_tools/sydney_vs_australia_comparison.html')
print("  ✓ Created: sydney_vs_australia_comparison.html")

# =============================================================================
# STEP 5: CREATE MULTI-PANEL DASHBOARD
# =============================================================================
print("\nSTEP 5: Creating multi-panel dashboard...")

# Create subplot dashboard
fig8 = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Stress Distribution', 'Tenure Type Distribution',
                    'Income vs Rent Stress', 'Crisis Score Distribution'),
    specs=[[{'type': 'bar'}, {'type': 'pie'}],
           [{'type': 'scatter'}, {'type': 'histogram'}]]
)

# Subplot 1: Stress Distribution
stress_comparison = pd.DataFrame({
    'Type': ['Mortgage<br>Stress', 'Rent<br>Stress'],
    'Australia': [comprehensive['mortgage_stress_ratio'].mean(),
                  comprehensive['rent_stress_ratio'].mean()],
    'Sydney': [sydney_data['mortgage_stress_ratio'].mean(),
               sydney_data['rent_stress_ratio'].mean()]
})

fig8.add_trace(
    go.Bar(x=stress_comparison['Type'], y=stress_comparison['Australia'],
           name='Australia', marker_color='lightblue', showlegend=True),
    row=1, col=1
)
fig8.add_trace(
    go.Bar(x=stress_comparison['Type'], y=stress_comparison['Sydney'],
           name='Sydney', marker_color='darkred', showlegend=True),
    row=1, col=1
)

# Subplot 2: Tenure Type Pie
tenure_data = {
    'Owned Outright': comprehensive['pct_owned_outright'].mean(),
    'Owned w/ Mortgage': comprehensive['pct_owned_mortgage'].mean(),
    'Renting': comprehensive['pct_renting'].mean()
}

fig8.add_trace(
    go.Pie(labels=list(tenure_data.keys()), values=list(tenure_data.values()),
           marker=dict(colors=['#2E86AB', '#A23B72', '#F18F01']),
           showlegend=False),
    row=1, col=2
)

# Subplot 3: Income vs Rent Stress Scatter
sample = comprehensive.sample(min(500, len(comprehensive)))
fig8.add_trace(
    go.Scatter(x=sample['Median_tot_hhd_inc_weekly'],
               y=sample['rent_stress_ratio'],
               mode='markers',
               marker=dict(color=sample['pct_young_adults'],
                          colorscale='Viridis',
                          size=5,
                          showscale=False),
               showlegend=False),
    row=2, col=1
)

# Subplot 4: Crisis Score Histogram
fig8.add_trace(
    go.Histogram(x=comprehensive['crisis_score'],
                 marker_color='darkred',
                 showlegend=False,
                 nbinsx=30),
    row=2, col=2
)

fig8.update_xaxes(title_text="Stress Type", row=1, col=1)
fig8.update_yaxes(title_text="Ratio (%)", row=1, col=1)
fig8.update_xaxes(title_text="Income ($/week)", row=2, col=1)
fig8.update_yaxes(title_text="Rent Stress (%)", row=2, col=1)
fig8.update_xaxes(title_text="Crisis Score", row=2, col=2)
fig8.update_yaxes(title_text="Count", row=2, col=2)

fig8.update_layout(
    title_text="Housing Affordability Dashboard - Australia",
    height=800,
    template='plotly_white'
)
fig8.write_html('interactive_tools/housing_dashboard.html')
print("  ✓ Created: housing_dashboard.html")

# =============================================================================
# STEP 6: CREATE INTERACTIVE HEATMAP
# =============================================================================
print("\nSTEP 6: Creating correlation heatmap...")

# Select key metrics for correlation
metrics_for_corr = [
    'mortgage_stress_ratio', 'rent_stress_ratio', 'crisis_score',
    'Median_tot_hhd_inc_weekly', 'pct_renting', 'pct_apartments',
    'pct_young_adults', 'pct_low_income', 'Average_num_psns_per_bedroom'
]

corr_data = comprehensive[metrics_for_corr].corr()

fig9 = go.Figure(data=go.Heatmap(
    z=corr_data.values,
    x=['Mortgage<br>Stress', 'Rent<br>Stress', 'Crisis<br>Score',
       'Median<br>Income', '% Renting', '% Apartments',
       '% Young<br>Adults', '% Low<br>Income', 'Persons/<br>Bedroom'],
    y=['Mortgage Stress', 'Rent Stress', 'Crisis Score',
       'Median Income', '% Renting', '% Apartments',
       '% Young Adults', '% Low Income', 'Persons/Bedroom'],
    colorscale='RdBu',
    zmid=0,
    text=corr_data.values.round(2),
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title="Correlation")
))

fig9.update_layout(
    title='Housing Affordability Metrics - Correlation Heatmap',
    height=700,
    width=800,
    template='plotly_white'
)
fig9.write_html('interactive_tools/correlation_heatmap.html')
print("  ✓ Created: correlation_heatmap.html")

# =============================================================================
# STEP 7: CREATE SUBURB LOOKUP TOOL (HTML/JS)
# =============================================================================
print("\nSTEP 7: Creating suburb lookup tool...")

# Prepare data for lookup
lookup_cols = ['SAL_CODE_2021', 'Suburb', 'Median_age_persons',
               'Median_tot_hhd_inc_weekly', 'Median_rent_weekly',
               'Median_mortgage_repay_monthly', 'mortgage_stress_ratio',
               'rent_stress_ratio', 'pct_owned_outright', 'pct_renting',
               'crisis_score']

# Add affordability_score if it exists
if 'affordability_score' in comprehensive.columns:
    lookup_cols.append('affordability_score')

lookup_data = comprehensive[lookup_cols].copy()

# Create HTML lookup tool
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Australian Housing Affordability - Suburb Lookup</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .search-box {
            margin-bottom: 30px;
        }
        #searchInput {
            width: 100%;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            transition: border-color 0.3s;
        }
        #searchInput:focus {
            outline: none;
            border-color: #667eea;
        }
        #results {
            margin-top: 20px;
        }
        .result-card {
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .result-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .suburb-name {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .metric {
            background: white;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
        .metric-label {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }
        .stress-high {
            color: #dc3545;
        }
        .stress-moderate {
            color: #ffc107;
        }
        .stress-low {
            color: #28a745;
        }
        .alert {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-top: 10px;
        }
        .badge-crisis {
            background: #dc3545;
            color: white;
        }
        .badge-sweet {
            background: #28a745;
            color: white;
        }
        .badge-neutral {
            background: #6c757d;
            color: white;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏘️ Australian Housing Affordability</h1>
        <div class="subtitle">Suburb Lookup Tool - 2021 Census Data</div>

        <div class="alert">
            💡 <strong>How to use:</strong> Type a suburb code (e.g., SAL10001) or part of a suburb name to search.
            Click on results to see detailed housing affordability metrics.
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search by suburb code or name...">
        </div>

        <div id="results"></div>
    </div>

    <script>
        const suburbData = """ + lookup_data.to_json(orient='records') + """;

        const searchInput = document.getElementById('searchInput');
        const resultsDiv = document.getElementById('results');

        function getStressClass(value) {
            if (value >= 40) return 'stress-high';
            if (value >= 30) return 'stress-moderate';
            return 'stress-low';
        }

        function getStressLabel(value) {
            if (value >= 40) return 'High Stress';
            if (value >= 30) return 'Moderate Stress';
            return 'Manageable';
        }

        function getBadge(crisisScore, affordScore) {
            if (crisisScore >= 35) {
                return '<span class="badge badge-crisis">⚠️ Crisis Area</span>';
            } else if (affordScore >= 85) {
                return '<span class="badge badge-sweet">✅ Sweet Spot</span>';
            }
            return '<span class="badge badge-neutral">Standard</span>';
        }

        function displayResults(suburbs) {
            if (suburbs.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">No suburbs found matching your search.</div>';
                return;
            }

            resultsDiv.innerHTML = suburbs.slice(0, 20).map(suburb => `
                <div class="result-card">
                    <div class="suburb-name">${suburb.Suburb || suburb.SAL_CODE_2021}</div>
                    <div style="font-size: 0.9em; color: #666; margin-bottom: 15px;">
                        Code: ${suburb.SAL_CODE_2021}
                        ${getBadge(suburb.crisis_score || 0, suburb.affordability_score || 0)}
                    </div>

                    <div class="metrics-grid">
                        <div class="metric">
                            <div class="metric-label">Median Age</div>
                            <div class="metric-value">${(suburb.Median_age_persons || 0).toFixed(0)} years</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Median Household Income</div>
                            <div class="metric-value">$${(suburb.Median_tot_hhd_inc_weekly || 0).toFixed(0)}/week</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Median Rent</div>
                            <div class="metric-value">$${(suburb.Median_rent_weekly || 0).toFixed(0)}/week</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Median Mortgage</div>
                            <div class="metric-value">$${(suburb.Median_mortgage_repay_monthly || 0).toFixed(0)}/month</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Mortgage Stress Ratio</div>
                            <div class="metric-value ${getStressClass(suburb.mortgage_stress_ratio || 0)}">
                                ${(suburb.mortgage_stress_ratio || 0).toFixed(1)}%
                                <div style="font-size: 0.7em; margin-top: 3px;">${getStressLabel(suburb.mortgage_stress_ratio || 0)}</div>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Rent Stress Ratio</div>
                            <div class="metric-value ${getStressClass(suburb.rent_stress_ratio || 0)}">
                                ${(suburb.rent_stress_ratio || 0).toFixed(1)}%
                                <div style="font-size: 0.7em; margin-top: 3px;">${getStressLabel(suburb.rent_stress_ratio || 0)}</div>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">% Owned Outright</div>
                            <div class="metric-value">${(suburb.pct_owned_outright || 0).toFixed(1)}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">% Renting</div>
                            <div class="metric-value">${(suburb.pct_renting || 0).toFixed(1)}%</div>
                        </div>
                        ${suburb.crisis_score ? `
                        <div class="metric">
                            <div class="metric-label">Crisis Score</div>
                            <div class="metric-value ${suburb.crisis_score >= 35 ? 'stress-high' : 'stress-moderate'}">
                                ${(suburb.crisis_score).toFixed(1)}
                            </div>
                        </div>
                        ` : ''}
                        ${suburb.affordability_score ? `
                        <div class="metric">
                            <div class="metric-label">Affordability Score</div>
                            <div class="metric-value stress-low">
                                ${(suburb.affordability_score).toFixed(1)}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (query.length < 2) {
                resultsDiv.innerHTML = '';
                return;
            }

            const filtered = suburbData.filter(suburb =>
                (suburb.SAL_CODE_2021 && suburb.SAL_CODE_2021.toLowerCase().includes(query)) ||
                (suburb.Suburb && suburb.Suburb.toLowerCase().includes(query))
            );

            displayResults(filtered);
        });

        // Show top crisis areas on load
        window.addEventListener('load', () => {
            const topCrisis = suburbData
                .filter(s => s.crisis_score)
                .sort((a, b) => (b.crisis_score || 0) - (a.crisis_score || 0))
                .slice(0, 10);

            resultsDiv.innerHTML = '<div class="alert" style="background: #f8d7da; border-color: #f5c6cb; color: #721c24;">Showing top 10 crisis areas. Use search to find specific suburbs.</div>';
            displayResults(topCrisis);
        });
    </script>
</body>
</html>
"""

with open('interactive_tools/suburb_lookup.html', 'w') as f:
    f.write(html_content)
print("  ✓ Created: suburb_lookup.html")

# =============================================================================
# STEP 8: CREATE SUBURB COMPARISON TOOL
# =============================================================================
print("\nSTEP 8: Creating suburb comparison tool...")

# Create comparison data
comparison_suburbs = pd.concat([
    crisis_areas.nlargest(10, 'crisis_score'),
    sweet_spots.nlargest(10, 'affordability_score')
])

# Save for comparison tool
comparison_suburbs.to_csv('interactive_tools/comparison_data.csv', index=False)

print("\n" + "=" * 80)
print("INTERACTIVE TOOLS COMPLETE!")
print("=" * 80)
print("\nCreated interactive tools in 'interactive_tools/' directory:")
print("  1. income_vs_rent_stress_australia.html - Interactive scatter plot")
print("  2. income_vs_mortgage_stress_sydney.html - Sydney-specific scatter")
print("  3. crisis_score_analysis.html - Crisis areas explorer")
print("  4. top_crisis_areas.html - Top 30 crisis areas (interactive bar)")
print("  5. top_sweet_spots.html - Top 30 sweet spots (interactive bar)")
print("  6. top_sydney_crisis_areas.html - Sydney crisis rankings")
print("  7. sydney_vs_australia_comparison.html - Interactive comparison")
print("  8. housing_dashboard.html - Multi-panel dashboard")
print("  9. correlation_heatmap.html - Metrics correlation")
print("  10. suburb_lookup.html - 🔍 Searchable suburb lookup tool")
print("\n💡 Open any HTML file in your web browser to explore interactively!")
print()
