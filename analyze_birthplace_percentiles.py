#!/usr/bin/env python3
"""
Analyze socio-economic characteristics of TOP 10% vs BOTTOM 10% suburbs
within each dominant birthplace country group.

Identifies outliers and patterns masked by median statistics.
"""

import csv
import pandas as pd
import numpy as np

# File paths
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
DETAILED_RESULTS = "/home/user/Census/results_birthplace_socioeconomic_detailed.csv"

print("="*100)
print("PERCENTILE ANALYSIS: TOP 10% vs BOTTOM 10% SUBURBS BY BIRTHPLACE COUNTRY")
print("="*100)

# Load detailed results
print("\nLoading detailed suburb-level data...")
df = pd.read_csv(DETAILED_RESULTS)
print(f"Loaded {len(df):,} suburbs")

# Focus on top 5 countries
top_5_countries = df['Top_Non_Australia_Country'].value_counts().head(5).index.tolist()
print(f"\nAnalyzing: {', '.join([c.replace('_', ' ') for c in top_5_countries])}")

# Function to get percentile groups
def get_percentile_groups(country_df, metric_col, country_name):
    """Get top 10% and bottom 10% by a given metric"""
    # Calculate percentile thresholds
    p10 = country_df[metric_col].quantile(0.10)
    p90 = country_df[metric_col].quantile(0.90)

    bottom_10 = country_df[country_df[metric_col] <= p10].copy()
    top_10 = country_df[country_df[metric_col] >= p90].copy()

    return bottom_10, top_10, p10, p90

# Analyze by multiple dimensions
print("\n" + "="*100)
print("ANALYSIS BY INCOME (Personal Income)")
print("="*100)

income_stats = {}

for country in top_5_countries:
    country_df = df[df['Top_Non_Australia_Country'] == country].copy()

    # Get percentile groups by income
    bottom_10, top_10, p10, p90 = get_percentile_groups(
        country_df, 'Median_tot_prsnl_inc_weekly', country
    )

    income_stats[country] = {
        'n_suburbs': len(country_df),
        'p10_threshold': p10,
        'p90_threshold': p90,
        'bottom_10_n': len(bottom_10),
        'top_10_n': len(top_10),
        # Bottom 10% stats
        'bottom_income': bottom_10['Median_tot_prsnl_inc_weekly'].mean(),
        'bottom_age': bottom_10['Median_age_persons'].mean(),
        'bottom_tertiary': bottom_10['Tertiary_Percentage'].mean(),
        'bottom_unemployment': bottom_10['Unemployment_Rate'].mean(),
        'bottom_hh_size': bottom_10['Average_household_size'].mean(),
        # Top 10% stats
        'top_income': top_10['Median_tot_prsnl_inc_weekly'].mean(),
        'top_age': top_10['Median_age_persons'].mean(),
        'top_tertiary': top_10['Tertiary_Percentage'].mean(),
        'top_unemployment': top_10['Unemployment_Rate'].mean(),
        'top_hh_size': top_10['Average_household_size'].mean(),
        # Example suburbs
        'bottom_examples': bottom_10.nlargest(3, 'Total_Population')['Suburb_Name'].tolist(),
        'top_examples': top_10.nlargest(3, 'Total_Population')['Suburb_Name'].tolist(),
    }

print("\n" + "-"*100)
print(f"{'Country':<15} {'Bottom 10% Income':<20} {'Top 10% Income':<20} {'Income Gap':<15} {'Top Tertiary%':<15}")
print("-"*100)

for country in top_5_countries:
    stats = income_stats[country]
    income_gap = stats['top_income'] - stats['bottom_income']
    income_gap_pct = (income_gap / stats['bottom_income'] * 100) if stats['bottom_income'] > 0 else 0

    country_display = country.replace('_', ' ')
    print(f"{country_display:<15} "
          f"${stats['bottom_income']:>7.0f}/week      "
          f"${stats['top_income']:>7.0f}/week      "
          f"+${income_gap:>6.0f} ({income_gap_pct:>4.0f}%)  "
          f"{stats['top_tertiary']:>6.1f}%")

print("-"*100)

# Detailed comparison
print("\n" + "="*100)
print("DETAILED PERCENTILE COMPARISON BY COUNTRY")
print("="*100)

for country in top_5_countries:
    stats = income_stats[country]
    country_display = country.replace('_', ' ')

    print(f"\n{'='*100}")
    print(f"{country_display.upper()} - TOP 10% vs BOTTOM 10% (by Income)")
    print(f"{'='*100}")
    print(f"Total suburbs: {stats['n_suburbs']} | Bottom 10%: {stats['bottom_10_n']} suburbs | Top 10%: {stats['top_10_n']} suburbs")
    print(f"Income threshold: Bottom ≤ ${stats['p10_threshold']:.0f}/week | Top ≥ ${stats['p90_threshold']:.0f}/week")

    print(f"\n{'Metric':<30} {'Bottom 10%':<20} {'Top 10%':<20} {'Difference':<20}")
    print("-"*90)

    # Income
    income_diff = stats['top_income'] - stats['bottom_income']
    income_diff_pct = (income_diff / stats['bottom_income'] * 100) if stats['bottom_income'] > 0 else 0
    print(f"{'Personal Income ($/week)':<30} ${stats['bottom_income']:<18.0f} ${stats['top_income']:<18.0f} +${income_diff:.0f} ({income_diff_pct:+.0f}%)")

    # Age
    age_diff = stats['top_age'] - stats['bottom_age']
    print(f"{'Median Age (years)':<30} {stats['bottom_age']:<18.1f} {stats['top_age']:<18.1f} {age_diff:+.1f} years")

    # Tertiary Education
    tertiary_diff = stats['top_tertiary'] - stats['bottom_tertiary']
    print(f"{'Tertiary Education (%)':<30} {stats['bottom_tertiary']:<18.1f} {stats['top_tertiary']:<18.1f} {tertiary_diff:+.1f} pp")

    # Unemployment
    unemp_diff = stats['top_unemployment'] - stats['bottom_unemployment']
    print(f"{'Unemployment Rate (%)':<30} {stats['bottom_unemployment']:<18.1f} {stats['top_unemployment']:<18.1f} {unemp_diff:+.1f} pp")

    # Household Size
    hh_diff = stats['top_hh_size'] - stats['bottom_hh_size']
    print(f"{'Household Size (persons)':<30} {stats['bottom_hh_size']:<18.2f} {stats['top_hh_size']:<18.2f} {hh_diff:+.2f}")

    # Example suburbs
    print(f"\n{'Bottom 10% Examples (largest population):':<50}")
    for suburb in stats['bottom_examples'][:3]:
        print(f"  • {suburb}")

    print(f"\n{'Top 10% Examples (largest population):':<50}")
    for suburb in stats['top_examples'][:3]:
        print(f"  • {suburb}")

# Cross-country extremes comparison
print("\n" + "="*100)
print("CROSS-COUNTRY COMPARISON: EXTREMES")
print("="*100)

print("\n1. HIGHEST-INCOME SUBURBS (Top 10% within each country):")
print("-"*100)
income_top_sorted = sorted(income_stats.items(), key=lambda x: x[1]['top_income'], reverse=True)
for i, (country, stats) in enumerate(income_top_sorted, 1):
    country_display = country.replace('_', ' ')
    print(f"  {i}. {country_display:<15} ${stats['top_income']:>7.0f}/week  "
          f"(Age: {stats['top_age']:.1f}, Tertiary: {stats['top_tertiary']:.1f}%, "
          f"Examples: {', '.join(stats['top_examples'][:2])})")

print("\n2. LOWEST-INCOME SUBURBS (Bottom 10% within each country):")
print("-"*100)
income_bottom_sorted = sorted(income_stats.items(), key=lambda x: x[1]['bottom_income'])
for i, (country, stats) in enumerate(income_bottom_sorted, 1):
    country_display = country.replace('_', ' ')
    print(f"  {i}. {country_display:<15} ${stats['bottom_income']:>7.0f}/week  "
          f"(Age: {stats['bottom_age']:.1f}, Tertiary: {stats['bottom_tertiary']:.1f}%, "
          f"Examples: {', '.join(stats['bottom_examples'][:2])})")

# Within-country inequality analysis
print("\n" + "="*100)
print("WITHIN-COUNTRY INEQUALITY ANALYSIS")
print("="*100)

print("\nIncome inequality (Top 10% vs Bottom 10% gap):")
print("-"*100)

inequality_data = []
for country in top_5_countries:
    stats = income_stats[country]
    income_gap = stats['top_income'] - stats['bottom_income']
    income_gap_pct = (income_gap / stats['bottom_income'] * 100) if stats['bottom_income'] > 0 else 0

    inequality_data.append({
        'country': country,
        'gap': income_gap,
        'gap_pct': income_gap_pct,
        'bottom': stats['bottom_income'],
        'top': stats['top_income']
    })

inequality_sorted = sorted(inequality_data, key=lambda x: x['gap_pct'], reverse=True)
for i, item in enumerate(inequality_sorted, 1):
    country_display = item['country'].replace('_', ' ')
    print(f"  {i}. {country_display:<15} Income gap: ${item['gap']:>6.0f}/week ({item['gap_pct']:>5.1f}%)  "
          f"[${item['bottom']:.0f} → ${item['top']:.0f}]")

# Novel findings
print("\n" + "="*100)
print("KEY FINDINGS FROM PERCENTILE ANALYSIS")
print("="*100)

print("\n1. WITHIN-GROUP VARIATION INSIGHTS:")

# Find country with highest variance
max_inequality = inequality_sorted[0]
min_inequality = inequality_sorted[-1]

print(f"\n   Highest inequality: {max_inequality['country'].replace('_', ' ')}")
print(f"   - Income gap between top 10% and bottom 10%: ${max_inequality['gap']:.0f}/week ({max_inequality['gap_pct']:.0f}%)")
print(f"   - This suggests diverse settlement patterns within {max_inequality['country'].replace('_', ' ')} communities")

print(f"\n   Lowest inequality: {min_inequality['country'].replace('_', ' ')}")
print(f"   - Income gap between top 10% and bottom 10%: ${min_inequality['gap']:.0f}/week ({min_inequality['gap_pct']:.0f}%)")
print(f"   - More homogeneous socio-economic outcomes across {min_inequality['country'].replace('_', ' ')} suburbs")

print("\n2. AGE-INCOME RELATIONSHIPS IN EXTREMES:")
for country in top_5_countries:
    stats = income_stats[country]
    age_diff = stats['top_age'] - stats['bottom_age']
    country_display = country.replace('_', ' ')

    if age_diff > 2:
        print(f"   • {country_display}: High-income suburbs are OLDER by {age_diff:.1f} years")
        print(f"     → Suggests wealth accumulation over time")
    elif age_diff < -2:
        print(f"   • {country_display}: High-income suburbs are YOUNGER by {abs(age_diff):.1f} years")
        print(f"     → Suggests high-skilled young professionals")
    else:
        print(f"   • {country_display}: Age is similar across income groups (±{abs(age_diff):.1f} years)")
        print(f"     → Income differences not driven by age/experience")

print("\n3. EDUCATION-INCOME CORRELATION IN EXTREMES:")
for country in top_5_countries:
    stats = income_stats[country]
    tertiary_diff = stats['top_tertiary'] - stats['bottom_tertiary']
    country_display = country.replace('_', ' ')

    print(f"   • {country_display}: Tertiary education gap = {tertiary_diff:+.1f} percentage points")
    if tertiary_diff > 20:
        print(f"     → STRONG education-income link (high-income suburbs much more educated)")
    elif tertiary_diff > 10:
        print(f"     → MODERATE education-income link")
    else:
        print(f"     → WEAK education-income link (income driven by other factors)")

# Save results
print("\n" + "="*100)
print("SAVING PERCENTILE ANALYSIS RESULTS")
print("="*100)

# Create summary DataFrame
summary_data = []
for country in top_5_countries:
    stats = income_stats[country]
    income_gap = stats['top_income'] - stats['bottom_income']
    income_gap_pct = (income_gap / stats['bottom_income'] * 100) if stats['bottom_income'] > 0 else 0

    summary_data.append({
        'Country': country.replace('_', ' '),
        'Total_Suburbs': stats['n_suburbs'],
        'Bottom_10pct_Income': stats['bottom_income'],
        'Bottom_10pct_Age': stats['bottom_age'],
        'Bottom_10pct_Tertiary': stats['bottom_tertiary'],
        'Bottom_10pct_Unemployment': stats['bottom_unemployment'],
        'Top_10pct_Income': stats['top_income'],
        'Top_10pct_Age': stats['top_age'],
        'Top_10pct_Tertiary': stats['top_tertiary'],
        'Top_10pct_Unemployment': stats['top_unemployment'],
        'Income_Gap_Dollars': income_gap,
        'Income_Gap_Percent': income_gap_pct,
        'Age_Difference': stats['top_age'] - stats['bottom_age'],
        'Tertiary_Difference': stats['top_tertiary'] - stats['bottom_tertiary'],
        'Bottom_Examples': '; '.join(stats['bottom_examples'][:3]),
        'Top_Examples': '; '.join(stats['top_examples'][:3])
    })

df_summary = pd.DataFrame(summary_data)
output_file = '/home/user/Census/results_birthplace_percentile_analysis.csv'
df_summary.to_csv(output_file, index=False)
print(f"✓ Saved: {output_file}")

print("\n" + "="*100)
print("ANALYSIS COMPLETE!")
print("="*100)
