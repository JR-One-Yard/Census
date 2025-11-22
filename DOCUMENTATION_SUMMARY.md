# 📚 Census Data Documentation Summary

## Question Asked
**"Is there documentation regarding the formatting of education and income data? Looking to search for suburbs with highest tertiary education, income, and oldest age."**

---

## ✅ Answer: YES - Complete Documentation Provided

### 📄 Documentation Files Created

1. **`DATA_ANALYSIS_GUIDE.md`** - Comprehensive guide to the data structure
   - Detailed explanation of all relevant tables (G02, G17, G49, G33, etc.)
   - Column format documentation
   - Sample data with explanations
   - Quick start recommendations

2. **`SAL_Suburb_Name_Mapping.csv`** - Lookup table
   - Maps SAL codes to suburb names
   - Contains 15,352 Australian suburbs
   - Format: `SAL_CODE, Suburb_Name, Area_sqkm`

3. **`analyze_top_suburbs.py`** - Ready-to-use analysis script
   - Finds top 20 suburbs by oldest median age
   - Finds top 20 suburbs by highest income
   - Finds top 20 suburbs by highest tertiary education
   - Finds top 20 suburbs with combined high scores
   - Exports results to CSV files

---

## 📊 Key Data Tables Identified

### **G02 - Selected Medians and Averages** ⭐ BEST FOR YOUR USE CASE
**Location:** `2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G02_AUST_SAL.csv`

**Columns:**
- `Median_age_persons` - Median age (OLDEST AGE)
- `Median_tot_prsnl_inc_weekly` - Median personal income (INCOME)
- `Median_tot_fam_inc_weekly` - Median family income
- `Median_tot_hhd_inc_weekly` - Median household income

### **G49A/G49B - Highest Non-School Qualification** ⭐ TERTIARY EDUCATION
**Location:** `2021Census_G49A_AUST_SAL.csv` (Males), `2021Census_G49B_AUST_SAL.csv` (Females)

**Education Levels:**
1. **Postgraduate Degree** - Masters, PhD
2. **Graduate Diploma & Certificate**
3. **Bachelor Degree**
4. **Advanced Diploma & Diploma**
5. **Certificate III & IV**
6. **Certificate I & II**

**Age Breakdown:** 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75-84, 85+

### **G17A/B/C - Total Personal Income (Weekly)**
**Location:** Detailed income brackets by age and sex

**Income Brackets:**
- Negative/Nil, $1-149, $150-299, $300-399, ..., $3500+
- Cross-tabulated with age groups and sex

---

## 📈 Analysis Results

### Top Suburbs with OLDEST Median Age:
1. **New Chum** - Age: 91
2. **Maude (SA)** - Age: 87
3. **Walyunga National Park** - Age: 84

### Top Suburbs with HIGHEST Personal Income:
1. **Bulga (Vic.)** - $3,500/week
2. **Petticoat Creek** - $3,500/week
3. **Warenda** - $3,500/week

### Top Suburbs with HIGHEST Tertiary Education:
1. **Melbourne** - 13,066 people with Bachelor degree or higher
2. **Point Cook** - 9,502 people
3. **Glen Waverley** - 7,757 people

### Top Suburbs with COMBINED High Education + Income + Older Age:
1. **Brighton (Vic.)** - Score: 0.941 (4,512 tertiary educated, age 48, income $1,259/week)
2. **Toorak** - Score: 0.938 (2,856 tertiary educated, age 47, income $1,427/week)
3. **Mosman** - Score: 0.930 (6,036 tertiary educated, age 45, income $1,487/week)

---

## 📁 Results Files Generated

All results have been exported to CSV files for further analysis:

1. **`results_top_age.csv`** - Top 20 suburbs by median age
2. **`results_top_income.csv`** - Top 20 suburbs by median income
3. **`results_top_education.csv`** - Top 20 suburbs by tertiary education
4. **`results_top_combined.csv`** - Top 20 suburbs by combined score

---

## 🔍 Original ABS Documentation

The following official documentation files are available in the repository:

### Readme Files (`/Readme/` folder):
- `2021AboutDataPacks_readme.txt` - Overview of DataPacks
- `2021Formats_readme.txt` - Format specifications
- `Summary_of_changes.txt` - R1 to R2 amendments
- `CreativeCommons_Licensing_readme.txt` - Licensing info

### Metadata Files (`/Metadata/` folder):
- **`Metadata_2021_GCP_DataPack_R1_R2.xlsx`** - Contains:
  - Sheet 1: "Table Number, Name, Population" - Lists all 119 tables
  - Sheet 2: "Cell Descriptors Information" - Column definitions

- **`2021_GCP_Sequential_Template_R2.xlsx`** - Visual template of all data cells

- **`2021Census_geog_desc_1st_2nd_3rd_release.xlsx`** - Geographic codes and names
  - Contains SAL (Suburbs and Localities) codes and names
  - 15,352 suburbs across Australia

---

## 🚀 How to Use

### Quick Analysis (Using G02):
```python
import pandas as pd

# Load the simple medians file
df = pd.read_csv('2021Census_G02_AUST_SAL.csv')

# Find top suburbs
top_age = df.nlargest(10, 'Median_age_persons')
top_income = df.nlargest(10, 'Median_tot_prsnl_inc_weekly')
```

### Detailed Analysis:
```bash
# Run the provided analysis script
python3 /home/user/Census/analyze_top_suburbs.py
```

This will:
- Analyze all 15,352 suburbs
- Generate rankings for age, income, education
- Export results to CSV files
- Display top 20 in each category

---

## 📌 Data Notes

### Coverage:
- **15,352 suburbs** (SAL - Suburbs and Localities)
- Based on **place of usual residence** (where people usually live)
- Second Release (R2) data - December 2022

### Data Protection:
- Small random adjustments applied to protect confidentiality
- Sums may differ slightly from totals

### Income Data:
- Weekly income (not annual)
- Median values provided for quick analysis
- Detailed breakdowns available in G17 tables

### Education Data:
- Only includes people **with qualifications** (not total population)
- Tertiary = Bachelor degree or higher
- Age breakdowns available

---

## 💡 Key Findings

1. **Highest education suburbs** are typically inner-city and wealthy suburban areas:
   - Melbourne CBD, Point Cook, Glen Waverley, Parramatta

2. **Highest income suburbs** include mining towns and wealthy enclaves:
   - Many small mining/rural areas with high wages
   - Also wealthy urban suburbs

3. **Oldest median age suburbs** are often:
   - Retirement areas
   - Small rural/remote locations
   - Low population areas

4. **Combined high education + income + older age** suburbs are predominantly:
   - Wealthy coastal suburbs (Brighton, Toorak, Mosman)
   - Established affluent areas with mature populations
   - Professional/executive residential areas

---

## 📞 Support

**ABS Data Services:**
- Phone: 1300 135 070
- Email: Client.services@abs.gov.au

**Repository Files:**
- All documentation in `/home/user/Census/`
- Analysis script: `analyze_top_suburbs.py`
- Results: `results_*.csv`

---

*This documentation was generated based on the 2021 Australian Census General Community Profile (GCP) DataPack - Second Release (R2)*
