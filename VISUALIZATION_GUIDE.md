# TOD Analysis - Visualization Guide

**Comprehensive guide to all visualizations, charts, and interactive dashboards**

---

## 📊 Quick Start

### Generating All Visualizations

```bash
# 1. Generate static visualizations (5 PNG files)
python3 tod_visualizations.py

# 2. Generate interactive visualizations (6 HTML files)
python3 tod_interactive_visualizations.py

# 3. Export GIS-compatible data
python3 tod_gis_export.py
```

**Total Runtime:** ~2-3 minutes
**Output Directory:** `visualizations/`

---

## 📁 File Index

### Static Visualizations (PNG)

| File | Size | Description |
|------|------|-------------|
| `01_state_comparison_dashboard.png` | ~300KB | 4-panel state comparison |
| `02_modal_split_analysis.png` | ~200KB | National & international modal split |
| `03_tod_score_distribution.png` | ~400KB | Distribution analysis (4 panels) |
| `04_car_dependency_heatmap.png` | ~250KB | Car dependency by category & state |
| `05_priority_investment_dashboard.png` | ~500KB | Investment priorities overview |

### Interactive Visualizations (HTML)

| File | Size | Description | Features |
|------|------|-------------|----------|
| `interactive_01_state_dashboard.html` | ~1MB | State comparison (4 panels) | Hover tooltips, zoom |
| `interactive_02_3d_explorer.html` | ~2MB | 3D scatter of 6,184 SA1s | Rotate, zoom, filter |
| `interactive_03_modal_split_sunburst.html` | ~800KB | Hierarchical modal split | Click to drill down |
| `interactive_04_priority_treemap.html` | ~600KB | Priority areas by state | Interactive sizing |
| `interactive_05_economic_impact.html` | ~1.5MB | Economic impact dashboard | Cumulative metrics |
| `interactive_06_top_opportunities_table.html` | ~400KB | Top 100 SA1s table | Sortable, searchable |

### GIS Exports (CSV + JSON)

| File | Records | Description |
|------|---------|-------------|
| `gis_export_complete_sa1.csv` | 61,844 | All SA1s with categories |
| `gis_export_sa2_aggregated.csv` | 2,472 | SA2-level aggregation |
| `gis_export_priority_areas.csv` | 4,796 | Priority 1 & 2 only |
| `gis_export_top_1000_enhanced.csv` | 1,000 | Top opportunities + metrics |
| `gis_export_metadata.json` | - | Field descriptions & usage |

---

## 📈 Static Visualizations

### 1. State Comparison Dashboard

**File:** `01_state_comparison_dashboard.png`

**4 Panels:**
1. **Car Dependency by State** (horizontal bar chart)
   - Color-coded by intensity (red scale)
   - National average line (83.7%)
   - Sorted highest to lowest

2. **Public Transit Usage by State** (horizontal bar chart)
   - Color-coded (green scale)
   - National average line (6.4%)
   - Sorted highest to lowest

3. **Average TOD Score by State** (horizontal bar chart)
   - Color-coded (viridis scale)
   - National average line (66.4)
   - Sorted highest to lowest

4. **Total Commuters by State** (vertical bar chart)
   - Color-coded (blue scale)
   - Values shown in millions
   - Sorted highest to lowest

**Key Insights:**
- QLD and SA have highest car dependency (85.9%)
- WA has highest transit usage (9.1%)
- ACT has highest average TOD score (74.4)
- NSW has most commuters (2.0M)

---

### 2. Modal Split Analysis

**File:** `02_modal_split_analysis.png`

**2 Panels:**

1. **Current Modal Split** (pie chart)
   - Private Vehicle: 86.5% (6.81M)
   - Public Transit: 7.1% (557K)
   - Active Transport: 4.6% (361K)
   - Exploded slices for visibility

2. **Australia vs. Global Best Practice** (grouped bar chart)
   - Compares: Australia, Target, Copenhagen, Singapore, Amsterdam
   - Shows car, transit, and active transport percentages
   - Highlights gap between current and best practice

**Key Insights:**
- Australia's sustainable transport (11.7%) far below global leaders
- Copenhagen: 65% sustainable transport
- Singapore: 70% public transit
- Amsterdam: 70% sustainable transport

---

### 3. TOD Score Distribution

**File:** `03_tod_score_distribution.png`

**4 Panels:**

1. **Histogram of TOD Scores**
   - 50 bins across 0-100 range
   - Mean (66.4) and median (68.5) lines
   - Shows right-skewed distribution

2. **TOD Score by State** (box plot)
   - Shows distribution range per state
   - Identifies outliers
   - Sorted by median TOD score

3. **TOD Score vs. Commuters** (scatter plot)
   - X-axis: Total commuters (log scale)
   - Y-axis: TOD score
   - Color: Car dependency ratio
   - 61,844 points

4. **Top 1000 by State** (bar chart)
   - Number of top opportunities per state
   - Color-coded by state
   - Shows which states have most high-priority areas

**Key Insights:**
- Most SA1s score between 60-75
- High commuter volume doesn't always mean high TOD score
- Car dependency correlates with higher TOD scores (opportunity)

---

### 4. Car Dependency Heatmap

**File:** `04_car_dependency_heatmap.png`

**2 Panels:**

1. **SA1 Areas by Car Dependency Level** (bar chart)
   - 5 categories: <50%, 50-70%, 70-80%, 80-90%, >90%
   - Color-coded from green (low) to red (extreme)
   - Shows percentage of SA1s in each category
   - **50.2% of SA1s have >90% car dependency!**

2. **State-wise Car Dependency Heatmap** (heatmap)
   - Rows: States (sorted by avg car dependency)
   - Columns: Dependency categories
   - Cell values: Percentage of SA1s
   - Red = high percentage, Green = low percentage

**Key Insights:**
- 31,060 SA1s have >90% car dependency
- Only 5,471 SA1s have <70% car dependency
- QLD has 61% of SA1s in >90% category
- NT has most diverse distribution

---

### 5. Priority Investment Dashboard

**File:** `05_priority_investment_dashboard.png`

**Complex multi-panel dashboard:**

**Top Panel:**
- Priority tier comparison (3 bars)
- Priority 1: 4,484 areas (High Score + Volume)
- Priority 2: 1,496 areas (Employment Centers)
- Priority 3: 60 areas (Multimodal Potential)

**Middle Row (3 panels):**

1. **Commute Pain Points**
   - 67 pain points identified
   - 42K affected commuters
   - 95% average car dependency

2. **Transit Corridors by State**
   - Top 6 states for corridor opportunities
   - NSW leads with most corridors
   - Color-coded bars

3. **Top Hub-and-Spoke Networks**
   - Top 8 hubs by potential modal shift
   - Potential new transit users per hub
   - Ranked bars

**Bottom Row (3 panels):**
- National metrics summary
- Potential impact summary
- Top opportunities summary

**Key Insights:**
- Clear prioritization framework for investment
- Pain points require immediate intervention
- Hub networks offer concentrated impact

---

## 🎮 Interactive Visualizations

### 1. State Dashboard (HTML)

**File:** `interactive_01_state_dashboard.html`

**Features:**
- **Hover tooltips** with exact values
- **Zoom and pan** on all charts
- **Export** to PNG from browser
- **Responsive** design

**4 Interactive Panels:**
- Same layout as static version
- Click legend items to toggle visibility
- Hover for detailed tooltips

**How to Use:**
1. Open HTML file in web browser
2. Hover over bars for details
3. Click-drag to zoom
4. Double-click to reset zoom

---

### 2. 3D TOD Score Explorer (HTML)

**File:** `interactive_02_3d_explorer.html`

**Features:**
- **6,184 SA1 points** (every 10th SA1 for performance)
- **3D scatter plot** with rotation
- **Color-coded** by TOD score (viridis scale)
- **Hover** shows SA1 code, commuters, car dependency, TOD score, state

**Axes:**
- X: Total Commuters (log scale)
- Y: Car Dependency (%)
- Z: TOD Score

**How to Use:**
1. Click-drag to rotate 3D view
2. Scroll to zoom
3. Hover over points for SA1 details
4. Explore clustering patterns

**Key Insights:**
- High TOD scores cluster at high car dependency
- Volume and TOD score not perfectly correlated
- State-level patterns visible in 3D

---

### 3. Modal Split Sunburst (HTML)

**File:** `interactive_03_modal_split_sunburst.html`

**Features:**
- **Hierarchical visualization**
- **Click to drill down** from mode to state
- **Hover** for exact commuter counts
- **Color-coded** by mode type

**Structure:**
- Inner ring: Transport mode (Car/Transit/Active)
- Outer ring: State breakdown

**How to Use:**
1. Click "Car" slice to see state breakdown
2. Click center to zoom out
3. Hover for percentages and counts

**Key Insights:**
- Visual comparison of modal split by state
- NSW and VIC dominate absolute numbers
- ACT and WA show better transit proportions

---

### 4. Priority Treemap (HTML)

**File:** `interactive_04_priority_treemap.html`

**Features:**
- **Hierarchical boxes** sized by SA1 count
- **Color-coded** by priority tier
- **Click** to drill down to state level
- **Hover** for exact counts and percentages

**Structure:**
- Priority 1 (red) vs Priority 2 (orange)
- Subdivided by state

**How to Use:**
1. Larger boxes = more SA1 areas
2. Click priority tier to see state breakdown
3. Click state to zoom in
4. Click header to zoom out

**Key Insights:**
- NSW has most priority areas (absolute)
- QLD has high Priority 1 concentration
- Visual sizing helps prioritize resources

---

### 5. Economic Impact Dashboard (HTML)

**File:** `interactive_05_economic_impact.html`

**Features:**
- **4 interactive panels**
- **Cumulative metrics** as you add SA1s
- **Area-fill** charts showing growth
- **Hover** for exact values at any point

**Panels:**

1. **Cumulative Modal Shift Potential**
   - Shows potential new transit users
   - As you add top SA1s (x-axis)
   - 20% modal shift assumption

2. **Annual Time Savings**
   - Cumulative hours saved per year
   - Based on 5 min/trip savings
   - 230 working days/year

3. **Economic Value ($)**
   - Dollar value of time savings
   - $25/hour assumption
   - Reaches $47.9M for top 1000

4. **TOD Score vs. Impact**
   - Scatter plot
   - X: TOD score
   - Y: Average economic value
   - Color by TOD score

**How to Use:**
1. Hover on cumulative charts to see "top N areas" impact
2. Identify diminishing returns point
3. Use scatter to see score-value correlation

**Key Insights:**
- Top 100 areas provide significant impact
- Returns diminish after ~500 areas
- Even top 1000 captures $48M in value

---

### 6. Top Opportunities Table (HTML)

**File:** `interactive_06_top_opportunities_table.html`

**Features:**
- **Top 100 SA1s** in detail
- **Sortable columns**
- **Scrollable** table
- **Export-friendly** (copy-paste)

**Columns:**
1. Rank (1-100)
2. SA1 Code
3. State
4. TOD Score
5. Car Dependency %
6. Transit Usage %
7. Total Commuters
8. SA2 Employment

**How to Use:**
1. Scroll to browse all 100
2. Click column headers to sort (if browser supports)
3. Select and copy rows for Excel/spreadsheets

**Key Insights:**
- Top 10 all have >95% TOD scores
- Many top areas have 0% transit usage
- Employment centers vary widely

---

## 🗺️ GIS-Compatible Exports

### Overview

All GIS exports are CSV files that can be **joined to ABS shapefiles** in QGIS, ArcGIS, or other GIS tools.

**Join Key:**
- For SA1 files: `SA1_CODE_2021`
- For SA2 files: `SA2_CODE`

**Required Shapefiles:**
- Download from ABS: [Digital Boundaries](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files)
- Files needed: SA1 2021, SA2 2021, SA3 2021

---

### 1. Complete SA1 Dataset

**File:** `gis_export_complete_sa1.csv`
**Records:** 61,844 SA1 areas

**Key Fields:**
- Geographic codes: `SA1_CODE_2021`, `SA2_CODE`, `SA3_CODE`, `state`
- Population: `total_population`, `total_commuters`
- Transport modes: `total_car`, `total_public_transit`, `total_active_transport`
- Ratios: `car_dependency_ratio`, `public_transit_ratio`, `active_transport_ratio`
- Employment: `sa2_employment`, `sa2_employment_density`
- Scores: `tod_score`, `commute_pain_score`
- **Categories:** `tod_category`, `car_dep_category`, `transit_category`
- **Priority:** `investment_priority`

**Category Fields:**

`tod_category`:
- Low (0-50)
- Medium (50-65)
- High (65-75)
- Very High (75-85)
- Extreme (85-100)

`car_dep_category`:
- Low (<50%)
- Moderate (50-70%)
- High (70-80%)
- Very High (80-90%)
- Extreme (>90%)

`investment_priority`:
- Priority 1
- Priority 2
- Not Priority

**How to Use in QGIS:**
1. Load ABS SA1 2021 shapefile
2. Layer → Add Layer → Add Delimited Text Layer
3. Select `gis_export_complete_sa1.csv`
4. Properties → Joins → Add join
5. Join field: `SA1_CODE_2021`
6. Target field: `SA1_CODE21` (or similar in shapefile)
7. Style by `tod_category` or `investment_priority`

---

### 2. SA2 Aggregated Dataset

**File:** `gis_export_sa2_aggregated.csv`
**Records:** 2,472 SA2 areas

**Purpose:** Easier to visualize than 61,844 SA1s

**Fields:**
- Same as SA1 but aggregated to SA2 level
- `sa1_count` - number of SA1s in this SA2
- Means and sums appropriately calculated

**How to Use:**
1. Join to ABS SA2 2021 shapefile
2. Use `SA2_CODE` as join key
3. Faster rendering than SA1 level
4. Good for regional overview maps

---

### 3. Priority Areas Only

**File:** `gis_export_priority_areas.csv`
**Records:** 4,796 priority SA1s (Priority 1 & 2)

**Purpose:** Focus map on investment priorities only

**Fields:**
- Same as complete SA1 dataset
- Filtered to only Priority 1 and Priority 2 areas

**How to Use:**
1. Join to SA1 shapefile
2. Create thematic map showing only priorities
3. Style Priority 1 (red) vs Priority 2 (orange)
4. Overlay on base map

---

### 4. Top 1000 Enhanced

**File:** `gis_export_top_1000_enhanced.csv`
**Records:** 1,000 top opportunities

**Enhanced Fields:**
- `rank` - 1 to 1000
- `potential_new_transit_users_20pct` - estimated new riders
- `annual_time_savings_hours` - hours saved per year
- `economic_value_annual` - dollar value
- `recommended_intervention` - suggested action

**Intervention Categories:**
- "New transit service required" - 0% transit currently
- "High-frequency transit to employment center" - high employment nearby
- "Express bus or BRT corridor" - high commuter volume
- "Enhanced local transit service" - moderate opportunity

**How to Use:**
1. Join to SA1 shapefile
2. Filter top 100, top 50, etc.
3. Label with `rank` or `recommended_intervention`
4. Create priority investment map

---

### 5. Metadata File

**File:** `gis_export_metadata.json`

**Contents:**
- Field descriptions
- Data dictionary
- How-to-use instructions
- Recommended shapefiles

---

## 💡 Visualization Best Practices

### Creating Effective Maps in QGIS

**Recommended Style:**

For **TOD Score:**
```
Graduated colors
Field: tod_score
Mode: Natural Breaks (Jenks)
Classes: 5
Color ramp: Spectral (inverted)
Low = red, High = green
```

For **Investment Priority:**
```
Categorized
Field: investment_priority
Priority 1: Red (#e74c3c)
Priority 2: Orange (#f39c12)
Not Priority: Light gray (#ecf0f1)
```

For **Car Dependency:**
```
Graduated colors
Field: car_dependency_ratio
Mode: Equal Interval
Classes: 5
Color ramp: Reds
```

**Layer Recommendations:**
1. Base layer: OpenStreetMap or light gray
2. SA1/SA2 polygons with TOD styling
3. Priority areas highlighted
4. Major roads overlay
5. Transit lines overlay (if available)
6. Employment centers (large dots)

---

## 🎨 Color Schemes Used

**Consistent color coding across all visualizations:**

- **Car Dependency:** Red scale (#ff6b6b to #c0392b)
- **Public Transit:** Teal/green scale (#4ecdc4 to #2ecc71)
- **Active Transport:** Light green (#95e1d3)
- **TOD Score:** Viridis/Plasma (purple-yellow)
- **Priority 1:** Red (#e74c3c)
- **Priority 2:** Orange (#f39c12)
- **Priority 3:** Blue (#3498db)

---

## 📊 Chart Type Guide

| Insight Needed | Chart Type | File |
|----------------|------------|------|
| Compare states | Horizontal bar | 01_state_comparison |
| National trends | Pie chart | 02_modal_split |
| Distribution | Histogram/box plot | 03_tod_score |
| Categories | Heatmap | 04_car_dependency |
| Hierarchies | Treemap/sunburst | interactive_03/04 |
| Trends over rank | Line chart | interactive_05 |
| Spatial patterns | 3D scatter | interactive_02 |
| Details | Table | interactive_06 |

---

## 🚀 Advanced Usage

### Combining Visualizations

**PowerPoint/Report:**
1. Use static PNGs for slides
2. Link to interactive HTML for deep dives
3. Include GIS maps for spatial context

**Web Dashboard:**
1. Embed interactive HTML in iframe
2. Link to GIS web maps
3. Provide CSV downloads

**Academic Paper:**
1. Static visualizations in figures
2. Interactive HTML in supplementary materials
3. GIS files for reproducibility

---

## 📝 Citation

When using these visualizations:

```
TOD Analysis Visualizations (2025)
Based on 2021 Australian Census Data
Australian Bureau of Statistics
Visualizations generated using Python (matplotlib, seaborn, plotly)
```

---

## ❓ FAQ

**Q: Can I modify the visualizations?**
A: Yes! All Python scripts can be edited. Modify colors, add panels, change thresholds.

**Q: Why are interactive files so large?**
A: They embed full Plotly.js library. Open them in a web browser for best experience.

**Q: Can I use these in commercial applications?**
A: Check ABS licensing for census data. Visualizations themselves follow repo license.

**Q: How do I regenerate after data updates?**
A: Re-run the Python scripts. They'll overwrite existing files.

**Q: Can I create animated visualizations?**
A: Yes! Plotly supports animation. Modify the interactive scripts to add time dimension.

**Q: Are there Power BI / Tableau versions?**
A: Not currently. Use the CSV exports to create custom dashboards in those tools.

---

## 🔧 Troubleshooting

**Issue:** Plots look blurry
- **Solution:** Increase DPI in scripts (change `dpi=300` to `dpi=600`)

**Issue:** Interactive files won't open
- **Solution:** Try different browser (Chrome/Firefox recommended)

**Issue:** GIS join not working
- **Solution:** Check SA1 code formats match (text vs numeric)

**Issue:** Out of memory errors
- **Solution:** Reduce data sampling or increase system RAM

**Issue:** Slow rendering
- **Solution:** Use SA2 aggregated data instead of SA1

---

## 📧 Support

For questions about visualizations:
1. Check the Python scripts for inline comments
2. Review this guide
3. Examine the generated files

---

**Last Updated:** November 22, 2025
**Visualization Suite Version:** 1.0
**Total Visualizations:** 16 (5 static + 6 interactive + 5 GIS exports)
