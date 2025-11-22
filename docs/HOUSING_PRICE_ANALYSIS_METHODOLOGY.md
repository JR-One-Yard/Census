# Housing Price Analysis - Available Data & Methodology

## 📊 Available Housing Price Proxies in 2021 Census

### Primary Data Source: Table G02
**File:** `2021Census_G02_AUST_SAL.csv`

**Available Metrics:**
1. **`Median_mortgage_repay_monthly`** - Median monthly mortgage repayment ($)
   - **Best proxy for house prices/values**
   - Higher mortgage = higher purchase price
   - Reflects property values in owner-occupied dwellings

2. **`Median_rent_weekly`** - Median weekly rent ($)
   - Alternative housing cost metric
   - Useful for rental-heavy suburbs (inner city apartments)
   - Correlates with property values but less directly

3. **`Median_tot_hhd_inc_weekly`** - Median total household income ($/week)
   - Already used in executive hotspot analysis
   - Correlates with housing affordability

### Secondary Data: Tables G40, G33
- **G40:** Rent amounts by landlord type (detailed rent brackets)
- **G33:** Household income distributions
- Less useful for correlation analysis (too granular)

## 🎯 Proposed Correlation Analysis

### Objective
Identify relationship between:
1. **Executive concentration** (manager % + executive industries %)
2. **Housing prices** (median mortgage repayments)

### Key Questions to Answer:
1. **Do executive hotspots correlate with high housing prices?**
   - Expected: YES (high-income professionals → expensive housing)

2. **Which suburbs have high prices but LOW executive concentration?**
   - These are the interesting outliers!
   - Potential explanations:
     - Wealthy retirees (e.g., beachside suburbs)
     - Investment properties (CBD apartments, low residency)
     - Foreign investment areas
     - Historical/prestige locations (heritage areas)
     - Professional class (doctors, lawyers) vs. executives

3. **Which suburbs have high executive concentration but LOWER prices?**
   - Value opportunities for executives
   - Emerging areas
   - Government/public sector concentration (Canberra effect)

## 📈 Analysis Methodology

### Step 1: Data Preparation
- Load G02 housing data (mortgage, rent) for all SAL suburbs
- Merge with executive hotspot scores from previous analysis
- Filter to urban areas (same criteria: ≥1,000 employed, ≥2,000 population)

### Step 2: Correlation Analysis
Calculate correlations between:
- Median mortgage vs. Manager concentration %
- Median mortgage vs. Executive industries %
- Median mortgage vs. Executive Score (composite)
- Median rent vs. same metrics

### Step 3: Scatter Plot Quadrants
Create 2x2 matrix:
```
                   High Executive Concentration
                   |
   High Price   Q1 | Q2    Low Price
   (Expensive)     |       (Affordable)
   ----------------+------------------
   Low Price    Q3 | Q4    High Price
   (Affordable)    |       (Expensive)
                   |
                   Low Executive Concentration
```

**Quadrant 1 (High Price + High Executive):** Expected pattern
- Milsons Point, Darling Point, Mosman, etc.

**Quadrant 2 (Low Price + High Executive):** Value opportunities
- Canberra suburbs? (high executive, but lower housing costs)

**Quadrant 3 (Low Price + Low Executive):** Working class suburbs
- Expected pattern

**Quadrant 4 (High Price + Low Executive):** INTERESTING OUTLIERS!
- Wealthy retiree suburbs
- Tourist/lifestyle destinations
- Investment/empty properties
- Old money vs. new money areas

### Step 4: Outlier Identification
Identify suburbs that are:
- **1+ standard deviation above mean** on housing price
- **1+ standard deviation below mean** on executive concentration

These are "expensive non-executive suburbs"

### Step 5: Characterization
For outlier suburbs, analyze:
- Age demographics (retirees?)
- Occupation mix (professionals vs. executives vs. other)
- Industry composition (tourism, health care, etc.)
- Dwelling types (houses vs. apartments)

## 🔍 Expected Findings

### High Price + High Executive (Q1)
- Sydney inner harbor: Milsons Point ($3,000+ mortgage?), Darling Point, Mosman
- Eastern suburbs: Woollahra, Bellevue Hill, Double Bay

### High Price + Low Executive (Q4) - THE INTERESTING ONES
**Potential candidates:**
- **Beachside lifestyle:** Bondi Beach (tourists/young professionals, not executives)
- **Retirement havens:** Gold Coast suburbs, Sunshine Coast
- **Heritage prestige:** Paddington houses (vs. inner city apartments)
- **Family suburbs:** Upper North Shore (professionals, not CBD executives)
- **Investment heavy:** CBD apartments (executives don't live there)

### Low Price + High Executive (Q2)
- **Canberra suburbs:** Campbell, Kingston (public sector salaries < private exec salaries)
- **Emerging areas:** Outer suburbs with rising professional class

## 📊 Statistical Metrics

### Correlation Coefficients
- **r > 0.7:** Strong positive correlation (expected for most metrics)
- **r = 0.4-0.7:** Moderate correlation
- **r < 0.4:** Weak correlation (interesting!)

### Residual Analysis
- Calculate predicted housing price based on executive concentration
- Identify suburbs with large **positive residuals** (higher price than predicted)
- These are the "expensive non-executive suburbs"

## 🎨 Visualization Ideas

1. **Scatter plot:** X-axis = Executive Score, Y-axis = Median Mortgage
   - Color by industry type (finance = blue, public admin = green, etc.)
   - Size by population

2. **Scatter plot:** X-axis = Manager %, Y-axis = Median Mortgage
   - Highlight top 30 executive hotspots
   - Annotate outliers

3. **Geographic map** (if possible):
   - Heatmap of housing prices
   - Overlay executive hotspot markers

## 💡 Hypotheses to Test

### H1: Executive concentration strongly predicts housing prices
- **Test:** Pearson correlation r > 0.7
- **Expected:** TRUE for Sydney, MIXED for Australia-wide

### H2: Finance/Professional industry concentration predicts prices better than manager %
- **Test:** Compare r-values
- **Expected:** TRUE (industry is more specific than occupation)

### H3: There exist high-price suburbs with low executive concentration
- **Test:** Identify Q4 outliers (high price, low executive)
- **Expected:** TRUE - beachside, retiree, heritage areas

### H4: Canberra suburbs show high executive, moderate price (public sector effect)
- **Test:** Compare Canberra vs. Sydney housing prices at same executive level
- **Expected:** TRUE

## 📁 Output Files

1. **`housing_price_correlation_analysis.csv`**
   - All suburbs with: executive metrics, housing prices, residuals

2. **`high_price_low_executive_outliers.csv`**
   - Suburbs in Q4 (expensive but not executive-heavy)

3. **`correlation_summary.txt`**
   - Statistical summary: correlations, R², outlier counts

## 🚀 Next Steps

1. Load G02 housing data
2. Merge with executive hotspot data
3. Calculate correlations
4. Identify Q4 outliers
5. Characterize outlier suburbs
6. Generate visualizations (if possible)

---

**Note:** Census doesn't provide actual property values, only mortgage/rent amounts. Mortgage repayments are the best proxy available as they correlate strongly with purchase price (higher price = higher loan = higher repayment).
