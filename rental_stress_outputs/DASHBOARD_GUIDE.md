# 🏘️ Rental Stress Monitoring Dashboard - User Guide

## Overview

An interactive web-based dashboard for real-time monitoring and analysis of rental stress, public housing needs, and investment prioritization across Australia's 61,844 SA1 statistical areas.

---

## 🚀 Quick Start

### Method 1: Using the Launch Script (Recommended)
```bash
./launch_dashboard.sh
```

### Method 2: Direct Launch
```bash
streamlit run advanced_step5_dashboard.py
```

### Method 3: Custom Port
```bash
streamlit run advanced_step5_dashboard.py --server.port 8502
```

---

## 📊 Dashboard Features

### 1. Overview Dashboard
**Purpose**: High-level national statistics and trends

**Features**:
- Real-time key metrics (stressed areas, housing gaps, average scores)
- Interactive pie charts for stress category distribution
- Investment priority breakdowns
- Histogram of rental stress score distribution

**Use Cases**:
- Quick status check of national rental stress
- Identify proportion of areas in different stress categories
- Monitor overall investment priorities

---

### 2. Geographic Analysis
**Purpose**: Spatial visualization of rental stress patterns

**Features**:
- Interactive maps with 5 different views:
  - Rental Stress Hotspots
  - Public Housing Gaps
  - Investment Priorities
  - Employment Accessibility
  - Combined Housing+Transport Burden
- Zoom, pan, and hover for detailed SA1 information
- Color-coded by intensity/score

**Use Cases**:
- Identify geographic clusters of rental stress
- Locate critical housing gap areas
- Assess spatial distribution of investment needs
- Plan targeted interventions by region

---

### 3. Temporal Trends
**Purpose**: Track changes over time (2016-2021-2026)

**Features**:
- **Rent vs Income Growth**: Compare 5-year growth rates
  - Histogram distributions
  - Scatter plot showing affordability deterioration
  - Median growth indicators

- **Stress Transitions**: Track SA1 movement between stress categories
  - Entered Stress
  - Exited Stress
  - Remained Stressed
  - Remained Affordable

- **Future Projections**: 2026 scenario forecasts
  - Business as Usual
  - Crisis Scenario
  - Policy Intervention
  - Comparative line charts

**Use Cases**:
- Understand historical trends
- Identify accelerating vs. improving areas
- Project future needs under different scenarios
- Inform long-term policy planning

---

### 4. Scenario Modeling
**Purpose**: Compare investment strategies and outcomes

**Features**:
- Summary table of all 6 scenarios ($0 to $13B)
- Budget vs Households Assisted visualization
- Gap closure percentage charts
- Cost efficiency analysis (cost per household)
- Interactive scatter plots for ROI comparison

**Scenarios Available**:
1. Baseline (No Investment) - $0
2. Budget-Constrained - $2B
3. Moderate Investment - $5B
4. Major Investment - $13B
5. Accessibility-Focused - $5B
6. Equity-Focused - $5B

**Use Cases**:
- Evaluate different funding levels
- Compare targeting strategies
- Assess cost-effectiveness
- Justify budget requests

---

### 5. Priority Areas
**Purpose**: Identify top investment targets

**Features**:
- Top 100 areas by different criteria:
  - Highest Rental Stress
  - Critical Housing Gaps
  - Optimal Locations (Accessibility)
  - High Low-Income Concentration
  - Severe Combined Burden

- Interactive data table with sortable columns
- Key metrics summary (total gap, avg stress, low-income HH)
- Exportable results

**Use Cases**:
- Generate priority lists for funding applications
- Target specific vulnerability types
- Balance efficiency vs equity considerations
- Create implementation roadmaps

---

### 6. Data Export
**Purpose**: Download analysis results

**Features**:
- Multiple export options:
  - Filtered SA1 Data (based on sidebar selections)
  - Top 500 Rental Stress Hotspots
  - Top 500 Investment Priorities
  - Critical Housing Gaps
  - Scenario Allocations

- Preview before download
- CSV format for easy import to Excel, GIS, etc.
- Summary statistics for exported data

**Use Cases**:
- Create custom reports
- Import into GIS software
- Share with stakeholders
- Offline analysis

---

## 🎛️ Dashboard Controls (Sidebar)

### View Selection
Radio buttons to switch between 6 main views

### Data Filters

#### State Filter
- Select one or multiple states
- "All" option for national view
- Instantly updates all visualizations

#### Stress Level Filter
- Slider from 0-100
- Filters SA1s by minimum rental stress score
- Useful for focusing on higher-priority areas

#### Filter Counter
- Shows number of SA1s matching current filters
- Updates in real-time

---

## 💡 Usage Tips

### For Policy Makers
1. Start with **Overview Dashboard** for quick status check
2. Use **Geographic Analysis** to identify regional clusters
3. Review **Scenario Modeling** to justify budget requests
4. Export **Priority Areas** for implementation planning

### For Researchers
1. Use **Temporal Trends** to understand historical patterns
2. Export filtered data for custom analysis
3. Cross-reference **Geographic** and **Priority** views
4. Leverage scenario data for impact studies

### For Housing Authorities
1. Filter by your state using sidebar controls
2. Identify top priority areas for construction
3. Use **Accessibility** maps to optimize site selection
4. Export data for integration with your systems

### For Community Organizations
1. Focus on **Priority Areas** with high vulnerability
2. Use **Combined Burden** view for transport poverty
3. Export data for advocacy and grant applications
4. Share visualizations with community members

---

## 📈 Metrics Explained

### Rental Stress Score (0-100)
Composite score based on:
- Rent-to-income ratio (35%)
- Low-income concentration (25%)
- Public housing gap (20%)
- Unemployment rate (10%)
- Public housing supply (10%)

**Interpretation**:
- 0-25: Low stress
- 25-50: Moderate stress
- 50-75: High stress
- 75-100: Critical stress

### Investment Priority Score (0-100)
Optimized allocation score based on:
- Rental stress (40%)
- Supply-demand gap (30%)
- Vulnerable population (20%)
- Unemployment (10%)

**Interpretation**:
- Higher score = Higher priority for investment
- Balances need with impact potential

### Optimal Location Score (0-100)
Multi-criteria score for best social housing sites:
- Housing stress (50%)
- Employment accessibility (30%)
- Public transport connectivity (20%)

**Interpretation**:
- Higher score = Better location for residents
- Maximizes affordability + opportunity

### Employment Accessibility Score (0-100)
Distance-based access to employment:
- 0-10km: Excellent (100)
- 10-20km: Good (50-100)
- 20-40km: Moderate (20-50)
- 40-60km: Limited (10-20)
- 60km+: Poor (0-10)

---

## 🔧 Technical Details

### System Requirements
- Python 3.8+
- Streamlit 1.28+
- Plotly 5.0+
- Pandas, NumPy

### Data Source
- 2021 Australian Census (SA1 level)
- 61,844 statistical areas
- Multiple census tables (G02, G33, G37, G40, G43)

### Performance
- Data caching for fast load times
- Filtered datasets for responsive UI
- Sampled data for large visualizations (where appropriate)

### Browser Support
- Chrome (recommended)
- Firefox
- Safari
- Edge

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check Streamlit installation
pip install streamlit plotly pandas numpy

# Try alternate port
streamlit run advanced_step5_dashboard.py --server.port 8502
```

### Data not loading
- Verify all CSV files exist in `rental_stress_outputs/` directories
- Check file permissions
- Ensure paths are correct

### Maps not displaying
- Requires internet connection for map tiles
- Check firewall settings
- Try refreshing browser

### Filters not working
- Clear browser cache
- Restart dashboard
- Check console for errors

---

## 📚 Additional Resources

### Related Files
- `rental_stress_outputs/EXECUTIVE_SUMMARY.md` - Full analysis report
- `rental_stress_outputs/ANALYSIS_SUMMARY.md` - Technical methodology
- `rental_stress_outputs/temporal_analysis/TEMPORAL_ANALYSIS_REPORT.md` - Trend analysis
- `rental_stress_outputs/transport_accessibility/TRANSPORT_ACCESSIBILITY_REPORT.md` - Accessibility study
- `rental_stress_outputs/scenario_modeling/SCENARIO_MODELING_REPORT.md` - Investment scenarios

### Data Files
All analysis outputs available in:
- `rental_stress_outputs/` - Main results
- `rental_stress_outputs/geographic_maps/` - Map data & GeoJSON
- `rental_stress_outputs/temporal_analysis/` - Historical & projections
- `rental_stress_outputs/transport_accessibility/` - Accessibility metrics
- `rental_stress_outputs/scenario_modeling/` - Investment allocations

### Scripts
- `rental_stress_analysis.py` - Core metrics calculation
- `spatial_regression_models.py` - Predictive modeling
- `advanced_step1_geographic_mapping.py` - Map generation
- `advanced_step2_temporal_analysis.py` - Trend analysis
- `advanced_step3_transport_accessibility.py` - Accessibility metrics
- `advanced_step4_scenario_modeling.py` - Scenario simulation
- `advanced_step5_dashboard.py` - This dashboard

---

## 🎯 Best Practices

### Workflow Recommendations

1. **Initial Exploration**
   - Start with Overview Dashboard (unfiltered)
   - Review national statistics
   - Identify overall trends

2. **Focused Analysis**
   - Apply state/stress filters
   - Drill down to specific regions
   - Use Geographic view for spatial patterns

3. **Priority Identification**
   - Review Priority Areas for different criteria
   - Export top targets
   - Cross-reference with local knowledge

4. **Scenario Planning**
   - Compare investment strategies
   - Assess budget requirements
   - Evaluate cost-effectiveness

5. **Reporting**
   - Export filtered datasets
   - Save visualizations (screenshot)
   - Reference markdown reports

---

## 📞 Support & Feedback

For questions, issues, or feature requests:

1. Check this user guide
2. Review related markdown reports
3. Consult source code comments
4. Contact your data analysis team

---

## 🔄 Updates & Maintenance

### Data Refresh
To update with new census data:
1. Replace CSV files in `rental_stress_outputs/`
2. Ensure column names match
3. Restart dashboard

### Adding New Scenarios
1. Run `advanced_step4_scenario_modeling.py` with new parameters
2. New scenario files auto-detected by dashboard
3. Restart to see changes

### Customization
Dashboard is fully customizable:
- Edit `advanced_step5_dashboard.py`
- Modify color schemes, layouts, metrics
- Add new views or features
- All Streamlit/Plotly code included

---

**Dashboard Version**: 1.0
**Last Updated**: November 2025
**Data Version**: 2021 Census (Second Release)

---

*Happy analyzing! 🏘️*
