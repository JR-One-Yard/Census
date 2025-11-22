#!/usr/bin/env python3
"""
Multi-City AI Advisory Target Comparison & Sydney Low-Performers

This script performs two analyses:
1. Compares Sydney with other major Australian cities for AI advisory targeting
2. Identifies the bottom 10 Sydney suburbs to avoid
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
DATA_DIR = Path("2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

print("=" * 120)
print("MULTI-CITY AI ADVISORY TARGET COMPARISON")
print("=" * 120)
print()

# ============================================================================
# Load Data (same as previous analysis)
# ============================================================================

print("Loading data...")

# Load SAL metadata
metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
sal_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

# Load housing/income data (G02)
g02_file = DATA_DIR / "2021Census_G02_AUST_SAL.csv"
g02_df = pd.read_csv(g02_file)

# Load age demographics (G01)
g01_file = DATA_DIR / "2021Census_G01_AUST_SAL.csv"
age_df = pd.read_csv(g01_file)

# Calculate age brackets
age_df['Age_55_64_yr_P'] = age_df['Age_55_64_yr_M'] + age_df['Age_55_64_yr_F']
age_df['Age_65_74_yr_P'] = age_df['Age_65_74_yr_M'] + age_df['Age_65_74_yr_F']
age_df['Total_Population'] = age_df['Tot_P_P']
age_df['Age_55_74_Total'] = age_df['Age_55_64_yr_P'] + age_df['Age_65_74_yr_P']
age_df['Age_55_74_Pct'] = (age_df['Age_55_74_Total'] / age_df['Total_Population'] * 100).fillna(0)

# Load occupation data (G60A)
g60a_file = DATA_DIR / "2021Census_G60A_AUST_SAL.csv"
occupation_df = pd.read_csv(g60a_file)

occupation_df['Total_Managers'] = (
    occupation_df['M_Tot_Managers'] + occupation_df['F_Tot_Managers']
)
occupation_df['Total_Professionals'] = (
    occupation_df['M_Tot_Professionals'] + occupation_df['F_Tot_Professionals']
)
occupation_df['Total_Employed'] = (
    occupation_df['M_Tot_Tot'] + occupation_df['F_Tot_Tot']
)

occupation_df['Manager_Concentration_Pct'] = (
    occupation_df['Total_Managers'] / occupation_df['Total_Employed'] * 100
).fillna(0)

occupation_df['Professional_Concentration_Pct'] = (
    occupation_df['Total_Professionals'] / occupation_df['Total_Employed'] * 100
).fillna(0)

# Merge all data
df = sal_df.copy()
df = df.merge(g02_df, left_on='Census_Code_2021', right_on='SAL_CODE_2021', how='inner')
df = df.merge(age_df[['SAL_CODE_2021', 'Total_Population', 'Age_55_74_Total', 'Age_55_74_Pct']],
              on='SAL_CODE_2021', how='left')
df = df.merge(occupation_df[['SAL_CODE_2021', 'Total_Employed', 'Total_Managers',
                              'Manager_Concentration_Pct', 'Professional_Concentration_Pct']],
              on='SAL_CODE_2021', how='left')

print(f"Loaded {len(df):,} total suburbs")
print()

# Apply urban filter
urban_df = df[
    (df['Total_Employed'] >= 800) &
    (df['Total_Population'] >= 1500) &
    (df['Median_mortgage_repay_monthly'] > 0) &
    (df['Manager_Concentration_Pct'] > 0)
].copy()

# Calculate composite scores
def normalize_to_100(series):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val) * 100)

urban_df['Manager_Score'] = normalize_to_100(urban_df['Manager_Concentration_Pct'])
urban_df['Professional_Score'] = normalize_to_100(urban_df['Professional_Concentration_Pct'])
urban_df['Age_55_74_Score'] = normalize_to_100(urban_df['Age_55_74_Pct'])
urban_df['Income_Score'] = normalize_to_100(urban_df['Median_tot_prsnl_inc_weekly'])
urban_df['Wealth_Score'] = normalize_to_100(urban_df['Median_mortgage_repay_monthly'])

urban_df['Target_Score'] = (
    urban_df['Manager_Score'] * 0.30 +
    urban_df['Age_55_74_Score'] * 0.30 +
    urban_df['Wealth_Score'] * 0.25 +
    urban_df['Professional_Score'] * 0.10 +
    urban_df['Income_Score'] * 0.05
)

# ============================================================================
# City Identification Function
# ============================================================================

def identify_city(suburb_name):
    """Identify which major Australian city a suburb belongs to"""
    suburb_lower = suburb_name.lower()

    # Sydney suburbs
    sydney_keywords = ['sydney', 'mosman', 'bondi', 'manly', 'parramatta', 'penrith', 'campbelltown',
                       'baulkham', 'hornsby', 'sutherland', 'randwick', 'woollahra', 'hunters hill',
                       'balmain', 'cremorne', 'vaucluse', 'kirribilli', 'paddington', 'surry hills',
                       'newtown', 'glebe', 'leichhardt', 'rozelle', 'drummoyne', 'strathfield',
                       'burwood', 'chatswood', 'lindfield', 'killara', 'pymble', 'turramurra',
                       'wahroonga', 'castle hill', 'ryde', 'eastwood', 'epping', 'carlingford',
                       'cronulla', 'caringbah', 'miranda', 'seaforth', 'balgowlah', 'avalon',
                       'clovelly', 'bronte', 'coogee', 'dover heights', 'rose bay', 'double bay',
                       'bellevue hill', 'longueville', 'northbridge', 'castlecrag', 'willoughby',
                       'dee why', 'collaroy', 'narrabeen', 'freshwater', 'curl curl', 'north sydney',
                       'crows nest', 'st leonards', 'greenwich', 'darlinghurst', 'potts point',
                       'elizabeth bay', 'edgecliff', 'queens park', 'annandale', 'redfern', 'waterloo',
                       'alexandria', 'roseville', 'gordon', 'st ives', 'cherrybrook', 'kellyville',
                       'bella vista', 'rouse hill', 'five dock', 'concord', 'gladesville']

    # Melbourne suburbs
    melbourne_keywords = ['melbourne', 'toorak', 'brighton', 'kew', 'malvern', 'camberwell', 'hawthorn',
                          'armadale', 'south yarra', 'prahran', 'glen iris', 'balwyn', 'canterbury',
                          'surrey hills', 'middle park', 'albert park', 'port melbourne', 'south melbourne',
                          'st kilda', 'elwood', 'caulfield', 'elsternwick', 'bentleigh', 'glen waverley',
                          'burwood', 'doncaster', 'templestowe', 'bulleen', 'ivanhoe', 'heidelberg',
                          'northcote', 'thornbury', 'preston', 'reservoir', 'bundoora', 'greensborough']

    # Brisbane suburbs
    brisbane_keywords = ['brisbane', 'paddington', 'toowong', 'indooroopilly', 'kenmore', 'chapel hill',
                         'bardon', 'ashgrove', 'kelvin grove', 'red hill', 'new farm', 'teneriffe',
                         'hawthorne', 'balmoral', 'bulimba', 'norman park', 'coorparoo', 'camp hill',
                         'carina', 'carindale', 'wynnum', 'manly', 'sandgate', 'hamilton', 'ascot',
                         'clayfield', 'hendra', 'nundah', 'kedron', 'gordon park', 'stafford']

    # Perth suburbs
    perth_keywords = ['perth', 'peppermint grove', 'cottesloe', 'claremont', 'nedlands', 'dalkeith',
                      'mosman park', 'swanbourne', 'floreat', 'city beach', 'wembley', 'subiaco',
                      'shenton park', 'crawley', 'mount lawley', 'highgate', 'leederville', 'west perth',
                      'north perth', 'east perth', 'south perth', 'como', 'applecross', 'ardross',
                      'mount pleasant', 'manning', 'waterford', 'shelley', 'rossmoyne', 'bateman']

    # Adelaide suburbs
    adelaide_keywords = ['adelaide', 'unley', 'burnside', 'norwood', 'prospect', 'walkerville',
                         'medindie', 'st peters', 'malvern', 'goodwood', 'wayville', 'parkside',
                         'eastwood', 'frewville', 'fullarton', 'glen osmond', 'toorak gardens',
                         'rose park', 'kent town', 'north adelaide', 'fitzroy', 'ovingham',
                         'glenelg', 'brighton', 'marino', 'seacliff', 'somerton park']

    # Canberra suburbs
    canberra_keywords = ['canberra', 'forrest', 'red hill', 'deakin', 'yarralumla', 'barton',
                         'kingston', 'manuka', 'griffith', 'narrabundah', 'garran', 'hughes',
                         'curtin', 'lyons', 'woden', 'phillip', 'belconnen', 'braddon', 'turner',
                         'acton', 'reid', 'campbell', 'russell', 'parkes', 'oconnor', 'ainslie',
                         'dickson', 'lyneham', 'hackett', 'watson', 'downer']

    if any(keyword in suburb_lower for keyword in sydney_keywords):
        return 'Sydney'
    elif any(keyword in suburb_lower for keyword in melbourne_keywords):
        return 'Melbourne'
    elif any(keyword in suburb_lower for keyword in brisbane_keywords):
        return 'Brisbane'
    elif any(keyword in suburb_lower for keyword in perth_keywords):
        return 'Perth'
    elif any(keyword in suburb_lower for keyword in adelaide_keywords):
        return 'Adelaide'
    elif any(keyword in suburb_lower for keyword in canberra_keywords):
        return 'Canberra'
    else:
        return 'Other'

urban_df['City'] = urban_df['Census_Name_2021'].apply(identify_city)

# Filter for major cities only
major_cities = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra']
cities_df = urban_df[urban_df['City'].isin(major_cities)].copy()

print(f"Suburbs in major cities: {len(cities_df):,}")
print()

# ============================================================================
# ANALYSIS 1: Top 20 Suburbs by City
# ============================================================================

print("=" * 120)
print("TOP 20 TARGET SUBURBS BY MAJOR CITY")
print("=" * 120)
print()

for city in ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra']:
    city_suburbs = cities_df[cities_df['City'] == city].sort_values('Target_Score', ascending=False)
    top_20 = city_suburbs.head(20)

    if len(top_20) > 0:
        print(f"\n{city.upper()} - TOP 20 SUBURBS")
        print("-" * 120)
        print(f"{'Rank':<5}{'Suburb':<35}{'Score':<8}{'Mgr%':<7}{'55-74%':<8}{'Income':<10}{'Mortgage':<10}")
        print(f"{'':5}{'':35}{'(0-100)':<8}{'':7}{'':8}{'$/wk':<10}{'$/mo':<10}")
        print("-" * 120)

        for idx, row in top_20.iterrows():
            rank = list(top_20.index).index(idx) + 1
            print(f"{rank:<5}{row['Census_Name_2021']:<35}{row['Target_Score']:>6.1f}  "
                  f"{row['Manager_Concentration_Pct']:>5.1f}%  {row['Age_55_74_Pct']:>6.1f}%  "
                  f"${row['Median_tot_prsnl_inc_weekly']:>7,.0f}  ${row['Median_mortgage_repay_monthly']:>8,.0f}")

        print()
        print(f"SUMMARY - {city}")
        print(f"  Average manager concentration: {top_20['Manager_Concentration_Pct'].mean():.1f}%")
        print(f"  Average age 55-74: {top_20['Age_55_74_Pct'].mean():.1f}%")
        print(f"  Average income: ${top_20['Median_tot_prsnl_inc_weekly'].mean():,.0f}/week")
        print(f"  Average mortgage: ${top_20['Median_mortgage_repay_monthly'].mean():,.0f}/month")
        print(f"  Total 55-74 population: {top_20['Age_55_74_Total'].sum():,}")
        print()

# ============================================================================
# ANALYSIS 2: City Comparison Summary
# ============================================================================

print("=" * 120)
print("CITY COMPARISON SUMMARY")
print("=" * 120)
print()

city_comparison = []
for city in major_cities:
    city_suburbs = cities_df[cities_df['City'] == city].sort_values('Target_Score', ascending=False)
    top_20 = city_suburbs.head(20)

    if len(top_20) > 0:
        city_comparison.append({
            'City': city,
            'Num_Suburbs': len(top_20),
            'Avg_Score': top_20['Target_Score'].mean(),
            'Avg_Manager_Pct': top_20['Manager_Concentration_Pct'].mean(),
            'Avg_Age_55_74_Pct': top_20['Age_55_74_Pct'].mean(),
            'Avg_Income': top_20['Median_tot_prsnl_inc_weekly'].mean(),
            'Avg_Mortgage': top_20['Median_mortgage_repay_monthly'].mean(),
            'Total_Pop_55_74': top_20['Age_55_74_Total'].sum()
        })

comparison_df = pd.DataFrame(city_comparison).sort_values('Avg_Score', ascending=False)

print(f"{'City':<15}{'Avg Score':<12}{'Mgr%':<8}{'55-74%':<8}{'Income':<12}{'Mortgage':<12}{'Pop 55-74':<12}")
print(f"{'':15}{'(0-100)':<12}{'':8}{'':8}{'$/wk':<12}{'$/mo':<12}{'':12}")
print("-" * 120)

for idx, row in comparison_df.iterrows():
    print(f"{row['City']:<15}{row['Avg_Score']:>10.1f}  {row['Avg_Manager_Pct']:>6.1f}%  "
          f"{row['Avg_Age_55_74_Pct']:>6.1f}%  ${row['Avg_Income']:>9,.0f}  "
          f"${row['Avg_Mortgage']:>10,.0f}  {row['Total_Pop_55_74']:>10,.0f}")

print()
print()

# ============================================================================
# ANALYSIS 3: Sydney - Bottom 10 Suburbs to AVOID
# ============================================================================

print("=" * 120)
print("SYDNEY - BOTTOM 10 SUBURBS TO AVOID")
print("=" * 120)
print()

sydney_suburbs = cities_df[cities_df['City'] == 'Sydney'].sort_values('Target_Score', ascending=True)
bottom_10 = sydney_suburbs.head(10)

print("These Sydney suburbs have executive presence but score LOW on our targeting criteria")
print()
print(f"{'Rank':<5}{'Suburb':<35}{'Score':<8}{'Mgr%':<7}{'55-74%':<8}{'Income':<10}{'Mortgage':<10}{'Why Avoid':<20}")
print(f"{'':5}{'':35}{'(0-100)':<8}{'':7}{'':8}{'$/wk':<10}{'$/mo':<10}{'':20}")
print("-" * 120)

for idx, row in bottom_10.iterrows():
    rank = list(bottom_10.index).index(idx) + 1

    # Identify why it scores low
    reasons = []
    if row['Age_55_74_Pct'] < 15:
        reasons.append('Too young')
    if row['Median_mortgage_repay_monthly'] < 2000:
        reasons.append('Low wealth')
    if row['Manager_Concentration_Pct'] < 15:
        reasons.append('Low exec %')
    if row['Median_tot_prsnl_inc_weekly'] < 1000:
        reasons.append('Low income')

    reason_str = ', '.join(reasons) if reasons else 'Multiple factors'

    print(f"{rank:<5}{row['Census_Name_2021']:<35}{row['Target_Score']:>6.1f}  "
          f"{row['Manager_Concentration_Pct']:>5.1f}%  {row['Age_55_74_Pct']:>6.1f}%  "
          f"${row['Median_tot_prsnl_inc_weekly']:>7,.0f}  ${row['Median_mortgage_repay_monthly']:>8,.0f}  "
          f"{reason_str:<20}")

print()
print("KEY INSIGHTS - What to Avoid:")
print(f"  Average manager concentration: {bottom_10['Manager_Concentration_Pct'].mean():.1f}%")
print(f"  Average age 55-74: {bottom_10['Age_55_74_Pct'].mean():.1f}%")
print(f"  Average income: ${bottom_10['Median_tot_prsnl_inc_weekly'].mean():,.0f}/week")
print(f"  Average mortgage: ${bottom_10['Median_mortgage_repay_monthly'].mean():,.0f}/month")
print()

# ============================================================================
# TIME OF YEAR RECOMMENDATIONS
# ============================================================================

print("=" * 120)
print("TIME-OF-YEAR RECOMMENDATIONS FOR DIRECT MAIL CAMPAIGN")
print("=" * 120)
print()

print("Based on demographic analysis of target suburbs (older executives, 55-74 age bracket):")
print()

print("BEST TIMES TO MAIL:")
print("-" * 120)
print()

print("1. LATE JANUARY - EARLY FEBRUARY (Post-Holiday)")
print("   • Executives back from summer holidays")
print("   • New year planning and goal-setting mindset")
print("   • Tax planning on their mind (new financial year ahead)")
print("   • Children/grandchildren likely returning to work/study - family guidance top of mind")
print("   • RECOMMENDED: Primary campaign launch")
print()

print("2. MID-MARCH - EARLY APRIL (Pre-EOFY)")
print("   • Financial year-end approaching - strategic thinking mode")
print("   • Tax planning and investment decisions being made")
print("   • Less travel (autumn, pre-Easter)")
print("   • Good weather for mail engagement (not too hot)")
print("   • RECOMMENDED: Secondary campaign or follow-up")
print()

print("3. LATE AUGUST - SEPTEMBER (Spring, Post-Tax)")
print("   • Tax returns filed, financial planning complete")
print("   • Spring optimism - good engagement period")
print("   • School holidays over (mid-Sept onwards)")
print("   • Warmer weather, more active engagement")
print("   • RECOMMENDED: Tertiary campaign")
print()

print("TIMES TO AVOID:")
print("-" * 120)
print()

print("❌ DECEMBER - MID JANUARY")
print("   • Summer holidays - many executives traveling")
print("   • Low engagement, mail may sit unread")
print("   • Family focus, not business/education planning")
print()

print("❌ MID-JUNE - JULY (EOFY + Winter Holidays)")
print("   • End of financial year - too busy with immediate tasks")
print("   • School holidays (late June-July)")
print("   • Ski trips to Japan/Europe (wealthy demographic)")
print("   • Low engagement period")
print()

print("❌ EASTER PERIOD (Late March/Early April)")
print("   • Variable dates, but typically travel period")
print("   • 4-day weekend disrupts mail delivery and engagement")
print()

print()
print("OPTIMAL CAMPAIGN CALENDAR:")
print("-" * 120)
print()
print("  Campaign 1 (Primary):   Week of Feb 5-12")
print("  Campaign 2 (Secondary): Week of Mar 18-25")
print("  Campaign 3 (Tertiary):  Week of Sep 10-17")
print()
print("Each campaign should target different geographic clusters to test response rates:")
print("  • Campaign 1: Lower North Shore + Eastern Suburbs (highest score suburbs)")
print("  • Campaign 2: Northern Beaches + Upper North Shore")
print("  • Campaign 3: Inner West + Parramatta/Ryde")
print()

# ============================================================================
# Export Results
# ============================================================================

# Export city comparison
comparison_df.to_csv(RESULTS_DIR / 'city_comparison_ai_advisory_targets.csv', index=False)

# Export bottom 10 Sydney suburbs
bottom_10_export = bottom_10[[
    'Census_Name_2021', 'Target_Score',
    'Manager_Concentration_Pct', 'Age_55_74_Pct',
    'Median_tot_prsnl_inc_weekly', 'Median_mortgage_repay_monthly'
]].copy()
bottom_10_export.columns = ['Suburb', 'Target_Score', 'Manager_Pct', 'Age_55_74_Pct',
                             'Median_Income_Weekly', 'Median_Mortgage_Monthly']
bottom_10_export.to_csv(RESULTS_DIR / 'sydney_bottom10_suburbs_to_avoid.csv', index=False)

# Export top 20 for each city
for city in major_cities:
    city_suburbs = cities_df[cities_df['City'] == city].sort_values('Target_Score', ascending=False)
    top_20 = city_suburbs.head(20)

    if len(top_20) > 0:
        export_df = top_20[[
            'Census_Name_2021', 'Target_Score',
            'Manager_Concentration_Pct', 'Professional_Concentration_Pct', 'Age_55_74_Pct',
            'Median_tot_prsnl_inc_weekly', 'Median_mortgage_repay_monthly',
            'Total_Population', 'Age_55_74_Total'
        ]].copy()
        export_df.columns = ['Suburb', 'Target_Score', 'Manager_Pct', 'Professional_Pct',
                             'Age_55_74_Pct', 'Median_Income_Weekly', 'Median_Mortgage_Monthly',
                             'Total_Population', 'Population_55_74']

        filename = f'{city.lower()}_top20_ai_advisory_targets.csv'
        export_df.to_csv(RESULTS_DIR / filename, index=False)

print("=" * 120)
print()
print("Results exported:")
print("  - results/city_comparison_ai_advisory_targets.csv")
print("  - results/sydney_bottom10_suburbs_to_avoid.csv")
print("  - results/{city}_top20_ai_advisory_targets.csv (for each city)")
print()
print("=" * 120)
