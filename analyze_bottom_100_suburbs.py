#!/usr/bin/env python3
"""
Analyze Bottom 100 Value Suburbs - What to Avoid
"""

import pandas as pd

# Load the full analysis
df = pd.read_csv('/home/user/Census/sydney_all_suburbs_value_analysis.csv')

# Sort by Value_Score ascending (worst first)
bottom_100 = df.sort_values('Value_Score', ascending=True).head(100)

# Save to CSV
bottom_100.to_csv('/home/user/Census/sydney_bottom_100_value_suburbs.csv', index=False)

print('=' * 120)
print('BOTTOM 100 VALUE SUBURBS - WHAT TO AVOID')
print('=' * 120)
print()
print('🚫 WORST 20 VALUE SUBURBS FOR FAMILIES:')
print()
print(f"{'Rank':<6}{'Suburb':<40}{'Value':>10}  {'Quality':>8}  {'Price':>8}  {'Mortgage':>10}  {'Income':>10}")
print('-' * 110)

for i, (_, row) in enumerate(bottom_100.head(20).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<40}{row['Value_Score']:>10.1f}  "
          f"{row['Quality_Index']:>8.1f}  {row['Price_Index']:>8.1f}  "
          f"${row['Median_mortgage_repay_monthly']:>9,.0f}  "
          f"${row['Median_tot_prsnl_inc_weekly']:>9,.0f}/w")

print()
print('=' * 120)
print('ANALYSIS OF LOW-VALUE CHARACTERISTICS')
print('=' * 120)
print()

# Analyze what makes these suburbs low value
print(f"Average Tertiary Education: {bottom_100['Tertiary_Pct'].mean():.1f}% (vs 35.5% Sydney avg)")
print(f"Average Weekly Income: ${bottom_100['Median_tot_prsnl_inc_weekly'].mean():.0f} (vs $804 Sydney median)")
print(f"Average Monthly Mortgage: ${bottom_100['Median_mortgage_repay_monthly'].mean():.0f} (vs $2,139 Sydney median)")
print(f"Average Median Age: {bottom_100['Median_age_persons'].mean():.1f} years (vs 42 Sydney avg)")
print(f"Average Quality Index: {bottom_100['Quality_Index'].mean():.1f} (vs 3,924 Sydney avg)")
print(f"Average Price Index: {bottom_100['Price_Index'].mean():.1f} (vs 50.0 Sydney avg)")
print()

# Categories of low value
print('📊 WHY THESE SUBURBS RANK LOW:')
print()

# Low quality, any price
low_quality = bottom_100[bottom_100['Quality_Index'] < 2000]
print(f"• {len(low_quality)} suburbs have LOW QUALITY (Quality Index < 2000)")
print(f"  - Poor education, low incomes, unfavorable demographics")

# High price, moderate quality
high_price = bottom_100[bottom_100['Price_Index'] > 60]
print(f"• {len(high_price)} suburbs have HIGH PRICE (Price Index > 60)")
print(f"  - Expensive relative to quality delivered")

# Both
both = bottom_100[(bottom_100['Quality_Index'] < 2000) & (bottom_100['Price_Index'] > 60)]
print(f"• {len(both)} suburbs have BOTH low quality AND high price (worst combination)")

print()

# Show some specific problematic patterns
print('🔍 SPECIFIC PROBLEM PATTERNS:')
print()

# Overpriced areas (high price, low-moderate quality)
overpriced = bottom_100[(bottom_100['Price_Index'] > 70) & (bottom_100['Quality_Index'] < 4000)]
if len(overpriced) > 0:
    print(f"• OVERPRICED ({len(overpriced)} suburbs): High cost, mediocre quality")
    for _, row in overpriced.head(5).iterrows():
        print(f"  - {row['Suburb_Name']}: Quality {row['Quality_Index']:.0f}, Price Index {row['Price_Index']:.0f}, "
              f"Mortgage ${row['Median_mortgage_repay_monthly']:.0f}")
print()

# Low education suburbs
low_edu = bottom_100[bottom_100['Tertiary_Pct'] < 20]
if len(low_edu) > 0:
    print(f"• LOW EDUCATION ({len(low_edu)} suburbs): <20% tertiary education")
    for _, row in low_edu.head(5).iterrows():
        print(f"  - {row['Suburb_Name']}: {row['Tertiary_Pct']:.1f}% tertiary, "
              f"Income ${row['Median_tot_prsnl_inc_weekly']:.0f}/w")
print()

# Poor demographics (very old or very young)
poor_demo = bottom_100[(bottom_100['Median_age_persons'] > 55) | (bottom_100['Median_age_persons'] < 30)]
if len(poor_demo) > 0:
    print(f"• POOR DEMOGRAPHICS ({len(poor_demo)} suburbs): Age <30 or >55 (not family-optimal)")
    for _, row in poor_demo.head(5).iterrows():
        print(f"  - {row['Suburb_Name']}: Age {row['Median_age_persons']:.0f}, "
              f"Household size {row['Average_household_size']:.1f}")
print()

print('=' * 120)
print('KEY TAKEAWAYS - AVOID THESE PATTERNS:')
print('=' * 120)
print()
print("1. HIGH PRICE + MODERATE QUALITY = Poor value")
print("   Example: Paying premium prices for average education/employment")
print()
print("2. LOW EDUCATION + LOW INCOME = Limited opportunity")
print("   Example: <20% tertiary education, <$600/week income")
print()
print("3. POOR DEMOGRAPHICS = Wrong life stage")
print("   Example: Median age >55 (retirees) or <30 (singles/young couples)")
print()
print("4. AFFORDABILITY STRESS = High mortgage-to-income ratio")
print(f"   Example: Paying >${bottom_100['Median_mortgage_repay_monthly'].quantile(0.75):.0f}/month "
          f"on ${bottom_100['Median_tot_prsnl_inc_weekly'].quantile(0.25):.0f}/week income")
print()

print('✓ Saved: sydney_bottom_100_value_suburbs.csv')
print()
