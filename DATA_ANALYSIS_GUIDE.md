# Census Data Analysis Guide
## Education, Income, and Age Data for Suburbs

This guide explains how to analyze education, income, and age data from the 2021 Australian Census.

---

## 📂 Data Location

All suburb (SAL - Suburbs and Localities) data is located at:
```
/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/
```

---

## 📊 Key Tables for Your Analysis

### 1. **G02 - Selected Medians and Averages** ⭐ RECOMMENDED
**File:** `2021Census_G02_AUST_SAL.csv`

**Contains:**
- `Median_age_persons` - Median age of the suburb
- `Median_tot_prsnl_inc_weekly` - Median weekly personal income
- `Median_tot_fam_inc_weekly` - Median weekly family income
- `Median_tot_hhd_inc_weekly` - Median weekly household income
- `Median_mortgage_repay_monthly` - Median monthly mortgage repayment
- `Median_rent_weekly` - Median weekly rent
- `Average_household_size` - Average household size

**Use this for:** Quick analysis of median age, income across suburbs.

**Sample Data:**
```csv
SAL_CODE_2021,Median_age_persons,Median_mortgage_repay_monthly,Median_tot_prsnl_inc_weekly,Median_rent_weekly,Median_tot_fam_inc_weekly,Average_num_psns_per_bedroom,Median_tot_hhd_inc_weekly,Average_household_size
SAL10001,59,867,887,0,1687,0.6,1625,2.4
SAL10002,42,2216,846,550,2684,0.8,2621,3.3
```

---

### 2. **G17 - Total Personal Income (Weekly) by Age by Sex**
**Files:**
- `2021Census_G17A_AUST_SAL.csv` (Males, income bands 1-299)
- `2021Census_G17B_AUST_SAL.csv` (Females, income bands 300-799)
- `2021Census_G17C_AUST_SAL.csv` (Persons, income bands 800+)

**Contains:** Detailed breakdown of income by:
- Age groups (15-19, 20-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75-84, 85+)
- Sex (M/F/P)
- Income brackets (Negative/Nil, $1-149, $150-299, $300-399, ..., $3500+)

**Column Format:**
- `M_1_149_15_19_yrs` = Males earning $1-149/week aged 15-19
- `F_3500_more_65_74_yrs` = Females earning $3500+/week aged 65-74
- `M_Tot_Tot` = Total males (all ages, all incomes)

**Use this for:** Detailed income distribution analysis by age and sex.

---

### 3. **G49 - Highest Non-School Qualification: Level of Education** ⭐ TERTIARY EDUCATION
**Files:**
- `2021Census_G49A_AUST_SAL.csv` (Males)
- `2021Census_G49B_AUST_SAL.csv` (Females and Persons)

**Education Levels:**
1. **Postgraduate Degree** (`PGrad_Deg`) - Masters, PhD
2. **Graduate Diploma & Graduate Certificate** (`GradDip_and_GradCert`)
3. **Bachelor Degree** (`BachDeg`)
4. **Advanced Diploma & Diploma** (`AdvDip_and_Dip`)
5. **Certificate III & IV** (`Cert_III_IV`)
6. **Certificate I & II** (`Cert_I_II`)

**Age Groups:** 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75-84, 85+

**Column Format:**
- `M_PGrad_Deg_25_34` = Males with Postgraduate Degree aged 25-34
- `F_BachDeg_35_44` = Females with Bachelor Degree aged 35-44
- `M_Tot_Total` = Total males with any qualification

**Sample Data:**
```csv
SAL_CODE_2021,M_PGrad_Deg_15_24,M_PGrad_Deg_25_34,M_PGrad_Deg_35_44,...
SAL10002,0,17,11,7,18,9,0,0,60,...
```

**Use this for:** Identifying suburbs with highest tertiary education rates.

---

### 4. **G33 - Total Household Income (Weekly) by Household Composition**
**File:** `2021Census_G33_AUST_SAL.csv`

**Contains:** Household income bands by household type:
- Family households (couple with/without children, one parent)
- Lone person households
- Group households

**Income Brackets:**
- Negative/Nil income
- $1-149, $150-299, $300-399, $400-499, $500-649, $650-799, $800-999
- $1000-1249, $1250-1499, $1500-1749, $1750-1999
- $2000-2499, $2500-2999, $3000-3499, $3500-3999, $4000-4499, $4500+
- Not stated

**Use this for:** Understanding household income distribution.

---

### 5. **Additional Useful Tables**

#### **G04 - Age by Sex**
- Detailed age breakdowns (single years from 0-99, 100+)
- Useful for precise age distribution analysis

#### **G16 - Highest Year of School Completed**
- School completion levels
- Age groups and sex breakdowns

---

## 🔍 How to Find Suburbs With Highest Values

### Example: Find suburbs with highest tertiary education

```python
import pandas as pd

# Load G49A (Males with tertiary qualifications)
df = pd.read_csv('2021Census_G49A_AUST_SAL.csv')

# Calculate total people with Bachelor degree or higher
df['Tertiary_Total'] = (
    df[[col for col in df.columns if 'PGrad_Deg' in col]].sum(axis=1) +
    df[[col for col in df.columns if 'GradDip_and_GradCert' in col]].sum(axis=1) +
    df[[col for col in df.columns if 'BachDeg' in col]].sum(axis=1)
)

# Sort by highest tertiary education
top_suburbs = df.nlargest(20, 'Tertiary_Total')
```

### Example: Find suburbs with highest median age and income

```python
# Load G02 (Medians and Averages)
df = pd.read_csv('2021Census_G02_AUST_SAL.csv')

# Filter and sort
top_age_income = df.nlargest(20, 'Median_age_persons')
top_income = df.nlargest(20, 'Median_tot_prsnl_inc_weekly')
```

---

## 📖 Important Notes

### Data Protection
- Small random adjustments applied to protect confidentiality
- Row/column sums may differ slightly from totals

### Counting Basis
- Data is based on **place of usual residence** (where people usually live)
- Not where they were on Census night

### Geography Mapping
To get actual suburb names, you'll need to join with:
```
/home/user/Census/2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx
```

This file contains mapping of `SAL_CODE_2021` to suburb names.

---

## 📚 Additional Documentation

### Main Documentation Files:
1. **Metadata_2021_GCP_DataPack_R1_R2.xlsx** - Complete table and column descriptions
2. **2021_GCP_Sequential_Template_R2.xlsx** - Template showing all available data cells
3. **2021Formats_readme.txt** - Format specifications
4. **2021AboutDataPacks_readme.txt** - General information about DataPacks

### Location:
```
/home/user/Census/2021_GCP_all_for_AUS_short-header/Readme/
/home/user/Census/2021_GCP_all_for_AUS_short-header/Metadata/
```

---

## 🎯 Quick Start Recommendation

For your specific use case (suburbs with highest tertiary education, income, and oldest age):

1. **Start with G02** - Quick overview of median age and income
2. **Use G49A & G49B** - Detailed tertiary education breakdown
3. **Use G17** - If you need detailed income distribution by age

**Pro Tip:** G02 gives you the fastest results for ranking suburbs by median values!

---

## 📞 Need Help?

- Check the metadata files for detailed column descriptions
- All readme files in `/Readme/` folder contain valuable information
- Contact ABS Data Services: Client.services@abs.gov.au or 1300 135 070
