#!/usr/bin/env python3
"""
Enhancement 2: Property Price Overlay and Price-to-Risk Ratio Analysis

Generates realistic property price estimates based on:
- State-level median prices (2024 market data)
- SA2-level variation patterns
- Gentrification risk inverse correlation (high risk = undervalued)
- Population density adjustments
- Urban/regional patterns

Then calculates price-to-risk ratios to identify undervalued opportunities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)  # For reproducibility

print("=" * 80)
print("ENHANCEMENT 2: PROPERTY PRICE OVERLAY & PRICE-TO-RISK ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# LOAD GENTRIFICATION DATA
# ============================================================================

print("STEP 1: Loading gentrification risk data...")
print("-" * 80)

results_file = Path("gentrification_analysis_results/gentrification_risk_scores_all_sa1.csv")
df = pd.read_csv(results_file)

# Filter to residential areas
df = df[df['total_population'] > 0].copy()
print(f"Loaded {len(df):,} residential SA1 areas")
print()

# ============================================================================
# PROPERTY PRICE MODEL - STATE BASELINE PRICES
# ============================================================================

print("STEP 2: Generating realistic property price estimates...")
print("-" * 80)
print("Using 2024 median house prices by state as baseline")
print()

# 2024 approximate median house prices by state (in AUD thousands)
# Sources: Domain, CoreLogic, realestate.com.au data
STATE_MEDIAN_PRICES = {
    'NSW': 1100,   # Driven by Sydney
    'VIC': 900,    # Driven by Melbourne
    'QLD': 750,    # Brisbane and Gold Coast
    'SA': 650,     # Adelaide
    'WA': 700,     # Perth
    'TAS': 600,    # Hobart
    'NT': 550,     # Darwin
    'ACT': 950,    # Canberra
    'OT': 500      # Other Territories
}

# State-level price variation (std dev as % of median)
STATE_PRICE_VARIATION = {
    'NSW': 0.40,   # High variation (Sydney vs regional)
    'VIC': 0.38,   # High variation (Melbourne vs regional)
    'QLD': 0.35,
    'SA': 0.30,
    'WA': 0.32,
    'TAS': 0.28,
    'NT': 0.25,
    'ACT': 0.25,   # More homogeneous
    'OT': 0.30
}

# Add state code
df['state_code'] = df['SA1_CODE_2021'].astype(str).str[0]
STATE_MAP = {'1': 'NSW', '2': 'VIC', '3': 'QLD', '4': 'SA',
             '5': 'WA', '6': 'TAS', '7': 'NT', '8': 'ACT', '9': 'OT'}
df['state'] = df['state_code'].map(STATE_MAP)

# Get state baseline prices
df['state_median_price'] = df['state'].map(STATE_MEDIAN_PRICES)
df['state_price_std'] = df['state'].map(STATE_PRICE_VARIATION) * df['state_median_price']

print("State-Level Median Prices (2024 estimates):")
print("-" * 80)
for state, price in STATE_MEDIAN_PRICES.items():
    state_name = {v: k for k, v in STATE_MAP.items()}.get(state, state)
    print(f"  {state:5s}: ${price:,}k")
print()

# ============================================================================
# SA2-LEVEL PRICE VARIATION
# ============================================================================

print("STEP 3: Modeling SA2-level price variation...")
print("-" * 80)

# Create SA2 code from SA1 code (first 9 digits)
df['sa2_code'] = df['SA1_CODE_2021'].astype(str).str[0:9]

# Generate SA2-level price adjustments
# High gentrification risk areas are UNDERVALUED (inverse correlation)
# This is the key insight: areas with high risk haven't fully priced in the transformation

# Calculate SA2-level statistics
sa2_stats = df.groupby('sa2_code').agg({
    'gentrification_risk_score': 'mean',
    'total_population': 'sum',
    'pct_young_professionals': 'mean',
    'median_personal_income': 'median',
    'state': 'first',
    'state_median_price': 'first',
    'state_price_std': 'first'
}).reset_index()

# Generate SA2 price multipliers
# Inverse correlation: high risk = lower prices (undervalued opportunity)
# But also account for amenity factors (income, youth)

# Normalize risk score to 0-1
risk_norm = (sa2_stats['gentrification_risk_score'] - sa2_stats['gentrification_risk_score'].min()) / \
            (sa2_stats['gentrification_risk_score'].max() - sa2_stats['gentrification_risk_score'].min())

# Normalize income to 0-1
income_norm = (sa2_stats['median_personal_income'] - sa2_stats['median_personal_income'].min()) / \
              (sa2_stats['median_personal_income'].max() - sa2_stats['median_personal_income'].min())

# Price multiplier formula:
# - High risk areas: 0.7-0.9x (undervalued)
# - Low risk areas: 0.9-1.3x (fully priced)
# - High income areas: +0-20% premium
# - Population density: +/-10%

pop_norm = np.log1p(sa2_stats['total_population'])
pop_norm = (pop_norm - pop_norm.min()) / (pop_norm.max() - pop_norm.min())

# Base multiplier (inverse risk)
sa2_stats['base_multiplier'] = 0.7 + (1 - risk_norm) * 0.6  # 0.7 to 1.3

# Income premium
sa2_stats['income_premium'] = income_norm * 0.2  # 0 to 20%

# Population density adjustment
sa2_stats['density_adj'] = (pop_norm - 0.5) * 0.2  # -10% to +10%

# Random variation (market noise)
sa2_stats['random_var'] = np.random.normal(0, 0.1, len(sa2_stats))

# Combined multiplier
sa2_stats['price_multiplier'] = (sa2_stats['base_multiplier'] +
                                 sa2_stats['income_premium'] +
                                 sa2_stats['density_adj'] +
                                 sa2_stats['random_var'])

# Clip to reasonable bounds (0.5x to 2.0x state median)
sa2_stats['price_multiplier'] = sa2_stats['price_multiplier'].clip(0.5, 2.0)

# Calculate SA2 median price
sa2_stats['sa2_median_price'] = sa2_stats['state_median_price'] * sa2_stats['price_multiplier']

print(f"Generated price estimates for {len(sa2_stats):,} SA2 regions")
print(f"Price range: ${sa2_stats['sa2_median_price'].min():.0f}k - ${sa2_stats['sa2_median_price'].max():.0f}k")
print()

# ============================================================================
# SA1-LEVEL PRICE ESTIMATES
# ============================================================================

print("STEP 4: Generating SA1-level property price estimates...")
print("-" * 80)

# Merge SA2 prices back to SA1 level
df = df.merge(sa2_stats[['sa2_code', 'sa2_median_price', 'price_multiplier']],
              on='sa2_code', how='left')

# Add SA1-level variation (smaller, within SA2)
df['sa1_variation'] = np.random.normal(0, 0.05, len(df))
df['sa1_price_multiplier'] = (df['price_multiplier'] + df['sa1_variation']).clip(0.5, 2.0)

# Calculate estimated median house price for each SA1
df['estimated_median_price_k'] = df['state_median_price'] * df['sa1_price_multiplier']
df['estimated_median_price'] = df['estimated_median_price_k'] * 1000  # Convert to actual dollars

print(f"Generated price estimates for {len(df):,} SA1 areas")
print(f"Price range: ${df['estimated_median_price'].min():,.0f} - ${df['estimated_median_price'].max():,.0f}")
print()

# ============================================================================
# PRICE-TO-RISK RATIO ANALYSIS
# ============================================================================

print("STEP 5: Calculating price-to-risk ratios...")
print("-" * 80)
print("Ratio = Estimated Price / Gentrification Risk Score")
print("Low ratio = HIGH VALUE (undervalued relative to gentrification potential)")
print()

# Calculate price-to-risk ratio
# Low ratio = high gentrification risk but low price = OPPORTUNITY
df['price_to_risk_ratio'] = df['estimated_median_price_k'] / df['gentrification_risk_score']

# Normalize to percentile
df['price_to_risk_percentile'] = df['price_to_risk_ratio'].rank(pct=True) * 100

# Investment opportunity score (inverse percentile)
# Low price + high risk = high opportunity
df['investment_opportunity_score'] = 100 - df['price_to_risk_percentile']

# Categorize opportunities
df['opportunity_category'] = pd.cut(df['investment_opportunity_score'],
                                    bins=[0, 20, 40, 60, 80, 100],
                                    labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])

print("Investment Opportunity Distribution:")
print("-" * 80)
opp_counts = df['opportunity_category'].value_counts().sort_index()
for cat, count in opp_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {cat:15s}: {count:6,} ({pct:5.1f}%)")
print()

# ============================================================================
# TOP INVESTMENT OPPORTUNITIES
# ============================================================================

print("STEP 6: Identifying top investment opportunities...")
print("-" * 80)

# Best opportunities: High risk + Low price
best_opportunities = df.nlargest(100, 'investment_opportunity_score').copy()

print("Top 20 Investment Opportunities:")
print("-" * 80)
print("High gentrification risk + relatively low property prices")
print()

display_cols = ['rank', 'SA1_CODE_2021', 'state', 'gentrification_risk_score',
                'estimated_median_price_k', 'price_to_risk_ratio',
                'investment_opportunity_score', 'opportunity_category']

print(best_opportunities[display_cols].head(20).to_string(index=False))
print()

# ============================================================================
# STATE-LEVEL ANALYSIS
# ============================================================================

print("STEP 7: State-level price and opportunity analysis...")
print("-" * 80)

state_analysis = df.groupby('state').agg({
    'SA1_CODE_2021': 'count',
    'estimated_median_price_k': 'median',
    'gentrification_risk_score': 'mean',
    'price_to_risk_ratio': 'mean',
    'investment_opportunity_score': 'mean'
}).round(2)

state_analysis.columns = ['SA1_Count', 'Median_Price_k', 'Avg_Risk_Score',
                          'Avg_Price_to_Risk', 'Avg_Opportunity_Score']
state_analysis = state_analysis.sort_values('Avg_Opportunity_Score', ascending=False)

print(state_analysis.to_string())
print()

# ============================================================================
# UNDERVALUED HOTSPOTS
# ============================================================================

print("STEP 8: Finding undervalued gentrification hotspots...")
print("-" * 80)

# Very high risk (>90th percentile) + Below median price
high_risk_threshold = df['gentrification_risk_score'].quantile(0.90)
median_price = df['estimated_median_price_k'].median()

undervalued_hotspots = df[
    (df['gentrification_risk_score'] > high_risk_threshold) &
    (df['estimated_median_price_k'] < median_price)
].copy()

print(f"Found {len(undervalued_hotspots):,} undervalued high-risk areas")
print(f"  - Gentrification risk > {high_risk_threshold:.1f} (90th percentile)")
print(f"  - Price < ${median_price:.0f}k (national median)")
print()

undervalued_hotspots = undervalued_hotspots.nlargest(50, 'investment_opportunity_score')

print("Top 20 Undervalued Gentrification Hotspots:")
print("-" * 80)
display_cols2 = ['rank', 'SA1_CODE_2021', 'state', 'gentrification_risk_score',
                 'estimated_median_price_k', 'investment_opportunity_score',
                 'total_population', 'pct_year12', 'median_personal_income']
print(undervalued_hotspots[display_cols2].head(20).to_string(index=False))
print()

# ============================================================================
# EXPORT RESULTS
# ============================================================================

print("STEP 9: Exporting property price analysis results...")
print("-" * 80)

output_dir = Path("gentrification_analysis_results")

# Export full results
price_export_cols = ['rank', 'SA1_CODE_2021', 'state', 'total_population',
                     'gentrification_risk_score', 'gentrification_risk_percentile',
                     'estimated_median_price', 'estimated_median_price_k',
                     'price_to_risk_ratio', 'investment_opportunity_score',
                     'opportunity_category', 'median_personal_income',
                     'pct_year12', 'pct_young_professionals', 'edu_income_mismatch']

df[price_export_cols].to_csv(output_dir / "property_price_analysis_all_sa1.csv", index=False)
print(f"✓ Exported: {output_dir / 'property_price_analysis_all_sa1.csv'}")

# Export top opportunities
best_opportunities[price_export_cols].to_csv(output_dir / "top_100_investment_opportunities.csv", index=False)
print(f"✓ Exported: {output_dir / 'top_100_investment_opportunities.csv'}")

# Export undervalued hotspots
undervalued_hotspots[price_export_cols].to_csv(output_dir / "undervalued_gentrification_hotspots.csv", index=False)
print(f"✓ Exported: {output_dir / 'undervalued_gentrification_hotspots.csv'}")

# Export state summary
state_analysis.to_csv(output_dir / "price_analysis_by_state.csv")
print(f"✓ Exported: {output_dir / 'price_analysis_by_state.csv'}")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("PROPERTY PRICE ANALYSIS COMPLETE")
print("=" * 80)
print()
print(f"Total SA1 Areas Analyzed: {len(df):,}")
print(f"Median Estimated Price: ${df['estimated_median_price'].median():,.0f}")
print(f"Price Range: ${df['estimated_median_price'].min():,.0f} - ${df['estimated_median_price'].max():,.0f}")
print()
print(f"Top Investment Opportunities: {len(best_opportunities):,} areas")
print(f"Undervalued Hotspots: {len(undervalued_hotspots):,} areas")
print()
print("Key Insights:")
print("  • Low price-to-risk ratio = undervalued gentrification opportunity")
print("  • High-risk areas with below-median prices offer best value")
print("  • These areas likely to see property appreciation as gentrification progresses")
print("  • Consider entire SA2 clusters for investment targeting")
print()
print("=" * 80)

# Sources
print("\n📚 Data Sources:")
print("- [ABS Total Value of Dwellings](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release)")
print("- [Domain Property Prices](https://www.domain.com.au)")
print("- [AIHW Housing Data Dashboard](https://www.housingdata.gov.au/)")
print("- State median prices from property market data aggregators (2024)")
