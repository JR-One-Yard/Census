#!/usr/bin/env python3
"""
Refined analysis to identify genuine CEO/Director demographic hotspots.
Cross-references manager concentration with median income and urban characteristics.
"""

import pandas as pd
import numpy as np

def main():
    print("="*120)
    print("REFINED ANALYSIS: CEO/DIRECTOR DEMOGRAPHIC HOTSPOTS")
    print("="*120)
    print("\nLoading Census data...")

    # Load occupation data (G60A)
    occupation_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G60A_AUST_SAL.csv"
    occupation_df = pd.read_csv(occupation_file)

    # Load median income data (G02)
    income_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G02_AUST_SAL.csv"
    income_df = pd.read_csv(income_file)

    # Load population data (G01) for urban filtering
    population_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G01_AUST_SAL.csv"
    population_df = pd.read_csv(population_file)

    # Load suburb names
    metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
    geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
    sal_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

    print(f"Loaded: {len(occupation_df):,} suburbs (occupation), {len(income_df):,} suburbs (income), {len(population_df):,} suburbs (population)")

    # Calculate manager metrics
    occupation_df['Total_Managers'] = (
        occupation_df['M_Tot_Managers'] + occupation_df['F_Tot_Managers']
    )
    occupation_df['Total_Professionals'] = (
        occupation_df['M_Tot_Professionals'] + occupation_df['F_Tot_Professionals']
    )
    occupation_df['Total_Employed'] = (
        occupation_df['M_Tot_Tot'] + occupation_df['F_Tot_Tot']
    )

    # Merge all datasets
    df = occupation_df.merge(income_df, on='SAL_CODE_2021', how='inner')
    df = df.merge(population_df[['SAL_CODE_2021', 'Tot_P_P']], on='SAL_CODE_2021', how='inner')
    df = df.merge(sal_df, left_on='SAL_CODE_2021', right_on='Census_Code_2021', how='left')
    df.rename(columns={'Census_Name_2021': 'Suburb_Name', 'Tot_P_P': 'Total_Population'}, inplace=True)

    print(f"Merged dataset: {len(df):,} suburbs")

    # Calculate metrics
    df['Manager_Concentration_Pct'] = (df['Total_Managers'] / df['Total_Employed'] * 100)
    df['Professional_Concentration_Pct'] = (df['Total_Professionals'] / df['Total_Employed'] * 100)
    df['Manager_Plus_Professional_Pct'] = (
        (df['Total_Managers'] + df['Total_Professionals']) / df['Total_Employed'] * 100
    )

    # URBAN FILTER: Focus on substantial urban areas
    # Criteria:
    # - Total employed >= 1000 (excludes tiny rural communities)
    # - Total population >= 2000 (ensures it's a real suburb, not a farm cluster)
    min_employed = 1000
    min_population = 2000

    print(f"\nApplying urban filters:")
    print(f"  - Minimum employed persons: {min_employed:,}")
    print(f"  - Minimum population: {min_population:,}")

    urban_df = df[
        (df['Total_Employed'] >= min_employed) &
        (df['Total_Population'] >= min_population)
    ].copy()

    print(f"  - Urban suburbs identified: {len(urban_df):,} (from {len(df):,} total)")

    # HIGH-INCOME FILTER: Focus on affluent areas
    # Use median personal income as a proxy for executive presence
    median_income_threshold = df['Median_tot_prsnl_inc_weekly'].quantile(0.75)  # Top 25%

    print(f"  - Median personal income threshold (75th percentile): ${median_income_threshold:,.0f}/week")

    affluent_urban_df = urban_df[
        urban_df['Median_tot_prsnl_inc_weekly'] >= median_income_threshold
    ].copy()

    print(f"  - Affluent urban suburbs: {len(affluent_urban_df):,}")

    # Create a composite "Executive Score"
    # Factors:
    # 1. Manager concentration (weight: 40%)
    # 2. Manager + Professional concentration (weight: 30%)
    # 3. Median personal income (weight: 30%)

    # Normalize metrics to 0-100 scale
    affluent_urban_df['Manager_Score'] = (
        (affluent_urban_df['Manager_Concentration_Pct'] - affluent_urban_df['Manager_Concentration_Pct'].min()) /
        (affluent_urban_df['Manager_Concentration_Pct'].max() - affluent_urban_df['Manager_Concentration_Pct'].min()) * 100
    )

    affluent_urban_df['Prof_Score'] = (
        (affluent_urban_df['Manager_Plus_Professional_Pct'] - affluent_urban_df['Manager_Plus_Professional_Pct'].min()) /
        (affluent_urban_df['Manager_Plus_Professional_Pct'].max() - affluent_urban_df['Manager_Plus_Professional_Pct'].min()) * 100
    )

    affluent_urban_df['Income_Score'] = (
        (affluent_urban_df['Median_tot_prsnl_inc_weekly'] - affluent_urban_df['Median_tot_prsnl_inc_weekly'].min()) /
        (affluent_urban_df['Median_tot_prsnl_inc_weekly'].max() - affluent_urban_df['Median_tot_prsnl_inc_weekly'].min()) * 100
    )

    affluent_urban_df['Executive_Score'] = (
        affluent_urban_df['Manager_Score'] * 0.40 +
        affluent_urban_df['Prof_Score'] * 0.30 +
        affluent_urban_df['Income_Score'] * 0.30
    )

    # Sort by Executive Score
    top_suburbs = affluent_urban_df.nlargest(50, 'Executive_Score').copy()

    # Output results
    print("\n" + "="*140)
    print("TOP 50 EXECUTIVE/DIRECTOR DEMOGRAPHIC HOTSPOTS")
    print("="*140)
    print("\nFilters Applied:")
    print(f"  • Urban areas only (≥{min_employed:,} employed, ≥{min_population:,} population)")
    print(f"  • High-income areas only (median income ≥${median_income_threshold:,.0f}/week)")
    print(f"  • Executive Score = 40% Manager Concentration + 30% Manager+Professional % + 30% Income")
    print("\n")

    print(f"{'Rank':<5} {'Suburb/Locality':<35} {'Exec':<6} {'Mgrs':<6} {'M+P%':<7} {'Med Inc':<9} {'Pop':<8} {'Employed':<9}")
    print(f"{'':5} {'':35} {'Score':<6} {'%':<6} {'':7} {'$/wk':<9} {'':8} {'':9}")
    print("-" * 140)

    for idx, (_, row) in enumerate(top_suburbs.iterrows(), 1):
        suburb = str(row['Suburb_Name'])[:33]
        exec_score = row['Executive_Score']
        mgr_pct = row['Manager_Concentration_Pct']
        mp_pct = row['Manager_Plus_Professional_Pct']
        med_inc = row['Median_tot_prsnl_inc_weekly']
        pop = int(row['Total_Population'])
        employed = int(row['Total_Employed'])

        print(f"{idx:<5} {suburb:<35} {exec_score:>5.1f}  {mgr_pct:>5.1f}% {mp_pct:>6.1f}% ${med_inc:>7,.0f}  {pop:>7,} {employed:>8,}")

    # Export to CSV
    output_file = "top_50_executive_hotspots.csv"
    export_cols = [
        'SAL_CODE_2021', 'Suburb_Name', 'Executive_Score',
        'Manager_Concentration_Pct', 'Manager_Plus_Professional_Pct',
        'Total_Managers', 'Total_Professionals', 'Total_Employed',
        'Median_tot_prsnl_inc_weekly', 'Median_tot_hhd_inc_weekly',
        'Total_Population'
    ]
    top_suburbs[export_cols].to_csv(output_file, index=False)

    print(f"\n\nResults exported to: {output_file}")

    # Comparative analysis
    print("\n" + "="*140)
    print("COMPARATIVE INSIGHTS")
    print("="*140)

    # Compare top 10 from this analysis vs original rural-heavy analysis
    print("\nTop 10 by Executive Score (this analysis - urban, high-income focus):")
    for idx, (_, row) in enumerate(top_suburbs.head(10).iterrows(), 1):
        print(f"  {idx:>2}. {row['Suburb_Name']:<40} (Score: {row['Executive_Score']:.1f}, Mgrs: {row['Manager_Concentration_Pct']:.1f}%, Income: ${row['Median_tot_prsnl_inc_weekly']:,.0f}/wk)")

    # Show geographic distribution
    print("\n" + "="*140)
    print("SUMMARY STATISTICS")
    print("="*140)
    print(f"Affluent urban suburbs analyzed: {len(affluent_urban_df):,}")
    print(f"Average manager concentration: {affluent_urban_df['Manager_Concentration_Pct'].mean():.2f}%")
    print(f"Average manager + professional concentration: {affluent_urban_df['Manager_Plus_Professional_Pct'].mean():.2f}%")
    print(f"Average median personal income: ${affluent_urban_df['Median_tot_prsnl_inc_weekly'].mean():,.2f}/week (${affluent_urban_df['Median_tot_prsnl_inc_weekly'].mean()*52:,.0f}/year)")
    print(f"Average median household income: ${affluent_urban_df['Median_tot_hhd_inc_weekly'].mean():,.2f}/week (${affluent_urban_df['Median_tot_hhd_inc_weekly'].mean()*52:,.0f}/year)")

    print("\n" + "="*140)

if __name__ == "__main__":
    main()
