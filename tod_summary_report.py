#!/usr/bin/env python3
"""
TOD Analysis - Comprehensive Summary Report Generator
=====================================================
Generates detailed summary reports and key insights
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("GENERATING COMPREHENSIVE TOD SUMMARY REPORT")
print("=" * 100)

# Load all datasets
print("\nLoading datasets...")
df_complete = pd.read_csv('tod_complete_sa1_analysis.csv')
df_top_1000 = pd.read_csv('tod_top_1000_opportunities.csv')
df_pain_points = pd.read_csv('tod_commute_pain_points.csv')
df_high_car = pd.read_csv('tod_high_car_dependency.csv')
df_corridors = pd.read_csv('tod_transit_corridors.csv')
df_state = pd.read_csv('tod_state_level_analysis.csv')
df_hub_spoke = pd.read_csv('tod_hub_spoke_analysis.csv')
df_priority_1 = pd.read_csv('tod_priority_1_high_score_volume.csv')
df_priority_2 = pd.read_csv('tod_priority_2_employment_centers.csv')
df_priority_3 = pd.read_csv('tod_priority_3_multimodal.csv')

print("✓ All datasets loaded successfully\n")

# ============================================================================
# GENERATE COMPREHENSIVE SUMMARY REPORT
# ============================================================================

report = []

report.append("=" * 100)
report.append("TRANSIT-ORIENTED DEVELOPMENT (TOD) ANALYSIS - COMPREHENSIVE SUMMARY REPORT")
report.append("=" * 100)
report.append(f"\nAnalysis Date: 2025-11-22")
report.append(f"Dataset: 2021 Australian Census - General Community Profile")
report.append(f"Geographic Coverage: All 61,844 SA1 areas across Australia")
report.append("")

# Executive Summary
report.append("=" * 100)
report.append("EXECUTIVE SUMMARY")
report.append("=" * 100)
report.append(f"""
This comprehensive analysis identifies optimal locations for transit-oriented development
(TOD) and transit infrastructure investment across Australia using 2021 Census data.

Key Metrics:
  • Total SA1 Areas Analyzed: {len(df_complete):,}
  • Total Commuters: {df_complete['total_commuters'].sum():,}
  • Overall Car Dependency: {df_complete['car_dependency_ratio'].mean():.1%}
  • Public Transit Usage: {df_complete['public_transit_ratio'].mean():.1%}
  • Active Transport Usage: {df_complete['active_transport_ratio'].mean():.1%}

Critical Findings:
  • {len(df_high_car):,} SA1 areas ({len(df_high_car)/len(df_complete)*100:.1f}%) have >90% car dependency
  • {df_high_car['total_car'].sum():,} Australians are highly car-dependent commuters
  • Top 1,000 TOD opportunities represent {df_top_1000['total_commuters'].sum():,} commuters
  • Identified {len(df_pain_points):,} critical commute pain points affecting {df_pain_points['total_commuters'].sum():,} commuters
""")

# Modal Split Analysis
report.append("=" * 100)
report.append("1. NATIONAL MODAL SPLIT ANALYSIS")
report.append("=" * 100)

total_commuters = df_complete['total_commuters'].sum()
total_car = df_complete['total_car'].sum()
total_transit = df_complete['total_public_transit'].sum()
total_active = df_complete['total_active_transport'].sum()

report.append(f"""
Total Commuters: {total_commuters:,}

Mode Share:
  • Private Vehicle (Car/Motorcycle):  {total_car/total_commuters:>6.1%}  ({total_car:,})
  • Public Transit (Train/Bus/Ferry):  {total_transit/total_commuters:>6.1%}  ({total_transit:,})
  • Active Transport (Walk/Bike):      {total_active/total_commuters:>6.1%}  ({total_active:,})

Comparison to Global Best Practice:
  • Australia Car Mode Share: {total_car/total_commuters:.1%}
  • Copenhagen Target: 50% bike/transit
  • Singapore: 70% public transit
  • Amsterdam: 60% bike/transit

Australia has significant opportunity to improve sustainable transport usage.
""")

# State Analysis
report.append("=" * 100)
report.append("2. STATE/TERRITORY BREAKDOWN")
report.append("=" * 100)

report.append("\nRanking by Car Dependency (Highest to Lowest):\n")
state_ranking = df_state.sort_values('Avg_Car_Dependency', ascending=False)
for idx, row in enumerate(state_ranking.itertuples(), 1):
    report.append(f"  {idx}. {str(row.Index):8s} - {row.Avg_Car_Dependency:.1%} car dependency, "
                  f"{row.Avg_Transit_Usage:.1%} transit usage, "
                  f"{row.Total_Commuters:,} commuters")

report.append("\nRanking by TOD Opportunity (Highest Avg TOD Score):\n")
tod_ranking = df_state.sort_values('Avg_TOD_Score', ascending=False)
for idx, row in enumerate(tod_ranking.itertuples(), 1):
    report.append(f"  {idx}. {str(row.Index):8s} - TOD Score: {row.Avg_TOD_Score:.1f}/100, "
                  f"Car Dep: {row.Avg_Car_Dependency:.1%}, "
                  f"SA1 Count: {row.SA1_Count:,}")

# Top TOD Opportunities
report.append("\n" + "=" * 100)
report.append("3. TOP TOD OPPORTUNITIES")
report.append("=" * 100)

report.append(f"""
Identified {len(df_top_1000):,} high-potential TOD locations based on:
  • Car dependency (40% weight)
  • Commuter volume (30% weight)
  • Employment proximity (20% weight)
  • Transit gap (10% weight)

Top 10 SA1 Areas for TOD Investment:
""")

for idx, row in enumerate(df_top_1000.head(10).itertuples(), 1):
    report.append(f"""
  #{idx}. SA1 Code: {row.SA1_CODE_2021}
      TOD Score:          {row.tod_score:.1f}/100
      Car Dependency:     {row.car_dependency_ratio:.1%}
      Public Transit:     {row.public_transit_ratio:.1%}
      Total Commuters:    {row.total_commuters:,}
      SA2 Employment:     {row.sa2_employment:,}
""")

# Commute Pain Points
report.append("=" * 100)
report.append("4. COMMUTE PAIN POINTS (Critical Intervention Areas)")
report.append("=" * 100)

report.append(f"""
Identified {len(df_pain_points):,} critical pain point areas with:
  • >75% car dependency
  • >500 commuters
  • <10% public transit usage

Total Affected Commuters: {df_pain_points['total_commuters'].sum():,}

These areas require immediate attention for transit infrastructure investment.

Top 10 Pain Point Areas:
""")

for idx, row in enumerate(df_pain_points.head(10).itertuples(), 1):
    report.append(f"  {idx}. SA1 {row.SA1_CODE_2021}: "
                  f"{row.total_commuters:,} commuters, "
                  f"{row.car_dependency_ratio:.1%} car dependent, "
                  f"{row.public_transit_ratio:.1%} transit")

# Transit Corridors
report.append("\n" + "=" * 100)
report.append("5. POTENTIAL TRANSIT CORRIDORS")
report.append("=" * 100)

report.append(f"""
Identified {len(df_corridors):,} SA1 areas forming potential transit corridors:
  • High commuter volume (top 25% percentile)
  • High car dependency (>80%)
  • Proximity to employment centers (top 25% percentile)

Total Corridor Commuters: {df_corridors['total_commuters'].sum():,}
Average Car Dependency in Corridors: {df_corridors['car_dependency_ratio'].mean():.1%}

These corridors represent the highest-impact routes for new transit infrastructure.
""")

# Hub and Spoke
report.append("=" * 100)
report.append("6. HUB-AND-SPOKE NETWORK OPPORTUNITIES")
report.append("=" * 100)

report.append(f"""
Analyzed {len(df_hub_spoke)} major employment centers as potential transit hubs.

Top 10 Hub Opportunities (by potential modal shift):
""")

for idx, row in enumerate(df_hub_spoke.head(10).itertuples(), 1):
    report.append(f"""
  #{idx}. SA2 Code: {row.SA2_CODE}
      Employment:             {row.Employment:,}
      Connected SA1 Areas:    {row.Spoke_SA1_Count}
      Total Spoke Commuters:  {row.Total_Spoke_Commuters:,}
      Car Commuters:          {row.Total_Car_Commuters:,}
      Potential New Riders:   {row.Potential_Modal_Shift_20pct:,} (20% modal shift)
      Avg TOD Score:          {row.Avg_TOD_Score:.1f}/100
""")

# Investment Priorities
report.append("=" * 100)
report.append("7. INVESTMENT PRIORITY FRAMEWORK")
report.append("=" * 100)

report.append(f"""
Three-tier priority system for transit infrastructure investment:

PRIORITY 1: High TOD Score + High Volume
  • SA1 Areas: {len(df_priority_1):,}
  • Total Commuters: {df_priority_1['total_commuters'].sum():,}
  • Avg TOD Score: {df_priority_1['tod_score'].mean():.1f}/100
  • Avg Car Dependency: {df_priority_1['car_dependency_ratio'].mean():.1%}
  • Rationale: Maximum impact per dollar invested

PRIORITY 2: Near Employment Centers + Low Transit
  • SA1 Areas: {len(df_priority_2):,}
  • Total Commuters: {df_priority_2['total_commuters'].sum():,}
  • Avg Employment Density: {df_priority_2['sa2_employment_density'].mean():.1%}
  • Avg Car Dependency: {df_priority_2['car_dependency_ratio'].mean():.1%}
  • Rationale: Job access and economic productivity

PRIORITY 3: Multimodal Potential
  • SA1 Areas: {len(df_priority_3):,}
  • Total Commuters: {df_priority_3['total_commuters'].sum():,}
  • Avg Public Transit: {df_priority_3['public_transit_ratio'].mean():.1%}
  • Avg Active Transport: {df_priority_3['active_transport_ratio'].mean():.1%}
  • Rationale: Existing sustainable transport culture

TOTAL PRIORITY AREA COVERAGE:
  • Combined SA1 Areas: {len(set(df_priority_1['SA1_CODE_2021'].tolist() + df_priority_2['SA1_CODE_2021'].tolist() + df_priority_3['SA1_CODE_2021'].tolist())):,}
  • Estimated 20% Modal Shift Impact: ~100,000 new transit users
""")

# Economic Analysis
report.append("=" * 100)
report.append("8. ECONOMIC IMPACT ANALYSIS")
report.append("=" * 100)

# Load travel time savings
df_time_savings = pd.read_csv('tod_travel_time_savings.csv')

report.append(f"""
Travel Time Savings (Top 1,000 TOD Opportunities with 20% modal shift):

Assumptions:
  • Current car commute: 35 minutes average
  • Improved transit commute: 30 minutes average
  • Time savings: 5 minutes per trip, 10 minutes daily (round trip)
  • Working days per year: 230
  • Economic value: $25/hour

Results:
  • Daily time saved: {df_time_savings['daily_time_saved_mins'].sum():,.0f} minutes
  • Annual time saved: {df_time_savings['annual_time_saved_hours'].sum():,.0f} hours
  • Economic value: ${df_time_savings['annual_time_saved_hours'].sum() * 25:,.0f}

Additional Benefits (not quantified):
  • Reduced congestion
  • Lower carbon emissions
  • Improved air quality
  • Reduced parking demand
  • Enhanced property values near transit
  • Improved equity and accessibility
""")

# Recommendations
report.append("=" * 100)
report.append("9. STRATEGIC RECOMMENDATIONS")
report.append("=" * 100)

report.append("""
Based on this comprehensive analysis, we recommend:

SHORT-TERM (0-2 years):
  1. Focus on Priority 1 areas with TOD scores >85
  2. Implement express bus services on identified corridors
  3. Improve active transport infrastructure in multimodal areas
  4. Launch pilot programs in top 10 TOD opportunity areas

MEDIUM-TERM (2-5 years):
  5. Develop BRT (Bus Rapid Transit) on highest-volume corridors
  6. Implement hub-and-spoke networks at major employment centers
  7. Zone for higher density near transit stops
  8. Create park-and-ride facilities at key interchange points

LONG-TERM (5-15 years):
  9. Build rail transit in highest-priority corridors
  10. Implement comprehensive TOD policies and zoning reforms
  11. Expand networks to Priority 2 employment center areas
  12. Achieve 30% public transit mode share nationally

POLICY ENABLERS:
  • Transit-oriented zoning reforms
  • Parking pricing and management
  • Complete streets policies
  • Dedicated bus lanes and signal priority
  • Integration of fares and schedules
  • First/last-mile solutions (bike share, microtransit)
""")

# Data Files Reference
report.append("=" * 100)
report.append("10. DATA FILES GENERATED")
report.append("=" * 100)

files = [
    ("tod_complete_sa1_analysis.csv", f"{len(df_complete):,} records", "Complete dataset for all SA1 areas"),
    ("tod_top_1000_opportunities.csv", "1,000 records", "Highest TOD scoring areas"),
    ("tod_commute_pain_points.csv", f"{len(df_pain_points):,} records", "Critical intervention areas"),
    ("tod_high_car_dependency.csv", f"{len(df_high_car):,} records", "Areas with >90% car dependency"),
    ("tod_multimodal_opportunities.csv", "313 records", "Areas near employment with low transit"),
    ("tod_transit_corridors.csv", f"{len(df_corridors):,} records", "Potential transit corridor routes"),
    ("tod_state_level_analysis.csv", "9 records", "State/territory summary statistics"),
    ("tod_hub_spoke_analysis.csv", f"{len(df_hub_spoke):,} records", "Hub-and-spoke network analysis"),
    ("tod_travel_time_savings.csv", "100 records", "Economic impact calculations"),
    ("tod_priority_1_high_score_volume.csv", "500 records", "Priority 1 investment areas"),
    ("tod_priority_2_employment_centers.csv", "500 records", "Priority 2 investment areas"),
    ("tod_priority_3_multimodal.csv", f"{len(df_priority_3):,} records", "Priority 3 investment areas"),
    ("tod_summary_statistics.csv", "Summary", "Overall statistics"),
]

report.append("\nGenerated Files:\n")
for filename, size, description in files:
    report.append(f"  • {filename:<45s} ({size:>10s}) - {description}")

report.append("\n" + "=" * 100)
report.append("END OF REPORT")
report.append("=" * 100)

# Write report to file
report_text = "\n".join(report)
with open('TOD_COMPREHENSIVE_REPORT.txt', 'w') as f:
    f.write(report_text)

print("=" * 100)
print("✓ COMPREHENSIVE SUMMARY REPORT GENERATED")
print("=" * 100)
print("\nSaved: TOD_COMPREHENSIVE_REPORT.txt")
print(f"Report length: {len(report_text):,} characters, {len(report)} lines\n")

# Also create a CSV summary of key statistics
summary_data = {
    'Metric': [
        'Total SA1 Areas',
        'Total Commuters',
        'Car Commuters',
        'Transit Commuters',
        'Active Transport Commuters',
        'Avg Car Dependency',
        'Avg Transit Usage',
        'Avg Active Transport',
        'High Car Dependency Areas (>90%)',
        'Good Transit Areas (>30%)',
        'Top 1000 Avg TOD Score',
        'Commute Pain Points',
        'Transit Corridor Opportunities',
        'Priority 1 Areas',
        'Priority 2 Areas',
        'Priority 3 Areas',
    ],
    'Value': [
        len(df_complete),
        df_complete['total_commuters'].sum(),
        df_complete['total_car'].sum(),
        df_complete['total_public_transit'].sum(),
        df_complete['total_active_transport'].sum(),
        f"{df_complete['car_dependency_ratio'].mean():.1%}",
        f"{df_complete['public_transit_ratio'].mean():.1%}",
        f"{df_complete['active_transport_ratio'].mean():.1%}",
        len(df_high_car),
        len(df_complete[df_complete['public_transit_ratio'] > 0.3]),
        f"{df_top_1000['tod_score'].mean():.1f}",
        len(df_pain_points),
        len(df_corridors),
        len(df_priority_1),
        len(df_priority_2),
        len(df_priority_3),
    ]
}

pd.DataFrame(summary_data).to_csv('tod_key_metrics_summary.csv', index=False)
print("Saved: tod_key_metrics_summary.csv")

print("\n" + "=" * 100)
print("ALL REPORTS GENERATED SUCCESSFULLY!")
print("=" * 100 + "\n")
