# 2021 Australian Census - Manager/Executive Demographics Analysis

Comprehensive analysis of the 2021 Australian Census data to identify suburbs with the highest concentration of managers and executives, validated through industry composition analysis.

## 📁 Repository Structure

```
Census/
├── analysis/                    # Analysis scripts
│   ├── analyze_manager_concentration_final.py
│   ├── analyze_executive_hotspots.py
│   └── analyze_executive_profile.py
├── results/                     # Analysis output (CSV files)
│   ├── top_50_manager_suburbs.csv
│   ├── top_50_executive_hotspots.csv
│   └── executive_hotspots_detailed_profile.csv
├── docs/                        # Documentation
│   └── ANALYSIS_SUMMARY.md
├── 2021_GCP_all_for_AUS_short-header/  # Census data (3.2GB)
└── README.md                    # This file
```

## 🎯 Quick Start

### Run the Analyses

```bash
# 1. Raw manager concentration (all suburbs)
python3 analysis/analyze_manager_concentration_final.py

# 2. Executive hotspots (urban + high-income filter)
python3 analysis/analyze_executive_hotspots.py

# 3. Industry composition profile
python3 analysis/analyze_executive_profile.py
```

## 📊 Key Findings

### Top 5 Executive Hotspots

1. **Milsons Point (NSW)** - Score: 85.3
   - 28.7% managers, 73.8% manager+professional
   - 47% in executive industries (Finance, Prof/Sci, Info/Media, Public Admin)
   - Median income: $1,866/week

2. **Campbell (ACT)** - Score: 80.6
   - 41.9% managers (highest among urban areas!)
   - 69.7% in executive industries (58% Public Administration)
   - Government executive hub

3. **Darling Point (NSW)** - Score: 79.9
   - 27.1% managers, 70.5% manager+professional
   - 42.8% in executive industries
   - Median income: $1,799/week

4. **Kingston (ACT)** - Score: 77.0
   - 25.2% managers
   - 64% in executive industries (46% Public Administration)
   - Median income: $1,777/week

5. **Birchgrove (NSW)** - Score: 76.7
   - 26.6% managers, 74% manager+professional
   - 42.9% in executive industries
   - Median income: $1,661/week

### Industry Validation

**Top 30 executive hotspots show:**
- **44.1%** employed in executive industries (Finance, Prof/Sci, Info/Media, Public Admin)
- **4.2x** the national average (10.5%)

**Finance/Insurance leaders:**
- Milsons Point: 16.0%
- Queens Park: 15.1%
- Double Bay: 15.0%

**Professional/Scientific/Technical leaders:**
- Paddington: 23.8%
- Wollstonecraft: 23.2%
- Castlecrag: 23.2%

### Geographic Patterns

**Sydney Inner Harbor dominates (35 of top 50):**
- Milsons Point, Darling Point, Birchgrove, Cremorne Point
- Paddington, Rozelle, Woollahra, Balmain
- Mosman, Bellevue Hill, Kirribilli

**Canberra (ACT) - Government Executive Hub:**
- Campbell, Kingston, Yarralumla, Deakin, Griffith
- 46-58% in Public Administration

**Other Capital Cities:**
- Melbourne: Middle Park, Cremorne (Vic.)
- Brisbane: Teneriffe
- Perth/Adelaide: Minimal representation

## 📈 Analysis Methodology

### Analysis 1: Raw Manager Concentration
- **Dataset:** All 15,352 Australian suburbs (SAL geography)
- **Metric:** Managers / Total Employed × 100
- **Result:** Dominated by rural/farming communities (farm managers)

### Analysis 2: Executive Hotspots (Refined)
- **Filters:**
  - Urban areas only (≥1,000 employed, ≥2,000 population)
  - High-income areas (median income ≥$900/week - top 25%)
- **Composite Score:**
  - 40% Manager concentration
  - 30% Manager + Professional concentration
  - 30% Median personal income
- **Result:** Sydney harbor + Canberra executive clusters

### Analysis 3: Industry Composition
- **Validation:** Cross-reference with industry employment data
- **Executive Industries:**
  - Finance & Insurance
  - Professional, Scientific & Technical
  - Information, Media & Telecommunications
  - Public Administration & Safety
- **Result:** 4.2x national rate in top 30 hotspots

## 📦 Data Source

**Australian Bureau of Statistics - 2021 Census**
- Product: General Community Profile (GCP) DataPacks
- Geography: SAL (Suburbs and Localities)
- Size: 3.2 GB, 2,023 CSV files
- License: Creative Commons

**Key Tables Used:**
- G60A: Occupation by Age and Sex
- G02: Median Income
- G01: Population
- G43: Labour Force Status
- G54C/D: Industry of Employment

## 💡 Interpretation

### What "Manager" Means
ANZSCO Major Group 1 (Managers) includes:
- Chief Executives & General Managers
- **Farm Managers** (explains rural dominance in raw data)
- Specialist Managers (HR, Sales, Marketing, Operations)
- Service/Hospitality Managers

### Why the Refined Analysis Matters
- **Raw data:** Farm managers skew results to rural areas
- **Refined analysis:** Urban + high-income filter reveals genuine corporate executive clusters
- **Industry validation:** Confirms professional/financial services concentration

### Limitations
1. Census uses 1-digit ANZSCO (8 categories only)
2. Cannot isolate specific roles like "CEO" or "Director" (requires 3-digit ANZSCO)
3. No distinction between employed managers vs. business owners
4. Data from 2020-2021 financial year

## 🔬 Requirements

```bash
pip install pandas openpyxl
```

## 📚 Documentation

See [docs/ANALYSIS_SUMMARY.md](docs/ANALYSIS_SUMMARY.md) for detailed methodology and findings.

## 📊 Results Files

All analysis outputs are in the `results/` directory:
- `top_50_manager_suburbs.csv` - Raw manager concentration (all suburbs)
- `top_50_executive_hotspots.csv` - Refined executive hotspots
- `executive_hotspots_detailed_profile.csv` - Industry composition breakdown

## 📝 License

Analysis code: MIT License
Census Data: Creative Commons (Australian Bureau of Statistics)

---

**Analysis Date:** November 2025
**Census Year:** 2021
