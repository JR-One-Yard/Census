# Sydney Housing Affordability Analysis & Interactive Tools

## 🌆 Sydney Analysis Summary

This analysis provides a deep dive into housing affordability across Greater Sydney, comparing it to national averages and identifying crisis areas and opportunities.

### Key Sydney Findings

**Overall Statistics:**
- **2,444 suburbs** analyzed in Greater Sydney
- **325 crisis areas** identified (13.3% of Sydney suburbs)
- **1,052 sweet spots** found (43.0% of Sydney suburbs)

**Sydney vs Australia:**
| Metric | Australia | Sydney | Difference |
|--------|-----------|--------|------------|
| Mortgage Stress | 24.0% | 26.5% | +10.4% higher |
| Rent Stress | 20.3% | 22.6% | +11.3% higher |
| Median Rent | $331/week | $386/week | +16.8% higher |
| Median Mortgage | $1,713/month | $1,973/month | +15.2% higher |
| % Apartments | 5.4% | 7.9% | +44.7% higher |

**Key Insights:**
- Sydney experiences **higher housing stress** than national average
- **Rents are 17% higher** in Sydney metro
- **Mortgages are 15% higher** in Sydney metro
- Sydney has **45% more apartments** than national average
- Despite higher costs, Sydney median income is only **5% higher**

---

## 📁 Sydney Analysis Output Files

### Data Files (CSV)
1. **sydney_housing_comprehensive.csv** - All 2,444 Sydney suburbs with full metrics
2. **sydney_crisis_areas.csv** - 325 Sydney crisis areas
3. **sydney_sweet_spots.csv** - 1,052 Sydney sweet spots
4. **sydney_vs_australia_comparison.csv** - Detailed comparison table
5. **sydney_young_adult_lockout.csv** - Top 20 areas locking out young adults
6. **sydney_family_lockout.csv** - Top 20 areas locking out families

### Visualizations
Located in `sydney_analysis_plots/`:
1. **sydney_vs_australia_comparison.png** - 4-panel comparison chart
2. **sydney_crisis_analysis.png** - Crisis area deep dive

---

## 🔍 Top Sydney Crisis Areas

**Top 10 Highest Crisis Scores:**

| Rank | Suburb Code | Crisis Score | Mortgage Stress | Rent Stress | Median Income |
|------|-------------|--------------|----------------|-------------|---------------|
| 1 | SAL11186 | 64.6 | 107.5% | 20.0% | $651/week |
| 2 | SAL11568 | 55.8 | 101.0% | 35.5% | $619/week |
| 3 | SAL13117 | 52.4 | 96.1% | 68.7% | $961/week |
| 4 | SAL13762 | 52.3 | 64.6% | 35.6% | $697/week |
| 5 | SAL14333 | 48.2 | 44.0% | 24.0% | $775/week |
| 6 | SAL10797 | 47.4 | 57.9% | 42.3% | $710/week |
| 7 | SAL10022 | 47.0 | 54.0% | 23.3% | $944/week |
| 8 | SAL10923 | 46.8 | 58.8% | 20.5% | $1,020/week |
| 9 | SAL12150 | 46.2 | 64.2% | 43.0% | $721/week |
| 10 | SAL13907 | 46.2 | 67.3% | 31.7% | $788/week |

**Crisis Characteristics:**
- **Extreme mortgage stress**: Many areas >100% (spending entire income on housing!)
- **Very low incomes**: $600-$1,000/week (below living wage)
- **High rental dependency**: 50-80% of residents renting
- **Severe overcrowding** in some areas

---

## ✅ Top Sydney Sweet Spots

**Top 10 Best Affordability Scores:**

| Rank | Suburb Code | Affordability Score | Mortgage Stress | Rent Stress | Median Income |
|------|-------------|---------------------|----------------|-------------|---------------|
| 1 | SAL11749 | 92.4 | 13.4% | 11.4% | $1,406/week |
| 2 | SAL13826 | 92.3 | 13.1% | 12.1% | $1,912/week |
| 3 | SAL13972 | 92.2 | 8.6% | 10.7% | $931/week |
| 4 | SAL10348 | 91.2 | 16.0% | 13.8% | $2,025/week |
| 5 | SAL13070 | 90.8 | 15.5% | 14.2% | $1,053/week |

**Sweet Spot Characteristics:**
- **Low stress ratios**: All well below 30% threshold
- **Manageable costs**: Rents $100-$280/week, Mortgages $345-$1,400/month
- **Solid incomes**: $900-$2,100/week (middle-income range)
- **Predominantly houses**: Good for families
- **Active homeownership**: Healthy mix of owners and renters

---

## 🛠️ Interactive Tools Guide

### Tool 1: HTML Interactive Visualizations

**Location:** `interactive_tools/` directory

**Available Tools:**
1. **suburb_lookup.html** 🔍 - **MAIN LOOKUP TOOL**
   - Searchable database of all 7,922 suburbs
   - Real-time search by code or name
   - Detailed metrics for each suburb
   - Crisis/Sweet Spot badges
   - **How to use:** Open in web browser, type to search

2. **income_vs_rent_stress_australia.html**
   - Interactive scatter plot
   - 2,000 suburb sample
   - Color-coded by young adult percentage
   - Hover for details

3. **income_vs_mortgage_stress_sydney.html**
   - Sydney-specific analysis
   - Color-coded by apartment concentration
   - Interactive zoom and pan

4. **crisis_score_analysis.html**
   - Explorer for crisis areas
   - Interactive filtering
   - Hover details on income and stress

5. **top_crisis_areas.html**
   - Interactive bar chart
   - Top 30 national crisis areas
   - Click and hover for details

6. **top_sweet_spots.html**
   - Top 30 affordability sweet spots
   - Interactive rankings
   - Sortable and filterable

7. **top_sydney_crisis_areas.html**
   - Sydney-specific crisis rankings
   - Interactive bar chart
   - Detailed hover information

8. **sydney_vs_australia_comparison.html**
   - Interactive comparison chart
   - Toggle between metrics
   - Visual differences highlighted

9. **housing_dashboard.html**
   - Multi-panel overview
   - 4 charts in one view
   - Interactive exploration

10. **correlation_heatmap.html**
    - Metric correlation analysis
    - Interactive hover for values
    - Identify relationships

**How to Use HTML Tools:**
```bash
# Simply open any HTML file in your web browser
open interactive_tools/suburb_lookup.html

# Or navigate to the file and double-click
```

---

### Tool 2: Streamlit Web Dashboard

**File:** `streamlit_dashboard.py`

**Features:**
- 🏠 **Overview** - National statistics and charts
- 🔍 **Suburb Search** - Search and explore detailed metrics
- 📊 **Crisis Areas** - Analyze high-risk suburbs
- ✅ **Sweet Spots** - Find affordable areas
- 🌆 **Sydney Analysis** - Sydney-specific deep dive
- 📈 **Comparison Tool** - Compare up to 5 suburbs side-by-side
- 📉 **Detailed Analytics** - Income quartiles, dwelling types, correlations

**How to Run:**
```bash
# Install Streamlit (if not already installed)
pip install streamlit

# Run the dashboard
streamlit run streamlit_dashboard.py

# Dashboard will open in your browser at http://localhost:8501
```

**Dashboard Navigation:**
1. Use sidebar to select different views
2. Interactive charts - hover, zoom, pan
3. Search functionality in Suburb Search page
4. Compare suburbs in Comparison Tool
5. Download data tables as CSV

---

### Tool 3: Analysis Scripts

**Sydney Analysis Script:**
```bash
python3 sydney_housing_crisis_analysis.py
```
**Outputs:**
- Detailed console analysis
- Sydney-specific CSV files
- Comparison statistics
- Visual plots

**Interactive Tools Creation:**
```bash
python3 create_interactive_tools.py
```
**Outputs:**
- All 10 HTML interactive tools
- Plotly visualizations
- Searchable lookup tool

---

## 📊 Understanding the Metrics

### Stress Ratios
**30% Rule:** Housing costs should not exceed 30% of household income

**Categories:**
- **Manageable:** <30% (affordable)
- **Moderate Stress:** 30-40% (borderline)
- **Severe Stress:** 40-50% (critical)
- **Extreme Stress:** >50% (crisis)

**Mortgage Stress Ratio:**
```
(Monthly Mortgage Payment / Monthly Household Income) × 100
```

**Rent Stress Ratio:**
```
(Weekly Rent / Weekly Household Income) × 100
```

### Crisis Score
**Formula:**
```
Crisis Score = (Mortgage Stress × 0.25) +
               (Rent Stress × 0.25) +
               (% Renting × 0.2) +
               (% Low Income × 0.15) +
               (Overcrowding × 0.15)
```

**Interpretation:**
- **<30:** Low risk
- **30-35:** Moderate risk
- **35-45:** High risk (crisis threshold)
- **>45:** Extreme crisis

### Affordability Score
**Formula:**
```
Affordability Score = ((100 - Mortgage Stress) × 0.3) +
                      ((100 - Rent Stress) × 0.3) +
                      (% Houses × 0.2) +
                      ((100 - % Small Dwellings) × 0.2)
```

**Interpretation:**
- **>90:** Excellent affordability (sweet spot)
- **85-90:** Very good affordability
- **80-85:** Good affordability
- **<80:** Below average

---

## 🎯 Use Cases

### For First Home Buyers
1. Open `suburb_lookup.html`
2. Search suburbs in your target area
3. Look for:
   - Low mortgage stress (<30%)
   - Active ownership market (>20% mortgaged)
   - Sweet spot badge
4. Cross-reference with `sydney_sweet_spots.csv`

### For Renters
1. Use `income_vs_rent_stress_australia.html`
2. Filter by your income level
3. Look for areas below 30% stress line
4. Check `suburb_lookup.html` for specific suburbs

### For Policy Makers
1. Review `sydney_crisis_areas.csv`
2. Use `housing_dashboard.html` for overview
3. Run `streamlit_dashboard.py` for deep analytics
4. Focus interventions on top crisis areas

### For Researchers
1. Use `correlation_heatmap.html` to identify relationships
2. Explore `streamlit_dashboard.py` detailed analytics
3. Download data from CSV files
4. Analyze trends across income quartiles and dwelling types

---

## 📈 Advanced Features

### Streamlit Dashboard Tips

**Filtering Data:**
- Use sidebar selectors
- Search by suburb name or code
- Filter by crisis/sweet spot status

**Downloading Data:**
- Most tables have download buttons
- Export to CSV for further analysis
- Screenshots for presentations

**Comparison Analysis:**
- Select up to 5 suburbs
- Side-by-side metric comparison
- Visual and tabular views

### HTML Tool Tips

**Suburb Lookup:**
- Type partial names (e.g., "Syd" finds all Sydney suburbs)
- Results update in real-time
- Shows top 20 matches
- Click to expand full details

**Interactive Charts:**
- Hover for tooltips
- Zoom with scroll
- Pan by clicking and dragging
- Double-click to reset view
- Legend toggle on/off

---

## 🚀 Next Steps

### Recommended Analyses

1. **Time-Series Analysis** (if 2016 data available)
   - Track stress changes 2016→2021
   - Identify rapidly deteriorating suburbs

2. **Geographic Mapping**
   - Plot crisis areas on map
   - Identify spatial clusters
   - Analyze proximity to services

3. **External Data Integration**
   - School quality data
   - Transport infrastructure
   - Employment centers
   - Crime statistics

4. **Predictive Modeling**
   - Forecast future crisis areas
   - Model impact of policy interventions
   - Predict price movements

### Contributing

To extend this analysis:
1. Fork repository
2. Add new metrics or visualizations
3. Update analysis scripts
4. Submit pull request

---

## 📚 Data Sources

**Primary Source:** 2021 Australian Census (Second Release - R2)
- **Publisher:** Australian Bureau of Statistics (ABS)
- **Release Date:** December 2022
- **License:** Creative Commons
- **Coverage:** 15,352 total suburbs (7,922 with sufficient data)

**Census Tables Used:**
- G01, G02: Demographics and medians
- G32, G33: Income by household type
- G37-G41: Housing tenure, mortgage, rent, dwellings

---

## 💡 Tips & Troubleshooting

### HTML Files Not Opening?
- Ensure file extensions are `.html`
- Right-click → Open With → Browser
- Some browsers block local JavaScript - use Chrome or Firefox

### Streamlit Not Starting?
```bash
# Check Streamlit is installed
pip install streamlit

# Run from Census directory
cd /path/to/Census
streamlit run streamlit_dashboard.py

# If port 8501 is busy
streamlit run streamlit_dashboard.py --server.port 8502
```

### Data Not Loading?
- Ensure all CSV files are in same directory
- Check file paths in scripts
- Run analysis scripts first to generate data

### Slow Performance?
- HTML tools work offline (fast)
- Streamlit may be slow with full dataset
- Use filters to reduce data size
- Sample data for exploration

---

## 📞 Support

For questions or issues:
1. Check this README
2. Review `HOUSING_AFFORDABILITY_CRISIS_REPORT.md`
3. Examine source code comments
4. Verify data files exist

---

## 🎓 Acknowledgments

Data provided by Australian Bureau of Statistics (ABS)

Analysis framework developed using:
- Python pandas, numpy
- Plotly for interactive visualizations
- Streamlit for web dashboard
- Matplotlib/Seaborn for static plots

---

**Last Updated:** November 2024
**Version:** 2.0
**Data Version:** 2021 Census R2
