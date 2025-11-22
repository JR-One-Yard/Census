#!/usr/bin/env python3
"""
Analyze Bottom Value SYDNEY Suburbs (excluding regional NSW)
"""

import pandas as pd

# Load the full analysis
df = pd.read_csv('/home/user/Census/sydney_all_suburbs_value_analysis.csv')

# More aggressive Sydney filtering - exclude suburbs with:
# 1. Very low income (<$600/week suggests regional)
# 2. Very old population (>55 suggests retirement towns)
# 3. Very small households (<2.2 suggests not family areas)
# Combined, these indicate regional/coastal retirement areas

# First, let's identify actually-Sydney suburbs by looking at income + density patterns
# True Sydney suburbs typically have:
# - Income >$650/week
# - Density >100 per sq km (excludes rural)
# - OR are well-known Sydney areas

sydney_proper = df[
    ((df['Median_tot_prsnl_inc_weekly'] > 650) & (df['Density_per_sqkm'] > 100)) |
    (df['Median_mortgage_repay_monthly'] > 1800)  # High mortgages = metro area
].copy()

print(f"Filtered to {len(sydney_proper)} actual Sydney metro suburbs")
print(f"(vs {len(df)} total NSW suburbs in original data)")
print()

# Now get bottom 100 of actual Sydney
bottom_100_sydney = sydney_proper.sort_values('Value_Score', ascending=True).head(100)

# Save to CSV
bottom_100_sydney.to_csv('/home/user/Census/sydney_bottom_100_actual_sydney_suburbs.csv', index=False)

print('=' * 120)
print('BOTTOM 100 VALUE SUBURBS - ACTUAL SYDNEY METRO AREA')
print('=' * 120)
print()
print('🚫 WORST 20 VALUE SUBURBS IN SYDNEY:')
print()
print(f"{'Rank':<6}{'Suburb':<40}{'Value':>10}  {'Quality':>8}  {'Price':>8}  {'Mortgage':>10}  {'Income':>10}")
print('-' * 110)

for i, (_, row) in enumerate(bottom_100_sydney.head(20).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<40}{row['Value_Score']:>10.1f}  "
          f"{row['Quality_Index']:>8.1f}  {row['Price_Index']:>8.1f}  "
          f"${row['Median_mortgage_repay_monthly']:>9,.0f}  "
          f"${row['Median_tot_prsnl_inc_weekly']:>9,.0f}/w")

print()
print('=' * 120)
print('ANALYSIS - WHY THESE SYDNEY SUBURBS HAVE POOR VALUE')
print('=' * 120)
print()

print(f"Average Tertiary Education: {bottom_100_sydney['Tertiary_Pct'].mean():.1f}% (vs 35.5% Sydney avg)")
print(f"Average Weekly Income: ${bottom_100_sydney['Median_tot_prsnl_inc_weekly'].mean():.0f} (vs $804 Sydney median)")
print(f"Average Monthly Mortgage: ${bottom_100_sydney['Median_mortgage_repay_monthly'].mean():.0f} (vs $2,139 Sydney median)")
print(f"Average Median Age: {bottom_100_sydney['Median_age_persons'].mean():.1f} years (vs 42 Sydney avg)")
print(f"Average Quality Index: {bottom_100_sydney['Quality_Index'].mean():.1f} (vs 3,924 Sydney avg)")
print(f"Average Price Index: {bottom_100_sydney['Price_Index'].mean():.1f} (vs 50.0 Sydney avg)")
print()

# Analyze the problems
print('📊 KEY PROBLEM CATEGORIES:')
print()

# Category 1: Overpriced for quality
overpriced = bottom_100_sydney[
    (bottom_100_sydney['Price_Index'] > 75) &
    (bottom_100_sydney['Quality_Index'] < sydney_proper['Quality_Index'].median())
]
print(f"1. OVERPRICED ({len(overpriced)} suburbs)")
print(f"   High price relative to quality delivered")
if len(overpriced) > 0:
    print(f"   Examples:")
    for _, row in overpriced.head(5).iterrows():
        print(f"   • {row['Suburb_Name']}: ${row['Median_mortgage_repay_monthly']:.0f}/mo mortgage, "
              f"Quality Index {row['Quality_Index']:.0f}")
print()

# Category 2: Low education
low_edu = bottom_100_sydney[bottom_100_sydney['Tertiary_Pct'] < 25]
print(f"2. LOW EDUCATION ({len(low_edu)} suburbs)")
print(f"   <25% tertiary education (vs 35.5% Sydney avg)")
if len(low_edu) > 0:
    print(f"   Examples:")
    for _, row in low_edu.head(5).iterrows():
        print(f"   • {row['Suburb_Name']}: {row['Tertiary_Pct']:.1f}% tertiary, "
              f"${row['Median_tot_prsnl_inc_weekly']:.0f}/w income")
print()

# Category 3: High mortgage-to-income ratio
bottom_100_sydney['Mortgage_Income_Ratio'] = (
    bottom_100_sydney['Median_mortgage_repay_monthly'] /
    (bottom_100_sydney['Median_tot_prsnl_inc_weekly'] * 52 / 12)
)
high_burden = bottom_100_sydney[bottom_100_sydney['Mortgage_Income_Ratio'] > 0.35]
print(f"3. AFFORDABILITY STRESS ({len(high_burden)} suburbs)")
print(f"   Mortgage >35% of monthly income")
if len(high_burden) > 0:
    print(f"   Examples:")
    for _, row in high_burden.head(5).iterrows():
        ratio = row['Mortgage_Income_Ratio']
        print(f"   • {row['Suburb_Name']}: ${row['Median_mortgage_repay_monthly']:.0f}/mo on "
              f"${row['Median_tot_prsnl_inc_weekly']:.0f}/w = {ratio*100:.1f}% of income")
print()

# Category 4: Poor demographics for families
poor_demo = bottom_100_sydney[
    (bottom_100_sydney['Median_age_persons'] > 50) |
    (bottom_100_sydney['Average_household_size'] < 2.3)
]
print(f"4. UNFAVORABLE FAMILY DEMOGRAPHICS ({len(poor_demo)} suburbs)")
print(f"   Median age >50 or household size <2.3")
if len(poor_demo) > 0:
    print(f"   Examples:")
    for _, row in poor_demo.head(5).iterrows():
        print(f"   • {row['Suburb_Name']}: Age {row['Median_age_persons']:.0f}, "
              f"Household {row['Average_household_size']:.1f} persons")
print()

# Identify specific problem suburbs by category
print('=' * 120)
print('RED FLAGS TO AVOID:')
print('=' * 120)
print()

# Identify the most problematic patterns
worst_combo = bottom_100_sydney[
    (bottom_100_sydney['Tertiary_Pct'] < 25) &
    (bottom_100_sydney['Price_Index'] > 70)
]
if len(worst_combo) > 0:
    print(f"⚠️  {len(worst_combo)} suburbs with LOW EDUCATION + HIGH PRICE (worst combination):")
    for _, row in worst_combo.head(10).iterrows():
        print(f"   • {row['Suburb_Name']}: {row['Tertiary_Pct']:.1f}% tertiary, "
              f"${row['Median_mortgage_repay_monthly']:.0f}/mo, "
              f"Income ${row['Median_tot_prsnl_inc_weekly']:.0f}/w")
print()

print('✓ Saved: sydney_bottom_100_actual_sydney_suburbs.csv')
print()
print('=' * 120)
print(f"NOTE: Original analysis included {len(df) - len(sydney_proper)} regional NSW towns.")
print(f"This analysis focuses on {len(sydney_proper)} actual Greater Sydney metro suburbs.")
print('=' * 120)
