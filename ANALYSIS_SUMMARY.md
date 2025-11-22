# 2021 Australian Census Manager/Executive Analysis

## Summary

This analysis examined 2021 Australian Census data to identify suburbs with the highest concentration of managers and executives. Two complementary approaches were used:

### Analysis 1: Raw Manager Concentration
**File:** `analyze_manager_concentration_final.py`
**Output:** `top_50_manager_suburbs.csv`

**Methodology:** Analyzed all 15,352 Australian suburbs (SAL geography) to find highest percentage of managers among employed persons.

**Key Findings:**
- Top suburbs are predominantly **rural/farming communities** (50-66% manager concentration)
- National average: **15.2%** manager concentration
- Rural dominance reflects agricultural structure (farmers = farm managers in ANZSCO classification)
- Top suburb: **ACT Remainder - Majura** (66.3%)

### Analysis 2: Executive/Director Hotspots (Refined)
**File:** `analyze_executive_hotspots.py`
**Output:** `top_50_executive_hotspots.csv`

**Methodology:**
- Filtered to urban areas (≥1,000 employed, ≥2,000 population)
- High-income areas only (median income ≥$900/week - top 25%)
- Composite "Executive Score" combining:
  - Manager concentration (40%)
  - Manager + Professional concentration (30%)
  - Median personal income (30%)

**Key Findings:**

#### Top 10 Executive Hotspots:
1. **Milsons Point (NSW)** - Score: 85.3, 28.7% managers, $1,866/week median income
2. **Campbell (ACT)** - Score: 80.6, 41.9% managers, $1,292/week median income
3. **Darling Point (NSW)** - Score: 79.9, 27.1% managers, $1,799/week median income
4. **Kingston (ACT)** - Score: 77.0, 25.2% managers, $1,777/week median income
5. **Birchgrove (NSW)** - Score: 76.7, 26.6% managers, $1,661/week median income
6. **Cremorne Point (NSW)** - Score: 74.3, 25.5% managers, $1,661/week median income
7. **Paddington (NSW)** - Score: 73.5, 23.4% managers, $1,698/week median income
8. **Rozelle (NSW)** - Score: 73.1, 26.4% managers, $1,652/week median income
9. **McMahons Point (NSW)** - Score: 72.5, 24.1% managers, $1,664/week median income
10. **Woollahra (NSW)** - Score: 71.7, 23.5% managers, $1,638/week median income

#### Geographic Patterns:

**Sydney Inner Harbor Suburbs** (Dominant):
- Milsons Point, Darling Point, Birchgrove, Cremorne Point, McMahons Point
- Paddington, Rozelle, Woollahra, Double Bay, Balmain
- Kirribilli, Mosman, Bellevue Hill
- Median incomes: $1,400-$1,900/week ($72,800-$98,800/year)
- Manager concentration: 23-29%
- Manager + Professional: 65-74%

**Canberra (ACT) Suburbs**:
- Campbell, Kingston, Yarralumla, Deakin, Griffith
- High government executive presence
- Median incomes: $1,300-$1,800/week
- Manager concentration: 22-42%

**Other Notable Areas**:
- Inner Melbourne: Middle Park, Cremorne (Vic.)
- Brisbane: Teneriffe
- Affluent beach suburbs: Manly, Bondi Beach, North Bondi

#### Socioeconomic Profile:

**Affluent Urban Suburbs (1,087 analyzed):**
- Average manager concentration: **16.1%**
- Average manager + professional: **46.8%**
- Average median personal income: **$1,099/week** ($57,148/year)
- Average median household income: **$2,395/week** ($124,550/year)

## Interpretation

### What the Data Reveals:

1. **Urban Executive Clusters:** Sydney's inner harbor and eastern suburbs dominate the executive landscape, with 70-74% of workers in manager/professional roles.

2. **Income as Proxy:** Median personal incomes of $1,400-$1,900/week ($72,800-$98,800/year) indicate genuine executive/professional demographics, not just business owners.

3. **Geographic Concentration:** Executive talent clusters heavily in:
   - Sydney inner harbor (proximity to CBD, harbor views, prestige)
   - Canberra (government executives)
   - Small pockets in Melbourne and Brisbane

4. **The "Manager" Category:** ANZSCO Major Group 1 (Managers) includes:
   - Chief Executives and General Managers
   - Farm Managers (explains rural dominance in raw data)
   - Specialist Managers (HR, Sales, Marketing, Operations)
   - Service/Hospitality Managers

### Limitations:

1. **Granularity:** Census DataPacks provide only 1-digit ANZSCO (8 categories). To specifically identify "CEOs and Directors" (ANZSCO 111), would require:
   - TableBuilder access (ABS subscription)
   - Custom data request from ABS
   - 2-digit or 3-digit ANZSCO classifications

2. **Self-Employment:** Census doesn't distinguish between employed managers vs. self-employed business owners.

3. **Income Timing:** Median income is based on 2020-2021 financial year (pre-pandemic recovery).

## Data Sources

**Australian Bureau of Statistics:**
- 2021 Census General Community Profile (GCP)
- Geography: SAL (Suburbs and Localities) - 15,352 suburbs
- Key Tables:
  - G60A: Occupation by Age and Sex
  - G02: Median Income and Household Characteristics
  - G01: Population and Dwelling Counts

**Data Pack:** 2021_GCP_all_for_AUS_short-header
**Size:** 3.2 GB (2,023 CSV files)
**License:** Creative Commons

## Usage

### Run Raw Manager Concentration Analysis:
```bash
python3 analyze_manager_concentration_final.py
```

### Run Executive Hotspots Analysis:
```bash
python3 analyze_executive_hotspots.py
```

### Requirements:
- Python 3.x
- pandas
- openpyxl (for reading metadata)

## Author
Analysis conducted using 2021 Australian Census DataPacks
Date: November 2025
