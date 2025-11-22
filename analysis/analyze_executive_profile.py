#!/usr/bin/env python3
"""
Deep dive analysis: Industry composition and education levels in executive hotspots.
Validates the CEO/Director demographic through industry and qualification data.
"""

import pandas as pd
import numpy as np

def main():
    print("="*130)
    print("EXECUTIVE DEMOGRAPHIC VALIDATION: INDUSTRY & EDUCATION ANALYSIS")
    print("="*130)
    print("\nLoading Census data...")

    # Load our top executive hotspots from previous analysis
    top_hotspots_file = "results/top_50_executive_hotspots.csv"
    hotspots_df = pd.read_csv(top_hotspots_file)
    top_30_codes = hotspots_df.head(30)['SAL_CODE_2021'].tolist()

    print(f"Loaded top 30 executive hotspots for detailed analysis")

    # Load industry data (G54C and G54D - employment by industry, Persons)
    # G54C has Finance, Prof/Sci, etc. G54D has remaining industries and totals
    industry_c_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G54C_AUST_SAL.csv"
    industry_d_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G54D_AUST_SAL.csv"

    industry_c_df = pd.read_csv(industry_c_file)
    industry_d_df = pd.read_csv(industry_d_file)

    # Merge the two tables on SAL_CODE
    industry_df = industry_c_df.merge(industry_d_df, on='SAL_CODE_2021', how='inner')

    # Skip education data for now - focus on industry composition
    # education_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G16B_AUST_SAL.csv"
    # education_df = pd.read_csv(education_file)

    # Load suburb names
    metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
    geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
    sal_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

    print(f"Loaded industry data: {len(industry_df):,} suburbs")

    # Calculate industry totals for each suburb (using Persons data)
    industry_df['Total_Finance_Insurance'] = industry_df['P_Fin_Insur_Tot']
    industry_df['Total_Professional_Scientific'] = industry_df['P_Pro_scien_tec_Tot']
    industry_df['Total_Info_Media_Telecom'] = industry_df['P_Info_media_teleco_Tot']
    industry_df['Total_Public_Admin'] = industry_df['P_Public_admin_sfty_Tot']
    industry_df['Total_Real_Estate'] = industry_df['P_RtnHir_REst_Tot']

    # Total employed in all industries
    industry_df['Total_All_Industries'] = industry_df['P_Tot_Tot']

    # Calculate "Executive Industries" percentage (Finance + Prof/Sci + Info/Media)
    industry_df['Executive_Industries_Total'] = (
        industry_df['Total_Finance_Insurance'] +
        industry_df['Total_Professional_Scientific'] +
        industry_df['Total_Info_Media_Telecom'] +
        industry_df['Total_Public_Admin']
    )

    industry_df['Executive_Industries_Pct'] = (
        industry_df['Executive_Industries_Total'] / industry_df['Total_All_Industries'] * 100
    )

    # Skip education metrics for now - complex to map qualification columns

    # Filter to top 30 hotspots
    top_industry = industry_df[industry_df['SAL_CODE_2021'].isin(top_30_codes)].copy()

    # Merge with suburb names
    top_industry = top_industry.merge(sal_df, left_on='SAL_CODE_2021', right_on='Census_Code_2021', how='left')

    # Merge with hotspots data
    comprehensive_df = hotspots_df.head(30).merge(
        top_industry[['SAL_CODE_2021', 'Total_Finance_Insurance', 'Total_Professional_Scientific',
                      'Total_Info_Media_Telecom', 'Total_Public_Admin', 'Executive_Industries_Pct',
                      'Total_All_Industries']],
        on='SAL_CODE_2021',
        how='left'
    )

    # Sort by Executive Score
    comprehensive_df = comprehensive_df.sort_values('Executive_Score', ascending=False)

    # OUTPUT RESULTS
    print("\n" + "="*130)
    print("TOP 30 EXECUTIVE HOTSPOTS - INDUSTRY COMPOSITION PROFILE")
    print("="*130)
    print("\nKey 'Executive Industries': Finance/Insurance, Professional/Scientific/Technical, Info/Media/Telecom, Public Admin\n")

    print(f"{'Rank':<5} {'Suburb':<35} {'Exec':<6} {'Exec Ind':<10} {'Finance':<9} {'Prof/Sci':<10} {'Info/Med':<9} {'Pub Admin':<10}")
    print(f"{'':5} {'':35} {'Score':<6} {'%':<10} {'%':<9} {'%':<10} {'%':<9} {'%':<10}")
    print("-" * 130)

    for idx, (_, row) in enumerate(comprehensive_df.iterrows(), 1):
        suburb = str(row['Suburb_Name'])[:33]
        exec_score = row['Executive_Score']
        exec_ind_pct = row['Executive_Industries_Pct']

        # Calculate percentages for specific industries
        finance_pct = (row['Total_Finance_Insurance'] / row['Total_All_Industries'] * 100) if row['Total_All_Industries'] > 0 else 0
        prof_pct = (row['Total_Professional_Scientific'] / row['Total_All_Industries'] * 100) if row['Total_All_Industries'] > 0 else 0
        info_pct = (row['Total_Info_Media_Telecom'] / row['Total_All_Industries'] * 100) if row['Total_All_Industries'] > 0 else 0
        pub_pct = (row['Total_Public_Admin'] / row['Total_All_Industries'] * 100) if row['Total_All_Industries'] > 0 else 0

        print(f"{idx:<5} {suburb:<35} {exec_score:>5.1f}  {exec_ind_pct:>8.1f}%  {finance_pct:>7.1f}%  {prof_pct:>8.1f}%  {info_pct:>7.1f}%  {pub_pct:>8.1f}%")

    # INDUSTRY BREAKDOWN
    print("\n" + "="*130)
    print("INDUSTRY COMPOSITION ANALYSIS")
    print("="*130)

    # Top 10 by Finance/Insurance concentration
    print("\nTop 10 suburbs by Finance/Insurance employment:")
    top_industry_sorted = top_industry.copy()
    top_industry_sorted['Finance_Pct'] = (
        top_industry_sorted['Total_Finance_Insurance'] / top_industry_sorted['Total_All_Industries'] * 100
    )
    top_finance = top_industry_sorted.nlargest(10, 'Finance_Pct')

    for idx, (_, row) in enumerate(top_finance.iterrows(), 1):
        suburb = str(row['Census_Name_2021'])[:40]
        finance_pct = (row['Total_Finance_Insurance'] / row['Total_All_Industries'] * 100)
        print(f"  {idx:>2}. {suburb:<40} {finance_pct:>6.1f}% ({int(row['Total_Finance_Insurance']):,} workers)")

    # Top 10 by Professional/Scientific concentration
    print("\nTop 10 suburbs by Professional/Scientific/Technical employment:")
    top_industry_sorted['ProfSci_Pct'] = (
        top_industry_sorted['Total_Professional_Scientific'] / top_industry_sorted['Total_All_Industries'] * 100
    )
    top_prof = top_industry_sorted.nlargest(10, 'ProfSci_Pct')

    for idx, (_, row) in enumerate(top_prof.iterrows(), 1):
        suburb = str(row['Census_Name_2021'])[:40]
        prof_pct = (row['Total_Professional_Scientific'] / row['Total_All_Industries'] * 100)
        print(f"  {idx:>2}. {suburb:<40} {prof_pct:>6.1f}% ({int(row['Total_Professional_Scientific']):,} workers)")

    # SKIP EDUCATION ANALYSIS FOR NOW

    # SUMMARY STATISTICS
    print("\n" + "="*130)
    print("COMPARATIVE STATISTICS: TOP 30 HOTSPOTS vs NATIONAL")
    print("="*130)

    # Calculate national averages
    national_exec_ind = industry_df['Executive_Industries_Pct'].mean()
    hotspot_exec_ind = comprehensive_df['Executive_Industries_Pct'].mean()

    print(f"\n{'Metric':<50} {'Top 30 Hotspots':<20} {'National Average':<20} {'Multiple':<10}")
    print("-" * 130)
    print(f"{'Executive Industries %':<50} {hotspot_exec_ind:>17.1f}%  {national_exec_ind:>17.1f}%  {hotspot_exec_ind/national_exec_ind:>8.1f}x")

    # Export comprehensive results
    output_file = "results/executive_hotspots_detailed_profile.csv"
    comprehensive_df.to_csv(output_file, index=False)

    print(f"\n\nDetailed results exported to: {output_file}")
    print("="*130)

if __name__ == "__main__":
    main()
