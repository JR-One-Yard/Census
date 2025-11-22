#!/usr/bin/env python3
"""
Advanced Insights Generator
Produces detailed analysis of lifestyle premium data including:
- Coastal vs Inland comparisons
- Metropolitan vs Regional analysis
- State-by-state breakdowns
- Value opportunity identification
"""

import pandas as pd
import numpy as np

# Load the full results
print("="*100)
print("ADVANCED LIFESTYLE PREMIUM INSIGHTS")
print("="*100)

print("\nLoading results...")
df = pd.read_csv('/home/user/Census/lifestyle_premium_outputs/lifestyle_premium_all_sa1s.csv')

# Filter to populated areas
df_pop = df[df['Tot_P_P'] >= 50].copy()

print(f"Total SA1s: {len(df):,}")
print(f"Populated SA1s (pop >= 50): {len(df_pop):,}")

# Add state names
state_names = {
    '1': 'NSW', '2': 'VIC', '3': 'QLD', '4': 'SA',
    '5': 'WA', '6': 'TAS', '7': 'NT', '8': 'ACT'
}
df_pop['state'] = df_pop['SA1_CODE_2021'].astype(str).str[0]
df_pop['state_name'] = df_pop['state'].map(state_names)

# ============================================================================
# INSIGHT 1: Coastal vs Inland Analysis
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 1: COASTAL VS INLAND LIFESTYLE PREMIUM")
print("="*100)

df_pop['is_coastal'] = df_pop['beach_avg_km'] <= 50  # Within 50km of beach
df_pop['is_highly_coastal'] = df_pop['beach_avg_km'] <= 10  # Within 10km

coastal_stats = df_pop.groupby('is_coastal').agg({
    'lifestyle_premium_index': ['mean', 'median'],
    'Median_tot_prsnl_inc_weekly': 'median',
    'Median_age_persons': 'median',
    'school_avg_km': 'mean',
    'hospital_avg_km': 'mean',
    'SA1_CODE_2021': 'count'
}).round(2)

print("\nCoastal vs Inland Comparison:")
print(coastal_stats)

highly_coastal_count = df_pop['is_highly_coastal'].sum()
print(f"\nSA1s within 10km of beach: {highly_coastal_count:,} ({highly_coastal_count/len(df_pop)*100:.1f}%)")

# ============================================================================
# INSIGHT 2: Metropolitan vs Regional
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 2: METROPOLITAN VS REGIONAL ANALYSIS")
print("="*100)

# Define metropolitan as having high density of schools and parks nearby
df_pop['is_metro'] = (
    (df_pop['schools_within_5km'] >= 1) &
    (df_pop['parks_within_5km'] >= 1) &
    (df_pop['hospital_avg_km'] <= 30)
)

metro_stats = df_pop.groupby('is_metro').agg({
    'lifestyle_premium_index': ['mean', 'median', 'max'],
    'Median_tot_prsnl_inc_weekly': ['mean', 'median'],
    'Median_age_persons': 'median',
    'beach_avg_km': 'mean',
    'value_score': 'mean',
    'SA1_CODE_2021': 'count'
}).round(2)

print("\nMetropolitan vs Regional Comparison:")
print(metro_stats)

# ============================================================================
# INSIGHT 3: State-by-State Value Opportunities
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 3: BEST VALUE OPPORTUNITIES BY STATE")
print("="*100)

for state_name in ['NSW', 'VIC', 'QLD', 'WA', 'SA']:
    state_df = df_pop[df_pop['state_name'] == state_name].copy()

    if len(state_df) == 0:
        continue

    # Top 5 value areas in this state
    top_value = state_df.nlargest(5, 'value_score')

    print(f"\n{state_name} - Top 5 Best Value Lifestyle Areas:")
    print(f"{'SA1 Code':<15} {'Lifestyle':<12} {'Income/wk':<12} {'Beach km':<10} {'Schools km':<12}")
    print("-" * 70)

    for idx, row in top_value.iterrows():
        # Filter out areas with 0 income (likely data issues)
        if row['Median_tot_prsnl_inc_weekly'] > 100:
            print(f"{row['SA1_CODE_2021']:<15} "
                  f"{row['lifestyle_premium_index']:>6.1f}/100   "
                  f"${row['Median_tot_prsnl_inc_weekly']:>6.0f}      "
                  f"{row['beach_avg_km']:>6.1f}     "
                  f"{row['school_avg_km']:>6.1f}")

# ============================================================================
# INSIGHT 4: Income vs Lifestyle Correlation
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 4: INCOME VS LIFESTYLE PREMIUM ANALYSIS")
print("="*100)

# Create income brackets
df_pop['income_bracket'] = pd.cut(
    df_pop['Median_tot_prsnl_inc_weekly'],
    bins=[0, 500, 800, 1200, 1600, 10000],
    labels=['<$500', '$500-800', '$800-1200', '$1200-1600', '>$1600']
)

income_lifestyle = df_pop.groupby('income_bracket').agg({
    'lifestyle_premium_index': ['mean', 'median', 'max'],
    'beach_avg_km': 'mean',
    'school_avg_km': 'mean',
    'parks_within_5km': 'mean',
    'SA1_CODE_2021': 'count'
}).round(2)

print("\nLifestyle Premium by Income Bracket:")
print(income_lifestyle)

# ============================================================================
# INSIGHT 5: Hidden Gems - High Lifestyle, Affordable
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 5: HIDDEN GEMS - HIGH LIFESTYLE, AFFORDABLE AREAS")
print("="*100)

# Areas with above-average lifestyle but below-median income
median_income = df_pop['Median_tot_prsnl_inc_weekly'].median()
mean_lifestyle = df_pop['lifestyle_premium_index'].mean()

hidden_gems = df_pop[
    (df_pop['lifestyle_premium_index'] > mean_lifestyle * 1.2) &
    (df_pop['Median_tot_prsnl_inc_weekly'] < median_income) &
    (df_pop['Median_tot_prsnl_inc_weekly'] > 400) &  # Exclude data issues
    (df_pop['Tot_P_P'] >= 200)  # Reasonable population
].nlargest(30, 'lifestyle_premium_index')

print(f"\nFound {len(hidden_gems)} hidden gem areas")
print(f"(Lifestyle > {mean_lifestyle * 1.2:.1f}, Income < ${median_income:.0f}/wk)")
print(f"\nTop 20 Hidden Gems:")
print(f"{'SA1 Code':<15} {'State':<6} {'Lifestyle':<12} {'Income/wk':<12} {'Beach km':<10} {'Pop':<8}")
print("-" * 80)

for idx, row in hidden_gems.head(20).iterrows():
    print(f"{row['SA1_CODE_2021']:<15} "
          f"{row['state_name']:<6} "
          f"{row['lifestyle_premium_index']:>6.1f}/100   "
          f"${row['Median_tot_prsnl_inc_weekly']:>6.0f}      "
          f"{row['beach_avg_km']:>6.1f}     "
          f"{row['Tot_P_P']:>5.0f}")

# Save hidden gems
hidden_gems.to_csv('/home/user/Census/lifestyle_premium_outputs/hidden_gem_areas.csv', index=False)
print(f"\n✓ Saved hidden gems to: lifestyle_premium_outputs/hidden_gem_areas.csv")

# ============================================================================
# INSIGHT 6: School Quality Demand Hotspots
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 6: SCHOOL QUALITY DEMAND HOTSPOTS")
print("="*100)

school_demand = df_pop.nlargest(20, 'school_demand_index')

print("\nTop 20 SA1s by School Quality Demand:")
print(f"{'SA1 Code':<15} {'State':<6} {'Demand Index':<15} {'Education':<12} {'Families':<10}")
print("-" * 75)

for idx, row in school_demand.iterrows():
    print(f"{row['SA1_CODE_2021']:<15} "
          f"{row['state_name']:<6} "
          f"{row['school_demand_index']:>8.1f}/100     "
          f"{row['Year12_Total']:>6.0f}       "
          f"{row['Families_with_children']:>6.0f}")

# ============================================================================
# INSIGHT 7: Lifestyle Premium by Age Demographics
# ============================================================================

print("\n" + "="*100)
print("INSIGHT 7: LIFESTYLE PREMIUM BY AGE DEMOGRAPHICS")
print("="*100)

df_pop['age_bracket'] = pd.cut(
    df_pop['Median_age_persons'],
    bins=[0, 30, 40, 50, 60, 100],
    labels=['<30', '30-40', '40-50', '50-60', '60+']
)

age_lifestyle = df_pop.groupby('age_bracket').agg({
    'lifestyle_premium_index': ['mean', 'median'],
    'Median_tot_prsnl_inc_weekly': 'median',
    'beach_avg_km': 'mean',
    'school_avg_km': 'mean',
    'value_score': 'mean',
    'SA1_CODE_2021': 'count'
}).round(2)

print("\nLifestyle Premium by Age Bracket:")
print(age_lifestyle)

# ============================================================================
# SUMMARY EXPORT
# ============================================================================

print("\n" + "="*100)
print("GENERATING SUMMARY EXPORTS")
print("="*100)

# Coastal areas
coastal_areas = df_pop[df_pop['is_highly_coastal']].nlargest(100, 'lifestyle_premium_index')
coastal_areas.to_csv('/home/user/Census/lifestyle_premium_outputs/top_100_coastal_areas.csv', index=False)
print("✓ Saved top 100 coastal areas")

# Regional gems (non-metro, high lifestyle)
regional_gems = df_pop[~df_pop['is_metro']].nlargest(100, 'lifestyle_premium_index')
regional_gems.to_csv('/home/user/Census/lifestyle_premium_outputs/top_100_regional_lifestyle.csv', index=False)
print("✓ Saved top 100 regional lifestyle areas")

# Metro value areas
metro_value = df_pop[df_pop['is_metro']].nlargest(100, 'value_score')
metro_value.to_csv('/home/user/Census/lifestyle_premium_outputs/top_100_metro_value.csv', index=False)
print("✓ Saved top 100 metro value areas")

# Statistical summary
summary_stats = pd.DataFrame({
    'Metric': [
        'Total SA1s Analyzed',
        'Populated SA1s (pop >= 50)',
        'Coastal SA1s (<50km from beach)',
        'Highly Coastal (<10km from beach)',
        'Metropolitan SA1s',
        'Mean Lifestyle Premium Index',
        'Median Lifestyle Premium Index',
        'Mean Income ($/week)',
        'Median Income ($/week)',
        'Mean Beach Distance (km)',
        'Mean School Distance (km)',
    ],
    'Value': [
        len(df),
        len(df_pop),
        df_pop['is_coastal'].sum(),
        df_pop['is_highly_coastal'].sum(),
        df_pop['is_metro'].sum(),
        round(df_pop['lifestyle_premium_index'].mean(), 2),
        round(df_pop['lifestyle_premium_index'].median(), 2),
        round(df_pop['Median_tot_prsnl_inc_weekly'].mean(), 2),
        round(df_pop['Median_tot_prsnl_inc_weekly'].median(), 2),
        round(df_pop['beach_avg_km'].mean(), 2),
        round(df_pop['school_avg_km'].mean(), 2),
    ]
})

summary_stats.to_csv('/home/user/Census/lifestyle_premium_outputs/summary_statistics.csv', index=False)
print("✓ Saved summary statistics")

print("\n" + "="*100)
print("ADVANCED INSIGHTS COMPLETE!")
print("="*100)
print("\nAll insights saved to: /home/user/Census/lifestyle_premium_outputs/")
