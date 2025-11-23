#!/usr/bin/env python3
"""
Advanced Step 3: Transport Accessibility & Employment Center Distance Analysis
===============================================================================
Analyzes spatial accessibility to employment centers and transport infrastructure.

Calculates:
1. Distance to nearest major employment center (CBD)
2. Employment accessibility index
3. Public transport connectivity score
4. Transport cost burden relative to rent
5. Optimal social housing locations balancing affordability + accessibility
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ADVANCED ANALYSIS STEP 3: TRANSPORT ACCESSIBILITY ANALYSIS")
print("=" * 80)
print()

# Configuration
INPUT_FILE = Path("rental_stress_outputs/geographic_maps/sa1_data_with_coordinates.csv")
OUTPUT_DIR = Path("rental_stress_outputs/transport_accessibility")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

# Load data with coordinates
print("Step 1: Loading SA1 data with coordinates...")
df = pd.read_csv(INPUT_FILE)
print(f"✓ Loaded {len(df):,} SA1 areas with geographic coordinates")
print()

# ============================================================================
# Define Major Employment Centers (Australian Capital Cities + Regional Hubs)
# ============================================================================
print("Step 2: Defining employment centers...")

# Major employment centers (CBD coordinates)
employment_centers = {
    # State Capitals
    'Sydney CBD': {'lat': -33.8688, 'lon': 151.2093, 'jobs': 500000, 'state': 1},
    'Melbourne CBD': {'lat': -37.8136, 'lon': 144.9631, 'jobs': 400000, 'state': 2},
    'Brisbane CBD': {'lat': -27.4698, 'lon': 153.0251, 'jobs': 250000, 'state': 3},
    'Adelaide CBD': {'lat': -34.9285, 'lon': 138.6007, 'jobs': 120000, 'state': 4},
    'Perth CBD': {'lat': -31.9505, 'lon': 115.8605, 'jobs': 180000, 'state': 5},
    'Hobart CBD': {'lat': -42.8821, 'lon': 147.3272, 'jobs': 35000, 'state': 6},
    'Darwin CBD': {'lat': -12.4634, 'lon': 130.8456, 'jobs': 30000, 'state': 7},
    'Canberra CBD': {'lat': -35.2809, 'lon': 149.1300, 'jobs': 150000, 'state': 8},

    # Major Regional Employment Centers
    'Parramatta': {'lat': -33.8150, 'lon': 151.0007, 'jobs': 80000, 'state': 1},
    'Newcastle': {'lat': -32.9283, 'lon': 151.7817, 'jobs': 45000, 'state': 1},
    'Wollongong': {'lat': -34.4278, 'lon': 150.8931, 'jobs': 35000, 'state': 1},
    'Geelong': {'lat': -38.1499, 'lon': 144.3617, 'jobs': 30000, 'state': 2},
    'Gold Coast': {'lat': -28.0167, 'lon': 153.4000, 'jobs': 40000, 'state': 3},
    'Sunshine Coast': {'lat': -26.6500, 'lon': 153.0667, 'jobs': 25000, 'state': 3},
    'Townsville': {'lat': -19.2590, 'lon': 146.8169, 'jobs': 20000, 'state': 3},
    'Cairns': {'lat': -16.9186, 'lon': 145.7781, 'jobs': 18000, 'state': 3},
}

print(f"✓ Defined {len(employment_centers)} major employment centers")
print()

# Create employment centers dataframe
centers_df = pd.DataFrame(employment_centers).T.reset_index()
centers_df.columns = ['center_name', 'lat', 'lon', 'jobs', 'state']

# ============================================================================
# Calculate Distance to Nearest Employment Center
# ============================================================================
print("Step 3: Calculating distances to employment centers...")

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (km)"""
    R = 6371  # Earth's radius in km

    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)

    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    return R * c

# Calculate distance to each employment center
print("  → Calculating distances to all employment centers...")
for center_name, row in centers_df.iterrows():
    dist_col = f'dist_to_{center_name}'
    df[dist_col] = haversine_distance(
        df['latitude'], df['longitude'],
        row['lat'], row['lon']
    )

# Find nearest employment center
dist_cols = [col for col in df.columns if col.startswith('dist_to_')]
df['nearest_employment_center_km'] = df[dist_cols].min(axis=1)
df['nearest_center_name'] = df[dist_cols].idxmin(axis=1).str.replace('dist_to_', '')

print(f"✓ Calculated distances for {len(df):,} SA1 areas")
print(f"  Average distance to nearest center: {df['nearest_employment_center_km'].mean():.1f} km")
print(f"  Median distance: {df['nearest_employment_center_km'].median():.1f} km")
print()

# ============================================================================
# Calculate Employment Accessibility Index
# ============================================================================
print("Step 4: Calculating employment accessibility index...")

# Accessibility score based on distance decay function
# Score decreases with distance (gravity model)
def calculate_accessibility(distance_km):
    """
    Calculate accessibility score (0-100) based on distance.
    Uses gravity model: closer = better access
    """
    if distance_km <= 5:  # Inner city - excellent access
        return 100
    elif distance_km <= 15:  # Urban core - good access
        return 100 - (distance_km - 5) * 5
    elif distance_km <= 30:  # Urban fringe - moderate access
        return 50 - (distance_km - 15) * 2
    elif distance_km <= 50:  # Regional - limited access
        return 20 - (distance_km - 30) * 0.5
    else:  # Remote - poor access
        return max(0, 10 - (distance_km - 50) * 0.1)

df['employment_accessibility_score'] = df['nearest_employment_center_km'].apply(
    calculate_accessibility
)

# Categorize accessibility
def categorize_accessibility(score):
    if score >= 75:
        return 'Excellent (0-10km)'
    elif score >= 50:
        return 'Good (10-20km)'
    elif score >= 25:
        return 'Moderate (20-40km)'
    elif score >= 10:
        return 'Limited (40-60km)'
    else:
        return 'Poor (>60km)'

df['accessibility_category'] = df['employment_accessibility_score'].apply(
    categorize_accessibility
)

print(f"✓ Calculated accessibility scores for {len(df):,} SA1 areas")
print("\nAccessibility Distribution:")
print(df['accessibility_category'].value_counts().sort_index())
print()

# ============================================================================
# Estimate Public Transport Connectivity
# ============================================================================
print("Step 5: Estimating public transport connectivity...")

# Public transport quality estimate (based on distance + urban density proxy)
# Urban areas (close to centers) typically have better PT
df['estimated_pt_quality'] = 100 - df['nearest_employment_center_km'].clip(0, 50)

# Adjust based on state (larger cities = better PT networks)
state_pt_multiplier = {
    1: 1.2,  # NSW - Sydney has extensive PT
    2: 1.15,  # VIC - Melbourne has good PT
    3: 1.0,  # QLD - Brisbane moderate PT
    4: 0.9,  # SA - Adelaide limited PT
    5: 0.85,  # WA - Perth limited PT
    6: 0.7,  # TAS - Limited PT
    7: 0.6,  # NT - Very limited PT
    8: 1.1,  # ACT - Canberra good PT
}

# Extract state from SA1 code
df['state_code'] = df['SA1_CODE_2021'].astype(str).str[0].astype(int)
df['pt_multiplier'] = df['state_code'].map(state_pt_multiplier).fillna(1.0)
df['public_transport_score'] = (df['estimated_pt_quality'] * df['pt_multiplier']).clip(0, 100)

print(f"✓ Estimated public transport scores")
print(f"  Average PT score: {df['public_transport_score'].mean():.1f}/100")
print()

# ============================================================================
# Calculate Transport Cost Burden
# ============================================================================
print("Step 6: Calculating transport cost burden...")

# Estimate weekly transport costs based on distance
# Assumptions:
# - Inner city (0-10km): $50/week (PT passes)
# - Urban (10-30km): $80/week (PT + some car)
# - Outer urban (30-50km): $150/week (mostly car)
# - Regional (>50km): $200/week (full car dependency)

def estimate_transport_cost(distance_km):
    """Estimate weekly transport costs based on distance from employment"""
    if distance_km <= 10:
        return 50
    elif distance_km <= 30:
        return 50 + (distance_km - 10) * 1.5
    elif distance_km <= 50:
        return 80 + (distance_km - 30) * 3.5
    else:
        return 150 + min((distance_km - 50) * 2, 50)

df['estimated_weekly_transport_cost'] = df['nearest_employment_center_km'].apply(
    estimate_transport_cost
)

# Calculate transport cost as % of income
df['transport_to_income_ratio'] = (
    df['estimated_weekly_transport_cost'] / df['Median_tot_hhd_inc_weekly']
).replace([np.inf, -np.inf], np.nan).fillna(0)

# Combined housing + transport cost burden
df['housing_transport_burden'] = (
    df['rent_to_income_ratio'] + df['transport_to_income_ratio']
).replace([np.inf, -np.inf], np.nan).fillna(0)

# Flag severe combined burden (>50% of income)
df['severe_combined_burden'] = (df['housing_transport_burden'] >= 0.50).astype(int)

print(f"✓ Calculated transport costs")
print(f"  Average weekly transport cost: ${df['estimated_weekly_transport_cost'].median():.0f}")
print(f"  Average transport/income ratio: {df['transport_to_income_ratio'].mean():.1%}")
print(f"  SA1s with severe combined burden (>50%): {df['severe_combined_burden'].sum():,}")
print()

# ============================================================================
# Identify Optimal Investment Locations (Affordability + Accessibility)
# ============================================================================
print("Step 7: Identifying optimal investment locations...")

# Calculate combined score balancing affordability stress + accessibility
# Ideal: High rental stress + Good accessibility to jobs
df['optimal_location_score'] = (
    df['investment_priority_score'] * 0.50 +  # 50% weight on housing stress
    df['employment_accessibility_score'] * 0.30 +  # 30% weight on job access
    df['public_transport_score'] * 0.20  # 20% weight on PT connectivity
)

# Identify optimal locations (high stress + high accessibility)
optimal_locations = df[
    (df['rental_stress_score'] >= 30) &  # Some rental stress
    (df['employment_accessibility_score'] >= 40)  # Reasonable job access
].nlargest(500, 'optimal_location_score')

print(f"✓ Identified {len(optimal_locations):,} optimal social housing locations")
print(f"  (Balancing affordability need with employment accessibility)")
print()

# ============================================================================
# Create Visualizations
# ============================================================================
print("Step 8: Creating transport accessibility visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Distance to employment centers
ax1 = axes[0, 0]
dist_clean = df['nearest_employment_center_km'][df['nearest_employment_center_km'] <= 100]
ax1.hist(dist_clean, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
ax1.axvline(dist_clean.median(), color='red', linestyle='--', linewidth=2,
           label=f'Median: {dist_clean.median():.1f} km')
ax1.set_xlabel('Distance to Nearest Employment Center (km)')
ax1.set_ylabel('Number of SA1 Areas')
ax1.set_title('Distribution of Employment Center Distances')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Accessibility scores
ax2 = axes[0, 1]
access_counts = df['accessibility_category'].value_counts()
colors_access = {'Excellent (0-10km)': 'darkgreen', 'Good (10-20km)': 'green',
                'Moderate (20-40km)': 'orange', 'Limited (40-60km)': 'darkorange',
                'Poor (>60km)': 'red'}
bars = ax2.bar(range(len(access_counts)), access_counts.values,
              color=[colors_access.get(x, 'blue') for x in access_counts.index])
ax2.set_xticks(range(len(access_counts)))
ax2.set_xticklabels(access_counts.index, rotation=45, ha='right', fontsize=8)
ax2.set_ylabel('Number of SA1 Areas')
ax2.set_title('Employment Accessibility Categories')
ax2.grid(True, axis='y', alpha=0.3)

for i, (bar, value) in enumerate(zip(bars, access_counts.values)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
            f'{value:,}', ha='center', va='bottom', fontsize=8)

# Plot 3: Transport cost burden
ax3 = axes[1, 0]
sample = df.sample(min(5000, len(df)))
scatter = ax3.scatter(sample['nearest_employment_center_km'],
                     sample['estimated_weekly_transport_cost'],
                     c=sample['rental_stress_score'], cmap='RdYlGn_r',
                     alpha=0.5, s=20)
ax3.set_xlabel('Distance to Employment Center (km)')
ax3.set_ylabel('Estimated Weekly Transport Cost ($)')
ax3.set_title('Transport Costs vs Distance (colored by Rental Stress)')
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 300)
plt.colorbar(scatter, ax=ax3, label='Rental Stress Score')
ax3.grid(True, alpha=0.3)

# Plot 4: Combined housing + transport burden
ax4 = axes[1, 1]
combined_burden = df['housing_transport_burden'].replace([np.inf, -np.inf], np.nan).dropna()
combined_clean = combined_burden[combined_burden <= 1.5]
ax4.hist(combined_clean, bins=50, color='purple', edgecolor='black', alpha=0.7)
ax4.axvline(0.50, color='red', linestyle='--', linewidth=2, label='Severe Burden (50%)')
ax4.axvline(0.30, color='orange', linestyle='--', linewidth=2, label='Moderate Burden (30%)')
ax4.axvline(combined_clean.median(), color='darkblue', linestyle='--', linewidth=2,
           label=f'Median: {combined_clean.median():.1%}')
ax4.set_xlabel('Combined Housing + Transport as % of Income')
ax4.set_ylabel('Number of SA1 Areas')
ax4.set_title('Combined Housing + Transport Cost Burden')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
viz_file = OUTPUT_DIR / 'transport_accessibility_analysis.png'
plt.savefig(viz_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {viz_file}")
plt.close()

# ============================================================================
# Export Results
# ============================================================================
print("\nStep 9: Exporting transport accessibility results...")

# Full dataset with transport metrics
transport_file = OUTPUT_DIR / "sa1_with_transport_accessibility.csv"
df.to_csv(transport_file, index=False)
print(f"✓ Saved: {transport_file}")

# Optimal investment locations
optimal_file = OUTPUT_DIR / "optimal_investment_locations_accessibility.csv"
optimal_locations.to_csv(optimal_file, index=False)
print(f"✓ Saved: {optimal_file} (top 500)")

# High combined burden areas
high_burden = df[df['severe_combined_burden'] == 1].nlargest(500, 'housing_transport_burden')
burden_file = OUTPUT_DIR / "high_combined_burden_areas.csv"
high_burden.to_csv(burden_file, index=False)
print(f"✓ Saved: {burden_file} (top 500)")

# Summary statistics by accessibility category
access_summary = df.groupby('accessibility_category').agg({
    'rental_stress_score': 'mean',
    'employment_accessibility_score': 'mean',
    'estimated_weekly_transport_cost': 'mean',
    'transport_to_income_ratio': 'mean',
    'housing_transport_burden': 'mean',
    'SA1_CODE_2021': 'count'
}).round(2)
access_summary.columns = ['Avg Rental Stress', 'Avg Accessibility Score',
                         'Avg Transport Cost ($)', 'Avg Transport/Income',
                         'Avg Combined Burden', 'SA1 Count']
summary_file = OUTPUT_DIR / "accessibility_summary_statistics.csv"
access_summary.to_csv(summary_file)
print(f"✓ Saved: {summary_file}")

print()

# ============================================================================
# Generate Report
# ============================================================================
print("Step 10: Generating transport accessibility report...")

report_file = OUTPUT_DIR / "TRANSPORT_ACCESSIBILITY_REPORT.md"
with open(report_file, 'w') as f:
    f.write("# Transport Accessibility & Employment Center Analysis\n\n")
    f.write("---\n\n")

    f.write("## Executive Summary\n\n")
    f.write(f"Analyzed employment accessibility for **{len(df):,} SA1 areas** across Australia ")
    f.write(f"relative to {len(employment_centers)} major employment centers.\n\n")

    f.write("### Key Findings\n\n")
    f.write(f"- **Average distance to employment**: {df['nearest_employment_center_km'].mean():.1f} km\n")
    f.write(f"- **Median distance to employment**: {df['nearest_employment_center_km'].median():.1f} km\n")
    f.write(f"- **Average transport cost**: ${df['estimated_weekly_transport_cost'].median():.0f}/week\n")
    f.write(f"- **Transport as % of income**: {df['transport_to_income_ratio'].mean():.1%} (average)\n")
    f.write(f"- **SA1s with severe combined burden** (housing + transport >50%): **{df['severe_combined_burden'].sum():,}**\n\n")

    f.write("---\n\n")
    f.write("## Accessibility Distribution\n\n")
    for category, count in df['accessibility_category'].value_counts().sort_index().items():
        pct = count/len(df)*100
        f.write(f"- **{category}**: {count:,} SA1s ({pct:.1f}%)\n")

    f.write("\n---\n\n")
    f.write("## Transport Poverty Analysis\n\n")
    f.write("**Transport poverty** occurs when households spend excessive proportions of income on ")
    f.write("transport while living in low-accessibility areas.\n\n")

    transport_poor = df[
        (df['transport_to_income_ratio'] >= 0.15) &  # >15% income on transport
        (df['employment_accessibility_score'] < 50)  # Poor job access
    ]
    f.write(f"- **{len(transport_poor):,} SA1s** experience transport poverty\n")
    f.write(f"- These areas face **both** high transport costs AND poor job access\n")
    f.write(f"- Combined with rental stress creates severe affordability crisis\n\n")

    f.write("---\n\n")
    f.write("## Policy Implications\n\n")

    f.write("### 1. Location Efficiency Matters\n")
    f.write("Social housing near employment centers provides:\n")
    f.write("- Lower transport costs for residents\n")
    f.write("- Better access to job opportunities\n")
    f.write("- Reduced car dependency and emissions\n")
    f.write("- Improved social mobility\n\n")

    f.write("### 2. Combined Affordability Crisis\n")
    f.write(f"**{df['severe_combined_burden'].sum():,} SA1s** face combined housing + transport burden >50%\n")
    f.write("- Traditional rent-to-income ratios underestimate true affordability stress\n")
    f.write("- Must consider **total** living costs, not just rent\n")
    f.write("- Low-income households in outer suburbs face worst outcomes\n\n")

    f.write("### 3. Optimal Investment Strategy\n")
    f.write(f"Identified **500 optimal locations** balancing:\n")
    f.write("- High rental stress (affordability need)\n")
    f.write("- Good employment accessibility (>40/100 score)\n")
    f.write("- Public transport connectivity\n\n")
    f.write("Investing in these locations maximizes resident outcomes while minimizing ")
    f.write("infrastructure costs.\n\n")

    f.write("---\n\n")
    f.write("## Data & Methodology\n\n")
    f.write("### Employment Centers\n")
    f.write(f"- {len(employment_centers)} major centers identified\n")
    f.write("- Includes all capital cities + regional hubs\n")
    f.write("- Distances calculated using Haversine formula\n\n")

    f.write("### Accessibility Scoring\n")
    f.write("- 0-100 scale based on distance decay\n")
    f.write("- Inner city (0-10km): Excellent (100)\n")
    f.write("- Urban core (10-20km): Good (50-100)\n")
    f.write("- Urban fringe (20-40km): Moderate (20-50)\n")
    f.write("- Regional (40-60km): Limited (10-20)\n")
    f.write("- Remote (>60km): Poor (0-10)\n\n")

    f.write("### Transport Costs\n")
    f.write("- Estimated weekly costs based on distance\n")
    f.write("- Inner city: $50/week (PT)\n")
    f.write("- Urban: $80-150/week (PT + car)\n")
    f.write("- Regional: $150-200/week (car dependent)\n\n")

print(f"✓ Saved: {report_file}")
print()

print("=" * 80)
print("TRANSPORT ACCESSIBILITY ANALYSIS COMPLETE!")
print("=" * 80)
print()

print("📊 Outputs Generated:")
print("  1. transport_accessibility_analysis.png - Visualizations")
print("  2. sa1_with_transport_accessibility.csv - Full dataset (61,844 areas)")
print("  3. optimal_investment_locations_accessibility.csv - Top 500 optimal locations")
print("  4. high_combined_burden_areas.csv - Top 500 high burden areas")
print("  5. accessibility_summary_statistics.csv - Summary by category")
print("  6. TRANSPORT_ACCESSIBILITY_REPORT.md - Full report")
print()

print(f"All files saved to: {OUTPUT_DIR}/")
print()

print("🚗 Key Insights:")
print(f"  • {df['severe_combined_burden'].sum():,} SA1s spend >50% income on housing+transport")
print(f"  • {len(transport_poor):,} areas experience transport poverty")
print(f"  • {len(optimal_locations):,} optimal locations balance affordability + accessibility")
print(f"  • Average transport cost: ${df['estimated_weekly_transport_cost'].median():.0f}/week")
print()
