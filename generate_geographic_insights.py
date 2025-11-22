#!/usr/bin/env python3
"""
Generate geographic insights and state-level summaries
Maps SA2 codes to readable names and creates state breakdowns
"""

import pandas as pd
import os

print("=" * 100)
print("🗺️  GENERATING GEOGRAPHIC INSIGHTS & STATE-LEVEL SUMMARIES")
print("=" * 100)
print()

# Load main analysis results
OUTPUT_DIR = "industry_clustering_analysis"
FULL_DATA = os.path.join(OUTPUT_DIR, "full_commercial_property_analysis.csv")

print("📊 Loading analysis results...")
df = pd.read_csv(FULL_DATA)
print(f"   ✓ Loaded {len(df):,} SA2 areas")
print()

# ============================================================================
# STATE/TERRITORY CLASSIFICATION
# ============================================================================

print("=" * 100)
print("STATE/TERRITORY CLASSIFICATION")
print("=" * 100)

def classify_state(sa2_code):
    """Classify SA2 code into state/territory based on first digit"""
    code_str = str(sa2_code)

    if code_str.startswith('1'):
        return 'NSW'
    elif code_str.startswith('2'):
        return 'VIC'
    elif code_str.startswith('3'):
        return 'QLD'
    elif code_str.startswith('4'):
        return 'SA'
    elif code_str.startswith('5'):
        return 'WA'
    elif code_str.startswith('6'):
        return 'TAS'
    elif code_str.startswith('7'):
        return 'NT'
    elif code_str.startswith('8'):
        return 'ACT'
    else:
        return 'Unknown'

df['State'] = df['SA2_CODE'].apply(classify_state)

# Count by state
state_counts = df['State'].value_counts().sort_index()
print("\n📍 SA2 Areas by State/Territory:")
for state, count in state_counts.items():
    print(f"   {state}: {count:,} areas")

print()

# ============================================================================
# STATE-LEVEL STATISTICS
# ============================================================================

print("=" * 100)
print("STATE-LEVEL COMMERCIAL PROPERTY STATISTICS")
print("=" * 100)
print()

# Group by state and calculate aggregates
state_stats = df.groupby('State').agg({
    'Total_Population': 'sum',
    'Total_High_Value_Professionals': 'sum',
    'Total_Managers': 'sum',
    'Total_Professionals': 'sum',
    'Total_White_Collar': 'sum',
    'Professional_Density_per_1000': 'mean',
    'Commercial_Opportunity_Score': 'mean',
    'Demand_Gap_Index': 'mean',
    'Is_Employment_Cluster': 'sum',
    'Is_Emerging_Cluster': 'sum'
}).round(2)

# Rename columns for clarity
state_stats.columns = [
    'Total_Population',
    'High_Value_Professionals',
    'Managers',
    'Professionals',
    'White_Collar_Workers',
    'Avg_Professional_Density',
    'Avg_Opportunity_Score',
    'Avg_Demand_Gap_Index',
    'Num_Employment_Clusters',
    'Num_Emerging_Clusters'
]

# Sort by total professionals
state_stats = state_stats.sort_values('High_Value_Professionals', ascending=False)

# Save state statistics
state_stats_file = os.path.join(OUTPUT_DIR, 'state_level_statistics.csv')
state_stats.to_csv(state_stats_file)
print(f"✅ Saved: {state_stats_file}")
print()

# Display state statistics
print("📊 STATE-LEVEL SUMMARY:")
print("-" * 100)
print(state_stats.to_string())
print()

# ============================================================================
# TOP OPPORTUNITIES BY STATE
# ============================================================================

print("=" * 100)
print("TOP 10 COMMERCIAL OPPORTUNITIES BY STATE")
print("=" * 100)
print()

for state in ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'ACT']:
    state_df = df[df['State'] == state].nlargest(10, 'Commercial_Opportunity_Score')

    if len(state_df) > 0:
        print(f"\n🏆 {state} - Top 10 Opportunities:")
        print("-" * 100)

        # Select key columns
        display_cols = [
            'SA2_CODE',
            'Total_Population',
            'Total_High_Value_Professionals',
            'Professional_Density_per_1000',
            'Commercial_Opportunity_Score',
            'Demand_Gap_Index',
            'Is_Employment_Cluster',
            'Is_Emerging_Cluster'
        ]

        state_top = state_df[display_cols].copy()
        state_top.columns = [
            'SA2_Code',
            'Population',
            'Professionals',
            'Prof_Density',
            'Opp_Score',
            'Demand_Gap',
            'Is_Cluster',
            'Is_Emerging'
        ]

        # Save to file
        state_file = os.path.join(OUTPUT_DIR, f'top_opportunities_{state.lower()}.csv')
        state_top.to_csv(state_file, index=False)

        # Display summary
        print(f"   Areas: {len(state_df)}")
        print(f"   Avg Opportunity Score: {state_df['Commercial_Opportunity_Score'].mean():.2f}")
        print(f"   Highest Score: {state_df['Commercial_Opportunity_Score'].max():.2f}")
        print(f"   Total Professionals: {state_df['Total_High_Value_Professionals'].sum():,}")
        print(f"   ✅ Saved: {state_file}")

# ============================================================================
# MARKET SIZE CLASSIFICATION
# ============================================================================

print("\n" + "=" * 100)
print("MARKET SIZE CLASSIFICATION")
print("=" * 100)
print()

def classify_market_size(population):
    """Classify market by population size"""
    if population >= 20000:
        return 'Large (20K+)'
    elif population >= 10000:
        return 'Medium (10-20K)'
    elif population >= 5000:
        return 'Small (5-10K)'
    else:
        return 'Very Small (<5K)'

df['Market_Size'] = df['Total_Population'].apply(classify_market_size)

market_size_stats = df.groupby('Market_Size').agg({
    'SA2_CODE': 'count',
    'Total_Population': 'sum',
    'Total_High_Value_Professionals': 'sum',
    'Commercial_Opportunity_Score': 'mean',
    'Demand_Gap_Index': 'mean'
}).round(2)

market_size_stats.columns = [
    'Num_Areas',
    'Total_Population',
    'Total_Professionals',
    'Avg_Opportunity_Score',
    'Avg_Demand_Gap'
]

print("📊 MARKET SIZE BREAKDOWN:")
print(market_size_stats.to_string())
print()

market_size_file = os.path.join(OUTPUT_DIR, 'market_size_statistics.csv')
market_size_stats.to_csv(market_size_file)
print(f"✅ Saved: {market_size_file}")
print()

# ============================================================================
# PROFESSIONAL DENSITY CLASSIFICATION
# ============================================================================

print("=" * 100)
print("PROFESSIONAL DENSITY CLASSIFICATION")
print("=" * 100)
print()

def classify_density(density):
    """Classify professional density"""
    if density >= 700:
        return 'Exceptional (700+)'
    elif density >= 500:
        return 'Very High (500-699)'
    elif density >= 400:
        return 'High (400-499)'
    elif density >= 300:
        return 'Average (300-399)'
    else:
        return 'Below Average (<300)'

df['Density_Class'] = df['Professional_Density_per_1000'].apply(classify_density)

density_stats = df.groupby('Density_Class').agg({
    'SA2_CODE': 'count',
    'Total_Population': 'sum',
    'Total_High_Value_Professionals': 'sum',
    'Commercial_Opportunity_Score': 'mean',
    'Demand_Gap_Index': 'mean'
}).round(2)

density_stats.columns = [
    'Num_Areas',
    'Total_Population',
    'Total_Professionals',
    'Avg_Opportunity_Score',
    'Avg_Demand_Gap'
]

print("📊 PROFESSIONAL DENSITY BREAKDOWN:")
print(density_stats.to_string())
print()

density_file = os.path.join(OUTPUT_DIR, 'density_classification_statistics.csv')
density_stats.to_csv(density_file)
print(f"✅ Saved: {density_file}")
print()

# ============================================================================
# HIGH-OPPORTUNITY HOTSPOT IDENTIFICATION
# ============================================================================

print("=" * 100)
print("HIGH-OPPORTUNITY HOTSPOTS (Opportunity Score >= 50)")
print("=" * 100)
print()

hotspots = df[df['Commercial_Opportunity_Score'] >= 50].copy()
hotspots = hotspots.sort_values('Commercial_Opportunity_Score', ascending=False)

print(f"🔥 Identified {len(hotspots)} high-opportunity hotspots")
print()

# Breakdown by state
hotspot_states = hotspots['State'].value_counts().sort_index()
print("   Hotspots by State:")
for state, count in hotspot_states.items():
    print(f"      {state}: {count} areas")

print()

# Save hotspots
hotspots_file = os.path.join(OUTPUT_DIR, 'high_opportunity_hotspots.csv')
hotspots[[
    'SA2_CODE',
    'State',
    'Total_Population',
    'Total_High_Value_Professionals',
    'Professional_Density_per_1000',
    'Median_tot_prsnl_inc_weekly',
    'Commercial_Opportunity_Score',
    'Demand_Gap_Index',
    'Is_Employment_Cluster',
    'Is_Emerging_Cluster'
]].to_csv(hotspots_file, index=False)

print(f"✅ Saved: {hotspots_file}")
print()

# ============================================================================
# INVESTMENT PORTFOLIO RECOMMENDATIONS
# ============================================================================

print("=" * 100)
print("INVESTMENT PORTFOLIO RECOMMENDATIONS")
print("=" * 100)
print()

print("💼 PORTFOLIO 1: Conservative (Established Markets)")
print("-" * 100)
conservative = df[
    (df['Is_Employment_Cluster'] == True) &
    (df['Commercial_Opportunity_Score'] >= 45) &
    (df['Total_Population'] >= 10000)
].nlargest(20, 'Commercial_Opportunity_Score')

print(f"   • {len(conservative)} recommended areas")
print(f"   • Avg Opportunity Score: {conservative['Commercial_Opportunity_Score'].mean():.2f}")
print(f"   • Avg Population: {conservative['Total_Population'].mean():,.0f}")
print(f"   • Risk Level: Low-Medium")

conservative_file = os.path.join(OUTPUT_DIR, 'portfolio_conservative.csv')
conservative[['SA2_CODE', 'State', 'Total_Population', 'Commercial_Opportunity_Score', 'Demand_Gap_Index']].to_csv(conservative_file, index=False)
print(f"   ✅ Saved: {conservative_file}")
print()

print("💼 PORTFOLIO 2: Balanced (Mixed Strategy)")
print("-" * 100)
balanced = df[
    (df['Commercial_Opportunity_Score'] >= 45) &
    (df['Demand_Gap_Index'] >= 30) &
    (df['Total_Population'] >= 5000)
].nlargest(20, 'Commercial_Opportunity_Score')

print(f"   • {len(balanced)} recommended areas")
print(f"   • Avg Opportunity Score: {balanced['Commercial_Opportunity_Score'].mean():.2f}")
print(f"   • Avg Demand Gap: {balanced['Demand_Gap_Index'].mean():.2f}")
print(f"   • Risk Level: Medium")

balanced_file = os.path.join(OUTPUT_DIR, 'portfolio_balanced.csv')
balanced[['SA2_CODE', 'State', 'Total_Population', 'Commercial_Opportunity_Score', 'Demand_Gap_Index']].to_csv(balanced_file, index=False)
print(f"   ✅ Saved: {balanced_file}")
print()

print("💼 PORTFOLIO 3: Aggressive (Emerging + High Gap)")
print("-" * 100)
aggressive = df[
    (
        (df['Is_Emerging_Cluster'] == True) |
        ((df['Demand_Gap_Index'] >= 40) & (df['Commercial_Opportunity_Score'] >= 45))
    ) &
    (df['Total_Population'] >= 3000)
].nlargest(20, 'Commercial_Opportunity_Score')

print(f"   • {len(aggressive)} recommended areas")
print(f"   • Avg Opportunity Score: {aggressive['Commercial_Opportunity_Score'].mean():.2f}")
print(f"   • Avg Demand Gap: {aggressive['Demand_Gap_Index'].mean():.2f}")
print(f"   • Emerging Clusters: {aggressive['Is_Emerging_Cluster'].sum()}")
print(f"   • Risk Level: Medium-High")

aggressive_file = os.path.join(OUTPUT_DIR, 'portfolio_aggressive.csv')
aggressive[['SA2_CODE', 'State', 'Total_Population', 'Commercial_Opportunity_Score', 'Demand_Gap_Index', 'Is_Emerging_Cluster']].to_csv(aggressive_file, index=False)
print(f"   ✅ Saved: {aggressive_file}")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 100)
print("✅ GEOGRAPHIC INSIGHTS COMPLETE!")
print("=" * 100)
print()
print("📄 Generated Additional Files:")
print("   1. state_level_statistics.csv")
print("   2. market_size_statistics.csv")
print("   3. density_classification_statistics.csv")
print("   4. high_opportunity_hotspots.csv")
print("   5. top_opportunities_[state].csv (for NSW, VIC, QLD, SA, WA, ACT)")
print("   6. portfolio_conservative.csv")
print("   7. portfolio_balanced.csv")
print("   8. portfolio_aggressive.csv")
print()
print("=" * 100)
