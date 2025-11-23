#!/usr/bin/env python3
"""
Advanced Step 5: Real-Time Rental Stress Monitoring Dashboard
===============================================================
Interactive web dashboard for monitoring rental stress and social housing needs.

Features:
- Real-time data filtering and visualization
- Interactive maps and charts
- Scenario comparison tools
- Export capabilities
- Predictive model integration

Launch with: streamlit run advanced_step5_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Rental Stress Monitoring Dashboard",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 36px;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    padding: 20px;
}
.metric-box {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 5px;
    border-left: 5px solid #1f77b4;
}
.stMetric {
    background-color: #ffffff;
    padding: 10px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Data Loading with Caching
# ============================================================================

@st.cache_data
def load_data():
    """Load all analysis datasets"""
    base_path = Path("rental_stress_outputs")

    # Main dataset with all metrics
    df_main = pd.read_csv(base_path / "transport_accessibility" / "sa1_with_transport_accessibility.csv")

    # Scenario data
    scenarios = {}
    scenario_path = base_path / "scenario_modeling"
    for i in range(1, 7):
        file = scenario_path / f"scenario_{i}_allocation.csv"
        if file.exists():
            scenarios[f"Scenario {i}"] = pd.read_csv(file)

    # Temporal data
    df_temporal = pd.read_csv(base_path / "temporal_analysis" / "temporal_analysis_2016_2021_2026.csv")

    return df_main, scenarios, df_temporal

@st.cache_data
def load_summary_stats():
    """Load summary statistics"""
    try:
        scenario_summary = pd.read_csv(
            Path("rental_stress_outputs/scenario_modeling/scenario_comparison_summary.csv")
        )
        return scenario_summary
    except:
        return None

# Load data
with st.spinner("Loading data..."):
    df_main, scenarios, df_temporal = load_data()
    scenario_summary = load_summary_stats()

# ============================================================================
# Dashboard Header
# ============================================================================

st.markdown('<div class="main-header">🏘️ Rental Stress & Social Housing Monitoring Dashboard</div>',
           unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
<div style='background-color: #e1f5ff; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
    <h4 style='margin:0; color: #0277bd;'>📊 Real-Time Analysis Dashboard</h4>
    <p style='margin:5px 0 0 0; color: #01579b;'>
        Interactive monitoring system for rental affordability, public housing gaps, and investment prioritization
        across <b>61,844 SA1 areas</b> in Australia.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar Controls
# ============================================================================

st.sidebar.title("🎛️ Dashboard Controls")

# View selection
view_mode = st.sidebar.radio(
    "Select View",
    ["📊 Overview Dashboard", "🗺️ Geographic Analysis", "📈 Temporal Trends",
     "💰 Scenario Modeling", "🎯 Priority Areas", "📥 Data Export"]
)

st.sidebar.markdown("---")

# Filters
st.sidebar.subheader("🔍 Data Filters")

# State filter
state_map = {
    1: "NSW", 2: "VIC", 3: "QLD", 4: "SA",
    5: "WA", 6: "TAS", 7: "NT", 8: "ACT"
}
df_main['state_name'] = df_main['SA1_CODE_2021'].astype(str).str[0].astype(int).map(state_map)
selected_states = st.sidebar.multiselect(
    "Select States",
    options=['All'] + list(state_map.values()),
    default='All'
)

# Stress level filter
stress_level = st.sidebar.select_slider(
    "Minimum Rental Stress Score",
    options=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    value=0
)

# Apply filters
df_filtered = df_main.copy()
if 'All' not in selected_states:
    df_filtered = df_filtered[df_filtered['state_name'].isin(selected_states)]
df_filtered = df_filtered[df_filtered['rental_stress_score'] >= stress_level]

st.sidebar.metric("Filtered SA1 Areas", f"{len(df_filtered):,}")

# ============================================================================
# VIEW 1: Overview Dashboard
# ============================================================================

if view_mode == "📊 Overview Dashboard":
    st.header("📊 National Overview")

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total SA1 Areas Analyzed",
            f"{len(df_filtered):,}",
            delta=f"{len(df_filtered)-len(df_main):,}" if len(df_filtered) != len(df_main) else None
        )

    with col2:
        stressed = (df_filtered['rental_stress'] == 1).sum()
        pct = stressed/len(df_filtered)*100 if len(df_filtered) > 0 else 0
        st.metric(
            "Areas in Rental Stress",
            f"{stressed:,}",
            delta=f"{pct:.1f}%",
            delta_color="inverse"
        )

    with col3:
        gap = df_filtered['public_housing_gap'].sum()
        st.metric(
            "Public Housing Gap",
            f"{gap:,.0f}",
            delta="dwellings needed",
            delta_color="off"
        )

    with col4:
        avg_stress = df_filtered['rental_stress_score'].mean()
        st.metric(
            "Average Stress Score",
            f"{avg_stress:.1f}/100",
            delta=f"{avg_stress-20:.1f}" if avg_stress > 20 else None,
            delta_color="inverse"
        )

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        # Stress category distribution
        st.subheader("Rental Stress Distribution")
        stress_dist = df_filtered['stress_category'].value_counts()
        fig = px.pie(
            values=stress_dist.values,
            names=stress_dist.index,
            color_discrete_sequence=px.colors.sequential.RdYlGn_r,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Investment priority distribution
        st.subheader("Investment Priority Distribution")
        priority_dist = df_filtered['investment_priority'].value_counts()
        fig = px.bar(
            x=priority_dist.index,
            y=priority_dist.values,
            color=priority_dist.values,
            color_continuous_scale='Reds',
            labels={'x': 'Priority Level', 'y': 'Number of SA1 Areas'}
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Full width chart
    st.subheader("Rental Stress Score Distribution")
    fig = px.histogram(
        df_filtered,
        x='rental_stress_score',
        nbins=50,
        color_discrete_sequence=['steelblue'],
        labels={'rental_stress_score': 'Rental Stress Score (0-100)'}
    )
    fig.add_vline(x=30, line_dash="dash", line_color="orange", annotation_text="Moderate Stress")
    fig.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="Severe Stress")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# VIEW 2: Geographic Analysis
# ============================================================================

elif view_mode == "🗺️ Geographic Analysis":
    st.header("🗺️ Geographic Distribution Analysis")

    # Map type selection
    map_type = st.selectbox(
        "Select Map View",
        ["Rental Stress Hotspots", "Public Housing Gaps", "Investment Priorities",
         "Employment Accessibility", "Combined Burden"]
    )

    # Prepare data for mapping
    map_df = df_filtered.copy()

    # Configure map based on selection
    if map_type == "Rental Stress Hotspots":
        map_df = map_df.nlargest(1000, 'rental_stress_score')
        color_col = 'rental_stress_score'
        color_scale = 'Reds'
        title = 'Top 1000 Rental Stress Hotspots'

    elif map_type == "Public Housing Gaps":
        map_df = map_df[map_df['critical_housing_gap'] == 1].nlargest(500, 'public_housing_gap')
        color_col = 'public_housing_gap'
        color_scale = 'OrRd'
        title = 'Critical Public Housing Gaps (Top 500)'

    elif map_type == "Investment Priorities":
        map_df = map_df.nlargest(500, 'investment_priority_score')
        color_col = 'investment_priority_score'
        color_scale = 'Viridis'
        title = 'Top 500 Investment Priority Areas'

    elif map_type == "Employment Accessibility":
        map_df = map_df.sample(min(2000, len(map_df)))
        color_col = 'employment_accessibility_score'
        color_scale = 'RdYlGn'
        title = 'Employment Accessibility (Sample 2000)'

    else:  # Combined Burden
        map_df = map_df[map_df['severe_combined_burden'] == 1].nlargest(500, 'housing_transport_burden')
        color_col = 'housing_transport_burden'
        color_scale = 'Purples'
        title = 'Severe Combined Housing+Transport Burden (Top 500)'

    # Create scatter map
    fig = px.scatter_mapbox(
        map_df,
        lat='latitude',
        lon='longitude',
        color=color_col,
        size=np.abs(map_df[color_col]) + 1,
        color_continuous_scale=color_scale,
        hover_data=['SA1_CODE_2021', 'rental_stress_score', 'public_housing_gap',
                   'low_income_pct', 'unemployment_rate'],
        zoom=3,
        center={'lat': -25, 'lon': 135},
        title=title,
        height=700
    )

    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

    # Statistics for displayed areas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Areas Displayed", f"{len(map_df):,}")
    with col2:
        st.metric("Avg Stress Score", f"{map_df['rental_stress_score'].mean():.1f}/100")
    with col3:
        st.metric("Total Housing Gap", f"{map_df['public_housing_gap'].sum():,.0f}")

# ============================================================================
# VIEW 3: Temporal Trends
# ============================================================================

elif view_mode == "📈 Temporal Trends":
    st.header("📈 Temporal Trends Analysis (2016-2021-2026)")

    # Trend type selection
    trend_type = st.selectbox(
        "Select Trend Analysis",
        ["Rent vs Income Growth", "Stress Transitions", "Future Projections"]
    )

    if trend_type == "Rent vs Income Growth":
        st.subheader("5-Year Change Analysis (2016-2021)")

        col1, col2 = st.columns(2)

        with col1:
            # Rent growth distribution
            fig = px.histogram(
                df_temporal,
                x='rent_pct_change',
                nbins=50,
                color_discrete_sequence=['red'],
                title='Rent Growth Distribution (%)',
                labels={'rent_pct_change': 'Rent Growth (%)'}
            )
            fig.add_vline(x=df_temporal['rent_pct_change'].median(),
                         line_dash="dash", annotation_text="Median")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Income growth distribution
            fig = px.histogram(
                df_temporal,
                x='income_pct_change',
                nbins=50,
                color_discrete_sequence=['green'],
                title='Income Growth Distribution (%)',
                labels={'income_pct_change': 'Income Growth (%)'}
            )
            fig.add_vline(x=df_temporal['income_pct_change'].median(),
                         line_dash="dash", annotation_text="Median")
            st.plotly_chart(fig, use_container_width=True)

        # Affordability deterioration
        st.subheader("Affordability Deterioration")
        sample = df_temporal.sample(min(5000, len(df_temporal)))
        fig = px.scatter(
            sample,
            x='rent_pct_change',
            y='income_pct_change',
            color='affordability_deterioration',
            color_continuous_scale='RdYlGn_r',
            title='Rent Growth vs Income Growth by SA1 Area',
            labels={'rent_pct_change': 'Rent Growth (%)',
                   'income_pct_change': 'Income Growth (%)'},
            height=500
        )
        fig.add_shape(type="line", x0=0, y0=0, x1=50, y1=50,
                     line=dict(color="gray", dash="dash"))
        st.plotly_chart(fig, use_container_width=True)

    elif trend_type == "Stress Transitions":
        st.subheader("Rental Stress Transitions (2016 → 2021)")

        transitions = df_temporal['stress_trend'].value_counts()
        fig = px.bar(
            x=transitions.index,
            y=transitions.values,
            color=transitions.index,
            color_discrete_map={
                'Remained Affordable': 'green',
                'Remained Stressed': 'red',
                'Entered Stress': 'orange',
                'Exited Stress': 'lightgreen'
            },
            title='Stress Transition Categories',
            labels={'x': 'Transition Type', 'y': 'Number of SA1 Areas'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            entered = (df_temporal['stress_trend'] == 'Entered Stress').sum()
            st.metric("Entered Stress", f"{entered:,}", delta="2016-2021", delta_color="inverse")
        with col2:
            exited = (df_temporal['stress_trend'] == 'Exited Stress').sum()
            st.metric("Exited Stress", f"{exited:,}", delta="2016-2021", delta_color="normal")
        with col3:
            remained = (df_temporal['stress_trend'] == 'Remained Stressed').sum()
            st.metric("Persistent Stress", f"{remained:,}", delta="5 years", delta_color="off")

    else:  # Future Projections
        st.subheader("2026 Scenario Projections")

        # Load projection files
        scenarios_2026 = {}
        for scenario_name in ['business_as_usual', 'crisis_scenario', 'policy_intervention']:
            try:
                file = Path(f"rental_stress_outputs/temporal_analysis/projection_2026_{scenario_name}.csv")
                scenarios_2026[scenario_name] = pd.read_csv(file)
            except:
                pass

        if scenarios_2026:
            # Calculate stressed counts for each scenario
            projections_data = []
            for name, df_scenario in scenarios_2026.items():
                stressed_count = (df_scenario['rental_stress_2026'] == 1).sum()
                projections_data.append({
                    'Scenario': name.replace('_', ' ').title(),
                    'Stressed SA1s': stressed_count
                })

            proj_df = pd.DataFrame(projections_data)

            # Add 2021 baseline
            stressed_2021 = (df_main['rental_stress'] == 1).sum()

            # Create projection line chart
            fig = go.Figure()

            for scenario in proj_df['Scenario'].unique():
                fig.add_trace(go.Scatter(
                    x=[2021, 2026],
                    y=[stressed_2021, proj_df[proj_df['Scenario'] == scenario]['Stressed SA1s'].values[0]],
                    mode='lines+markers',
                    name=scenario,
                    line=dict(width=3),
                    marker=dict(size=10)
                ))

            fig.update_layout(
                title='Projected Rental Stress Trends (2021-2026)',
                xaxis_title='Year',
                yaxis_title='Number of Stressed SA1 Areas',
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Show scenario comparison
            st.dataframe(proj_df, use_container_width=True)

# ============================================================================
# VIEW 4: Scenario Modeling
# ============================================================================

elif view_mode == "💰 Scenario Modeling":
    st.header("💰 Investment Scenario Analysis")

    if scenario_summary is not None:
        # Show summary table
        st.subheader("Scenario Comparison Summary")
        st.dataframe(scenario_summary, use_container_width=True)

        # Visualization
        col1, col2 = st.columns(2)

        with col1:
            # Budget vs Households Assisted
            fig = px.bar(
                scenario_summary,
                x='Scenario',
                y='Households Assisted',
                color='Budget ($B)',
                color_continuous_scale='Blues',
                title='Households Assisted by Scenario'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gap closure
            fig = px.bar(
                scenario_summary,
                x='Scenario',
                y='Gap Closed (%)',
                color='Gap Closed (%)',
                color_continuous_scale='Greens',
                title='Supply Gap Closure by Scenario'
            )
            fig.update_xaxes(tickangle=45)
            fig.add_hline(y=100, line_dash="dash", line_color="red",
                         annotation_text="Full Gap Closure")
            st.plotly_chart(fig, use_container_width=True)

        # ROI Analysis
        st.subheader("Cost Efficiency Analysis")
        fig = px.scatter(
            scenario_summary[scenario_summary['Cost per HH ($)'] > 0],
            x='Dwellings',
            y='Cost per HH ($)',
            size='Households Assisted',
            color='Stress Reduction (SA1s)',
            hover_name='Scenario',
            title='Cost per Household vs Total Dwellings',
            labels={'Cost per HH ($)': 'Cost per Household ($)'},
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Scenario summary data not available")

# ============================================================================
# VIEW 5: Priority Areas
# ============================================================================

elif view_mode == "🎯 Priority Areas":
    st.header("🎯 Priority Investment Targets")

    # Priority type selection
    priority_type = st.selectbox(
        "Select Priority Criteria",
        ["Highest Rental Stress", "Critical Housing Gaps", "Optimal Locations (Accessibility)",
         "High Low-Income Concentration", "Combined Burden"]
    )

    # Get top areas based on selection
    if priority_type == "Highest Rental Stress":
        top_areas = df_filtered.nlargest(100, 'rental_stress_score')
        sort_col = 'rental_stress_score'
    elif priority_type == "Critical Housing Gaps":
        top_areas = df_filtered[df_filtered['critical_housing_gap'] == 1].nlargest(100, 'public_housing_gap')
        sort_col = 'public_housing_gap'
    elif priority_type == "Optimal Locations (Accessibility)":
        top_areas = df_filtered.nlargest(100, 'optimal_location_score')
        sort_col = 'optimal_location_score'
    elif priority_type == "High Low-Income Concentration":
        top_areas = df_filtered.nlargest(100, 'low_income_pct')
        sort_col = 'low_income_pct'
    else:  # Combined Burden
        top_areas = df_filtered[df_filtered['severe_combined_burden'] == 1].nlargest(100, 'housing_transport_burden')
        sort_col = 'housing_transport_burden'

    st.subheader(f"Top 100 Priority Areas - {priority_type}")

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Priority Areas", f"{len(top_areas):,}")
    with col2:
        st.metric("Total Housing Gap", f"{top_areas['public_housing_gap'].sum():,.0f}")
    with col3:
        st.metric("Avg Stress Score", f"{top_areas['rental_stress_score'].mean():.1f}/100")
    with col4:
        st.metric("Low-Income HH", f"{top_areas['low_income_households'].sum():,.0f}")

    # Data table with key columns
    display_cols = ['SA1_CODE_2021', 'state_name', 'rental_stress_score', 'public_housing_gap',
                   'low_income_pct', 'investment_priority_score', 'employment_accessibility_score']
    st.dataframe(
        top_areas[display_cols].sort_values(sort_col, ascending=False),
        use_container_width=True,
        height=400
    )

# ============================================================================
# VIEW 6: Data Export
# ============================================================================

elif view_mode == "📥 Data Export":
    st.header("📥 Data Export & Download")

    st.subheader("Export Filtered Data")

    # Export options
    export_type = st.selectbox(
        "Select Dataset to Export",
        ["Filtered SA1 Data", "Top 500 Rental Stress Hotspots", "Top 500 Investment Priorities",
         "Critical Housing Gaps", "Scenario Allocations"]
    )

    # Prepare export data
    if export_type == "Filtered SA1 Data":
        export_df = df_filtered
    elif export_type == "Top 500 Rental Stress Hotspots":
        export_df = df_filtered.nlargest(500, 'rental_stress_score')
    elif export_type == "Top 500 Investment Priorities":
        export_df = df_filtered.nlargest(500, 'investment_priority_score')
    elif export_type == "Critical Housing Gaps":
        export_df = df_filtered[df_filtered['critical_housing_gap'] == 1]
    else:
        export_df = df_filtered

    # Show preview
    st.write(f"**Preview ({len(export_df):,} rows)**")
    st.dataframe(export_df.head(20), use_container_width=True)

    # Download button
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{export_type.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Summary statistics
    st.subheader("Summary Statistics for Export")
    st.write(export_df.describe())

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><b>Rental Stress & Social Housing Monitoring Dashboard</b></p>
    <p>Data Source: 2021 Australian Census | Analysis: 61,844 SA1 Areas</p>
    <p>© 2025 | Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)
