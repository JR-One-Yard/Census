#!/usr/bin/env python3
"""
Streamlit Web Dashboard for Housing Affordability Analysis
Run with: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page config
st.set_page_config(
    page_title="Australian Housing Affordability Dashboard",
    page_icon="🏘️",
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
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .crisis-badge {
        background: #dc3545;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .sweet-badge {
        background: #28a745;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    comprehensive = pd.read_csv('housing_affordability_comprehensive.csv')
    crisis = pd.read_csv('housing_crisis_areas.csv')
    sweet = pd.read_csv('housing_affordability_sweet_spots.csv')
    sydney = pd.read_csv('sydney_housing_comprehensive.csv')
    sydney_crisis = pd.read_csv('sydney_crisis_areas.csv')
    sydney_sweet = pd.read_csv('sydney_sweet_spots.csv')

    return {
        'comprehensive': comprehensive,
        'crisis': crisis,
        'sweet': sweet,
        'sydney': sydney,
        'sydney_crisis': sydney_crisis,
        'sydney_sweet': sydney_sweet
    }

data = load_data()

# Header
st.markdown('<div class="main-header">🏘️ Australian Housing Affordability Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">2021 Census Data - Comprehensive Analysis</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select View",
    ["🏠 Overview", "🔍 Suburb Search", "📊 Crisis Areas", "✅ Sweet Spots",
     "🌆 Sydney Analysis", "📈 Comparison Tool", "📉 Detailed Analytics"]
)

# =============================================================================
# PAGE 1: OVERVIEW
# =============================================================================
if page == "🏠 Overview":
    st.header("National Housing Affordability Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Suburbs Analyzed",
            f"{len(data['comprehensive']):,}",
            delta=None
        )

    with col2:
        avg_mort_stress = data['comprehensive']['mortgage_stress_ratio'].mean()
        st.metric(
            "Avg Mortgage Stress",
            f"{avg_mort_stress:.1f}%",
            delta=f"{avg_mort_stress - 30:.1f}% vs threshold",
            delta_color="inverse"
        )

    with col3:
        avg_rent_stress = data['comprehensive']['rent_stress_ratio'].mean()
        st.metric(
            "Avg Rent Stress",
            f"{avg_rent_stress:.1f}%",
            delta=f"{avg_rent_stress - 30:.1f}% vs threshold",
            delta_color="inverse"
        )

    with col4:
        crisis_count = len(data['crisis'])
        st.metric(
            "Crisis Areas",
            f"{crisis_count:,}",
            delta=f"{crisis_count/len(data['comprehensive'])*100:.1f}% of total"
        )

    st.markdown("---")

    # Charts row 1
    col1, col2 = st.columns(2)

    with col1:
        # Stress distribution
        fig1 = go.Figure()
        fig1.add_trace(go.Histogram(
            x=data['comprehensive']['mortgage_stress_ratio'],
            name='Mortgage Stress',
            marker_color='steelblue',
            opacity=0.7,
            nbinsx=50
        ))
        fig1.add_trace(go.Histogram(
            x=data['comprehensive']['rent_stress_ratio'],
            name='Rent Stress',
            marker_color='coral',
            opacity=0.7,
            nbinsx=50
        ))
        fig1.add_vline(x=30, line_dash="dash", line_color="red",
                      annotation_text="30% Threshold")
        fig1.update_layout(
            title="Housing Stress Distribution",
            xaxis_title="Stress Ratio (%)",
            yaxis_title="Number of Suburbs",
            barmode='overlay',
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Tenure type pie
        tenure_data = {
            'Owned Outright': data['comprehensive']['pct_owned_outright'].mean(),
            'Owned w/ Mortgage': data['comprehensive']['pct_owned_mortgage'].mean(),
            'Renting': data['comprehensive']['pct_renting'].mean()
        }
        fig2 = go.Figure(data=[go.Pie(
            labels=list(tenure_data.keys()),
            values=list(tenure_data.values()),
            marker=dict(colors=['#2E86AB', '#A23B72', '#F18F01'])
        )])
        fig2.update_layout(
            title="Average Housing Tenure Distribution",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Charts row 2
    col1, col2 = st.columns(2)

    with col1:
        # Income vs Rent Stress scatter
        sample = data['comprehensive'].sample(min(1000, len(data['comprehensive'])))
        fig3 = px.scatter(
            sample,
            x='Median_tot_hhd_inc_weekly',
            y='rent_stress_ratio',
            color='pct_young_adults',
            size='total_population',
            hover_data=['Suburb'],
            title='Income vs Rent Stress',
            labels={
                'Median_tot_hhd_inc_weekly': 'Median Income ($/week)',
                'rent_stress_ratio': 'Rent Stress (%)',
                'pct_young_adults': '% Young Adults'
            },
            color_continuous_scale='Viridis'
        )
        fig3.add_hline(y=30, line_dash="dash", line_color="red")
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # Crisis score distribution
        fig4 = go.Figure(data=[go.Histogram(
            x=data['comprehensive']['crisis_score'],
            marker_color='darkred',
            nbinsx=40
        )])
        crisis_threshold = data['comprehensive']['crisis_score'].quantile(0.90)
        fig4.add_vline(x=crisis_threshold, line_dash="dash", line_color="orange",
                      annotation_text=f"Top 10% ({crisis_threshold:.1f})")
        fig4.update_layout(
            title="Crisis Score Distribution",
            xaxis_title="Crisis Score",
            yaxis_title="Number of Suburbs",
            height=400
        )
        st.plotly_chart(fig4, use_container_width=True)

# =============================================================================
# PAGE 2: SUBURB SEARCH
# =============================================================================
elif page == "🔍 Suburb Search":
    st.header("Suburb Lookup Tool")

    search_query = st.text_input("🔍 Search by suburb code or name:", "")

    if search_query:
        # Filter suburbs
        filtered = data['comprehensive'][
            data['comprehensive']['SAL_CODE_2021'].str.contains(search_query, case=False, na=False) |
            data['comprehensive']['Suburb'].str.contains(search_query, case=False, na=False)
        ].head(20)

        if len(filtered) > 0:
            st.success(f"Found {len(filtered)} suburb(s)")

            for _, suburb in filtered.iterrows():
                with st.expander(f"📍 {suburb['Suburb']} ({suburb['SAL_CODE_2021']})"):
                    # Badges
                    if suburb['crisis_score'] >= 35:
                        st.markdown('<span class="crisis-badge">⚠️ CRISIS AREA</span>',
                                  unsafe_allow_html=True)

                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Median Age", f"{suburb['Median_age_persons']:.0f} years")
                        st.metric("Median Income", f"${suburb['Median_tot_hhd_inc_weekly']:.0f}/week")

                    with col2:
                        st.metric("Median Rent", f"${suburb['Median_rent_weekly']:.0f}/week")
                        st.metric("Median Mortgage", f"${suburb['Median_mortgage_repay_monthly']:.0f}/month")

                    with col3:
                        mort_stress = suburb['mortgage_stress_ratio']
                        st.metric("Mortgage Stress", f"{mort_stress:.1f}%",
                                delta=f"{mort_stress - 30:.1f}% vs threshold",
                                delta_color="inverse")
                        st.metric("% Owned Outright", f"{suburb['pct_owned_outright']:.1f}%")

                    with col4:
                        rent_stress = suburb['rent_stress_ratio']
                        st.metric("Rent Stress", f"{rent_stress:.1f}%",
                                delta=f"{rent_stress - 30:.1f}% vs threshold",
                                delta_color="inverse")
                        st.metric("% Renting", f"{suburb['pct_renting']:.1f}%")

                    # Additional info
                    st.markdown("**Additional Metrics:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"- Young Adults (15-34): {suburb['pct_young_adults']:.1f}%")
                        st.write(f"- Low Income HH: {suburb['pct_low_income']:.1f}%")
                    with col2:
                        st.write(f"- Apartments: {suburb['pct_apartments']:.1f}%")
                        st.write(f"- Persons/Bedroom: {suburb['Average_num_psns_per_bedroom']:.2f}")
                    with col3:
                        st.write(f"- Crisis Score: {suburb['crisis_score']:.1f}")
                        st.write(f"- Population: {suburb['total_population']:,.0f}")

        else:
            st.warning("No suburbs found matching your search.")
    else:
        st.info("💡 Enter a suburb code (e.g., SAL10001) or name to begin searching.")

# =============================================================================
# PAGE 3: CRISIS AREAS
# =============================================================================
elif page == "📊 Crisis Areas":
    st.header("Housing Crisis Areas Analysis")

    st.markdown(f"""
    **Identified {len(data['crisis']):,} high-crisis areas** (top 10% by crisis score)

    Crisis areas are characterized by:
    - High mortgage/rent stress ratios (often >30%)
    - Low median incomes
    - High rental dependency
    - Overcrowding indicators
    """)

    # Top crisis areas
    st.subheader("Top 30 Crisis Areas")

    top_crisis = data['crisis'].nlargest(30, 'crisis_score')

    fig = go.Figure(data=[go.Bar(
        x=top_crisis['crisis_score'],
        y=top_crisis['Suburb'],
        orientation='h',
        marker=dict(
            color=top_crisis['crisis_score'],
            colorscale='Reds',
            showscale=True
        ),
        text=top_crisis['crisis_score'].round(1),
        textposition='outside'
    )])

    fig.update_layout(
        xaxis_title='Crisis Score',
        height=800,
        yaxis=dict(autorange="reversed")
    )

    st.plotly_chart(fig, use_container_width=True)

    # Crisis factors
    st.subheader("Average Crisis Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Mortgage Stress", f"{data['crisis']['mortgage_stress_ratio'].mean():.1f}%")

    with col2:
        st.metric("Avg Rent Stress", f"{data['crisis']['rent_stress_ratio'].mean():.1f}%")

    with col3:
        st.metric("Avg % Renting", f"{data['crisis']['pct_renting'].mean():.1f}%")

    with col4:
        st.metric("Avg Median Income", f"${data['crisis']['Median_tot_hhd_inc_weekly'].mean():.0f}/week")

    # Detailed table
    st.subheader("Crisis Areas Data Table")
    st.dataframe(
        top_crisis[['Suburb', 'mortgage_stress_ratio', 'rent_stress_ratio',
                    'Median_tot_hhd_inc_weekly', 'pct_renting', 'crisis_score']],
        use_container_width=True
    )

# =============================================================================
# PAGE 4: SWEET SPOTS
# =============================================================================
elif page == "✅ Sweet Spots":
    st.header("Affordability Sweet Spots")

    st.markdown(f"""
    **Found {len(data['sweet']):,} affordability sweet spots**

    Sweet spots offer:
    - Low stress ratios (<30%)
    - Reasonable housing costs
    - Good dwelling mix (houses)
    - Active homeownership markets
    """)

    # Top sweet spots
    st.subheader("Top 30 Sweet Spots")

    # Check if affordability_score exists in sweet spots
    if 'affordability_score' in data['sweet'].columns:
        top_sweet = data['sweet'].nlargest(30, 'affordability_score')
        score_col = 'affordability_score'
    else:
        # Sort by lowest combined stress
        data['sweet']['combined_stress'] = (data['sweet']['mortgage_stress_ratio'] +
                                            data['sweet']['rent_stress_ratio']) / 2
        top_sweet = data['sweet'].nsmallest(30, 'combined_stress')
        score_col = 'combined_stress'

    fig = go.Figure(data=[go.Bar(
        x=top_sweet[score_col] if score_col in top_sweet.columns else top_sweet['mortgage_stress_ratio'],
        y=top_sweet['Suburb'],
        orientation='h',
        marker=dict(
            color=top_sweet[score_col] if score_col in top_sweet.columns else top_sweet['mortgage_stress_ratio'],
            colorscale='Greens',
            showscale=True
        ),
        text=(top_sweet[score_col] if score_col in top_sweet.columns
              else top_sweet['mortgage_stress_ratio']).round(1),
        textposition='outside'
    )])

    fig.update_layout(
        xaxis_title='Affordability Score' if score_col == 'affordability_score' else 'Combined Stress',
        height=800,
        yaxis=dict(autorange="reversed")
    )

    st.plotly_chart(fig, use_container_width=True)

    # Sweet spot characteristics
    st.subheader("Average Sweet Spot Characteristics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Mortgage Stress", f"{data['sweet']['mortgage_stress_ratio'].mean():.1f}%")

    with col2:
        st.metric("Avg Rent Stress", f"{data['sweet']['rent_stress_ratio'].mean():.1f}%")

    with col3:
        st.metric("Avg Median Income", f"${data['sweet']['Median_tot_hhd_inc_weekly'].mean():.0f}/week")

    with col4:
        st.metric("Avg Median Rent", f"${data['sweet']['Median_rent_weekly'].mean():.0f}/week")

# =============================================================================
# PAGE 5: SYDNEY ANALYSIS
# =============================================================================
elif page == "🌆 Sydney Analysis":
    st.header("Sydney Metro Housing Analysis")

    st.markdown(f"""
    **Sydney Metro Analysis:**
    - {len(data['sydney']):,} suburbs analyzed
    - {len(data['sydney_crisis']):,} crisis areas identified
    - {len(data['sydney_sweet']):,} sweet spots found
    """)

    # Sydney vs Australia comparison
    st.subheader("Sydney vs Australia Comparison")

    comparison = {
        'Metric': ['Mortgage Stress', 'Rent Stress', 'Median Income', '% Renting'],
        'Australia': [
            data['comprehensive']['mortgage_stress_ratio'].mean(),
            data['comprehensive']['rent_stress_ratio'].mean(),
            data['comprehensive']['Median_tot_hhd_inc_weekly'].mean(),
            data['comprehensive']['pct_renting'].mean()
        ],
        'Sydney': [
            data['sydney']['mortgage_stress_ratio'].mean(),
            data['sydney']['rent_stress_ratio'].mean(),
            data['sydney']['Median_tot_hhd_inc_weekly'].mean(),
            data['sydney']['pct_renting'].mean()
        ]
    }

    fig = go.Figure(data=[
        go.Bar(name='Australia', x=comparison['Metric'], y=comparison['Australia'],
               marker_color='lightblue'),
        go.Bar(name='Sydney', x=comparison['Metric'], y=comparison['Sydney'],
               marker_color='darkred')
    ])

    fig.update_layout(
        barmode='group',
        height=400,
        yaxis_title='Value'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Sydney crisis areas
    st.subheader("Top 20 Sydney Crisis Areas")

    top_sydney_crisis = data['sydney_crisis'].nlargest(20, 'crisis_score')

    st.dataframe(
        top_sydney_crisis[['Suburb', 'mortgage_stress_ratio', 'rent_stress_ratio',
                          'Median_tot_hhd_inc_weekly', 'crisis_score']],
        use_container_width=True
    )

# =============================================================================
# PAGE 6: COMPARISON TOOL
# =============================================================================
elif page == "📈 Comparison Tool":
    st.header("Suburb Comparison Tool")

    st.markdown("Select multiple suburbs to compare their housing affordability metrics.")

    # Suburb selection
    suburb_list = data['comprehensive']['Suburb'].dropna().unique()
    selected_suburbs = st.multiselect(
        "Select suburbs to compare (max 5):",
        suburb_list,
        max_selections=5
    )

    if selected_suburbs:
        comparison_data = data['comprehensive'][
            data['comprehensive']['Suburb'].isin(selected_suburbs)
        ]

        if len(comparison_data) > 0:
            # Create comparison charts
            metrics = ['mortgage_stress_ratio', 'rent_stress_ratio',
                      'Median_tot_hhd_inc_weekly', 'Median_rent_weekly',
                      'pct_owned_outright', 'pct_renting']

            metric_names = ['Mortgage Stress (%)', 'Rent Stress (%)',
                           'Median Income ($/week)', 'Median Rent ($/week)',
                           '% Owned Outright', '% Renting']

            for i in range(0, len(metrics), 2):
                col1, col2 = st.columns(2)

                with col1:
                    if i < len(metrics):
                        fig = go.Figure(data=[go.Bar(
                            x=comparison_data['Suburb'],
                            y=comparison_data[metrics[i]],
                            marker_color='steelblue'
                        )])
                        fig.update_layout(
                            title=metric_names[i],
                            yaxis_title=metric_names[i],
                            height=300
                        )
                        if 'stress' in metrics[i].lower():
                            fig.add_hline(y=30, line_dash="dash", line_color="red")
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    if i+1 < len(metrics):
                        fig = go.Figure(data=[go.Bar(
                            x=comparison_data['Suburb'],
                            y=comparison_data[metrics[i+1]],
                            marker_color='coral'
                        )])
                        fig.update_layout(
                            title=metric_names[i+1],
                            yaxis_title=metric_names[i+1],
                            height=300
                        )
                        if 'stress' in metrics[i+1].lower():
                            fig.add_hline(y=30, line_dash="dash", line_color="red")
                        st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.subheader("Detailed Comparison")
            st.dataframe(comparison_data[['Suburb'] + metrics], use_container_width=True)

    else:
        st.info("Please select suburbs to compare.")

# =============================================================================
# PAGE 7: DETAILED ANALYTICS
# =============================================================================
else:  # Detailed Analytics
    st.header("Detailed Analytics")

    analysis_type = st.selectbox(
        "Select Analysis Type:",
        ["Income Quartile Analysis", "Dwelling Type Impact", "Age Demographics",
         "Correlation Analysis"]
    )

    if analysis_type == "Income Quartile Analysis":
        st.subheader("Housing Stress by Income Quartile")

        # Create income quartiles
        data['comprehensive']['income_quartile'] = pd.qcut(
            data['comprehensive']['Median_tot_hhd_inc_weekly'],
            q=4, labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)']
        )

        quartile_analysis = data['comprehensive'].groupby('income_quartile')[
            ['mortgage_stress_ratio', 'rent_stress_ratio']
        ].mean()

        fig = go.Figure(data=[
            go.Bar(name='Mortgage Stress', x=quartile_analysis.index,
                   y=quartile_analysis['mortgage_stress_ratio'], marker_color='steelblue'),
            go.Bar(name='Rent Stress', x=quartile_analysis.index,
                   y=quartile_analysis['rent_stress_ratio'], marker_color='coral')
        ])

        fig.add_hline(y=30, line_dash="dash", line_color="red",
                     annotation_text="30% Threshold")
        fig.update_layout(
            barmode='group',
            xaxis_title='Income Quartile',
            yaxis_title='Stress Ratio (%)',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(quartile_analysis, use_container_width=True)

    elif analysis_type == "Dwelling Type Impact":
        st.subheader("Stress by Apartment Concentration")

        # Create apartment categories
        data['comprehensive']['apartment_category'] = pd.cut(
            data['comprehensive']['pct_apartments'],
            bins=[0, 10, 30, 50, 100],
            labels=['Low (<10%)', 'Medium (10-30%)', 'High (30-50%)', 'Very High (>50%)']
        )

        dwelling_analysis = data['comprehensive'].groupby('apartment_category')[
            ['mortgage_stress_ratio', 'rent_stress_ratio', 'pct_renting']
        ].mean()

        fig = make_subplots(rows=1, cols=2,
                           subplot_titles=('Stress Ratios', 'Rental Percentage'))

        fig.add_trace(
            go.Bar(name='Mortgage Stress', x=dwelling_analysis.index,
                   y=dwelling_analysis['mortgage_stress_ratio'], marker_color='steelblue'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Rent Stress', x=dwelling_analysis.index,
                   y=dwelling_analysis['rent_stress_ratio'], marker_color='coral'),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(x=dwelling_analysis.index,
                   y=dwelling_analysis['pct_renting'], marker_color='purple',
                   showlegend=False),
            row=1, col=2
        )

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(dwelling_analysis, use_container_width=True)

    elif analysis_type == "Age Demographics":
        st.subheader("Housing Metrics by Age Profile")

        # Show correlations with age
        age_corr = data['comprehensive'][[
            'Median_age_persons', 'mortgage_stress_ratio', 'rent_stress_ratio',
            'pct_owned_outright', 'pct_young_adults'
        ]].corr()['Median_age_persons'].drop('Median_age_persons')

        fig = go.Figure(data=[go.Bar(
            x=age_corr.index,
            y=age_corr.values,
            marker_color=['red' if x < 0 else 'green' for x in age_corr.values]
        )])

        fig.update_layout(
            title='Correlation with Median Age',
            xaxis_title='Metric',
            yaxis_title='Correlation Coefficient',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    else:  # Correlation Analysis
        st.subheader("Metric Correlation Heatmap")

        metrics = [
            'mortgage_stress_ratio', 'rent_stress_ratio', 'crisis_score',
            'Median_tot_hhd_inc_weekly', 'pct_renting', 'pct_apartments',
            'pct_young_adults', 'pct_low_income'
        ]

        corr_matrix = data['comprehensive'][metrics].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}'
        ))

        fig.update_layout(
            title='Housing Metrics Correlation Matrix',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📊 Data Source: 2021 Australian Census (Second Release - R2)</p>
    <p>🏘️ Australian Housing Affordability Dashboard | Analyzing {num_suburbs:,} Suburbs</p>
</div>
""".format(num_suburbs=len(data['comprehensive'])), unsafe_allow_html=True)
