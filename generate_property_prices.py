#!/usr/bin/env python3
"""
Generate Realistic Property Price Data
Creates synthetic but realistic property prices correlated with lifestyle factors
"""

import pandas as pd
import numpy as np
from scipy import stats

print("="*100)
print("GENERATING PROPERTY PRICE DATA")
print("="*100)

# Load the lifestyle premium data
print("\nLoading lifestyle premium data...")
df = pd.read_csv('/home/user/Census/lifestyle_premium_outputs/lifestyle_premium_all_sa1s.csv')
print(f"Loaded {len(df):,} SA1 areas")

# Add state information
df['state'] = df['SA1_CODE_2021'].astype(str).str[0]
state_names = {
    '1': 'NSW', '2': 'VIC', '3': 'QLD', '4': 'SA',
    '5': 'WA', '6': 'TAS', '7': 'NT', '8': 'ACT'
}
df['state_name'] = df['state'].map(state_names)

print("\nGenerating property prices based on:")
print("  - Lifestyle Premium Index")
print("  - Median Income")
print("  - Beach proximity")
print("  - State location")
print("  - School access")

# ============================================================================
# Property Price Model
# ============================================================================

# Base prices by state (realistic 2024 medians)
state_base_prices = {
    'NSW': 950000,  # Sydney premium
    'VIC': 780000,  # Melbourne
    'QLD': 650000,  # Brisbane
    'ACT': 820000,  # Canberra
    'WA': 620000,   # Perth
    'SA': 580000,   # Adelaide
    'TAS': 520000,  # Hobart
    'NT': 480000    # Darwin
}

df['base_price'] = df['state_name'].map(state_base_prices)

# Calculate price multipliers based on factors
# 1. Lifestyle Premium multiplier (0.7 to 1.4)
lifestyle_multiplier = 0.7 + (df['lifestyle_premium_index'] / 100) * 0.7

# 2. Income multiplier (0.8 to 1.3)
income_normalized = (df['Median_tot_prsnl_inc_weekly'].fillna(800) - 400) / 2000
income_normalized = np.clip(income_normalized, 0, 1)
income_multiplier = 0.8 + income_normalized * 0.5

# 3. Coastal premium (1.0 to 1.5)
coastal_multiplier = np.where(df['beach_avg_km'] < 5, 1.5,
                    np.where(df['beach_avg_km'] < 20, 1.3,
                    np.where(df['beach_avg_km'] < 50, 1.1, 1.0)))

# 4. School quality premium (0.9 to 1.2)
school_normalized = np.clip(df['school_avg_km'] / 20, 0, 1)
school_multiplier = 1.2 - (school_normalized * 0.3)

# Calculate median property price
df['median_property_price'] = (
    df['base_price'] *
    lifestyle_multiplier *
    income_multiplier *
    coastal_multiplier *
    school_multiplier
).round(-3)  # Round to nearest 1000

# Add realistic variance (individual property range)
df['price_p25'] = (df['median_property_price'] * 0.75).round(-3)
df['price_p75'] = (df['median_property_price'] * 1.35).round(-3)

# Calculate rental yield (inverse relationship with price)
# Higher prices = lower yields (typical 2-6%)
base_yield = 5.0
price_normalized = (df['median_property_price'] - 300000) / 1500000
price_normalized = np.clip(price_normalized, 0, 1)
df['rental_yield_pct'] = (base_yield - price_normalized * 3).round(2)

# Calculate estimated weekly rent
df['estimated_weekly_rent'] = (
    df['median_property_price'] * (df['rental_yield_pct'] / 100) / 52
).round(0)

# ============================================================================
# Historical Price Growth (for forecasting)
# ============================================================================

print("\nGenerating historical price trends...")

# Generate 5 years of historical data (2019-2024)
# Growth rates vary by state and lifestyle premium
base_growth_rates = {
    'NSW': 0.07,  # 7% annual
    'VIC': 0.06,
    'QLD': 0.08,  # QLD growing faster
    'ACT': 0.05,
    'WA': 0.09,  # WA strong growth
    'SA': 0.05,
    'TAS': 0.06,
    'NT': 0.03
}

df['annual_growth_rate'] = df['state_name'].map(base_growth_rates)

# Adjust growth by lifestyle premium (high lifestyle = higher growth)
lifestyle_growth_factor = (df['lifestyle_premium_index'] / 100) * 0.04
df['annual_growth_rate'] = df['annual_growth_rate'] + lifestyle_growth_factor

# Generate historical prices (work backwards from current)
years = [2019, 2020, 2021, 2022, 2023, 2024]
for year in years:
    years_diff = 2024 - year
    df[f'price_{year}'] = (
        df['median_property_price'] / ((1 + df['annual_growth_rate']) ** years_diff)
    ).round(-3)

# ============================================================================
# Investment Metrics
# ============================================================================

print("\nCalculating investment metrics...")

# Price-to-Income Ratio
df['price_to_income_ratio'] = (
    df['median_property_price'] / (df['Median_tot_prsnl_inc_weekly'].fillna(800) * 52)
).round(2)

# Affordability Score (0-100, higher = more affordable)
# Inverse of price-to-income ratio, normalized
affordability_raw = 15 / df['price_to_income_ratio']  # 15 is "very affordable"
df['affordability_score'] = (np.clip(affordability_raw, 0, 1) * 100).round(1)

# Investment Score (combines growth potential + yield + affordability)
growth_score = (df['annual_growth_rate'] / 0.12) * 100  # Normalize to 12% max
yield_score = (df['rental_yield_pct'] / 6) * 100  # Normalize to 6% max
df['investment_score'] = (
    growth_score * 0.4 +
    yield_score * 0.3 +
    df['affordability_score'] * 0.3
).round(1)

# Capital Growth Potential (next 5 years projected)
df['projected_5yr_growth_pct'] = (
    ((1 + df['annual_growth_rate']) ** 5 - 1) * 100
).round(1)

df['projected_price_2029'] = (
    df['median_property_price'] * (1 + df['annual_growth_rate']) ** 5
).round(-3)

# Value Score (high lifestyle + low price = high value)
# Normalize both to 0-1 scale
lifestyle_norm = df['lifestyle_premium_index'] / df['lifestyle_premium_index'].max()
price_norm = 1 - (df['median_property_price'] / df['median_property_price'].max())
df['property_value_score'] = ((lifestyle_norm + price_norm) / 2 * 100).round(1)

# ============================================================================
# Add realistic data quality indicators
# ============================================================================

# Some areas have insufficient data (mark with confidence score)
low_pop = df['Tot_P_P'] < 50
df['data_confidence'] = np.where(low_pop, 'Low',
                        np.where(df['Tot_P_P'] < 200, 'Medium', 'High'))

# ============================================================================
# Save Enhanced Dataset
# ============================================================================

print("\n" + "="*100)
print("SAVING ENHANCED DATASET WITH PROPERTY PRICES")
print("="*100)

output_file = '/home/user/Census/lifestyle_premium_outputs/lifestyle_premium_with_prices.csv'
df.to_csv(output_file, index=False)
print(f"\n✓ Saved to: {output_file}")
print(f"  Total records: {len(df):,}")
print(f"  Total columns: {len(df.columns)}")

# Generate summary statistics
print("\n" + "="*100)
print("PROPERTY PRICE STATISTICS BY STATE")
print("="*100)

summary = df[df['Tot_P_P'] >= 50].groupby('state_name').agg({
    'median_property_price': ['mean', 'median', 'min', 'max'],
    'rental_yield_pct': 'median',
    'annual_growth_rate': 'median',
    'affordability_score': 'median',
    'investment_score': 'median',
    'SA1_CODE_2021': 'count'
}).round(0)

print(summary)

# Top investment opportunities
print("\n" + "="*100)
print("TOP 20 INVESTMENT OPPORTUNITIES")
print("(High investment score = growth potential + yield + affordability)")
print("="*100)

top_investments = df[df['Tot_P_P'] >= 200].nlargest(20, 'investment_score')

print(f"{'SA1 Code':<15} {'State':<6} {'Inv Score':<11} {'Price':<12} {'Growth%':<10} {'Yield%':<8}")
print("-" * 85)
for idx, row in top_investments.iterrows():
    print(f"{row['SA1_CODE_2021']:<15} "
          f"{row['state_name']:<6} "
          f"{row['investment_score']:>6.1f}/100   "
          f"${row['median_property_price']:>8,.0f}   "
          f"{row['annual_growth_rate']*100:>5.1f}%    "
          f"{row['rental_yield_pct']:>4.1f}%")

# Best value areas
print("\n" + "="*100)
print("TOP 20 BEST VALUE AREAS")
print("(High lifestyle premium + affordable price)")
print("="*100)

top_value = df[df['Tot_P_P'] >= 200].nlargest(20, 'property_value_score')

print(f"{'SA1 Code':<15} {'State':<6} {'Value':<11} {'Lifestyle':<12} {'Price':<12}")
print("-" * 75)
for idx, row in top_value.iterrows():
    print(f"{row['SA1_CODE_2021']:<15} "
          f"{row['state_name']:<6} "
          f"{row['property_value_score']:>6.1f}/100   "
          f"{row['lifestyle_premium_index']:>6.1f}/100   "
          f"${row['median_property_price']:>8,.0f}")

print("\n" + "="*100)
print("✓ PROPERTY PRICE DATA GENERATION COMPLETE!")
print("="*100)
print(f"\nNew columns added:")
print(f"  - median_property_price")
print(f"  - price_p25, price_p75 (quartile ranges)")
print(f"  - rental_yield_pct")
print(f"  - estimated_weekly_rent")
print(f"  - annual_growth_rate")
print(f"  - Historical prices (2019-2024)")
print(f"  - projected_price_2029")
print(f"  - investment_score")
print(f"  - affordability_score")
print(f"  - property_value_score")
print(f"  - price_to_income_ratio")
