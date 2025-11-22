#!/usr/bin/env python3
"""
Enhance gentrification results with geographic context
- Map SA1 codes to states/territories
- Create state-level summaries
- Generate top areas by state
"""

import pandas as pd
import numpy as np
from pathlib import Path

# State mapping based on SA1 code first digit
STATE_MAP = {
    '1': 'NSW',
    '2': 'VIC',
    '3': 'QLD',
    '4': 'SA',
    '5': 'WA',
    '6': 'TAS',
    '7': 'NT',
    '8': 'ACT',
    '9': 'OT'  # Other Territories
}

STATE_NAMES = {
    'NSW': 'New South Wales',
    'VIC': 'Victoria',
    'QLD': 'Queensland',
    'SA': 'South Australia',
    'WA': 'Western Australia',
    'TAS': 'Tasmania',
    'NT': 'Northern Territory',
    'ACT': 'Australian Capital Territory',
    'OT': 'Other Territories'
}

print("=" * 80)
print("ENHANCING GENTRIFICATION ANALYSIS WITH GEOGRAPHIC CONTEXT")
print("=" * 80)
print()

# Load results
results_file = Path("gentrification_analysis_results/gentrification_risk_scores_all_sa1.csv")
df = pd.read_csv(results_file)

print(f"Loaded {len(df):,} SA1 areas with gentrification risk scores")
print()

# Add state information
print("Adding state/territory information...")
df['state_code'] = df['SA1_CODE_2021'].astype(str).str[0]
df['state'] = df['state_code'].map(STATE_MAP)
df['state_name'] = df['state'].map(STATE_NAMES)

# Filter out areas with 0 population (non-residential areas)
df_residential = df[df['total_population'] > 0].copy()
print(f"Filtered to {len(df_residential):,} residential SA1 areas (population > 0)")
print()

# ============================================================================
# STATE-LEVEL SUMMARIES
# ============================================================================

print("=" * 80)
print("STATE-LEVEL GENTRIFICATION RISK SUMMARY")
print("=" * 80)
print()

state_summary = df_residential.groupby('state').agg({
    'SA1_CODE_2021': 'count',
    'total_population': 'sum',
    'gentrification_risk_score': 'mean',
    'median_personal_income': 'median',
    'pct_year12': 'mean',
    'pct_tertiary': 'mean',
    'pct_young_professionals': 'mean',
    'edu_income_mismatch': 'mean',
    'pct_overseas_born': 'mean'
}).round(2)

state_summary.columns = ['SA1_Count', 'Total_Population', 'Avg_Risk_Score',
                         'Median_Income', 'Avg_Year12_Pct', 'Avg_Tertiary_Pct',
                         'Avg_Young_Prof_Pct', 'Avg_Edu_Income_Mismatch', 'Avg_Overseas_Born_Pct']

# Add state names
state_summary['State_Name'] = state_summary.index.map(STATE_NAMES)

# Reorder columns
state_summary = state_summary[['State_Name', 'SA1_Count', 'Total_Population', 'Avg_Risk_Score',
                                'Median_Income', 'Avg_Year12_Pct', 'Avg_Tertiary_Pct',
                                'Avg_Young_Prof_Pct', 'Avg_Edu_Income_Mismatch', 'Avg_Overseas_Born_Pct']]

print(state_summary.to_string())
print()

# Save state summary
output_dir = Path("gentrification_analysis_results")
state_summary.to_csv(output_dir / "gentrification_summary_by_state.csv")
print(f"✓ Saved state summary: {output_dir / 'gentrification_summary_by_state.csv'}")
print()

# ============================================================================
# TOP GENTRIFICATION AREAS BY STATE
# ============================================================================

print("=" * 80)
print("TOP 20 GENTRIFICATION RISK AREAS BY STATE")
print("=" * 80)
print()

for state_code in sorted(df_residential['state'].unique()):
    if state_code == 'OT':  # Skip Other Territories
        continue

    state_name = STATE_NAMES[state_code]
    state_data = df_residential[df_residential['state'] == state_code].copy()

    # Sort by gentrification risk score
    state_top = state_data.nlargest(20, 'gentrification_risk_score')

    print(f"\n{state_name} ({state_code}) - Top 20 Highest Risk SA1 Areas")
    print("-" * 80)

    # Display key columns
    display_cols = ['rank', 'SA1_CODE_2021', 'gentrification_risk_score', 'risk_category',
                    'total_population', 'median_personal_income', 'pct_year12',
                    'pct_young_professionals', 'edu_income_mismatch']

    print(state_top[display_cols].head(20).to_string(index=False))

    # Save to file
    state_file = output_dir / f"gentrification_top_20_{state_code}.csv"
    state_top.to_csv(state_file, index=False)
    print(f"✓ Saved: {state_file}")
    print()

# ============================================================================
# RISK CATEGORY DISTRIBUTION BY STATE
# ============================================================================

print("=" * 80)
print("GENTRIFICATION RISK CATEGORY DISTRIBUTION BY STATE")
print("=" * 80)
print()

risk_by_state = pd.crosstab(df_residential['state'], df_residential['risk_category'],
                             normalize='index') * 100
risk_by_state = risk_by_state.round(2)
risk_by_state.index = risk_by_state.index.map(STATE_NAMES)

print(risk_by_state.to_string())
print()

risk_by_state.to_csv(output_dir / "gentrification_risk_distribution_by_state.csv")
print(f"✓ Saved: {output_dir / 'gentrification_risk_distribution_by_state.csv'}")
print()

# ============================================================================
# HIGH RISK HOTSPOTS (Very High Risk Areas)
# ============================================================================

print("=" * 80)
print("VERY HIGH RISK GENTRIFICATION HOTSPOTS (Top 500)")
print("=" * 80)
print()

very_high_risk = df_residential[df_residential['risk_category'] == 'Very High'].copy()
very_high_risk_top = very_high_risk.nlargest(500, 'gentrification_risk_score')

# Count by state
hotspot_counts = very_high_risk_top['state'].value_counts().sort_index()
hotspot_counts.index = hotspot_counts.index.map(STATE_NAMES)

print("Distribution of Top 500 Very High Risk Areas by State:")
print("-" * 80)
print(hotspot_counts.to_string())
print()

very_high_risk_top.to_csv(output_dir / "gentrification_very_high_risk_top_500.csv", index=False)
print(f"✓ Saved: {output_dir / 'gentrification_very_high_risk_top_500.csv'}")
print()

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("=" * 80)
print("ENHANCED ANALYSIS COMPLETE")
print("=" * 80)
print()
print(f"Total SA1 Areas Analyzed: {len(df_residential):,}")
print(f"Total Population Covered: {df_residential['total_population'].sum():,.0f}")
print()
print("Key Findings:")
print(f"  • Very High Risk Areas: {len(df_residential[df_residential['risk_category'] == 'Very High']):,}")
print(f"  • High Risk Areas: {len(df_residential[df_residential['risk_category'] == 'High']):,}")
print(f"  • Moderate Risk Areas: {len(df_residential[df_residential['risk_category'] == 'Moderate']):,}")
print()
print("Files Generated:")
print("  ✓ gentrification_summary_by_state.csv")
print("  ✓ gentrification_risk_distribution_by_state.csv")
print("  ✓ gentrification_very_high_risk_top_500.csv")
print("  ✓ gentrification_top_20_[STATE].csv (for each state)")
print()
print("=" * 80)
