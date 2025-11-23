#!/usr/bin/env python3
"""
🏖️ LIFESTYLE EXPLORER DASHBOARD
Interactive exploration of 61,844 Australian SA1 areas

Features:
- Filter by state, income, lifestyle score, population
- Interactive maps and visualizations
- Compare multiple areas
- Export filtered results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Lifestyle Explorer Dashboard",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# Load Data (with caching)
# ============================================================================

@st.cache_data
def load_data():
    """Load the lifestyle premium data with caching"""
    df = pd.read_csv('/home/user/Census/lifestyle_premium_outputs/lifestyle_premium_with_prices.csv')
    # Add derived columns
    df['coastal_category'] = pd.cut(
        df['beach_avg_km'],
        bins=[0, 5, 20, 50, 1000],
        labels=['Highly Coastal (<5km)', 'Coastal (5-20km)', 'Near Coast (20-50km)', 'Inland (>50km)']
    )
    return df

# Load data
with st.spinner('Loading lifestyle data...'):
    df = load_data()

# ============================================================================
# Header
# ============================================================================

st.markdown('<div class="main-header">🏖️ Lifestyle Explorer Dashboard</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; margin-bottom: 2rem;'>
    Explore <b>{len(df):,}</b> SA1 areas across Australia |
    Filter, compare, and discover your ideal location
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar Filters
# ============================================================================

st.sidebar.header("🔍 Filters")

# State filter
states = ['All'] + sorted(df['state_name'].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "State",
    states,
    default=['All'],
    help="Select one or more states"
)

# Lifestyle score filter
lifestyle_range = st.sidebar.slider(
    "Lifestyle Premium Index",
    float(df['lifestyle_premium_index'].min()),
    float(df['lifestyle_premium_index'].max()),
    (10.0, 25.0),
    help="Filter by lifestyle premium score (0-100)"
)

# Property price filter (in thousands)
price_range = st.sidebar.slider(
    "Property Price ($'000)",
    int(df['median_property_price'].min() / 1000),
    int(df['median_property_price'].max() / 1000),
    (300, 1000),
    help="Filter by median property price"
)

# Income filter
income_range = st.sidebar.slider(
    "Median Weekly Income ($)",
    int(df['Median_tot_prsnl_inc_weekly'].min()),
    int(df['Median_tot_prsnl_inc_weekly'].max()),
    (500, 1500),
    help="Filter by median personal income"
)

# Population filter
min_population = st.sidebar.number_input(
    "Minimum Population",
    min_value=0,
    max_value=5000,
    value=50,
    step=50,
    help="Exclude areas with low population"
)

# Coastal filter
coastal_filter = st.sidebar.multiselect(
    "Coastal Category",
    df['coastal_category'].dropna().unique().tolist(),
    default=df['coastal_category'].dropna().unique().tolist(),
    help="Filter by proximity to beach"
)

# Apply filters
df_filtered = df.copy()

if 'All' not in selected_states:
    df_filtered = df_filtered[df_filtered['state_name'].isin(selected_states)]

df_filtered = df_filtered[
    (df_filtered['lifestyle_premium_index'] >= lifestyle_range[0]) &
    (df_filtered['lifestyle_premium_index'] <= lifestyle_range[1]) &
    (df_filtered['median_property_price'] >= price_range[0] * 1000) &
    (df_filtered['median_property_price'] <= price_range[1] * 1000) &
    (df_filtered['Median_tot_prsnl_inc_weekly'] >= income_range[0]) &
    (df_filtered['Median_tot_prsnl_inc_weekly'] <= income_range[1]) &
    (df_filtered['Tot_P_P'] >= min_population) &
    (df_filtered['coastal_category'].isin(coastal_filter))
]

st.sidebar.markdown(f"**{len(df_filtered):,}** areas match filters")

# ============================================================================
# Key Metrics
# ============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Areas",
        f"{len(df_filtered):,}",
        help="Number of SA1 areas matching filters"
    )

with col2:
    avg_lifestyle = df_filtered['lifestyle_premium_index'].mean()
    st.metric(
        "Avg Lifestyle",
        f"{avg_lifestyle:.1f}",
        help="Average lifestyle premium index"
    )

with col3:
    median_price = df_filtered['median_property_price'].median()
    st.metric(
        "Median Price",
        f"${median_price/1000:.0f}K",
        help="Median property price"
    )

with col4:
    median_income = df_filtered['Median_tot_prsnl_inc_weekly'].median()
    st.metric(
        "Median Income",
        f"${median_income:.0f}/wk",
        help="Median weekly personal income"
    )

with col5:
    avg_beach = df_filtered['beach_avg_km'].mean()
    st.metric(
        "Avg Beach Dist",
        f"{avg_beach:.0f} km",
        help="Average distance to beach"
    )

st.markdown("---")

# ============================================================================
# Main Content Tabs
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🗺️ Geographic Map",
    "📈 Detailed Analysis",
    "🔍 Area Lookup",
    "💾 Export Data"
])

# ----------------------------------------------------------------------------
# TAB 1: Overview
# ----------------------------------------------------------------------------

with tab1:
    st.header("Overview & Key Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        # Lifestyle vs Property Price scatter
        fig_scatter = px.scatter(
            df_filtered,
            x='median_property_price',
            y='lifestyle_premium_index',
            color='state_name',
            size='Tot_P_P',
            hover_data=['SA1_CODE_2021', 'Median_tot_prsnl_inc_weekly', 'beach_avg_km'],
            title='Lifestyle Premium vs Property Price',
            labels={
                'median_property_price': 'Median Property Price ($)',
                'lifestyle_premium_index': 'Lifestyle Premium Index',
                'state_name': 'State'
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_traces(marker=dict(opacity=0.6))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        # Distribution by state
        state_counts = df_filtered['state_name'].value_counts().reset_index()
        state_counts.columns = ['State', 'Count']

        fig_bar = px.bar(
            state_counts,
            x='State',
            y='Count',
            title='Areas by State',
            color='Count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Lifestyle Premium distribution
        fig_hist = px.histogram(
            df_filtered,
            x='lifestyle_premium_index',
            nbins=50,
            title='Lifestyle Premium Index Distribution',
            labels={'lifestyle_premium_index': 'Lifestyle Premium Index'},
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Coastal vs Inland
        coastal_stats = df_filtered.groupby('coastal_category').agg({
            'lifestyle_premium_index': 'mean',
            'median_property_price': 'median'
        }).reset_index()

        fig_coastal = px.bar(
            coastal_stats,
            x='coastal_category',
            y='lifestyle_premium_index',
            title='Average Lifestyle Score by Coastal Category',
            labels={
                'coastal_category': 'Coastal Category',
                'lifestyle_premium_index': 'Avg Lifestyle Score'
            },
            color='lifestyle_premium_index',
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig_coastal, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 2: Geographic Map
# ----------------------------------------------------------------------------

with tab2:
    st.header("Geographic Distribution Map")

    # Sample data for performance (plotly can struggle with 60k points)
    sample_size = min(5000, len(df_filtered))
    df_map = df_filtered.sample(n=sample_size) if len(df_filtered) > sample_size else df_filtered

    if len(df_map) > 0:
        fig_map = px.scatter_mapbox(
            df_map,
            lat='latitude',
            lon='longitude',
            color='lifestyle_premium_index',
            size='Tot_P_P',
            hover_data=['SA1_CODE_2021', 'state_name', 'median_property_price', 'beach_avg_km'],
            color_continuous_scale='RdYlGn',
            zoom=3,
            center={'lat': -25, 'lon': 135},
            title=f'Lifestyle Premium Index Across Australia (showing {len(df_map):,} areas)',
            labels={'lifestyle_premium_index': 'Lifestyle Index'}
        )

        fig_map.update_layout(
            mapbox_style="open-street-map",
            height=700
        )

        st.plotly_chart(fig_map, use_container_width=True)

        if len(df_filtered) > sample_size:
            st.info(f"📊 Showing {sample_size:,} randomly sampled areas out of {len(df_filtered):,} for performance")
    else:
        st.warning("No areas match the current filters")

# ----------------------------------------------------------------------------
# TAB 3: Detailed Analysis
# ----------------------------------------------------------------------------

with tab3:
    st.header("Detailed Statistical Analysis")

    # Correlation heatmap
    st.subheader("📊 Correlation Analysis")

    corr_columns = [
        'lifestyle_premium_index',
        'median_property_price',
        'Median_tot_prsnl_inc_weekly',
        'beach_avg_km',
        'school_avg_km',
        'hospital_avg_km',
        'Year12_Total',
        'Median_age_persons'
    ]

    corr_data = df_filtered[corr_columns].corr()

    fig_corr = px.imshow(
        corr_data,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='RdBu_r',
        title='Correlation Matrix of Key Metrics'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Income vs Lifestyle analysis
    st.subheader("💰 Income vs Lifestyle Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Create income brackets
        df_filtered['income_bracket'] = pd.cut(
            df_filtered['Median_tot_prsnl_inc_weekly'],
            bins=[0, 600, 900, 1200, 1500, 5000],
            labels=['<$600', '$600-900', '$900-1200', '$1200-1500', '>$1500']
        )

        income_lifestyle = df_filtered.groupby('income_bracket').agg({
            'lifestyle_premium_index': ['mean', 'count']
        }).reset_index()
        income_lifestyle.columns = ['Income Bracket', 'Avg Lifestyle', 'Count']

        fig_income = px.bar(
            income_lifestyle,
            x='Income Bracket',
            y='Avg Lifestyle',
            text='Count',
            title='Average Lifestyle by Income Bracket',
            labels={'Avg Lifestyle': 'Average Lifestyle Score'},
            color='Avg Lifestyle',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_income, use_container_width=True)

    with col2:
        # Age demographics
        df_filtered['age_bracket'] = pd.cut(
            df_filtered['Median_age_persons'],
            bins=[0, 30, 40, 50, 60, 100],
            labels=['<30', '30-40', '40-50', '50-60', '60+']
        )

        age_lifestyle = df_filtered.groupby('age_bracket').agg({
            'lifestyle_premium_index': 'mean',
            'SA1_CODE_2021': 'count'
        }).reset_index()
        age_lifestyle.columns = ['Age Bracket', 'Avg Lifestyle', 'Count']

        fig_age = px.line(
            age_lifestyle,
            x='Age Bracket',
            y='Avg Lifestyle',
            markers=True,
            title='Average Lifestyle by Age Bracket',
            labels={'Avg Lifestyle': 'Average Lifestyle Score'}
        )
        st.plotly_chart(fig_age, use_container_width=True)

    # Top performers table
    st.subheader("🏆 Top 20 Areas by Lifestyle Premium")

    top_20 = df_filtered.nlargest(20, 'lifestyle_premium_index')[[
        'SA1_CODE_2021', 'state_name', 'lifestyle_premium_index',
        'median_property_price', 'Median_tot_prsnl_inc_weekly',
        'beach_avg_km', 'Tot_P_P'
    ]].copy()

    top_20['median_property_price'] = top_20['median_property_price'].apply(lambda x: f"${x:,.0f}")
    top_20['Median_tot_prsnl_inc_weekly'] = top_20['Median_tot_prsnl_inc_weekly'].apply(lambda x: f"${x:.0f}")
    top_20['beach_avg_km'] = top_20['beach_avg_km'].apply(lambda x: f"{x:.1f} km")
    top_20.columns = ['SA1 Code', 'State', 'Lifestyle Score', 'Median Price', 'Income/wk', 'Beach Dist', 'Population']

    st.dataframe(top_20, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 4: Area Lookup
# ----------------------------------------------------------------------------

with tab4:
    st.header("🔍 Look Up Specific SA1 Area")

    # Search by SA1 code
    sa1_code = st.text_input(
        "Enter SA1 Code",
        placeholder="e.g., 30905124513",
        help="Enter the 11-digit SA1 code"
    )

    if sa1_code:
        area_data = df[df['SA1_CODE_2021'].astype(str) == sa1_code]

        if len(area_data) > 0:
            area = area_data.iloc[0]

            st.success(f"✓ Found SA1: {sa1_code}")

            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Lifestyle Score", f"{area['lifestyle_premium_index']:.1f}/100")
            with col2:
                st.metric("Median Price", f"${area['median_property_price']:,.0f}")
            with col3:
                st.metric("Income/week", f"${area['Median_tot_prsnl_inc_weekly']:.0f}")
            with col4:
                st.metric("Population", f"{area['Tot_P_P']:.0f}")

            # Detailed information
            st.subheader("Detailed Information")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📍 Location**")
                st.write(f"State: {area['state_name']}")
                st.write(f"Coordinates: {area['latitude']:.4f}, {area['longitude']:.4f}")

                st.markdown("**🏖️ Amenity Access**")
                st.write(f"Beach: {area['beach_avg_km']:.1f} km")
                st.write(f"Parks within 5km: {area['parks_within_5km']:.0f}")
                st.write(f"School: {area['school_avg_km']:.1f} km")
                st.write(f"Hospital: {area['hospital_avg_km']:.1f} km")

            with col2:
                st.markdown("**👥 Demographics**")
                st.write(f"Median Age: {area['Median_age_persons']:.0f} years")
                st.write(f"Year 12+ Education: {area['Year12_Total']:.0f} people")
                st.write(f"Families with Children: {area['Families_with_children']:.0f}")

                st.markdown("**💰 Economics**")
                st.write(f"Median Household Income: ${area['Median_tot_hhd_inc_weekly']:.0f}/week")
                st.write(f"Rental Yield: {area['rental_yield_pct']:.1f}%")
                st.write(f"Estimated Rent: ${area['estimated_weekly_rent']:.0f}/week")

            # Score breakdown
            st.subheader("Score Breakdown")

            scores = {
                'Beach Access': area['beach_score'] * 100,
                'Park Access': area['park_score'] * 100,
                'School Proximity': area['school_score'] * 100,
                'Hospital Access': area['hospital_score'] * 100,
                'Education Level': area['education_score'] * 100,
                'Income Level': area['income_score'] * 100,
                'Age Preference': area['age_score'] * 100
            }

            fig_scores = go.Figure(go.Bar(
                x=list(scores.values()),
                y=list(scores.keys()),
                orientation='h',
                marker=dict(color=list(scores.values()), colorscale='Viridis')
            ))

            fig_scores.update_layout(
                title='Component Scores (0-100)',
                xaxis_title='Score',
                height=400
            )

            st.plotly_chart(fig_scores, use_container_width=True)

        else:
            st.error(f"❌ No SA1 area found with code: {sa1_code}")

# ----------------------------------------------------------------------------
# TAB 5: Export Data
# ----------------------------------------------------------------------------

with tab5:
    st.header("💾 Export Filtered Data")

    st.write(f"Current filters return **{len(df_filtered):,}** SA1 areas")

    # Column selection
    export_columns = st.multiselect(
        "Select columns to export",
        df_filtered.columns.tolist(),
        default=[
            'SA1_CODE_2021', 'state_name', 'lifestyle_premium_index',
            'median_property_price', 'Median_tot_prsnl_inc_weekly',
            'beach_avg_km', 'school_avg_km', 'Tot_P_P'
        ]
    )

    if export_columns:
        export_df = df_filtered[export_columns]

        # Preview
        st.subheader("Preview (first 10 rows)")
        st.dataframe(export_df.head(10), use_container_width=True)

        # Download button
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"lifestyle_premium_filtered_{len(export_df)}_areas.csv",
            mime="text/csv"
        )

        st.success(f"✓ Ready to export {len(export_df):,} areas with {len(export_columns)} columns")
    else:
        st.warning("Please select at least one column to export")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>
        🏖️ Lifestyle Explorer Dashboard |
        Data: ABS 2021 Census |
        Total SA1 Areas: {total:,} |
        Built with Streamlit & Plotly
    </small>
</div>
""".format(total=len(df)), unsafe_allow_html=True)
