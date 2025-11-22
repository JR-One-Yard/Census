# 🏢 Workforce Industry Clustering & Commercial Property Demand Analysis

## Quick Start Guide

This directory contains a comprehensive analysis of **commercial property investment opportunities** across Australia based on 2021 Census data.

---

## 📂 Files Overview

| File | Records | Description | Use Case |
|------|---------|-------------|----------|
| **top_500_commercial_property_opportunities.csv** | 500 | Best investment opportunities overall | Primary investment shortlist |
| **top_500_commercial_demand_gaps.csv** | 500 | Undersupplied markets | Development opportunities |
| **employment_clusters_all.csv** | 363 | Established commercial centers | Mature market investments |
| **emerging_employment_clusters.csv** | 4 | High-growth emerging markets | First-mover opportunities |
| **full_commercial_property_analysis.csv** | 2,355 | Complete dataset | Custom analysis |
| **analysis_summary_statistics.csv** | 1 | National statistics | Benchmarking |
| **ANALYSIS_REPORT.md** | - | Full methodology & insights | Detailed documentation |

---

## 🎯 Quick Actions

### Find Top Investment Opportunities
```bash
# Top 10 overall opportunities
head -11 top_500_commercial_property_opportunities.csv

# Top 10 emerging clusters (first-mover advantage)
cat emerging_employment_clusters.csv
```

### Filter by Criteria

**High-opportunity areas (Excel/Python/R):**
```python
import pandas as pd

# Load full dataset
df = pd.read_csv('full_commercial_property_analysis.csv')

# Filter: High professionals + Low commercial stock + High income
opportunities = df[
    (df['Professional_Density_per_1000'] > 500) &      # 1.4x national average
    (df['Commercial_Density_Proxy'] < 5000) &          # Low commercial stock
    (df['Median_tot_prsnl_inc_weekly'] > 1400) &       # Above median income
    (df['Total_Population'] > 5000)                    # Viable market size
].sort_values('Commercial_Opportunity_Score', ascending=False)

# Save filtered results
opportunities.to_csv('custom_opportunities.csv', index=False)
```

---

## 📊 Key Metrics Explained

### Opportunity Score (0-100)
**Higher = Better Investment Opportunity**

Weighted composite of:
- Professional Demand (30%)
- Professional Density (25%)
- Industry Concentration (20%)
- Commercial Deficit (15%)
- Income Level (10%)

**Threshold Guide:**
- **60+** = Exceptional opportunity
- **50-59** = Excellent opportunity
- **40-49** = Good opportunity
- **30-39** = Moderate opportunity
- **<30** = Low opportunity

### Demand Gap Index (0-100)
**Higher = Greater Supply-Demand Mismatch**

Formula: `(Professional Demand + Professional Density) / 2 × Commercial Deficit / 100`

**Threshold Guide:**
- **45+** = Severe undersupply
- **35-44** = High undersupply
- **25-34** = Moderate undersupply
- **<25** = Balanced/oversupplied

### Professional Density (per 1,000 population)
**Higher = More Knowledge Workers**

National Average: **354.15** per 1,000

**Threshold Guide:**
- **700+** = Exceptional concentration (2x average)
- **500-699** = Very high concentration (1.4-2x average)
- **400-499** = High concentration (1.1-1.4x average)
- **300-399** = Average concentration
- **<300** = Below average

---

## 🗺️ Geographic Mapping

### Get Suburb Names

SA2 codes need to be mapped to actual suburb/city names using the ABS geography file:

```bash
# Location of geography mapping file
/home/user/Census/2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx
```

**In Excel/Python:**
1. Load the geography descriptor file
2. Look up SA2_CODE in the SA2 sheet
3. Get the suburb name from the SA2_NAME column

### Example SA2 Code Lookups

Some common patterns:
- **1XXXXX** = NSW
- **2XXXXX** = VIC
- **3XXXXX** = QLD
- **4XXXXX** = SA
- **5XXXXX** = WA
- **6XXXXX** = TAS
- **7XXXXX** = NT
- **8XXXXX** = ACT

---

## 💡 Investment Strategy Quick Reference

### Strategy 1: Emerging Markets (Highest Return Potential)
**Target File:** `emerging_employment_clusters.csv` (4 areas)

**Profile:**
- Professional Density: 650-950 per 1,000
- Median Income: $1,310-$1,777/week
- Commercial Stock: Very low

**Investment Types:**
- New office parks
- Co-working spaces
- Mixed-use developments

**Risk/Return:** Medium-High risk, High return

---

### Strategy 2: Established Markets (Proven Demand)
**Target File:** `employment_clusters_all.csv` (363 areas)

**Profile:**
- Professional Density: >436 per 1,000
- Large professional workforce: >5,000 workers
- Existing commercial infrastructure

**Investment Types:**
- Office upgrades (B to A grade)
- Mixed-use conversions
- Smart office retrofits

**Risk/Return:** Low-Medium risk, Medium return

---

### Strategy 3: Demand Gap Arbitrage
**Target File:** `top_500_commercial_demand_gaps.csv`

**Profile:**
- High professional workforce
- Very low commercial supply
- Demand Gap Index: >40

**Investment Types:**
- Infill office development
- Commercial ground floors
- Suburban business parks

**Risk/Return:** Medium risk, Medium-High return

---

## 🔍 Common Analysis Tasks

### Find areas near me (by SA2 code prefix)

```bash
# NSW areas (SA2 codes starting with 1)
grep "^1" top_500_commercial_property_opportunities.csv

# Victoria areas (SA2 codes starting with 2)
grep "^2" top_500_commercial_property_opportunities.csv

# Queensland areas (SA2 codes starting with 3)
grep "^3" top_500_commercial_property_opportunities.csv
```

### Filter by income level

```python
# High-income areas only (>$1,500/week)
df = pd.read_csv('full_commercial_property_analysis.csv')
high_income = df[df['Median_tot_prsnl_inc_weekly'] > 1500]
```

### Find clusters with low commercial stock

```python
# Clusters with demand gap
df = pd.read_csv('employment_clusters_all.csv')
undersupplied = df[df['Demand_Gap_Index'] > 35]
```

---

## 📈 Benchmarking Your Investment

### Compare to National Averages

| Metric | National Average | Top 10% Threshold | Top 1% Threshold |
|--------|------------------|-------------------|------------------|
| **Professional Density** | 354.15 per 1,000 | 600+ | 900+ |
| **Median Income** | ~$1,050/week | $1,400+ | $1,700+ |
| **Opportunity Score** | 29.36 | 45+ | 55+ |
| **Demand Gap Index** | 20.88 | 35+ | 45+ |

### What Makes a Top-Tier Opportunity?

✅ Professional Density: **>600 per 1,000** (Top 10%)
✅ Median Income: **>$1,400/week** (Top 10%)
✅ Opportunity Score: **>50** (Top 5%)
✅ Demand Gap Index: **>40** (Undersupplied)
✅ Population: **>5,000** (Viable market)

---

## 🚨 Red Flags to Avoid

❌ Professional Density < 200 (weak knowledge worker base)
❌ Commercial Density Proxy > 15,000 (oversupplied)
❌ Median Income < $800 (weak purchasing power)
❌ Population < 1,000 (market too small)
❌ Opportunity Score < 20 (poor fundamentals)

---

## 📞 Need Help?

**Documentation:** See `ANALYSIS_REPORT.md` for full methodology and insights

**Custom Analysis:** Use `full_commercial_property_analysis.csv` with your own filters

**Data Questions:** Refer to census documentation in `/Readme` and `/Metadata` folders

---

**Analysis Version:** 1.0
**Date:** 2025-11-22
**Coverage:** 2,355 SA2 areas, 25.4M population, 9.1M professionals
**Data Source:** 2021 Australian Census (ABS)
