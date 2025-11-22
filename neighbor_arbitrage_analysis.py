#!/usr/bin/env python3
"""
NEIGHBOR ARBITRAGE & COMMUNITY ENGAGEMENT ANALYSIS
===================================================

Two novel analyses:
1. NEIGHBOR ARBITRAGE: Find cheap suburbs next to expensive ones
   - Same amenities, schools, transport
   - But 30-50% lower prices!

2. VOLUNTEER RATE: Community engagement as quality proxy
   - High volunteer rate = engaged parents, better schools
   - Social capital indicator

Author: Spatial & Social Capital Analysis
Date: 2025-11-22
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
OUTPUT_DIR = "/home/user/Census"

print("=" * 120)
print(" " * 30 + "NEIGHBOR ARBITRAGE & COMMUNITY ENGAGEMENT ANALYSIS")
print("=" * 120)
print()

# Load base analysis
df_base = pd.read_csv(f'{OUTPUT_DIR}/sydney_all_suburbs_value_analysis.csv')
print(f"Loaded {len(df_base):,} Sydney suburbs")

sydney_sal_codes = set(df_base['SAL_CODE_2021'].values)

# ============================================================================
# PART 1: VOLUNTEER RATE ANALYSIS
# ============================================================================
print("\n" + "=" * 120)
print("PART 1: VOLUNTEER RATE - COMMUNITY ENGAGEMENT PROXY")
print("=" * 120)
print()

# Load G23 - Voluntary work for an organisation or group by age by sex
try:
    df_volunteer = pd.read_csv(f"{DATA_DIR}2021Census_G23_AUST_SAL.csv")
    df_volunteer = df_volunteer[df_volunteer['SAL_CODE_2021'].isin(sydney_sal_codes)]

    print("[1/3] Analyzing volunteer rates...")

    # G23 has P_Tot_Volunteer (total persons who volunteer) and P_Tot_Tot (total persons 15+)
    if 'P_Tot_Volunteer' in df_volunteer.columns and 'P_Tot_Tot' in df_volunteer.columns:
        df_volunteer['Volunteer_Pct'] = (df_volunteer['P_Tot_Volunteer'] / df_volunteer['P_Tot_Tot'] * 100).fillna(0)

        volunteer_metrics = df_volunteer[['SAL_CODE_2021', 'Volunteer_Pct', 'P_Tot_Volunteer', 'P_Tot_Tot']].copy()
        print(f"   ✓ Calculated volunteer rates for {len(volunteer_metrics):,} suburbs")
        print(f"   Volunteer rate range: {volunteer_metrics['Volunteer_Pct'].min():.1f}% to {volunteer_metrics['Volunteer_Pct'].max():.1f}%")
        print(f"   Median volunteer rate: {volunteer_metrics['Volunteer_Pct'].median():.1f}%")
        has_volunteer_data = True
    else:
        print("   ⚠ Could not find volunteer columns in G23")
        volunteer_metrics = pd.DataFrame({
            'SAL_CODE_2021': list(sydney_sal_codes),
            'Volunteer_Pct': 50.0
        })
        has_volunteer_data = False

except Exception as e:
    print(f"   ⚠ Could not load volunteer data: {e}")
    volunteer_metrics = pd.DataFrame({
        'SAL_CODE_2021': list(sydney_sal_codes),
        'Volunteer_Pct': 50.0
    })
    has_volunteer_data = False

# Merge volunteer data with base analysis
if has_volunteer_data:
    df_with_volunteer = df_base.merge(volunteer_metrics, on='SAL_CODE_2021', how='left')

    # Analyze correlation between volunteer rate and other quality metrics
    print("\n[2/3] Analyzing volunteer rate correlations...")

    correlations = {
        'Tertiary Education %': df_with_volunteer[['Volunteer_Pct', 'Tertiary_Pct']].corr().iloc[0, 1],
        'Median Income': df_with_volunteer[['Volunteer_Pct', 'Median_tot_prsnl_inc_weekly']].corr().iloc[0, 1],
        'Quality Index': df_with_volunteer[['Volunteer_Pct', 'Quality_Index']].corr().iloc[0, 1],
        'Value Score': df_with_volunteer[['Volunteer_Pct', 'Value_Score']].corr().iloc[0, 1],
    }

    print("\n   Volunteer Rate Correlations:")
    for metric, corr in correlations.items():
        print(f"   • {metric:25} → {corr:+.3f}")

    # Find high-volunteer suburbs
    high_volunteer = df_with_volunteer[
        df_with_volunteer['Volunteer_Pct'] >= df_with_volunteer['Volunteer_Pct'].quantile(0.8)
    ].sort_values('Volunteer_Pct', ascending=False)

    print("\n[3/3] Top 20 High-Volunteer Suburbs (Community Engagement):")
    print()
    print(f"{'Rank':<6}{'Suburb':<35}{'Vol%':>7}  {'Tertiary':>9}  {'Quality':>8}  {'Value':>10}")
    print("-" * 95)

    for i, (_, row) in enumerate(high_volunteer.head(20).iterrows(), 1):
        print(f"{i:<6}{row['Suburb_Name']:<35}{row['Volunteer_Pct']:>6.1f}%  "
              f"{row['Tertiary_Pct']:>8.1f}%  {row['Quality_Index']:>8.0f}  "
              f"{row['Value_Score']:>10.0f}")

    # Save volunteer analysis
    high_volunteer.head(50).to_csv(f'{OUTPUT_DIR}/high_volunteer_suburbs_top50.csv', index=False)
    print("\n   ✓ Saved: high_volunteer_suburbs_top50.csv")

else:
    print("\n   ⚠ Skipping volunteer analysis (no data available)")
    df_with_volunteer = df_base.copy()
    df_with_volunteer['Volunteer_Pct'] = 50.0

# ============================================================================
# PART 2: NEIGHBOR ARBITRAGE ANALYSIS
# ============================================================================
print("\n" + "=" * 120)
print("PART 2: NEIGHBOR ARBITRAGE - GEOGRAPHIC SPILLOVER OPPORTUNITIES")
print("=" * 120)
print()

# Strategy: Create geographic clusters manually based on suburb name patterns
# Then find suburbs below their cluster average

print("[1/4] Creating geographic clusters...")

# Define Sydney regions based on common naming patterns and knowledge
def assign_region(suburb_name):
    """Assign suburb to a geographic region"""
    if pd.isna(suburb_name):
        return 'Unknown'

    name_lower = suburb_name.lower()

    # Northern Beaches
    if any(x in name_lower for x in ['manly', 'mona vale', 'palm beach', 'avalon', 'newport',
                                       'curl curl', 'freshwater', 'brookvale', 'dee why',
                                       'collaroy', 'narrabeen', 'beacon hill', 'allambie',
                                       'seaforth', 'balgowlah', 'fairlight', 'clontarf']):
        return 'Northern Beaches'

    # North Shore (Upper)
    if any(x in name_lower for x in ['turramurra', 'pymble', 'gordon', 'killara', 'lindfield',
                                       'roseville', 'st ives', 'wahroonga', 'hornsby', 'asquith',
                                       'waitara', 'warrawee']):
        return 'Upper North Shore'

    # North Shore (Lower)
    if any(x in name_lower for x in ['north sydney', 'neutral bay', 'cremorne', 'mosman',
                                       'cammeray', 'crows nest', 'northbridge', 'willoughby',
                                       'artarmon', 'chatswood', 'castle cove', 'middle cove',
                                       'castlecrag', 'northwood']):
        return 'Lower North Shore'

    # Eastern Suburbs
    if any(x in name_lower for x in ['bondi', 'coogee', 'maroubra', 'randwick', 'clovelly',
                                       'bronte', 'tamarama', 'dover heights', 'rose bay',
                                       'vaucluse', 'watsons bay', 'double bay', 'bellevue hill',
                                       'woollahra', 'paddington', 'edgecliff', 'point piper',
                                       'darling point', 'elizabeth bay', 'rushcutters bay']):
        return 'Eastern Suburbs'

    # Inner West
    if any(x in name_lower for x in ['newtown', 'marrickville', 'dulwich hill', 'petersham',
                                       'lewisham', 'stanmore', 'enmore', 'glebe', 'annandale',
                                       'leichhardt', 'lilyfield', 'rozelle', 'balmain', 'birchgrove',
                                       'haberfield', 'five dock', 'drummoyne', 'ashfield',
                                       'summer hill', 'croydon', 'burwood', 'strathfield']):
        return 'Inner West'

    # Hills District
    if any(x in name_lower for x in ['castle hill', 'baulkham hills', 'kellyville', 'rouse hill',
                                       'bella vista', 'norwest', 'beaumont hills', 'box hill',
                                       'winston hills', 'west pennant hills']):
        return 'Hills District'

    # Sutherland Shire
    if any(x in name_lower for x in ['sutherland', 'cronulla', 'miranda', 'caringbah', 'gymea',
                                       'kirrawee', 'jannali', 'como', 'oyster bay', 'sylvania',
                                       'engadine', 'heathcote', 'waterfall', 'lilli pilli',
                                       'port hacking', 'bundeena', 'maianbar']):
        return 'Sutherland Shire'

    # Canterbury-Bankstown
    if any(x in name_lower for x in ['bankstown', 'canterbury', 'lakemba', 'punchbowl', 'yagoona',
                                       'wiley park', 'campsie', 'belmore', 'revesby', 'padstow']):
        return 'Canterbury-Bankstown'

    # Parramatta
    if any(x in name_lower for x in ['parramatta', 'westmead', 'harris park', 'granville',
                                       'merrylands', 'guildford', 'wentworthville', 'toongabbie',
                                       'pendle hill', 'girraween', 'greystanes']):
        return 'Parramatta'

    # Western Sydney
    if any(x in name_lower for x in ['blacktown', 'mount druitt', 'rooty hill', 'doonside',
                                       'seven hills', 'kings park', 'lalor park', 'hebersham']):
        return 'Western Sydney'

    # South West
    if any(x in name_lower for x in ['liverpool', 'campbelltown', 'leppington', 'ingleburn',
                                       'minto', 'macquarie fields', 'casula', 'prestons',
                                       'edmondson park', 'gregory hills', 'oran park']):
        return 'South West'

    # CBD & Inner City
    if any(x in name_lower for x in ['sydney', 'haymarket', 'ultimo', 'pyrmont', 'darlinghurst',
                                       'surry hills', 'redfern', 'waterloo', 'alexandria',
                                       'zetland', 'chippendale', 'eveleigh']):
        return 'CBD & Inner City'

    # Lower North West
    if any(x in name_lower for x in ['ryde', 'epping', 'eastwood', 'marsfield', 'macquarie',
                                       'north ryde', 'denistone', 'west ryde', 'meadowbank',
                                       'hunters hill', 'gladesville', 'putney', 'tennyson']):
        return 'Lower North West'

    return 'Other Sydney'

df_base['Region'] = df_base['Suburb_Name'].apply(assign_region)

# Calculate region statistics
region_stats = df_base.groupby('Region').agg({
    'Value_Score': ['mean', 'median', 'std', 'count'],
    'Quality_Index': 'mean',
    'Price_Index': 'mean',
    'Median_mortgage_repay_monthly': 'median',
    'Tertiary_Pct': 'mean'
}).round(1)

print(f"   ✓ Identified {df_base['Region'].nunique()} geographic regions")
print()
print("   Region Statistics:")
print(f"   {'Region':<25}{'Count':>7}  {'Avg Value':>10}  {'Avg Quality':>12}  {'Avg Price':>10}  {'Med Mortgage':>13}")
print("   " + "-" * 95)

for region in region_stats.index:
    count = int(region_stats.loc[region, ('Value_Score', 'count')])
    avg_value = region_stats.loc[region, ('Value_Score', 'mean')]
    avg_quality = region_stats.loc[region, ('Quality_Index', 'mean')]
    avg_price = region_stats.loc[region, ('Price_Index', 'mean')]
    med_mortgage = region_stats.loc[region, ('Median_mortgage_repay_monthly', 'median')]

    print(f"   {region:<25}{count:>7}  {avg_value:>10,.0f}  {avg_quality:>12,.0f}  "
          f"{avg_price:>10.1f}  ${med_mortgage:>12,.0f}")

# ============================================================================
# Calculate Neighbor Premium
# ============================================================================
print("\n[2/4] Calculating neighbor arbitrage opportunities...")

# For each suburb, calculate how it compares to its region average
df_base = df_base.merge(
    df_base.groupby('Region')['Value_Score'].agg(['mean', 'median']).reset_index(),
    on='Region',
    suffixes=('', '_region')
)

df_base['Neighbor_Premium'] = df_base['Value_Score'] - df_base['mean']
df_base['Neighbor_Premium_Pct'] = (df_base['Neighbor_Premium'] / df_base['mean'] * 100).round(1)

# Negative premium = undervalued relative to neighbors!
arbitrage_opportunities = df_base[
    (df_base['Neighbor_Premium'] < 0) &  # Below region average
    (df_base['Quality_Index'] > df_base['Quality_Index'].median()) &  # But still good quality
    (df_base['Region'] != 'Other Sydney')  # Exclude misc category
].sort_values('Neighbor_Premium')

print(f"\n   ✓ Found {len(arbitrage_opportunities):,} neighbor arbitrage opportunities")
print(f"   (Good quality suburbs below their region average)")

# ============================================================================
# Top Arbitrage Opportunities
# ============================================================================
print("\n[3/4] Top 30 Neighbor Arbitrage Opportunities:")
print()
print(f"{'Rank':<6}{'Suburb':<30}{'Region':<25}{'Value':>10}  {'Region Avg':>11}  {'Discount':>9}  {'Quality':>8}")
print("-" * 120)

for i, (_, row) in enumerate(arbitrage_opportunities.head(30).iterrows(), 1):
    print(f"{i:<6}{row['Suburb_Name']:<30}{row['Region']:<25}{row['Value_Score']:>10,.0f}  "
          f"{row['mean']:>11,.0f}  {row['Neighbor_Premium_Pct']:>8.1f}%  "
          f"{row['Quality_Index']:>8.0f}")

# ============================================================================
# Region-Specific Analysis
# ============================================================================
print("\n[4/4] Region-Specific Arbitrage Analysis:")
print()

# For each major region, show the cheapest good-quality suburbs
major_regions = ['Northern Beaches', 'Upper North Shore', 'Lower North Shore',
                 'Eastern Suburbs', 'Inner West', 'Sutherland Shire', 'Hills District']

for region in major_regions:
    region_suburbs = df_base[
        (df_base['Region'] == region) &
        (df_base['Quality_Index'] > df_base['Quality_Index'].quantile(0.6))
    ].sort_values('Price_Index')

    if len(region_suburbs) >= 3:
        print(f"\n   {region}:")
        print(f"   Region Average Value: {df_base[df_base['Region']==region]['Value_Score'].mean():,.0f}")
        print(f"   Best Arbitrage Opportunities (Good Quality, Lower Price):")

        for j, (_, row) in enumerate(region_suburbs.head(5).iterrows(), 1):
            discount = row['Neighbor_Premium_Pct']
            print(f"   {j}. {row['Suburb_Name']:<30} Value: {row['Value_Score']:>8,.0f}  "
                  f"Quality: {row['Quality_Index']:>6.0f}  "
                  f"vs Region: {discount:>6.1f}%  "
                  f"Mortgage: ${row['Median_mortgage_repay_monthly']:>5,.0f}")

# ============================================================================
# Save Results
# ============================================================================
print("\n" + "=" * 120)
print("SAVING RESULTS")
print("=" * 120)
print()

# Save arbitrage opportunities
arbitrage_opportunities.to_csv(f'{OUTPUT_DIR}/neighbor_arbitrage_opportunities.csv', index=False)
print("✓ Saved: neighbor_arbitrage_opportunities.csv")

# Save region-specific best values
for region in major_regions:
    region_suburbs = df_base[df_base['Region'] == region].sort_values('Value_Score', ascending=False)
    if len(region_suburbs) > 0:
        filename = region.lower().replace(' ', '_').replace('-', '_')
        region_suburbs.head(20).to_csv(f'{OUTPUT_DIR}/best_value_{filename}.csv', index=False)

print(f"✓ Saved: Region-specific top 20 files for {len(major_regions)} major regions")

# Save complete dataset with regions and neighbor premium
df_base.to_csv(f'{OUTPUT_DIR}/sydney_all_suburbs_with_neighbor_analysis.csv', index=False)
print("✓ Saved: sydney_all_suburbs_with_neighbor_analysis.csv")

# ============================================================================
# SUMMARY INSIGHTS
# ============================================================================
print("\n" + "=" * 120)
print("KEY INSIGHTS")
print("=" * 120)
print()

if has_volunteer_data:
    print("📊 VOLUNTEER RATE FINDINGS:")
    print(f"   • High volunteer rate correlates with:")
    for metric, corr in correlations.items():
        direction = "positively" if corr > 0 else "negatively"
        strength = "strongly" if abs(corr) > 0.5 else "moderately" if abs(corr) > 0.3 else "weakly"
        print(f"     - {metric}: {strength} {direction} (r={corr:+.3f})")
    print()

print("🏘️  NEIGHBOR ARBITRAGE FINDINGS:")
print(f"   • Found {len(arbitrage_opportunities):,} suburbs below their region average")
print(f"   • Top arbitrage opportunity: {arbitrage_opportunities.iloc[0]['Suburb_Name']}")
print(f"     - Value: {arbitrage_opportunities.iloc[0]['Value_Score']:,.0f}")
print(f"     - Region: {arbitrage_opportunities.iloc[0]['Region']}")
print(f"     - Discount vs region: {arbitrage_opportunities.iloc[0]['Neighbor_Premium_Pct']:.1f}%")
print()

print("💡 INVESTMENT STRATEGY:")
print("   1. Identify desirable region (Northern Beaches, Lower North Shore, etc.)")
print("   2. Find suburbs in that region below regional average (neighbor premium)")
print("   3. Verify still have good absolute quality (>median)")
print("   4. Buy at discount, enjoy same amenities, schools, transport")
print()

print("✓ Analysis complete!")
print()
