#!/usr/bin/env python3
"""
Analyze 2021 Australian Census Data
Find the top 5 countries of birth (excluding Australia) that appear most frequently
as the #1 non-Australia birthplace across Sydney suburbs
"""

import csv
import pandas as pd
from collections import Counter
import re

# File paths
DATA_DIR = "/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/"
MAPPING_FILE = "/home/user/Census/SAL_Suburb_Name_Mapping.csv"

print("="*100)
print("ANALYZING TOP NON-AUSTRALIA BIRTHPLACES ACROSS SYDNEY SUBURBS")
print("="*100)

# Load suburb name mapping with area information
print("\nLoading suburb name mapping...")
suburb_names = {}
suburb_areas = {}
with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        suburb_names[row['SAL_CODE']] = row['Suburb_Name']
        try:
            suburb_areas[row['SAL_CODE']] = float(row['Area_sqkm'])
        except (ValueError, KeyError):
            suburb_areas[row['SAL_CODE']] = 0

print(f"Loaded {len(suburb_names):,} suburb names")

# Define common Sydney suburbs/areas (Greater Sydney region)
# Using a comprehensive list based on Greater Sydney statistical area
# We'll filter for NSW suburbs that are commonly in Greater Sydney
# This is a simplified approach - ideally we'd use GCCSA mapping

def is_sydney_suburb(suburb_name, area_sqkm):
    """
    Determine if a suburb is in Greater Sydney.
    Uses area filtering and keyword exclusion to identify urban Sydney suburbs.
    """
    if not suburb_name or pd.isna(suburb_name):
        return False

    suburb_lower = suburb_name.lower()

    # Exclude obvious non-Sydney NSW regions by keyword
    exclude_keywords = [
        'newcastle', 'hunter', 'maitland', 'cessnock', 'singleton',
        'central coast', 'gosford', 'wyong', 'lake macquarie',
        'wollongong', 'shellharbour', 'kiama', 'shoalhaven', 'nowra',
        'blue mountains', 'lithgow', 'oberon', 'bathurst', 'orange',
        'dubbo', 'wagga', 'albury', 'broken hill', 'lismore', 'byron',
        'ballina', 'port macquarie', 'coffs harbour', 'armidale', 'tamworth',
        'goulburn', 'queanbeyan', 'grafton', 'griffith', 'tweed',
        'kempsey', 'muswellbrook', 'scone', 'glen innes', 'inverell',
        'moree', 'narrabri', 'gunnedah', 'coonabarabran', 'mudgee',
        'forbes', 'parkes', 'cowra', 'young', 'hay', 'deniliquin',
        'tumut', 'snowy', 'cooma', 'bega', 'merimbula'
    ]

    for keyword in exclude_keywords:
        if keyword in suburb_lower:
            return False

    # Filter by area - Greater Sydney suburbs are typically < 30 sq km
    # Rural areas and regional towns are much larger
    # Most urban Sydney suburbs are < 20 sq km
    if area_sqkm > 30:
        return False

    return True

# Load G09 tables A through H to get all country of birth data
print("\nLoading country of birth data from G09 tables...")

# First, load one table to get the SAL codes
df_base = pd.read_csv(f"{DATA_DIR}2021Census_G09A_AUST_SAL.csv")

# Initialize dictionary to store total counts by country for each SAL
country_totals = {}

# List of G09 table files
g09_tables = ['G09A', 'G09B', 'G09C', 'G09D', 'G09E', 'G09F', 'G09G', 'G09H']

for table in g09_tables:
    print(f"  Loading {table}...")
    df = pd.read_csv(f"{DATA_DIR}2021Census_{table}_AUST_SAL.csv")

    # Get columns that end with _Tot (total columns for each country)
    total_cols = [col for col in df.columns if col.endswith('_Tot')]

    # For each SAL code, sum up the country totals
    for _, row in df.iterrows():
        sal_code = row['SAL_CODE_2021']

        if sal_code not in country_totals:
            country_totals[sal_code] = {}

        for col in total_cols:
            # Extract country name from column (format: M_CountryName_Tot, F_CountryName_Tot, P_CountryName_Tot)
            # We'll use P_ (Persons) columns if available, otherwise sum M_ and F_
            if col.startswith('P_'):
                country_name = col.replace('P_', '').replace('_Tot', '')

                # Skip non-country columns
                if country_name in ['Tot', 'COB_NS', 'Elsewhere']:
                    continue

                if country_name not in country_totals[sal_code]:
                    country_totals[sal_code][country_name] = 0
                country_totals[sal_code][country_name] += row[col]
            elif col.startswith('M_'):
                country_name = col.replace('M_', '').replace('_Tot', '')

                # Skip non-country columns
                if country_name in ['Tot', 'COB_NS', 'Elsewhere']:
                    continue

                if country_name not in country_totals[sal_code]:
                    country_totals[sal_code][country_name] = 0
                # Add male count
                country_totals[sal_code][country_name] += row[col]

print(f"\nProcessed {len(country_totals):,} suburbs/localities")

# Filter for Sydney suburbs (NSW SAL codes typically start with SAL1)
print("\nFiltering for Sydney suburbs...")

sydney_data = []

for sal_code, countries in country_totals.items():
    # Check if this is a NSW suburb (SAL codes starting with SAL1 are NSW)
    if not sal_code.startswith('SAL1'):
        continue

    suburb_name = suburb_names.get(sal_code, 'Unknown')
    area_sqkm = suburb_areas.get(sal_code, 0)

    # Apply Sydney filter
    if not is_sydney_suburb(suburb_name, area_sqkm):
        continue

    # Find the top non-Australia country
    # Sort countries by count
    sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)

    # Find top non-Australia country
    top_non_aus = None
    top_non_aus_count = 0
    australia_count = 0

    for country, count in sorted_countries:
        if country == 'Australia':
            australia_count = count
            continue
        if top_non_aus is None:
            top_non_aus = country
            top_non_aus_count = count
            break

    total_pop = sum(countries.values())

    # Only include suburbs with reasonable population (> 100 people)
    # to avoid statistical noise from very small suburbs
    if top_non_aus and australia_count > 0 and total_pop > 100:
        sydney_data.append({
            'SAL_CODE': sal_code,
            'Suburb_Name': suburb_name,
            'Top_Non_Australia_Country': top_non_aus,
            'Top_Non_Australia_Count': top_non_aus_count,
            'Australia_Count': australia_count,
            'Total_Population': total_pop,
            'Percentage_Non_Aus': (top_non_aus_count / total_pop * 100) if total_pop > 0 else 0
        })

print(f"Found {len(sydney_data)} Sydney suburbs with country of birth data")

# Count which countries appear most frequently as #1 non-Australia birthplace
print("\nCounting top non-Australia countries across Sydney suburbs...")

country_frequency = Counter([d['Top_Non_Australia_Country'] for d in sydney_data])

print("\n" + "="*100)
print("TOP 5 COUNTRIES OF BIRTH (EXCLUDING AUSTRALIA)")
print("Ranked by how frequently they appear as #1 non-Australia birthplace across Sydney suburbs")
print("="*100)

for i, (country, count) in enumerate(country_frequency.most_common(5), 1):
    # Clean up country name for display
    country_display = country.replace('_', ' ')
    print(f"\n{i}. {country_display}")
    print(f"   Appears as #1 in {count} Sydney suburbs ({count/len(sydney_data)*100:.1f}% of Sydney suburbs)")

    # Show some example suburbs
    example_suburbs = [d['Suburb_Name'] for d in sydney_data if d['Top_Non_Australia_Country'] == country][:5]
    print(f"   Example suburbs: {', '.join(example_suburbs[:3])}")

# Create detailed results DataFrame
df_results = pd.DataFrame(sydney_data)
df_results = df_results.sort_values('Top_Non_Australia_Count', ascending=False)

# Save detailed results
output_file = '/home/user/Census/results_sydney_birthplace_top_countries.csv'
df_results.to_csv(output_file, index=False)
print(f"\n✓ Saved detailed results to: {output_file}")

# Show some interesting statistics
print("\n" + "="*100)
print("ADDITIONAL STATISTICS")
print("="*100)

print(f"\nTotal Sydney suburbs analyzed: {len(sydney_data):,}")
print(f"Unique countries appearing as #1 non-Australia: {len(country_frequency)}")

# Show top 10 suburbs by non-Australia population percentage
print("\nTop 10 Sydney suburbs by highest non-Australia birthplace concentration:")
df_top_concentration = df_results.nlargest(10, 'Percentage_Non_Aus')
for idx, row in df_top_concentration.iterrows():
    print(f"  {row['Suburb_Name']:40} | {row['Top_Non_Australia_Country'].replace('_', ' '):20} | "
          f"{row['Percentage_Non_Aus']:5.1f}% ({row['Top_Non_Australia_Count']:,} people)")

print("\n" + "="*100)
print("ANALYSIS COMPLETE!")
print("="*100)
