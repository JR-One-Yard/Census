#!/usr/bin/env python3
"""
💰 INVESTMENT RESEARCH DASHBOARD
Property investment analysis with price forecasting

Features:
- Investment opportunity ranking
- Property price forecasting (5-year projections)
- ROI calculations and comparisons
- Risk/return analysis
- Portfolio optimization suggestions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression

# Page configuration
st.set_page_config(
    page_title="Investment Research Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2ca02c;
        text-align: center;
        margin-bottom: 1rem;
    }
    .investment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .opportunity-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# Load Data
# ============================================================================

@st.cache_data
def load_data():
    """Load investment data with caching"""
    df = pd.read_csv('/home/user/Census/lifestyle_premium_outputs/lifestyle_premium_with_prices.csv')
    return df

# Load data
with st.spinner('Loading investment data...'):
    df = load_data()

# ============================================================================
# Header
# ============================================================================

st.markdown('<div class="main-header">💰 Investment Research Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <b>Property Investment Analysis & Forecasting</b> |
    Find high-growth opportunities | Optimize your portfolio
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar - Investment Criteria
# ============================================================================

st.sidebar.header("📊 Investment Criteria")

# Investment strategy
strategy = st.sidebar.radio(
    "Investment Strategy",
    ["Growth", "Yield", "Balanced", "Value"],
    help="Growth: High capital appreciation | Yield: High rental returns | Balanced: Mix | Value: Undervalued opportunities"
)

# State preference
states = ['All'] + sorted(df['state_name'].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "Target States",
    states,
    default=['All']
)

# Budget range
budget_range = st.sidebar.slider(
    "Investment Budget ($'000)",
    100,
    2000,
    (300, 800),
    step=50,
    help="Your property purchase budget"
)

# Risk tolerance
risk_tolerance = st.sidebar.select_slider(
    "Risk Tolerance",
    options=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
    value='Medium',
    help="Higher risk may offer higher returns"
)

# Investment horizon
horizon = st.sidebar.selectbox(
    "Investment Horizon",
    ["1 year", "3 years", "5 years", "10 years"],
    index=2,
    help="How long you plan to hold the investment"
)

# Minimum population (for liquidity)
min_pop = st.sidebar.number_input(
    "Minimum Population",
    min_value=50,
    max_value=2000,
    value=200,
    step=50,
    help="Higher population = better liquidity"
)

# Apply basic filters
df_filtered = df[df['Tot_P_P'] >= min_pop].copy()

if 'All' not in selected_states:
    df_filtered = df_filtered[df_filtered['state_name'].isin(selected_states)]

df_filtered = df_filtered[
    (df_filtered['median_property_price'] >= budget_range[0] * 1000) &
    (df_filtered['median_property_price'] <= budget_range[1] * 1000)
]

# Apply strategy-specific scoring
if strategy == "Growth":
    df_filtered['strategy_score'] = (
        df_filtered['annual_growth_rate'] * 70 +
        df_filtered['lifestyle_premium_index'] * 0.3
    )
elif strategy == "Yield":
    df_filtered['strategy_score'] = (
        df_filtered['rental_yield_pct'] * 15 +
        df_filtered['affordability_score'] * 0.3
    )
elif strategy == "Balanced":
    df_filtered['strategy_score'] = df_filtered['investment_score']
elif strategy == "Value":
    df_filtered['strategy_score'] = df_filtered['property_value_score']

st.sidebar.markdown(f"**{len(df_filtered):,}** opportunities found")

# ============================================================================
# Key Investment Metrics
# ============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    avg_growth = df_filtered['annual_growth_rate'].mean() * 100
    st.metric(
        "Avg Growth Rate",
        f"{avg_growth:.1f}%",
        help="Average annual price growth"
    )

with col2:
    avg_yield = df_filtered['rental_yield_pct'].mean()
    st.metric(
        "Avg Rental Yield",
        f"{avg_yield:.1f}%",
        help="Average rental yield"
    )

with col3:
    median_price = df_filtered['median_property_price'].median()
    st.metric(
        "Median Price",
        f"${median_price/1000:.0f}K",
        help="Median property price"
    )

with col4:
    avg_roi = (avg_growth + avg_yield)
    st.metric(
        "Avg Total Return",
        f"{avg_roi:.1f}%",
        help="Growth + Yield"
    )

with col5:
    median_p2i = df_filtered['price_to_income_ratio'].median()
    st.metric(
        "Median P/I Ratio",
        f"{median_p2i:.1f}x",
        help="Price to income ratio (affordability)"
    )

st.markdown("---")

# ============================================================================
# Main Tabs
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Top Opportunities",
    "📈 Price Forecasting",
    "💹 ROI Analysis",
    "🗺️ Geographic Trends",
    "📊 Portfolio Builder"
])

# ----------------------------------------------------------------------------
# TAB 1: Top Opportunities
# ----------------------------------------------------------------------------

with tab1:
    st.header("🎯 Top Investment Opportunities")

    # Strategy explanation
    strategy_info = {
        "Growth": "Focused on areas with highest capital appreciation potential based on historical growth rates and lifestyle improvements.",
        "Yield": "Prioritizes high rental returns and affordability for positive cash flow investments.",
        "Balanced": "Optimal mix of growth potential, rental yield, and affordability.",
        "Value": "Undervalued areas with high lifestyle premium relative to current prices."
    }

    st.info(f"**{strategy} Strategy:** {strategy_info[strategy]}")

    # Top opportunities
    top_n = st.slider("Number of opportunities to show", 10, 100, 20, step=10)
    top_opportunities = df_filtered.nlargest(top_n, 'strategy_score')

    col1, col2 = st.columns([2, 1])

    with col1:
        # Scatter plot
        fig_scatter = px.scatter(
            top_opportunities,
            x='median_property_price',
            y='annual_growth_rate',
            size='rental_yield_pct',
            color='state_name',
            hover_data=['SA1_CODE_2021', 'lifestyle_premium_index', 'investment_score'],
            title=f'Top {top_n} Opportunities: Price vs Growth Rate',
            labels={
                'median_property_price': 'Property Price ($)',
                'annual_growth_rate': 'Annual Growth Rate',
                'rental_yield_pct': 'Rental Yield %',
                'state_name': 'State'
            }
        )
        fig_scatter.update_yaxes(tickformat='.1%')
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        # State distribution
        state_dist = top_opportunities['state_name'].value_counts().head(5)
        fig_pie = px.pie(
            values=state_dist.values,
            names=state_dist.index,
            title=f'Top States (Top {top_n})'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Detailed table
    st.subheader("📋 Detailed Opportunity List")

    display_df = top_opportunities[[
        'SA1_CODE_2021', 'state_name', 'median_property_price',
        'annual_growth_rate', 'rental_yield_pct', 'investment_score',
        'projected_price_2029', 'lifestyle_premium_index'
    ]].copy()

    display_df['annual_growth_rate'] = display_df['annual_growth_rate'].apply(lambda x: f"{x*100:.1f}%")
    display_df['rental_yield_pct'] = display_df['rental_yield_pct'].apply(lambda x: f"{x:.1f}%")
    display_df['median_property_price'] = display_df['median_property_price'].apply(lambda x: f"${x:,.0f}")
    display_df['projected_price_2029'] = display_df['projected_price_2029'].apply(lambda x: f"${x:,.0f}")
    display_df.columns = [
        'SA1 Code', 'State', 'Current Price', 'Growth Rate',
        'Rental Yield', 'Inv Score', '2029 Price', 'Lifestyle'
    ]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 2: Price Forecasting
# ----------------------------------------------------------------------------

with tab2:
    st.header("📈 Property Price Forecasting")

    # Select area for detailed forecast
    col1, col2 = st.columns([3, 1])

    with col1:
        sa1_code_forecast = st.text_input(
            "Enter SA1 Code for Detailed Forecast",
            placeholder="e.g., 30905124513"
        )

    with col2:
        forecast_years = st.number_input(
            "Forecast Years",
            min_value=1,
            max_value=20,
            value=10,
            step=1
        )

    if sa1_code_forecast:
        area = df[df['SA1_CODE_2021'].astype(str) == sa1_code_forecast]

        if len(area) > 0:
            area = area.iloc[0]

            st.success(f"✓ Forecasting for SA1: {sa1_code_forecast} ({area['state_name']})")

            # Generate forecast
            current_price = area['median_property_price']
            growth_rate = area['annual_growth_rate']

            years = list(range(2019, 2025 + forecast_years))
            historical_prices = [area[f'price_{year}'] if f'price_{year}' in area.index and year <= 2024 else None for year in years]

            # Calculate forecasted prices
            forecast_prices = []
            for i, year in enumerate(years):
                if year <= 2024:
                    forecast_prices.append(historical_prices[i])
                else:
                    years_ahead = year - 2024
                    forecasted = current_price * ((1 + growth_rate) ** years_ahead)
                    forecast_prices.append(forecasted)

            # Create forecast dataframe
            forecast_df = pd.DataFrame({
                'Year': years,
                'Price': forecast_prices,
                'Type': ['Historical' if y <= 2024 else 'Forecast' for y in years]
            })

            # Plot
            fig_forecast = go.Figure()

            # Historical
            historical = forecast_df[forecast_df['Type'] == 'Historical']
            fig_forecast.add_trace(go.Scatter(
                x=historical['Year'],
                y=historical['Price'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))

            # Forecast
            forecasted = forecast_df[forecast_df['Type'] == 'Forecast']
            fig_forecast.add_trace(go.Scatter(
                x=forecasted['Year'],
                y=forecasted['Price'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='red', width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))

            # Add confidence interval (±20%)
            upper_bound = forecasted['Price'] * 1.2
            lower_bound = forecasted['Price'] * 0.8

            fig_forecast.add_trace(go.Scatter(
                x=forecasted['Year'],
                y=upper_bound,
                mode='lines',
                name='Upper Bound (+20%)',
                line=dict(width=0),
                showlegend=False
            ))

            fig_forecast.add_trace(go.Scatter(
                x=forecasted['Year'],
                y=lower_bound,
                mode='lines',
                name='Lower Bound (-20%)',
                line=dict(width=0),
                fillcolor='rgba(255,0,0,0.2)',
                fill='tonexty',
                showlegend=True
            ))

            fig_forecast.update_layout(
                title=f'Price Forecast for SA1 {sa1_code_forecast}',
                xaxis_title='Year',
                yaxis_title='Property Price ($)',
                hovermode='x unified',
                height=500
            )

            st.plotly_chart(fig_forecast, use_container_width=True)

            # Investment projections
            st.subheader("💰 Investment Projection")

            col1, col2, col3, col4 = st.columns(4)

            future_price = forecast_prices[-1]
            capital_gain = future_price - current_price
            total_return_pct = (capital_gain / current_price) * 100
            annual_return = ((future_price / current_price) ** (1/forecast_years) - 1) * 100

            with col1:
                st.metric(
                    "Current Price",
                    f"${current_price:,.0f}"
                )

            with col2:
                st.metric(
                    f"{years[-1]} Price",
                    f"${future_price:,.0f}",
                    delta=f"+${capital_gain:,.0f}"
                )

            with col3:
                st.metric(
                    "Total Return",
                    f"{total_return_pct:.1f}%",
                    help="Total capital appreciation"
                )

            with col4:
                st.metric(
                    "Annual Return",
                    f"{annual_return:.1f}%",
                    help="Annualized return"
                )

            # Rental income projection
            st.subheader("🏠 Rental Income Projection")

            rental_yield = area['rental_yield_pct'] / 100
            annual_rent = current_price * rental_yield
            total_rental_income = annual_rent * forecast_years

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Rental Yield",
                    f"{area['rental_yield_pct']:.1f}%"
                )

            with col2:
                st.metric(
                    "Annual Rent",
                    f"${annual_rent:,.0f}",
                    help="Estimated annual rental income"
                )

            with col3:
                st.metric(
                    f"Total Rent ({forecast_years}yr)",
                    f"${total_rental_income:,.0f}",
                    help=f"Total rental income over {forecast_years} years"
                )

            # Combined return
            total_gain = capital_gain + total_rental_income
            combined_return = (total_gain / current_price) * 100

            st.success(f"""
            **Total Investment Return ({forecast_years} years):**
            - Capital Gain: ${capital_gain:,.0f} ({total_return_pct:.1f}%)
            - Rental Income: ${total_rental_income:,.0f}
            - **Combined Total: ${total_gain:,.0f} ({combined_return:.1f}% total return)**
            """)

        else:
            st.error(f"❌ No area found with SA1 code: {sa1_code_forecast}")

    else:
        # Show aggregate forecast trends
        st.info("👆 Enter an SA1 code above for detailed forecast, or view aggregate trends below")

        # State-level growth forecast
        state_forecast = df_filtered.groupby('state_name').agg({
            'median_property_price': 'median',
            'annual_growth_rate': 'median',
            'rental_yield_pct': 'median'
        }).reset_index()

        # Calculate 5-year projections
        state_forecast['price_2029'] = (
            state_forecast['median_property_price'] *
            (1 + state_forecast['annual_growth_rate']) ** 5
        )

        state_forecast['growth_amount'] = state_forecast['price_2029'] - state_forecast['median_property_price']

        fig_state = px.bar(
            state_forecast,
            x='state_name',
            y='growth_amount',
            color='annual_growth_rate',
            title='5-Year Projected Capital Growth by State',
            labels={
                'state_name': 'State',
                'growth_amount': 'Projected 5-Year Growth ($)',
                'annual_growth_rate': 'Growth Rate'
            },
            color_continuous_scale='RdYlGn'
        )

        st.plotly_chart(fig_state, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 3: ROI Analysis
# ----------------------------------------------------------------------------

with tab3:
    st.header("💹 Return on Investment Analysis")

    # ROI calculator
    st.subheader("🧮 ROI Calculator")

    col1, col2, col3 = st.columns(3)

    with col1:
        purchase_price = st.number_input(
            "Purchase Price ($)",
            min_value=100000,
            max_value=5000000,
            value=500000,
            step=50000
        )

    with col2:
        deposit_pct = st.slider(
            "Deposit %",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )

    with col3:
        holding_period = st.number_input(
            "Holding Period (years)",
            min_value=1,
            max_value=30,
            value=7,
            step=1
        )

    # Calculate ROI scenarios
    deposit = purchase_price * (deposit_pct / 100)
    loan = purchase_price - deposit

    # Find similar properties in dataset
    similar = df_filtered[
        (df_filtered['median_property_price'] >= purchase_price * 0.8) &
        (df_filtered['median_property_price'] <= purchase_price * 1.2)
    ]

    if len(similar) > 0:
        avg_growth = similar['annual_growth_rate'].mean()
        avg_yield = similar['rental_yield_pct'].mean() / 100

        future_value = purchase_price * ((1 + avg_growth) ** holding_period)
        capital_gain = future_value - purchase_price
        total_rent = purchase_price * avg_yield * holding_period

        # Assume 3% interest rate on loan
        interest_rate = 0.03
        total_interest = loan * interest_rate * holding_period

        net_profit = capital_gain + total_rent - total_interest

        roi = (net_profit / deposit) * 100
        annual_roi = ((1 + roi/100) ** (1/holding_period) - 1) * 100

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Deposit Required", f"${deposit:,.0f}")

        with col2:
            st.metric("Future Value", f"${future_value:,.0f}")

        with col3:
            st.metric("Net Profit", f"${net_profit:,.0f}")

        with col4:
            st.metric("ROI", f"{roi:.1f}%", f"{annual_roi:.1f}% p.a.")

        # Detailed breakdown
        st.subheader("📊 Detailed Breakdown")

        breakdown_data = {
            'Component': [
                'Purchase Price',
                'Deposit',
                'Loan',
                f'Future Value ({holding_period}yr)',
                'Capital Gain',
                f'Total Rental Income ({holding_period}yr)',
                f'Total Interest Paid ({holding_period}yr)',
                '**Net Profit**',
                '**ROI on Deposit**'
            ],
            'Amount': [
                f"${purchase_price:,.0f}",
                f"${deposit:,.0f}",
                f"${loan:,.0f}",
                f"${future_value:,.0f}",
                f"${capital_gain:,.0f}",
                f"${total_rent:,.0f}",
                f"-${total_interest:,.0f}",
                f"**${net_profit:,.0f}**",
                f"**{roi:.1f}%**"
            ]
        }

        st.table(pd.DataFrame(breakdown_data))

        st.info(f"""
        **Assumptions:** Based on {len(similar):,} similar properties in dataset
        - Average growth rate: {avg_growth*100:.1f}% p.a.
        - Average rental yield: {avg_yield*100:.1f}% p.a.
        - Interest rate: 3.0% p.a. (fixed)
        """)

    else:
        st.warning("No similar properties found in dataset for this price range")

# ----------------------------------------------------------------------------
# TAB 4: Geographic Trends
# ----------------------------------------------------------------------------

with tab4:
    st.header("🗺️ Geographic Investment Trends")

    # State comparison
    st.subheader("State-by-State Comparison")

    state_metrics = df_filtered.groupby('state_name').agg({
        'median_property_price': 'median',
        'annual_growth_rate': 'median',
        'rental_yield_pct': 'median',
        'investment_score': 'mean',
        'SA1_CODE_2021': 'count'
    }).reset_index()

    state_metrics.columns = [
        'State', 'Median Price', 'Growth Rate',
        'Rental Yield', 'Inv Score', 'Count'
    ]

    # Create multi-metric visualization
    fig_states = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Median Price', 'Growth Rate', 'Rental Yield', 'Investment Score'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )

    fig_states.add_trace(
        go.Bar(x=state_metrics['State'], y=state_metrics['Median Price'], name='Price'),
        row=1, col=1
    )

    fig_states.add_trace(
        go.Bar(x=state_metrics['State'], y=state_metrics['Growth Rate']*100, name='Growth'),
        row=1, col=2
    )

    fig_states.add_trace(
        go.Bar(x=state_metrics['State'], y=state_metrics['Rental Yield'], name='Yield'),
        row=2, col=1
    )

    fig_states.add_trace(
        go.Bar(x=state_metrics['State'], y=state_metrics['Inv Score'], name='Score'),
        row=2, col=2
    )

    fig_states.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig_states.update_yaxes(title_text="Rate (%)", row=1, col=2)
    fig_states.update_yaxes(title_text="Yield (%)", row=2, col=1)
    fig_states.update_yaxes(title_text="Score", row=2, col=2)

    fig_states.update_layout(height=600, showlegend=False)

    st.plotly_chart(fig_states, use_container_width=True)

    # Map visualization
    st.subheader("Geographic Distribution")

    sample_size = min(3000, len(df_filtered))
    df_map = df_filtered.sample(n=sample_size) if len(df_filtered) > sample_size else df_filtered

    fig_map = px.scatter_mapbox(
        df_map,
        lat='latitude',
        lon='longitude',
        color='investment_score',
        size='median_property_price',
        hover_data=['SA1_CODE_2021', 'state_name', 'annual_growth_rate', 'rental_yield_pct'],
        color_continuous_scale='RdYlGn',
        zoom=3,
        center={'lat': -25, 'lon': 135},
        title=f'Investment Score Distribution (showing {len(df_map):,} areas)'
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        height=600
    )

    st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 5: Portfolio Builder
# ----------------------------------------------------------------------------

with tab5:
    st.header("📊 Portfolio Builder")

    st.info("🚧 Build a diversified property portfolio by selecting multiple SA1 areas")

    # Portfolio selection
    portfolio_size = st.number_input(
        "Number of properties in portfolio",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )

    # Auto-suggest diversified portfolio
    if st.button("🎲 Generate Diversified Portfolio"):
        # Select diverse properties across states and strategies
        portfolio = pd.DataFrame()

        for state in df_filtered['state_name'].unique()[:portfolio_size]:
            state_data = df_filtered[df_filtered['state_name'] == state]
            if len(state_data) > 0:
                best = state_data.nlargest(1, 'investment_score')
                portfolio = pd.concat([portfolio, best])

        if len(portfolio) < portfolio_size:
            remaining = portfolio_size - len(portfolio)
            additional = df_filtered.nlargest(remaining, 'investment_score')
            portfolio = pd.concat([portfolio, additional])

        portfolio = portfolio.head(portfolio_size)

        st.success(f"✓ Generated portfolio with {len(portfolio)} properties")

        # Display portfolio
        portfolio_display = portfolio[[
            'SA1_CODE_2021', 'state_name', 'median_property_price',
            'annual_growth_rate', 'rental_yield_pct', 'investment_score'
        ]].copy()

        portfolio_display['annual_growth_rate'] = portfolio_display['annual_growth_rate'].apply(lambda x: f"{x*100:.1f}%")
        portfolio_display['rental_yield_pct'] = portfolio_display['rental_yield_pct'].apply(lambda x: f"{x:.1f}%")
        portfolio_display['median_property_price'] = portfolio_display['median_property_price'].apply(lambda x: f"${x:,.0f}")

        portfolio_display.columns = ['SA1', 'State', 'Price', 'Growth', 'Yield', 'Score']

        st.dataframe(portfolio_display, use_container_width=True, hide_index=True)

        # Portfolio metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_investment = portfolio['median_property_price'].sum()
            st.metric("Total Investment", f"${total_investment/1e6:.2f}M")

        with col2:
            avg_growth = portfolio['annual_growth_rate'].mean() * 100
            st.metric("Avg Growth", f"{avg_growth:.1f}%")

        with col3:
            avg_yield = portfolio['rental_yield_pct'].mean()
            st.metric("Avg Yield", f"{avg_yield:.1f}%")

        with col4:
            total_return = avg_growth + avg_yield
            st.metric("Avg Total Return", f"{total_return:.1f}%")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>
        💰 Investment Research Dashboard |
        For informational purposes only - Not financial advice |
        Always consult a licensed financial advisor
    </small>
</div>
""", unsafe_allow_html=True)
