#!/usr/bin/env python3
"""
Housing Price Correlation Analysis

Analyzes the relationship between executive concentration and housing prices.
Identifies interesting outliers: expensive suburbs with low executive presence.
"""

import pandas as pd
import numpy as np

def main():
    print("="*130)
    print("HOUSING PRICE vs. EXECUTIVE CONCENTRATION CORRELATION ANALYSIS")
    print("="*130)
    print("\nLoading data...")

    # Load executive hotspots data from previous analysis
    hotspots_file = "results/top_50_executive_hotspots.csv"
    hotspots_df = pd.read_csv(hotspots_file)

    # Load housing price data (G02)
    housing_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G02_AUST_SAL.csv"
    housing_df = pd.read_csv(housing_file)

    # Load detailed executive profile data (has industry composition)
    profile_file = "results/executive_hotspots_detailed_profile.csv"
    try:
        profile_df = pd.read_csv(profile_file)
        has_industry_data = True
    except:
        has_industry_data = False

    # Load occupation data for all suburbs
    occupation_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G60A_AUST_SAL.csv"
    occupation_df = pd.read_csv(occupation_file)

    # Load suburb names
    metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
    geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
    sal_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

    print(f"Loaded housing data: {len(housing_df):,} suburbs")

    # Calculate manager concentration for all suburbs
    occupation_df['Total_Managers'] = (
        occupation_df['M_Tot_Managers'] + occupation_df['F_Tot_Managers']
    )
    occupation_df['Total_Employed'] = (
        occupation_df['M_Tot_Tot'] + occupation_df['F_Tot_Tot']
    )
    occupation_df['Total_Professionals'] = (
        occupation_df['M_Tot_Professionals'] + occupation_df['F_Tot_Professionals']
    )

    occupation_df['Manager_Concentration_Pct'] = (
        occupation_df['Total_Managers'] / occupation_df['Total_Employed'] * 100
    )
    occupation_df['Manager_Plus_Professional_Pct'] = (
        (occupation_df['Total_Managers'] + occupation_df['Total_Professionals']) /
        occupation_df['Total_Employed'] * 100
    )

    # Merge all data
    df = housing_df.merge(
        occupation_df[['SAL_CODE_2021', 'Manager_Concentration_Pct', 'Manager_Plus_Professional_Pct',
                       'Total_Managers', 'Total_Employed']],
        on='SAL_CODE_2021',
        how='inner'
    )

    # Merge suburb names
    df = df.merge(sal_df, left_on='SAL_CODE_2021', right_on='Census_Code_2021', how='left')
    df.rename(columns={'Census_Name_2021': 'Suburb_Name'}, inplace=True)

    # Load population data for filtering
    population_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G01_AUST_SAL.csv"
    population_df = pd.read_csv(population_file)
    df = df.merge(population_df[['SAL_CODE_2021', 'Tot_P_P']], on='SAL_CODE_2021', how='inner')
    df.rename(columns={'Tot_P_P': 'Total_Population'}, inplace=True)

    print(f"Merged dataset: {len(df):,} suburbs")

    # URBAN FILTER - same as executive hotspots analysis
    min_employed = 1000
    min_population = 2000

    urban_df = df[
        (df['Total_Employed'] >= min_employed) &
        (df['Total_Population'] >= min_population) &
        (df['Median_mortgage_repay_monthly'] > 0)  # Filter out zero/null mortgages
    ].copy()

    print(f"Urban suburbs with mortgage data: {len(urban_df):,}")

    # CORRELATION ANALYSIS
    print("\n" + "="*130)
    print("CORRELATION COEFFICIENTS")
    print("="*130)

    # Calculate correlations
    corr_mortgage_manager = urban_df['Median_mortgage_repay_monthly'].corr(urban_df['Manager_Concentration_Pct'])
    corr_mortgage_prof = urban_df['Median_mortgage_repay_monthly'].corr(urban_df['Manager_Plus_Professional_Pct'])
    corr_rent_manager = urban_df[urban_df['Median_rent_weekly'] > 0]['Median_rent_weekly'].corr(
        urban_df[urban_df['Median_rent_weekly'] > 0]['Manager_Concentration_Pct']
    )

    print(f"\nMedian Mortgage vs. Manager Concentration:           r = {corr_mortgage_manager:.3f}")
    print(f"Median Mortgage vs. Manager+Professional:             r = {corr_mortgage_prof:.3f}")
    print(f"Median Rent vs. Manager Concentration:                r = {corr_rent_manager:.3f}")

    if corr_mortgage_manager > 0.5:
        strength = "STRONG positive"
    elif corr_mortgage_manager > 0.3:
        strength = "MODERATE positive"
    else:
        strength = "WEAK"

    print(f"\nInterpretation: {strength} correlation between executive concentration and housing prices")

    # RESIDUAL ANALYSIS - Find outliers
    print("\n" + "="*130)
    print("OUTLIER IDENTIFICATION: High Price + Low Executive Concentration")
    print("="*130)

    # Define thresholds
    mortgage_threshold_75 = urban_df['Median_mortgage_repay_monthly'].quantile(0.75)
    mortgage_threshold_90 = urban_df['Median_mortgage_repay_monthly'].quantile(0.90)
    manager_threshold_25 = urban_df['Manager_Concentration_Pct'].quantile(0.25)

    print(f"\n75th percentile mortgage: ${mortgage_threshold_75:,.0f}/month")
    print(f"90th percentile mortgage: ${mortgage_threshold_90:,.0f}/month")
    print(f"25th percentile manager concentration: {manager_threshold_25:.1f}%")

    # QUADRANT 4: High Price + Low Executive
    outliers_q4 = urban_df[
        (urban_df['Median_mortgage_repay_monthly'] >= mortgage_threshold_75) &
        (urban_df['Manager_Concentration_Pct'] <= manager_threshold_25)
    ].copy()

    outliers_q4 = outliers_q4.sort_values('Median_mortgage_repay_monthly', ascending=False)

    print(f"\nFound {len(outliers_q4)} suburbs with HIGH housing prices but LOW executive concentration")
    print("\n" + "="*130)
    print("TOP 30 HIGH-PRICE, LOW-EXECUTIVE SUBURBS (The Interesting Outliers)")
    print("="*130)
    print(f"\nCriteria: Mortgage ≥ ${mortgage_threshold_75:,.0f}/month AND Manager % ≤ {manager_threshold_25:.1f}%\n")

    print(f"{'Rank':<5} {'Suburb':<40} {'Mortgage':<12} {'Mgr %':<8} {'M+P %':<8} {'Med Inc':<10}")
    print(f"{'':5} {'':40} {'$/month':<12} {'':8} {'':8} {'$/week':<10}")
    print("-" * 130)

    for idx, (_, row) in enumerate(outliers_q4.head(30).iterrows(), 1):
        suburb = str(row['Suburb_Name'])[:38]
        mortgage = row['Median_mortgage_repay_monthly']
        mgr_pct = row['Manager_Concentration_Pct']
        mp_pct = row['Manager_Plus_Professional_Pct']
        med_inc = row['Median_tot_prsnl_inc_weekly']

        print(f"{idx:<5} {suburb:<40} ${mortgage:>10,.0f}  {mgr_pct:>6.1f}%  {mp_pct:>6.1f}%  ${med_inc:>8,.0f}")

    # QUADRANT 1: High Price + High Executive (expected pattern)
    manager_threshold_75 = urban_df['Manager_Concentration_Pct'].quantile(0.75)

    q1_suburbs = urban_df[
        (urban_df['Median_mortgage_repay_monthly'] >= mortgage_threshold_75) &
        (urban_df['Manager_Concentration_Pct'] >= manager_threshold_75)
    ].copy()

    q1_suburbs = q1_suburbs.sort_values('Median_mortgage_repay_monthly', ascending=False)

    print("\n" + "="*130)
    print("HIGH-PRICE, HIGH-EXECUTIVE SUBURBS (Expected Pattern)")
    print("="*130)
    print(f"\nCriteria: Mortgage ≥ ${mortgage_threshold_75:,.0f}/month AND Manager % ≥ {manager_threshold_75:.1f}%\n")

    print(f"{'Rank':<5} {'Suburb':<40} {'Mortgage':<12} {'Mgr %':<8} {'M+P %':<8} {'Med Inc':<10}")
    print("-" * 130)

    for idx, (_, row) in enumerate(q1_suburbs.head(20).iterrows(), 1):
        suburb = str(row['Suburb_Name'])[:38]
        mortgage = row['Median_mortgage_repay_monthly']
        mgr_pct = row['Manager_Concentration_Pct']
        mp_pct = row['Manager_Plus_Professional_Pct']
        med_inc = row['Median_tot_prsnl_inc_weekly']

        print(f"{idx:<5} {suburb:<40} ${mortgage:>10,.0f}  {mgr_pct:>6.1f}%  {mp_pct:>6.1f}%  ${med_inc:>8,.0f}")

    # SUMMARY STATISTICS
    print("\n" + "="*130)
    print("SUMMARY STATISTICS BY QUADRANT")
    print("="*130)

    q1_count = len(q1_suburbs)
    q4_count = len(outliers_q4)

    print(f"\nQuadrant 1 (High Price + High Executive):  {q1_count:>4} suburbs  - Expected executive areas")
    print(f"Quadrant 4 (High Price + Low Executive):   {q4_count:>4} suburbs  - Interesting outliers!")

    print(f"\nAverage mortgage in Q1 (executive areas):  ${q1_suburbs['Median_mortgage_repay_monthly'].mean():>10,.0f}/month")
    print(f"Average mortgage in Q4 (outlier areas):    ${outliers_q4['Median_mortgage_repay_monthly'].mean():>10,.0f}/month")

    print(f"\nAverage manager % in Q1:                   {q1_suburbs['Manager_Concentration_Pct'].mean():>10.1f}%")
    print(f"Average manager % in Q4:                   {outliers_q4['Manager_Concentration_Pct'].mean():>10.1f}%")

    # EXPORT RESULTS
    output_q4 = "results/high_price_low_executive_outliers.csv"
    outliers_q4[['SAL_CODE_2021', 'Suburb_Name', 'Median_mortgage_repay_monthly',
                 'Median_rent_weekly', 'Manager_Concentration_Pct',
                 'Manager_Plus_Professional_Pct', 'Median_tot_prsnl_inc_weekly',
                 'Total_Population', 'Total_Employed']].to_csv(output_q4, index=False)

    output_full = "results/housing_price_correlation_analysis.csv"
    urban_df[['SAL_CODE_2021', 'Suburb_Name', 'Median_mortgage_repay_monthly',
              'Median_rent_weekly', 'Manager_Concentration_Pct',
              'Manager_Plus_Professional_Pct', 'Median_tot_prsnl_inc_weekly',
              'Total_Population', 'Total_Employed']].to_csv(output_full, index=False)

    print(f"\n\nResults exported:")
    print(f"  - {output_q4}")
    print(f"  - {output_full}")
    print("="*130)

if __name__ == "__main__":
    main()
