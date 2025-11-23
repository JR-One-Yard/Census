#!/usr/bin/env python3
"""
TOD Analysis - GIS-Compatible Data Export
=========================================
Exports TOD analysis results in GIS-compatible formats

Formats:
1. CSV with geographic codes (for QGIS/ArcGIS joins)
2. Summary by geographic region
3. Simplified exports for mapping tools

Author: Claude Code
"""

import pandas as pd
import json

print("=" * 100)
print("TOD ANALYSIS - GIS-COMPATIBLE DATA EXPORT")
print("=" * 100)

# Load data
print("\n[1/5] Loading TOD analysis data...")
df_complete = pd.read_csv('tod_complete_sa1_analysis.csv')
df_top_1000 = pd.read_csv('tod_top_1000_opportunities.csv')
df_corridors = pd.read_csv('tod_transit_corridors.csv')
df_pain_points = pd.read_csv('tod_commute_pain_points.csv')

# Add state
def extract_state(sa1_code):
    state_map = {1: 'NSW', 2: 'VIC', 3: 'QLD', 4: 'SA', 5: 'WA',
                 6: 'TAS', 7: 'NT', 8: 'ACT', 9: 'Other'}
    return state_map.get(int(str(sa1_code)[0]), 'Unknown')

df_complete['state'] = df_complete['SA1_CODE_2021'].apply(extract_state)

print("  ✓ Data loaded successfully")

# ============================================================================
# EXPORT 1: Complete SA1 dataset with categories
# ============================================================================

print("\n[2/5] Creating categorized SA1 export for GIS...")

df_gis = df_complete.copy()

# Add categorical fields for easier mapping
df_gis['tod_category'] = pd.cut(
    df_gis['tod_score'],
    bins=[0, 50, 65, 75, 85, 100],
    labels=['Low (0-50)', 'Medium (50-65)', 'High (65-75)', 'Very High (75-85)', 'Extreme (85-100)']
)

df_gis['car_dep_category'] = pd.cut(
    df_gis['car_dependency_ratio'],
    bins=[0, 0.5, 0.7, 0.8, 0.9, 1.0],
    labels=['Low (<50%)', 'Moderate (50-70%)', 'High (70-80%)', 'Very High (80-90%)', 'Extreme (>90%)']
)

df_gis['transit_category'] = pd.cut(
    df_gis['public_transit_ratio'],
    bins=[0, 0.05, 0.10, 0.20, 0.30, 1.0],
    labels=['Very Low (<5%)', 'Low (5-10%)', 'Moderate (10-20%)', 'High (20-30%)', 'Very High (>30%)']
)

# Priority classification
df_gis['investment_priority'] = 'Not Priority'
df_gis.loc[
    (df_gis['tod_score'] > 80) &
    (df_gis['total_commuters'] > df_gis['total_commuters'].quantile(0.9)),
    'investment_priority'
] = 'Priority 1'
df_gis.loc[
    (df_gis['sa2_employment_density'] > df_gis['sa2_employment_density'].quantile(0.75)) &
    (df_gis['public_transit_ratio'] < 0.10) &
    (df_gis['total_commuters'] > 200),
    'investment_priority'
] = 'Priority 2'

# Select GIS-friendly columns
gis_cols = [
    'SA1_CODE_2021', 'SA2_CODE', 'SA3_CODE', 'state',
    'total_population', 'total_commuters',
    'total_car', 'total_public_transit', 'total_active_transport',
    'car_dependency_ratio', 'public_transit_ratio', 'active_transport_ratio',
    'sa2_employment', 'sa2_employment_density',
    'tod_score', 'commute_pain_score',
    'tod_category', 'car_dep_category', 'transit_category',
    'investment_priority'
]

df_gis[gis_cols].to_csv('visualizations/gis_export_complete_sa1.csv', index=False)
print("  ✓ Saved: visualizations/gis_export_complete_sa1.csv (61,844 SA1s)")

# ============================================================================
# EXPORT 2: SA2-level aggregation (easier to map)
# ============================================================================

print("\n[3/5] Creating SA2-level aggregation...")

df_sa2_agg = df_complete.groupby('SA2_CODE').agg({
    'SA3_CODE': 'first',
    'state': 'first',
    'total_population': 'sum',
    'total_commuters': 'sum',
    'total_car': 'sum',
    'total_public_transit': 'sum',
    'total_active_transport': 'sum',
    'sa2_employment': 'first',
    'sa2_employment_density': 'first',
    'tod_score': 'mean',
    'car_dependency_ratio': 'mean',
    'public_transit_ratio': 'mean',
    'active_transport_ratio': 'mean'
}).reset_index()

df_sa2_agg['sa1_count'] = df_complete.groupby('SA2_CODE').size().values

# Add categories
df_sa2_agg['tod_category'] = pd.cut(
    df_sa2_agg['tod_score'],
    bins=[0, 50, 65, 75, 85, 100],
    labels=['Low', 'Medium', 'High', 'Very High', 'Extreme']
)

df_sa2_agg.to_csv('visualizations/gis_export_sa2_aggregated.csv', index=False)
print(f"  ✓ Saved: visualizations/gis_export_sa2_aggregated.csv ({len(df_sa2_agg)} SA2s)")

# ============================================================================
# EXPORT 3: Priority areas only (for focused mapping)
# ============================================================================

print("\n[4/5] Creating priority areas export...")

priority_areas = df_gis[df_gis['investment_priority'].isin(['Priority 1', 'Priority 2'])].copy()
priority_areas.to_csv('visualizations/gis_export_priority_areas.csv', index=False)
print(f"  ✓ Saved: visualizations/gis_export_priority_areas.csv ({len(priority_areas)} priority SA1s)")

# ============================================================================
# EXPORT 4: Top opportunities with enhanced metadata
# ============================================================================

print("\n[5/5] Creating enhanced top opportunities export...")

df_top_enhanced = df_top_1000.copy()
df_top_enhanced['rank'] = range(1, len(df_top_enhanced)+1)
df_top_enhanced['state'] = df_top_enhanced['SA1_CODE_2021'].apply(extract_state)

# Calculate potential impact metrics
df_top_enhanced['potential_new_transit_users_20pct'] = (df_top_enhanced['total_car'] * 0.20).astype(int)
df_top_enhanced['annual_time_savings_hours'] = (df_top_enhanced['total_car'] * 0.20 * 10 * 230 / 60).astype(int)
df_top_enhanced['economic_value_annual'] = (df_top_enhanced['annual_time_savings_hours'] * 25).astype(int)

# Add recommendations
def get_recommendation(row):
    if row['car_dependency_ratio'] > 0.95 and row['public_transit_ratio'] < 0.05:
        return 'New transit service required'
    elif row['car_dependency_ratio'] > 0.85 and row['sa2_employment'] > 5000:
        return 'High-frequency transit to employment center'
    elif row['total_commuters'] > 400:
        return 'Express bus or BRT corridor'
    else:
        return 'Enhanced local transit service'

df_top_enhanced['recommended_intervention'] = df_top_enhanced.apply(get_recommendation, axis=1)

df_top_enhanced.to_csv('visualizations/gis_export_top_1000_enhanced.csv', index=False)
print(f"  ✓ Saved: visualizations/gis_export_top_1000_enhanced.csv ({len(df_top_enhanced)} top opportunities)")

# ============================================================================
# Create GIS metadata file
# ============================================================================

metadata = {
    "title": "TOD Analysis - GIS Export",
    "date": "2025-11-22",
    "source": "2021 Australian Census",
    "geographic_levels": {
        "SA1": "Statistical Area Level 1 (finest granularity)",
        "SA2": "Statistical Area Level 2 (employment centers)",
        "SA3": "Statistical Area Level 3 (regional context)"
    },
    "files": {
        "gis_export_complete_sa1.csv": {
            "description": "Complete SA1 dataset with categories",
            "records": len(df_gis),
            "key_field": "SA1_CODE_2021"
        },
        "gis_export_sa2_aggregated.csv": {
            "description": "SA2-level aggregation (easier to visualize)",
            "records": len(df_sa2_agg),
            "key_field": "SA2_CODE"
        },
        "gis_export_priority_areas.csv": {
            "description": "Priority 1 and Priority 2 areas only",
            "records": len(priority_areas),
            "key_field": "SA1_CODE_2021"
        },
        "gis_export_top_1000_enhanced.csv": {
            "description": "Top 1000 opportunities with impact metrics",
            "records": len(df_top_enhanced),
            "key_field": "SA1_CODE_2021"
        }
    },
    "key_fields": {
        "tod_score": "Transit-Oriented Development score (0-100)",
        "car_dependency_ratio": "Proportion of commuters using cars (0-1)",
        "public_transit_ratio": "Proportion using public transit (0-1)",
        "tod_category": "Categorical TOD score (Low/Medium/High/Very High/Extreme)",
        "car_dep_category": "Categorical car dependency level",
        "investment_priority": "Investment priority tier (Priority 1/2 or Not Priority)"
    },
    "how_to_use": [
        "1. Import CSV into QGIS or ArcGIS",
        "2. Join to ABS SA1/SA2 shapefiles using SA1_CODE_2021 or SA2_CODE",
        "3. Style by tod_category or investment_priority fields",
        "4. Filter to Priority 1/2 areas for focused analysis"
    ],
    "recommended_shapefiles": [
        "ABS SA1 2021 boundaries",
        "ABS SA2 2021 boundaries",
        "ABS SA3 2021 boundaries"
    ]
}

with open('visualizations/gis_export_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("\n  ✓ Saved: visualizations/gis_export_metadata.json")

print("\n" + "=" * 100)
print("GIS EXPORT COMPLETE!")
print("=" * 100)
print("\nGenerated 5 GIS-compatible files:")
print("  1. Complete SA1 dataset (61,844 areas)")
print("  2. SA2 aggregation (2,472 areas)")
print("  3. Priority areas only")
print("  4. Top 1000 enhanced")
print("  5. Metadata (JSON)")
print("\nThese files can be joined to ABS shapefiles in QGIS/ArcGIS")
print("using SA1_CODE_2021 or SA2_CODE as the join key.")
print("=" * 100)
