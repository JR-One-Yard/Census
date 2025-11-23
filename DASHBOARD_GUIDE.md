# 🎯 Dashboard User Guide

## Interactive Lifestyle & Investment Dashboards

This guide explains how to use the two interactive dashboards for exploring Australian Census 2021 lifestyle and property investment data.

---

## 📋 Quick Start

### Prerequisites

All required packages are already installed:
- streamlit
- plotly
- folium
- statsmodels
- pandas, numpy, scipy

### Launch Dashboards

**Option 1: Use the Launcher Script** (Recommended)
```bash
cd /home/user/Census
./launch_dashboards.sh
```

Then select:
- `1` for Lifestyle Explorer Dashboard
- `2` for Investment Research Dashboard
- `3` to launch both simultaneously

**Option 2: Direct Launch**
```bash
# Lifestyle Explorer
streamlit run dashboard_lifestyle_explorer.py

# Investment Research
streamlit run dashboard_investment_research.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## 🏖️ Dashboard 1: Lifestyle Explorer

### Purpose
Explore and compare all 61,844 SA1 areas across Australia based on lifestyle factors, amenities, demographics, and location.

### Features

#### 🔍 Sidebar Filters
- **State**: Filter by one or multiple states
- **Lifestyle Premium Index**: Slider to filter by lifestyle score (0-100)
- **Property Price**: Budget range filter ($'000)
- **Median Income**: Income range filter ($/week)
- **Minimum Population**: Exclude low-population areas
- **Coastal Category**: Filter by beach proximity
  - Highly Coastal (<5km)
  - Coastal (5-20km)
  - Near Coast (20-50km)
  - Inland (>50km)

#### 📊 Tab 1: Overview
- **Scatter Plot**: Lifestyle vs Property Price with state colors
- **State Distribution**: Bar chart showing areas by state
- **Lifestyle Distribution**: Histogram of lifestyle premium scores
- **Coastal Analysis**: Average lifestyle by coastal category

**Use Case:** Get a quick overview of the data and identify patterns

#### 🗺️ Tab 2: Geographic Map
- **Interactive Map**: Plotly map showing lifestyle scores across Australia
- **Color-coded**: Red (low) to Green (high) lifestyle scores
- **Size**: Bubble size represents population
- **Hover**: Details on SA1 code, state, price, beach distance

**Use Case:** Visualize geographic patterns and find clusters of high-lifestyle areas

**Note:** Map shows max 5,000 areas for performance (randomly sampled if more)

#### 📈 Tab 3: Detailed Analysis
- **Correlation Matrix**: Heatmap showing relationships between metrics
- **Income vs Lifestyle**: How income brackets affect lifestyle scores
- **Age Demographics**: Lifestyle patterns by age group
- **Top 20 Table**: Best performing areas with full details

**Use Case:** Deep dive into statistical relationships and patterns

#### 🔍 Tab 4: Area Lookup
- **SA1 Code Search**: Enter specific SA1 code for detailed profile
- **Key Metrics**: Lifestyle score, price, income, population
- **Location Details**: State, coordinates, coastal category
- **Amenity Access**: Distances to beaches, parks, schools, hospitals
- **Demographics**: Age, education, family composition
- **Economics**: Income, rental yield, estimated rent
- **Score Breakdown**: Visual breakdown of 7 component scores

**Use Case:** Research a specific area in detail

#### 💾 Tab 5: Export Data
- **Column Selection**: Choose which columns to export
- **Preview**: See first 10 rows before download
- **CSV Download**: Export filtered data for further analysis

**Use Case:** Extract data for use in Excel, R, Python, or other tools

### Tips & Tricks

1. **Find Hidden Gems**: Set lifestyle >15, income <$900/wk
2. **Coastal Premium**: Compare "Highly Coastal" vs "Inland" in Overview tab
3. **State Comparison**: Clear all state filters, then select one at a time
4. **Population Filter**: Use min population 200+ for better data quality
5. **Export Custom Views**: Filter data, select columns, download CSV

---

## 💰 Dashboard 2: Investment Research

### Purpose
Analyze property investment opportunities with price forecasting, ROI calculations, and portfolio optimization.

### Features

#### 📊 Sidebar - Investment Criteria
- **Investment Strategy**:
  - **Growth**: Focus on capital appreciation
  - **Yield**: Prioritize rental returns
  - **Balanced**: Mix of both
  - **Value**: Undervalued opportunities
- **Target States**: Select preferred states
- **Budget**: Investment budget range ($'000)
- **Risk Tolerance**: Very Low to Very High
- **Investment Horizon**: 1, 3, 5, or 10 years
- **Minimum Population**: For better liquidity

#### 🎯 Tab 1: Top Opportunities
- **Strategy-Based Ranking**: Top opportunities for your selected strategy
- **Scatter Plot**: Price vs Growth Rate (sized by rental yield)
- **State Distribution**: Top states for opportunities
- **Detailed Table**: Full metrics for each opportunity
  - Current Price
  - Growth Rate
  - Rental Yield
  - Investment Score
  - 2029 Projected Price
  - Lifestyle Score

**Use Case:** Find the best investment opportunities matching your criteria

#### 📈 Tab 2: Price Forecasting
- **Individual Forecasts**: Enter SA1 code for 1-20 year price projection
- **Historical Data**: Shows 2019-2024 actual prices
- **Forecast Line**: Projected prices with confidence intervals (±20%)
- **Investment Projections**:
  - Current vs Future Price
  - Capital Gain
  - Total Return %
  - Annualized Return %
- **Rental Income Projection**:
  - Annual rental income
  - Total rent over investment period
  - Combined capital + rental return

**State-Level Trends**: If no SA1 entered, shows aggregate state forecasts

**Use Case:** Project future returns for specific properties

#### 💹 Tab 3: ROI Analysis
- **ROI Calculator**:
  - Enter purchase price
  - Set deposit % (5-100%)
  - Set holding period (1-30 years)
- **Automatic Calculations**:
  - Deposit required
  - Future value projection
  - Net profit (capital + rent - interest)
  - ROI % on deposit
  - Annualized ROI
- **Detailed Breakdown**: Itemized revenue and costs

**Assumptions**:
- Growth/yield based on similar properties in dataset
- 3% interest rate on loan
- No maintenance costs (conservative estimate)

**Use Case:** Calculate expected returns on investment

#### 🗺️ Tab 4: Geographic Trends
- **State Comparison**: Multi-metric view
  - Median Price by state
  - Growth Rate by state
  - Rental Yield by state
  - Investment Score by state
- **Interactive Map**: Geographic distribution of investment scores
  - Color: Investment score (red=low, green=high)
  - Size: Property price
  - Hover: Full details

**Use Case:** Identify which states offer best opportunities

#### 📊 Tab 5: Portfolio Builder
- **Auto-Generate**: Create diversified portfolio across states
- **Portfolio Metrics**:
  - Total investment value
  - Average growth rate
  - Average rental yield
  - Average total return
- **Diversification**: Automatically selects across different states

**Use Case:** Build a balanced multi-property portfolio

### Investment Strategies Explained

#### 🚀 Growth Strategy
- **Focus**: Capital appreciation
- **Best for**: Long-term investors, high risk tolerance
- **Metrics**: Prioritizes annual growth rate and lifestyle premium
- **Typical returns**: Higher capital gains, lower rental yield

#### 💵 Yield Strategy
- **Focus**: Rental income
- **Best for**: Cash flow investors, retirees
- **Metrics**: Prioritizes rental yield % and affordability
- **Typical returns**: Lower capital gains, higher rental yield

#### ⚖️ Balanced Strategy
- **Focus**: Mix of growth and yield
- **Best for**: Most investors
- **Metrics**: Investment score (combines all factors)
- **Typical returns**: Moderate capital gains + rental income

#### 💎 Value Strategy
- **Focus**: Undervalued areas
- **Best for**: Patient investors, value seekers
- **Metrics**: High lifestyle premium / low price ratio
- **Typical returns**: Variable, depends on market timing

### Tips & Tricks

1. **Compare Strategies**: Try each strategy and note differences
2. **Forecast Multiple Areas**: Compare forecasts for top 3-5 opportunities
3. **Calculate Leverage**: Use ROI calculator with 10% deposit vs 50% deposit
4. **Geographic Diversification**: Use Portfolio Builder for multiple states
5. **Risk Assessment**: Higher growth = higher risk, balance your portfolio

---

## 🔧 Troubleshooting

### Dashboard won't start
```bash
# Check if streamlit is installed
pip list | grep streamlit

# If not installed
pip install streamlit plotly folium streamlit-folium statsmodels
```

### Port already in use
```bash
# Use a different port
streamlit run dashboard_lifestyle_explorer.py --server.port 8502
```

### Map not showing
- Check internet connection (uses OpenStreetMap)
- Try refreshing the page
- Reduce number of points (use filters)

### Slow performance
- Apply more restrictive filters
- Increase minimum population filter
- Map auto-samples to 5,000 points if more

### Data not loading
```bash
# Verify data file exists
ls -lh /home/user/Census/lifestyle_premium_outputs/lifestyle_premium_with_prices.csv

# If missing, regenerate
python3 /home/user/Census/generate_property_prices.py
```

---

## 📊 Data Dictionary

### Key Metrics Explained

| Metric | Range | Description |
|--------|-------|-------------|
| **Lifestyle Premium Index** | 0-100 | Composite score of 7 lifestyle factors |
| **Investment Score** | 0-100 | Growth potential + yield + affordability |
| **Property Value Score** | 0-100 | High lifestyle / low price ratio |
| **Annual Growth Rate** | 3-12% | Projected annual price appreciation |
| **Rental Yield** | 2-6% | Annual rent / property price |
| **Price-to-Income Ratio** | 5-20x | Property price / annual income |
| **Affordability Score** | 0-100 | Inverse of price-to-income (higher = more affordable) |

### Component Scores (Lifestyle Index)

1. **Beach Score** (20%): Distance to nearest beaches
2. **Park Score** (15%): Number of parks within 5km
3. **School Score** (25%): Distance to nearest schools
4. **Hospital Score** (15%): Distance to nearest hospitals
5. **Education Score** (10%): Year 12+ completion rates
6. **Income Score** (10%): Median personal income
7. **Age Score** (5%): Age preference curve (peak at 40-45)

---

## 💡 Use Cases & Examples

### Use Case 1: First Home Buyer
**Goal**: Find affordable area with good lifestyle near Brisbane

**Dashboard**: Lifestyle Explorer
1. Filter: State = QLD
2. Filter: Property Price = $300-500K
3. Filter: Lifestyle Index = 15-25
4. Tab 1: View scatter plot, identify clusters
5. Tab 2: Check map for geographic distribution
6. Tab 4: Look up specific SA1 codes for details
7. Tab 5: Export top 10 for further research

### Use Case 2: Growth Investor
**Goal**: High capital appreciation, 5-year horizon

**Dashboard**: Investment Research
1. Strategy: Growth
2. States: QLD, WA (high growth states)
3. Budget: $400-600K
4. Horizon: 5 years
5. Tab 1: Review top opportunities
6. Tab 2: Forecast top 3 areas
7. Tab 3: Calculate ROI for best option
8. Decision: Choose highest annualized return

### Use Case 3: Yield Investor
**Goal**: Positive cash flow for retirement income

**Dashboard**: Investment Research
1. Strategy: Yield
2. Risk: Low-Medium
3. Budget: $300-500K
4. Tab 1: Find high-yield properties
5. Tab 3: Use ROI calculator with 30% deposit
6. Calculate: Ensure rental income > loan repayments
7. Tab 5: Build 3-property portfolio for diversification

### Use Case 4: Value Hunter
**Goal**: Undervalued areas before market catches on

**Dashboard**: Both
1. **Lifestyle Explorer**:
   - Filter: Lifestyle >18, Income <$800/wk
   - Tab 3: Check correlation analysis
   - Export: Top 20 candidates
2. **Investment Research**:
   - Strategy: Value
   - Review: Property Value Score
   - Forecast: 10-year projection
   - Decision: Buy areas with improving infrastructure

### Use Case 5: Coastal Lifestyle Buyer
**Goal**: Beach proximity, family-friendly

**Dashboard**: Lifestyle Explorer
1. Filter: Coastal Category = "Highly Coastal" or "Coastal"
2. Filter: Min Population = 500
3. Filter: Lifestyle Index = 16+
4. Tab 3: Check age demographics (look for 30-50 range)
5. Tab 4: Look up school proximity
6. Result: Beach lifestyle + good schools

---

## 🎓 Advanced Features

### Comparing Multiple Areas

**Method 1: Screenshots**
1. Look up Area 1 in Tab 4
2. Take screenshot
3. Look up Area 2 in Tab 4
4. Compare side-by-side

**Method 2: Export & Analyze**
1. Filter to your top 5 candidates
2. Export to CSV
3. Open in Excel/Google Sheets
4. Create custom comparison table

### Custom Filters

**Hidden Gem Filter:**
- Lifestyle Index: 17-24
- Property Price: $350-550K
- Income: $600-900/wk
- Min Population: 300

**Coastal Premium Filter:**
- Coastal Category: Highly Coastal
- Lifestyle Index: 15+
- Property Price: Any
- Compare to Inland equivalents

**High Growth Filter:**
- Strategy: Growth
- States: WA, QLD
- Budget: <$600K
- Investment Score: >80

### Data Analysis Workflows

**Workflow 1: Market Research**
1. Lifestyle Explorer: Explore & Filter
2. Export: Top 50 areas
3. Investment Dashboard: Forecast each
4. Spreadsheet: Compare all forecasts
5. Decision: Top 3 finalists

**Workflow 2: Portfolio Optimization**
1. Investment Dashboard: Generate portfolio
2. Note: SA1 codes
3. Lifestyle Explorer: Look up each
4. Verify: All meet lifestyle criteria
5. Investment Dashboard: Total ROI calculation

---

## 🔐 Data Quality & Limitations

### Data Confidence Levels
- **High**: Population ≥ 200
- **Medium**: Population 50-199
- **Low**: Population < 50

### Synthetic Data Components
- **Property Prices**: Modeled based on lifestyle + location (not actual market prices)
- **Amenity Locations**: Realistic distribution patterns (not exact addresses)
- **Coordinates**: Generated from SA1 patterns (not precise centroids)

### Real Data Components
- **Census Data**: Actual ABS 2021 Census (100% accurate)
- **Demographics**: Real population, income, age, education
- **Geographic Patterns**: Based on actual Australian geography

### Recommendations
1. Use these dashboards for **initial research and filtering**
2. Validate findings with:
   - domain.com.au or realestate.com.au for actual prices
   - Google Maps for precise amenity locations
   - Local real estate agents for market insights
3. Consider this a **decision support tool**, not financial advice

---

## 📞 Support & Feedback

### Getting Help
- Review this guide first
- Check Troubleshooting section
- Verify data files exist and are up-to-date

### Making Improvements
- Fork the repository
- Modify dashboard code
- Add new metrics or visualizations
- Submit pull requests

### Known Limitations
- Map performance with >5,000 points
- Forecasts assume constant growth rates (real markets vary)
- Synthetic property prices (for demonstration)
- No historical price trends (Census 2021 only)

---

## 🚀 Next Steps

### To Enhance These Dashboards:

1. **Real Property Data**
   - Integrate domain.com.au API
   - Add actual median prices
   - Include rental history

2. **Real Amenity Data**
   - Use OpenStreetMap Overpass API
   - Get exact locations
   - Add more amenity types

3. **Additional Features**
   - Saved searches
   - Email alerts
   - Comparison tables
   - PDF reports

4. **Machine Learning**
   - Price prediction models
   - Recommend similar areas
   - Cluster analysis
   - Trend detection

---

## 📚 References

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python/)
- [Australian Bureau of Statistics](https://www.abs.gov.au)
- [ASGS Geography](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs)

---

**Happy Exploring! 🏖️💰**

*Remember: These dashboards are for research purposes. Always consult qualified professionals before making investment decisions.*
