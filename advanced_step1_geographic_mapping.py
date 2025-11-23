#!/usr/bin/env python3
"""
Advanced Step 1: Geographic Mapping with Interactive Visualizations
====================================================================
Creates interactive maps with SA1 boundaries and rental stress visualization.
Since actual shapefiles aren't included, we'll create representative coordinate mappings.
"""

import pandas as pd
import numpy as np
import folium
from folium import plugins
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ADVANCED ANALYSIS STEP 1: GEOGRAPHIC MAPPING")
print("=" * 80)
print()

# Configuration
INPUT_FILE = Path("rental_stress_outputs/rental_stress_analysis_full.csv")
GEO_FILE = Path("2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx")
OUTPUT_DIR = Path("rental_stress_outputs/geographic_maps")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Load data
print("Step 1: Loading data...")
df = pd.read_csv(INPUT_FILE)
print(f"✓ Loaded {len(df):,} SA1 areas with rental stress data")

# Load geographic reference
print("Step 2: Loading geographic reference data...")
geo_df = pd.read_excel(GEO_FILE, sheet_name='2021_ASGS_MAIN_Structures')
sa1_geo = geo_df[geo_df['ASGS_Structure'] == 'SA1'].copy()
sa1_geo = sa1_geo.rename(columns={'Census_Code_2021': 'SA1_CODE_2021'})
print(f"✓ Loaded {len(sa1_geo):,} SA1 geographic records")

# Merge geographic data
df = df.merge(sa1_geo[['SA1_CODE_2021', 'Area sqkm']], on='SA1_CODE_2021', how='left')
print()

# ============================================================================
# Create Synthetic Coordinates Based on SA1 Code Structure
# ============================================================================
print("Step 3: Generating coordinate approximations...")
print("Note: Creating synthetic centroids based on SA1 code hierarchy")
print("      (In production, use actual ABS SA1 boundary shapefiles)")
print()

def sa1_code_to_coordinates(sa1_code):
    """
    Convert SA1 code to approximate coordinates based on code structure.
    SA1 codes are 11 digits: XXXXXXXXXXX where:
    - Digit 1: State (1=NSW, 2=VIC, 3=QLD, 4=SA, 5=WA, 6=TAS, 7=NT, 8=ACT)
    - Digits 2-11: Geographic subdivision

    This creates a grid-based coordinate system for visualization.
    """
    code_str = str(int(sa1_code))

    # State-based base coordinates (approximate state centroids)
    state_coords = {
        '1': (-33.0, 147.0),  # NSW - Sydney region
        '2': (-37.5, 144.5),  # VIC - Melbourne region
        '3': (-27.0, 153.0),  # QLD - Brisbane region
        '4': (-35.0, 138.5),  # SA - Adelaide region
        '5': (-32.0, 116.0),  # WA - Perth region
        '6': (-42.0, 147.0),  # TAS - Hobart region
        '7': (-19.5, 134.0),  # NT - Darwin region
        '8': (-35.3, 149.1),  # ACT - Canberra
        '9': (-35.0, 140.0),  # Other territories
    }

    state_digit = code_str[0]
    base_lat, base_lon = state_coords.get(state_digit, (-25.0, 135.0))

    # Use subsequent digits to create offset within state
    # This creates a deterministic spread based on SA1 code
    sa4_code = int(code_str[1:4]) if len(code_str) > 3 else 0
    sa3_code = int(code_str[4:6]) if len(code_str) > 5 else 0
    sa2_code = int(code_str[6:8]) if len(code_str) > 7 else 0
    sa1_local = int(code_str[8:]) if len(code_str) > 8 else 0

    # Create offsets (scaled to create realistic spread)
    lat_offset = ((sa4_code % 20) - 10) * 0.5 + ((sa2_code % 10) - 5) * 0.1 + ((sa1_local % 10) - 5) * 0.01
    lon_offset = ((sa3_code % 20) - 10) * 0.5 + ((sa2_code % 10) - 5) * 0.1 + ((sa1_local % 10) - 5) * 0.01

    lat = base_lat + lat_offset
    lon = base_lon + lon_offset

    return lat, lon

# Generate coordinates for all SA1 areas
print("  → Generating coordinates for 61,844 SA1 areas...")
coords = df['SA1_CODE_2021'].apply(lambda x: sa1_code_to_coordinates(x))
df['latitude'] = coords.apply(lambda x: x[0])
df['longitude'] = coords.apply(lambda x: x[1])
print(f"✓ Coordinates generated for {len(df):,} areas")
print()

# ============================================================================
# Create Interactive Map 1: Rental Stress Hotspots (National)
# ============================================================================
print("Step 4: Creating interactive map - National Rental Stress Hotspots...")

# Filter to areas with rental stress for cleaner visualization
stressed_areas = df[df['rental_stress'] == 1].copy()
print(f"  → Visualizing {len(stressed_areas):,} stressed areas")

# Create base map centered on Australia
aus_map = folium.Map(
    location=[-25.0, 135.0],
    zoom_start=4,
    tiles='OpenStreetMap'
)

# Add title
title_html = '''
<div style="position: fixed;
            top: 10px; left: 50px; width: 400px; height: 90px;
            background-color: white; border:2px solid grey; z-index:9999;
            font-size:14px; padding: 10px">
<h4 style="margin-bottom:5px;">🏘️ Rental Stress Hotspots - Australia</h4>
<p style="margin:0; font-size:12px;">
Areas where households spend ≥30% of income on rent<br>
<b style="color:red;">Red</b> = Severe stress (≥50%)
<b style="color:orange;">Orange</b> = Moderate stress (30-50%)
</p>
</div>
'''
aus_map.get_root().html.add_child(folium.Element(title_html))

# Create color function based on stress level
def get_color(stress_score):
    if stress_score >= 75:
        return 'darkred'
    elif stress_score >= 50:
        return 'red'
    elif stress_score >= 30:
        return 'orange'
    elif stress_score >= 15:
        return 'yellow'
    else:
        return 'lightgreen'

# Add markers for top 1000 stressed areas
top_stressed = stressed_areas.nlargest(1000, 'rental_stress_score')

for idx, row in top_stressed.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        popup=f"""
        <b>SA1: {int(row['SA1_CODE_2021'])}</b><br>
        Rental Stress Score: {row['rental_stress_score']:.1f}/100<br>
        Rent/Income Ratio: {row['rent_to_income_ratio']:.1%}<br>
        Median Rent: ${row['Median_rent_weekly']:.0f}/week<br>
        Median HH Income: ${row['Median_tot_hhd_inc_weekly']:.0f}/week<br>
        Low-Income HH: {row['low_income_pct']:.1f}%<br>
        Public Housing Gap: {row['public_housing_gap']:.0f} dwellings
        """,
        color=get_color(row['rental_stress_score']),
        fill=True,
        fillOpacity=0.6
    ).add_to(aus_map)

# Add heatmap layer
heat_data = [[row['latitude'], row['longitude'], row['rental_stress_score']]
             for idx, row in top_stressed.iterrows()]
plugins.HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(
    folium.FeatureGroup(name='Stress Heatmap').add_to(aus_map)
)

# Add layer control
folium.LayerControl().add_to(aus_map)

# Save map
map_file = OUTPUT_DIR / "national_rental_stress_map.html"
aus_map.save(str(map_file))
print(f"✓ Saved: {map_file}")
print()

# ============================================================================
# Create Interactive Map 2: Public Housing Gaps
# ============================================================================
print("Step 5: Creating interactive map - Public Housing Supply Gaps...")

# Filter critical gap areas
critical_gaps = df[df['critical_housing_gap'] == 1].copy()
print(f"  → Visualizing {len(critical_gaps):,} critical gap areas")

gap_map = folium.Map(
    location=[-25.0, 135.0],
    zoom_start=4,
    tiles='CartoDB positron'
)

# Add title
gap_title_html = '''
<div style="position: fixed;
            top: 10px; left: 50px; width: 400px; height: 90px;
            background-color: white; border:2px solid grey; z-index:9999;
            font-size:14px; padding: 10px">
<h4 style="margin-bottom:5px;">🏗️ Public Housing Supply-Demand Gaps</h4>
<p style="margin:0; font-size:12px;">
Areas with critical shortfalls (>10 dwellings needed)<br>
Circle size = Gap magnitude | Color = Priority level
</p>
</div>
'''
gap_map.get_root().html.add_child(folium.Element(gap_title_html))

# Add markers for top 500 gap areas
top_gaps = critical_gaps.nlargest(500, 'public_housing_gap')

for idx, row in top_gaps.iterrows():
    # Circle size based on gap magnitude
    gap_size = min(row['public_housing_gap'] / 5, 15)  # Scale for visibility

    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=gap_size,
        popup=f"""
        <b>SA1: {int(row['SA1_CODE_2021'])}</b><br>
        <b>Supply-Demand Gap: {row['public_housing_gap']:.0f} dwellings</b><br>
        Public Housing: {row['public_housing_dwellings']:.0f}<br>
        Estimated Demand: {row['estimated_demand']:.0f}<br>
        Low-Income HH: {row['low_income_households']:.0f}<br>
        Investment Priority: {row['investment_priority_score']:.1f}/100
        """,
        color='darkred',
        fill=True,
        fillColor='red',
        fillOpacity=0.7
    ).add_to(gap_map)

gap_map_file = OUTPUT_DIR / "public_housing_gaps_map.html"
gap_map.save(str(gap_map_file))
print(f"✓ Saved: {gap_map_file}")
print()

# ============================================================================
# Create Interactive Map 3: Investment Priorities
# ============================================================================
print("Step 6: Creating interactive map - Investment Priorities...")

# Get top investment priorities
top_investment = df.nlargest(500, 'investment_priority_score')
print(f"  → Visualizing top 500 investment priority areas")

inv_map = folium.Map(
    location=[-25.0, 135.0],
    zoom_start=4,
    tiles='OpenStreetMap'
)

# Add title
inv_title_html = '''
<div style="position: fixed;
            top: 10px; left: 50px; width: 400px; height: 90px;
            background-color: white; border:2px solid grey; z-index:9999;
            font-size:14px; padding: 10px">
<h4 style="margin-bottom:5px;">🎯 Optimal Social Housing Investment Locations</h4>
<p style="margin:0; font-size:12px;">
Top 500 priority areas for social housing construction<br>
Darker red = Higher priority | Click markers for details
</p>
</div>
'''
inv_map.get_root().html.add_child(folium.Element(inv_title_html))

def get_priority_color(score):
    if score >= 75:
        return 'darkred'
    elif score >= 50:
        return 'red'
    elif score >= 35:
        return 'orange'
    else:
        return 'yellow'

# Add markers
for idx, row in top_investment.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        popup=f"""
        <b>SA1: {int(row['SA1_CODE_2021'])}</b><br>
        <b>Investment Priority: {row['investment_priority_score']:.1f}/100</b><br>
        Rental Stress: {row['rental_stress_score']:.1f}/100<br>
        Displacement Risk: {row['displacement_risk_score']:.1f}/100<br>
        Public Housing Gap: {row['public_housing_gap']:.0f} dwellings<br>
        Low-Income HH: {row['low_income_pct']:.1f}%<br>
        Unemployment: {row['unemployment_rate']:.1f}%<br>
        Area: {row['Area sqkm']:.1f} sq km
        """,
        color=get_priority_color(row['investment_priority_score']),
        fill=True,
        fillOpacity=0.7
    ).add_to(inv_map)

# Add cluster layer for better performance
from folium.plugins import MarkerCluster
marker_cluster = MarkerCluster().add_to(inv_map)

inv_map_file = OUTPUT_DIR / "investment_priorities_map.html"
inv_map.save(str(inv_map_file))
print(f"✓ Saved: {inv_map_file}")
print()

# ============================================================================
# Create State-Level Summary Maps (Major States)
# ============================================================================
print("Step 7: Creating state-level detailed maps...")

# State configurations (major states only)
states = {
    'NSW': {'code_prefix': '1', 'center': (-33.0, 147.0), 'zoom': 6, 'name': 'New South Wales'},
    'VIC': {'code_prefix': '2', 'center': (-37.5, 144.5), 'zoom': 6, 'name': 'Victoria'},
    'QLD': {'code_prefix': '3', 'center': (-27.0, 153.0), 'zoom': 6, 'name': 'Queensland'},
}

for state_code, config in states.items():
    # Filter state data
    state_df = df[df['SA1_CODE_2021'].astype(str).str.startswith(config['code_prefix'])].copy()
    state_stressed = state_df[state_df['rental_stress'] == 1].nlargest(200, 'rental_stress_score')

    print(f"  → Creating {config['name']} map ({len(state_stressed)} hotspots)...")

    # Create state map
    state_map = folium.Map(
        location=config['center'],
        zoom_start=config['zoom'],
        tiles='OpenStreetMap'
    )

    # Add title
    state_title = f'''
    <div style="position: fixed;
                top: 10px; left: 50px; width: 350px; height: 80px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px">
    <h4 style="margin-bottom:5px;">🏘️ {config['name']} - Rental Stress</h4>
    <p style="margin:0; font-size:12px;">
    Top 200 rental stress hotspots<br>
    Total stressed SA1s: {len(state_df[state_df['rental_stress'] == 1]):,}
    </p>
    </div>
    '''
    state_map.get_root().html.add_child(folium.Element(state_title))

    # Add markers
    for idx, row in state_stressed.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            popup=f"""
            <b>SA1: {int(row['SA1_CODE_2021'])}</b><br>
            Stress Score: {row['rental_stress_score']:.1f}/100<br>
            Rent/Income: {row['rent_to_income_ratio']:.1%}<br>
            Median Rent: ${row['Median_rent_weekly']:.0f}/wk<br>
            Low-Income: {row['low_income_pct']:.1f}%
            """,
            color=get_color(row['rental_stress_score']),
            fill=True,
            fillOpacity=0.6
        ).add_to(state_map)

    # Save state map
    state_map_file = OUTPUT_DIR / f"{state_code.lower()}_rental_stress_map.html"
    state_map.save(str(state_map_file))
    print(f"     ✓ Saved: {state_map_file}")

print()

# ============================================================================
# Export Enhanced Data with Coordinates
# ============================================================================
print("Step 8: Exporting enhanced dataset with coordinates...")

# Save full dataset with coordinates
coords_file = OUTPUT_DIR / "sa1_data_with_coordinates.csv"
df.to_csv(coords_file, index=False)
print(f"✓ Saved: {coords_file} ({len(df):,} records)")

# Create GeoJSON for top hotspots (for use in GIS tools)
print("Step 9: Creating GeoJSON files for GIS compatibility...")

def create_geojson(data, filename, name_field='SA1_CODE_2021'):
    """Create GeoJSON from dataframe with lat/lon"""
    features = []
    for idx, row in data.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {k: (v if not pd.isna(v) and v != np.inf and v != -np.inf else None)
                          for k, v in row.to_dict().items()
                          if k not in ['latitude', 'longitude']}
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)

# Create GeoJSON files
geojson_hotspots = OUTPUT_DIR / "rental_stress_hotspots.geojson"
create_geojson(df.nlargest(1000, 'rental_stress_score'), geojson_hotspots)
print(f"✓ Saved: {geojson_hotspots}")

geojson_gaps = OUTPUT_DIR / "public_housing_gaps.geojson"
create_geojson(df[df['critical_housing_gap'] == 1].nlargest(500, 'public_housing_gap'), geojson_gaps)
print(f"✓ Saved: {geojson_gaps}")

geojson_investment = OUTPUT_DIR / "investment_priorities.geojson"
create_geojson(df.nlargest(500, 'investment_priority_score'), geojson_investment)
print(f"✓ Saved: {geojson_investment}")

print()

# ============================================================================
# Summary Statistics
# ============================================================================
print("=" * 80)
print("GEOGRAPHIC MAPPING COMPLETE!")
print("=" * 80)
print()

print("📍 Generated Interactive Maps:")
print("  1. national_rental_stress_map.html - National overview (1,000 hotspots)")
print("  2. public_housing_gaps_map.html - Critical supply gaps (500 areas)")
print("  3. investment_priorities_map.html - Top investment locations (500 areas)")
print("  4. nsw_rental_stress_map.html - New South Wales detail")
print("  5. vic_rental_stress_map.html - Victoria detail")
print("  6. qld_rental_stress_map.html - Queensland detail")
print()

print("📊 Data Files:")
print("  7. sa1_data_with_coordinates.csv - Full dataset with lat/lon (61,844 records)")
print("  8. rental_stress_hotspots.geojson - Top 1000 hotspots (GIS-ready)")
print("  9. public_housing_gaps.geojson - Critical gaps (GIS-ready)")
print(" 10. investment_priorities.geojson - Investment targets (GIS-ready)")
print()

print("💡 Usage:")
print("  • Open HTML files in web browser for interactive exploration")
print("  • Import GeoJSON files into QGIS, ArcGIS, or other GIS tools")
print("  • Coordinates are synthetic approximations based on SA1 codes")
print("  • For production use, replace with actual ABS SA1 boundary shapefiles")
print()

print(f"All files saved to: {OUTPUT_DIR}/")
print()

print("📝 Next steps:")
print("  • Download actual ABS ASGS SA1 boundaries from:")
print("    https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/")
print("  • Replace synthetic coordinates with actual SA1 centroids/polygons")
print("  • Add basemap layers (satellite, terrain, etc.)")
print()
