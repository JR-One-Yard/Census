#!/usr/bin/env python3
"""
Analyze 2021 Australian Census data to find suburbs with highest concentration of managers.
Final version with proper suburb name mapping
"""

import pandas as pd

def main():
    print("Loading Census data...")

    # Load occupation data (G60A) - contains manager counts by age and sex
    occupation_file = "2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS/SAL/AUS/2021Census_G60A_AUST_SAL.csv"
    occupation_df = pd.read_csv(occupation_file)

    print(f"Loaded occupation data: {len(occupation_df):,} suburbs")

    # Calculate total managers (male + female)
    occupation_df['Total_Managers'] = (
        occupation_df['M_Tot_Managers'] +
        occupation_df['F_Tot_Managers']
    )

    # Calculate total employed from occupation data
    occupation_df['Total_Employed'] = (
        occupation_df['M_Tot_Tot'] +
        occupation_df['F_Tot_Tot']
    )

    # Load suburb names from metadata
    print("Loading suburb names from metadata...")
    metadata_file = "2021_GCP_all_for_AUS_short-header/Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx"

    # Read Non-ABS structures and filter for SAL
    geo_df = pd.read_excel(metadata_file, sheet_name='2021_ASGS_Non_ABS_Structures')
    sal_df = geo_df[geo_df['ASGS_Structure'] == 'SAL'][['Census_Code_2021', 'Census_Name_2021']].copy()

    print(f"Loaded {len(sal_df):,} suburb names")

    # Merge suburb names with occupation data
    occupation_df = occupation_df.merge(
        sal_df,
        left_on='SAL_CODE_2021',
        right_on='Census_Code_2021',
        how='left'
    )

    occupation_df.rename(columns={'Census_Name_2021': 'Suburb_Name'}, inplace=True)
    occupation_df['Suburb_Name'] = occupation_df['Suburb_Name'].fillna('Unknown')

    # Filter out suburbs with very few employed people (to avoid skewed percentages)
    min_employed = 100
    occupation_df = occupation_df[occupation_df['Total_Employed'] >= min_employed].copy()

    # Calculate manager concentration (percentage)
    occupation_df['Manager_Concentration_Pct'] = (
        occupation_df['Total_Managers'] / occupation_df['Total_Employed'] * 100
    )

    # Sort by manager concentration
    top_suburbs = occupation_df.nlargest(50, 'Manager_Concentration_Pct').copy()

    # Output results
    print("\n" + "="*130)
    print("TOP 50 AUSTRALIAN SUBURBS BY MANAGER CONCENTRATION (2021 Census)")
    print("="*130)
    print(f"\nFiltered to suburbs/localities with at least {min_employed} employed persons")
    print(f"Manager Concentration = (Total Managers / Total Employed Persons) × 100")
    print("\nNote: 'Managers' includes CEOs, Directors, General Managers, and Specialist Managers")
    print("      as classified under ANZSCO Major Group 1 - Managers\n")

    print(f"{'Rank':<6} {'SAL Code':<12} {'Suburb/Locality':<45} {'Managers':<10} {'Employed':<10} {'Conc %':<10}")
    print("-" * 130)

    for idx, (_, row) in enumerate(top_suburbs.iterrows(), 1):
        sal_code = row['SAL_CODE_2021']
        suburb = str(row['Suburb_Name'])[:43]  # Truncate long names
        managers = int(row['Total_Managers'])
        employed = int(row['Total_Employed'])
        concentration = row['Manager_Concentration_Pct']

        print(f"{idx:<6} {sal_code:<12} {suburb:<45} {managers:<10,} {employed:<10,} {concentration:>9.2f}%")

    # Export to CSV
    output_file = "top_50_manager_suburbs.csv"
    export_cols = ['SAL_CODE_2021', 'Suburb_Name', 'Total_Managers', 'Total_Employed', 'Manager_Concentration_Pct']
    top_suburbs[export_cols].to_csv(output_file, index=False)

    print(f"\n\nDetailed results exported to: {output_file}")

    # Summary statistics
    print("\n" + "="*130)
    print("SUMMARY STATISTICS")
    print("="*130)
    print(f"Total suburbs/localities analyzed (with ≥{min_employed} employed persons): {len(occupation_df):,}")
    print(f"Average manager concentration: {occupation_df['Manager_Concentration_Pct'].mean():.2f}%")
    print(f"Median manager concentration: {occupation_df['Manager_Concentration_Pct'].median():.2f}%")
    print(f"Highest concentration: {occupation_df['Manager_Concentration_Pct'].max():.2f}% ({top_suburbs.iloc[0]['Suburb_Name']})")
    print(f"Standard deviation: {occupation_df['Manager_Concentration_Pct'].std():.2f}%")

    # Show distribution
    print(f"\nDistribution of manager concentration across all analyzed suburbs:")
    print(f"  > 30%:   {len(occupation_df[occupation_df['Manager_Concentration_Pct'] > 30]):>5,} suburbs ({len(occupation_df[occupation_df['Manager_Concentration_Pct'] > 30])/len(occupation_df)*100:.1f}%)")
    print(f"  20-30%:  {len(occupation_df[(occupation_df['Manager_Concentration_Pct'] >= 20) & (occupation_df['Manager_Concentration_Pct'] < 30)]):>5,} suburbs ({len(occupation_df[(occupation_df['Manager_Concentration_Pct'] >= 20) & (occupation_df['Manager_Concentration_Pct'] < 30)])/len(occupation_df)*100:.1f}%)")
    print(f"  10-20%:  {len(occupation_df[(occupation_df['Manager_Concentration_Pct'] >= 10) & (occupation_df['Manager_Concentration_Pct'] < 20)]):>5,} suburbs ({len(occupation_df[(occupation_df['Manager_Concentration_Pct'] >= 10) & (occupation_df['Manager_Concentration_Pct'] < 20)])/len(occupation_df)*100:.1f}%)")
    print(f"  < 10%:   {len(occupation_df[occupation_df['Manager_Concentration_Pct'] < 10]):>5,} suburbs ({len(occupation_df[occupation_df['Manager_Concentration_Pct'] < 10])/len(occupation_df)*100:.1f}%)")

    # Additional insights
    print(f"\n" + "="*130)
    print("ADDITIONAL INSIGHTS")
    print("="*130)

    # Top 10 suburbs by absolute number of managers
    top_absolute = occupation_df.nlargest(10, 'Total_Managers')
    print("\nTop 10 suburbs by absolute number of managers:")
    for idx, (_, row) in enumerate(top_absolute.iterrows(), 1):
        print(f"  {idx:>2}. {row['Suburb_Name']:<40} {int(row['Total_Managers']):>6,} managers ({row['Manager_Concentration_Pct']:.1f}%)")

    print("\n" + "="*130)

if __name__ == "__main__":
    main()
