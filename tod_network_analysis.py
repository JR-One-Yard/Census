#!/usr/bin/env python3
"""
Network Analysis & Travel Time Optimization for TOD
===================================================
Builds commuter flow networks and identifies optimal transit corridors

This script extends the TOD analysis with:
1. Commuter flow network modeling
2. Transit corridor optimization
3. Hub-and-spoke network analysis
4. Travel time savings calculations
5. State-level breakdowns

Author: Claude Code
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("NETWORK ANALYSIS & TRAVEL TIME OPTIMIZATION")
print("=" * 100)

# ============================================================================
# LOAD PREVIOUS ANALYSIS RESULTS
# ============================================================================

print("\n[1/7] Loading TOD analysis results...")
df_complete = pd.read_csv('tod_complete_sa1_analysis.csv')
df_top_1000 = pd.read_csv('tod_top_1000_opportunities.csv')
df_multimodal = pd.read_csv('tod_multimodal_opportunities.csv')

print(f"  ✓ Loaded {len(df_complete):,} SA1 areas")
print(f"  ✓ Loaded {len(df_top_1000):,} top opportunities")
print(f"  ✓ Loaded {len(df_multimodal):,} multimodal opportunities")

# ============================================================================
# EXTRACT STATE/TERRITORY INFORMATION
# ============================================================================

print("\n[2/7] Extracting state/territory information...")

def extract_state_from_sa1(sa1_code):
    """
    Extract state code from SA1 code (first digit)
    1 = NSW, 2 = VIC, 3 = QLD, 4 = SA, 5 = WA, 6 = TAS, 7 = NT, 8 = ACT, 9 = Other
    """
    state_map = {
        1: 'NSW',
        2: 'VIC',
        3: 'QLD',
        4: 'SA',
        5: 'WA',
        6: 'TAS',
        7: 'NT',
        8: 'ACT',
        9: 'Other'
    }
    first_digit = int(str(sa1_code)[0])
    return state_map.get(first_digit, 'Unknown')

df_complete['state'] = df_complete['SA1_CODE_2021'].apply(extract_state_from_sa1)
df_top_1000['state'] = df_top_1000['SA1_CODE_2021'].apply(extract_state_from_sa1)

print("  ✓ State information added")

# ============================================================================
# STATE-LEVEL ANALYSIS
# ============================================================================

print("\n[3/7] Analyzing by State/Territory...")

state_analysis = df_complete.groupby('state').agg({
    'SA1_CODE_2021': 'count',
    'total_commuters': 'sum',
    'total_car': 'sum',
    'total_public_transit': 'sum',
    'total_active_transport': 'sum',
    'car_dependency_ratio': 'mean',
    'public_transit_ratio': 'mean',
    'active_transport_ratio': 'mean',
    'tod_score': 'mean',
    'total_population': 'sum'
}).round(4)

state_analysis.columns = [
    'SA1_Count', 'Total_Commuters', 'Car_Commuters', 'Transit_Commuters',
    'Active_Commuters', 'Avg_Car_Dependency', 'Avg_Transit_Usage',
    'Avg_Active_Transport', 'Avg_TOD_Score', 'Total_Population'
]

print("\nState-level Summary:")
print(state_analysis.to_string())

state_analysis.to_csv('tod_state_level_analysis.csv')
print("\n  ✓ Saved: tod_state_level_analysis.csv")

# ============================================================================
# COMMUTER FLOW NETWORK ANALYSIS
# ============================================================================

print("\n[4/7] Building commuter flow networks...")

# Group by SA2 to identify major flows
sa2_flows = df_complete.groupby('SA2_CODE').agg({
    'total_commuters': 'sum',
    'total_car': 'sum',
    'total_public_transit': 'sum',
    'sa2_employment': 'first',
    'sa2_employment_density': 'first',
    'tod_score': 'mean',
    'car_dependency_ratio': 'mean'
}).reset_index()

# Identify major employment hubs (top 50 SA2s by employment)
major_hubs = sa2_flows.nlargest(50, 'sa2_employment')

print(f"  ✓ Identified {len(major_hubs)} major employment hubs")
print(f"  ✓ Total employment in major hubs: {major_hubs['sa2_employment'].sum():,}")

# Calculate potential transit corridors
# Corridors = high commuter volume + high car dependency + proximity to employment hub

potential_corridors = df_complete[
    (df_complete['total_commuters'] > df_complete['total_commuters'].quantile(0.75)) &
    (df_complete['car_dependency_ratio'] > 0.80) &
    (df_complete['sa2_employment'] > df_complete['sa2_employment'].quantile(0.75))
]

print(f"  ✓ Identified {len(potential_corridors)} potential transit corridor SA1s")
print(f"  ✓ Total commuters in corridors: {potential_corridors['total_commuters'].sum():,}")

potential_corridors[
    ['SA1_CODE_2021', 'SA2_CODE', 'state', 'total_commuters', 'total_car',
     'car_dependency_ratio', 'sa2_employment', 'tod_score']
].to_csv('tod_transit_corridors.csv', index=False)

print("  ✓ Saved: tod_transit_corridors.csv")

# ============================================================================
# HUB-AND-SPOKE NETWORK ANALYSIS
# ============================================================================

print("\n[5/7] Analyzing hub-and-spoke opportunities...")

# For each major employment hub, find surrounding high-car-dependency areas
hub_analysis = []

for idx, hub in major_hubs.head(20).iterrows():
    sa2_code = hub['SA2_CODE']

    # Find SA1 areas in this SA2
    spoke_areas = df_complete[
        (df_complete['SA2_CODE'] == sa2_code) &
        (df_complete['car_dependency_ratio'] > 0.75) &
        (df_complete['total_commuters'] > 100)
    ]

    if len(spoke_areas) > 0:
        hub_analysis.append({
            'SA2_CODE': sa2_code,
            'Employment': hub['sa2_employment'],
            'Spoke_SA1_Count': len(spoke_areas),
            'Total_Spoke_Commuters': spoke_areas['total_commuters'].sum(),
            'Total_Car_Commuters': spoke_areas['total_car'].sum(),
            'Avg_Car_Dependency': spoke_areas['car_dependency_ratio'].mean(),
            'Potential_Modal_Shift_20pct': int(spoke_areas['total_car'].sum() * 0.20),
            'Avg_TOD_Score': spoke_areas['tod_score'].mean()
        })

df_hub_analysis = pd.DataFrame(hub_analysis)
df_hub_analysis = df_hub_analysis.sort_values('Potential_Modal_Shift_20pct', ascending=False)

print(f"  ✓ Analyzed {len(df_hub_analysis)} hub-and-spoke networks")
print(f"  ✓ Total potential modal shift (20%): {df_hub_analysis['Potential_Modal_Shift_20pct'].sum():,} commuters")

df_hub_analysis.to_csv('tod_hub_spoke_analysis.csv', index=False)
print("  ✓ Saved: tod_hub_spoke_analysis.csv")

# ============================================================================
# TRAVEL TIME SAVINGS ESTIMATION
# ============================================================================

print("\n[6/7] Estimating travel time savings potential...")

# Assumptions for travel time savings:
# - Average car commute in high-car-dependency areas: 35 minutes
# - Potential transit with TOD improvements: 30 minutes
# - Savings: 5 minutes per trip, 10 minutes per day (round trip)
# - Working days per year: 230

AVG_CAR_COMMUTE_MINS = 35
IMPROVED_TRANSIT_MINS = 30
SAVINGS_PER_TRIP = AVG_CAR_COMMUTE_MINS - IMPROVED_TRANSIT_MINS
WORKING_DAYS = 230

# Calculate for top TOD opportunities
top_opportunities_time_savings = df_top_1000.copy()

# Assume 20% modal shift to transit
top_opportunities_time_savings['potential_transit_users'] = (
    top_opportunities_time_savings['total_car'] * 0.20
)

top_opportunities_time_savings['daily_time_saved_mins'] = (
    top_opportunities_time_savings['potential_transit_users'] *
    SAVINGS_PER_TRIP * 2  # Round trip
)

top_opportunities_time_savings['annual_time_saved_hours'] = (
    top_opportunities_time_savings['daily_time_saved_mins'] *
    WORKING_DAYS / 60
)

total_daily_savings = top_opportunities_time_savings['daily_time_saved_mins'].sum()
total_annual_savings = top_opportunities_time_savings['annual_time_saved_hours'].sum()

print(f"\n  Travel Time Savings (Top 1000 TOD Opportunities with 20% modal shift):")
print(f"  ✓ Daily time saved: {total_daily_savings:,.0f} minutes ({total_daily_savings/60:,.0f} hours)")
print(f"  ✓ Annual time saved: {total_annual_savings:,.0f} hours ({total_annual_savings/8:,.0f} work-days)")
print(f"  ✓ Economic value (@ $25/hour): ${total_annual_savings * 25:,.0f}")

top_opportunities_time_savings[
    ['SA1_CODE_2021', 'state', 'total_commuters', 'total_car',
     'potential_transit_users', 'daily_time_saved_mins', 'annual_time_saved_hours', 'tod_score']
].head(100).to_csv('tod_travel_time_savings.csv', index=False)

print("  ✓ Saved: tod_travel_time_savings.csv")

# ============================================================================
# NETWORK OPTIMIZATION RECOMMENDATIONS
# ============================================================================

print("\n[7/7] Generating network optimization recommendations...")

# Priority 1: High TOD Score + High Commuter Volume
priority_1 = df_complete[
    (df_complete['tod_score'] > 80) &
    (df_complete['total_commuters'] > df_complete['total_commuters'].quantile(0.90))
].sort_values('tod_score', ascending=False)

# Priority 2: Near Employment Centers + Low Current Transit
priority_2 = df_complete[
    (df_complete['sa2_employment_density'] > df_complete['sa2_employment_density'].quantile(0.75)) &
    (df_complete['public_transit_ratio'] < 0.10) &
    (df_complete['total_commuters'] > 200)
].sort_values('sa2_employment_density', ascending=False)

# Priority 3: Multimodal Potential (multiple transport types already present)
priority_3 = df_complete[
    (df_complete['public_transit_ratio'] > 0.05) &
    (df_complete['active_transport_ratio'] > 0.05) &
    (df_complete['car_dependency_ratio'] > 0.70) &
    (df_complete['total_commuters'] > 300)
].sort_values('tod_score', ascending=False)

print(f"\n  Priority Investment Categories:")
print(f"  ✓ Priority 1 (High TOD + High Volume): {len(priority_1):,} SA1 areas, {priority_1['total_commuters'].sum():,} commuters")
print(f"  ✓ Priority 2 (Near Employment Centers): {len(priority_2):,} SA1 areas, {priority_2['total_commuters'].sum():,} commuters")
print(f"  ✓ Priority 3 (Multimodal Potential): {len(priority_3):,} SA1 areas, {priority_3['total_commuters'].sum():,} commuters")

# Save priority lists
priority_1.head(500).to_csv('tod_priority_1_high_score_volume.csv', index=False)
priority_2.head(500).to_csv('tod_priority_2_employment_centers.csv', index=False)
priority_3.head(500).to_csv('tod_priority_3_multimodal.csv', index=False)

print("\n  ✓ Saved: tod_priority_1_high_score_volume.csv")
print("  ✓ Saved: tod_priority_2_employment_centers.csv")
print("  ✓ Saved: tod_priority_3_multimodal.csv")

# ============================================================================
# FINAL NETWORK ANALYSIS SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("NETWORK ANALYSIS SUMMARY")
print("=" * 100)

print(f"""
Key Findings:

1. MAJOR EMPLOYMENT HUBS
   - Identified {len(major_hubs)} major employment centers
   - Total employment: {major_hubs['sa2_employment'].sum():,}
   - Average commuter volume per hub: {major_hubs['total_commuters'].mean():,.0f}

2. TRANSIT CORRIDORS
   - Potential corridors identified: {len(potential_corridors)}
   - Total corridor commuters: {potential_corridors['total_commuters'].sum():,}
   - Average car dependency in corridors: {potential_corridors['car_dependency_ratio'].mean():.1%}

3. HUB-AND-SPOKE NETWORKS
   - Analyzed {len(df_hub_analysis)} hub networks
   - Potential modal shift (20%): {df_hub_analysis['Potential_Modal_Shift_20pct'].sum():,} new transit users
   - Top hub potential: {df_hub_analysis['Potential_Modal_Shift_20pct'].max():,} users

4. TRAVEL TIME SAVINGS
   - Daily savings (top 1000): {total_daily_savings/60:,.0f} hours
   - Annual savings: {total_annual_savings:,.0f} hours
   - Economic value: ${total_annual_savings * 25:,.0f}

5. INVESTMENT PRIORITIES
   - Priority 1 areas: {len(priority_1):,} (High TOD score + volume)
   - Priority 2 areas: {len(priority_2):,} (Near employment centers)
   - Priority 3 areas: {len(priority_3):,} (Multimodal potential)

Total Potential Impact:
   - Car commuters in priority areas: {(priority_1['total_car'].sum() + priority_2['total_car'].sum() + priority_3['total_car'].sum()) / 3:,.0f}
   - With 20% modal shift: {((priority_1['total_car'].sum() + priority_2['total_car'].sum() + priority_3['total_car'].sum()) / 3) * 0.20:,.0f} new transit users
""")

print("=" * 100)
print("✓ NETWORK ANALYSIS COMPLETE!")
print("=" * 100 + "\n")
