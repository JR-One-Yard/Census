#!/usr/bin/env python3
"""
Suburban Transformation Prediction Engine
==========================================
Analyze dwelling type distributions across LGAs and SA1s to identify:
- High detached house % near urban centers (subdivision potential)
- Low medium/high-density % but high income/education (luxury apartment demand)
- Aging population in large houses (downsizing wave incoming)
- Time-decay models for housing stock transformation
- Comprehensive redevelopment readiness scores
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Base path for census data
BASE_PATH = Path("/home/user/Census/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS")

class SuburbanTransformationEngine:
    """Main engine for analyzing suburban transformation potential"""

    def __init__(self):
        self.lga_data = {}
        self.sa1_data = {}
        self.urban_centers = None
        print("🏗️  Suburban Transformation Prediction Engine initialized")

    def load_dwelling_data(self, geography='LGA'):
        """Load dwelling structure data (G36) for a geography level"""
        print(f"\n📂 Loading dwelling structure data for {geography}...")

        file_path = BASE_PATH / geography / "AUS" / f"2021Census_G36_AUST_{geography}.csv"
        df = pd.read_csv(file_path)

        # Extract dwelling type totals from G36
        code_col = f"{geography}_CODE_2021"

        # G36 contains: Separate_house, SD/row/terrace/townhouse, Flat/apartment, Other
        # We need to aggregate across all the income/mortgage categories

        # Find columns for each dwelling type
        separate_cols = [col for col in df.columns if 'Separate_h' in col and 'Tot_DS' not in col]
        semi_cols = [col for col in df.columns if 'sd_r' in col and 'Tot_DS' not in col]
        flat_cols = [col for col in df.columns if 'Flat_apart' in col or 'Flt_apart' in col and 'Tot_DS' not in col]
        other_cols = [col for col in df.columns if 'Other_dwg' in col and 'Tot_DS' not in col]

        # Use the correct G36 column names
        result = pd.DataFrame()
        result[code_col] = df[code_col]
        result['separate_house'] = df['OPDs_Separate_house_Dwellings']
        result['semi_attached'] = df['OPDs_SD_r_t_h_th_Tot_Dwgs']
        result['flat_apartment'] = df['OPDs_Flt_apart_Tot_Dwgs']
        result['other_dwelling'] = df['OPDs_Other_dwelling_Tot_Dwgs']
        result['total_dwellings'] = df['Total_PDs_Dwellings']

        # Calculate percentages
        result['pct_separate'] = (result['separate_house'] / result['total_dwellings'] * 100).round(2)
        result['pct_semi_attached'] = (result['semi_attached'] / result['total_dwellings'] * 100).round(2)
        result['pct_apartment'] = (result['flat_apartment'] / result['total_dwellings'] * 100).round(2)
        result['pct_other'] = (result['other_dwelling'] / result['total_dwellings'] * 100).round(2)

        # Calculate density metrics
        result['pct_low_density'] = result['pct_separate']  # Only separate houses
        result['pct_medium_density'] = result['pct_semi_attached']  # Townhouses, row houses
        result['pct_high_density'] = result['pct_apartment']  # Apartments

        print(f"   ✓ Loaded {len(result)} {geography} areas with dwelling data")
        return result

    def load_age_data(self, geography='LGA'):
        """Load age distribution data (G02 for median, G04B for 55+ ages)"""
        print(f"\n📂 Loading age data for {geography}...")

        # Load G02 for median age
        g02_path = BASE_PATH / geography / "AUS" / f"2021Census_G02_AUST_{geography}.csv"
        g02 = pd.read_csv(g02_path)

        code_col = f"{geography}_CODE_2021"
        result = pd.DataFrame()
        result[code_col] = g02[code_col]
        result['median_age'] = g02['Median_age_persons']

        # Load G04B for 55+ age distribution
        g04b_path = BASE_PATH / geography / "AUS" / f"2021Census_G04B_AUST_{geography}.csv"
        g04b = pd.read_csv(g04b_path)

        # Calculate percentage of population over 55 (potential downsizers)
        # Use Tot_P for total population
        total_pop = g04b['Tot_P']

        # Age groups 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85-89, 90-94, 95-99, 100+
        age_55_plus = g04b['Age_yr_55_59_P'] + g04b['Age_yr_60_64_P'] + g04b['Age_yr_65_69_P'] + \
                      g04b['Age_yr_70_74_P'] + g04b['Age_yr_75_79_P'] + g04b['Age_yr_80_84_P'] + \
                      g04b['Age_yr_85_89_P'] + g04b['Age_yr_90_94_P'] + g04b['Age_yr_95_99_P'] + \
                      g04b['Age_yr_100_yr_over_P']

        result['pct_age_55_plus'] = (age_55_plus / total_pop * 100).round(2)
        result['total_population'] = total_pop

        print(f"   ✓ Loaded age data for {len(result)} {geography} areas")
        return result

    def load_income_data(self, geography='LGA'):
        """Load income data (G02 for median income)"""
        print(f"\n📂 Loading income data for {geography}...")

        g02_path = BASE_PATH / geography / "AUS" / f"2021Census_G02_AUST_{geography}.csv"
        g02 = pd.read_csv(g02_path)

        code_col = f"{geography}_CODE_2021"
        result = pd.DataFrame()
        result[code_col] = g02[code_col]
        result['median_personal_income'] = g02['Median_tot_prsnl_inc_weekly']
        result['median_household_income'] = g02['Median_tot_hhd_inc_weekly']
        result['median_family_income'] = g02['Median_tot_fam_inc_weekly']

        print(f"   ✓ Loaded income data for {len(result)} {geography} areas")
        return result

    def load_education_data(self, geography='LGA'):
        """Load education data (G49 for tertiary qualifications)"""
        print(f"\n📂 Loading education data for {geography}...")

        # Load G49A (Males) and G49B (Females and Persons)
        g49a_path = BASE_PATH / geography / "AUS" / f"2021Census_G49A_AUST_{geography}.csv"
        g49b_path = BASE_PATH / geography / "AUS" / f"2021Census_G49B_AUST_{geography}.csv"

        g49a = pd.read_csv(g49a_path)
        g49b = pd.read_csv(g49b_path)

        code_col = f"{geography}_CODE_2021"
        result = pd.DataFrame()
        result[code_col] = g49a[code_col]

        # Count people with Bachelor degree or higher (Postgrad + Grad Cert/Dip + Bachelor)
        # Using the total columns from G49B (which has Persons data)

        # Find all Postgraduate Degree columns
        postgrad_cols = [col for col in g49b.columns if 'P_PGrad_Deg' in col and 'Tot' not in col]
        grad_cert_cols = [col for col in g49b.columns if 'P_GradDip_and_GradCert' in col and 'Tot' not in col]
        bachelor_cols = [col for col in g49b.columns if 'P_BachDeg' in col and 'Tot' not in col]

        # Sum across all age groups
        postgrad_total = g49b[postgrad_cols].sum(axis=1) if postgrad_cols else 0
        grad_cert_total = g49b[grad_cert_cols].sum(axis=1) if grad_cert_cols else 0
        bachelor_total = g49b[bachelor_cols].sum(axis=1) if bachelor_cols else 0

        tertiary_total = postgrad_total + grad_cert_total + bachelor_total

        # Get total population with any qualification
        total_qualified = g49b['P_Tot_Total']

        result['tertiary_qualified'] = tertiary_total
        result['total_qualified'] = total_qualified
        result['pct_tertiary'] = (tertiary_total / total_qualified * 100).round(2)

        # Handle division by zero
        result['pct_tertiary'] = result['pct_tertiary'].replace([np.inf, -np.inf], 0).fillna(0)

        print(f"   ✓ Loaded education data for {len(result)} {geography} areas")
        return result

    def identify_urban_centers(self):
        """Identify major urban centers from GCCSA data"""
        print("\n📂 Identifying major urban centers (GCCSA)...")

        # Load GCCSA population data
        gccsa_path = BASE_PATH / "GCCSA" / "AUS" / "2021Census_G01_AUST_GCCSA.csv"
        gccsa = pd.read_csv(gccsa_path)

        # GCCSAs are the major capital city statistical areas
        # Higher population = more urban
        result = pd.DataFrame()
        result['gccsa_code'] = gccsa['GCCSA_CODE_2021']
        result['gccsa_name'] = gccsa['GCCSA_CODE_2021']  # We'll map names later if needed
        result['population'] = gccsa['Tot_P_P']

        # Rank by population (higher = more urban)
        result['urban_rank'] = result['population'].rank(ascending=False)
        result['is_major_urban'] = result['urban_rank'] <= 8  # Top 8 capital cities

        print(f"   ✓ Identified {result['is_major_urban'].sum()} major urban centers")
        self.urban_centers = result
        return result

    def calculate_urban_proximity_score(self, data, geography='LGA'):
        """
        Calculate urban proximity score for each area
        For simplicity, we'll use population density as a proxy
        Higher population = closer to urban center
        """
        print(f"\n📊 Calculating urban proximity scores for {geography}...")

        # Use population as a proxy for urban proximity
        # In a real analysis, you'd use actual geographic coordinates
        data['urban_proximity_score'] = (data['total_population'].rank(pct=True) * 100).round(2)

        print(f"   ✓ Calculated urban proximity scores")
        return data

    def analyze_subdivision_potential(self, data, geography='LGA'):
        """
        Identify areas with high subdivision potential:
        - High % of separate houses (>70%)
        - High urban proximity score (>60)
        - Good population base (>5000)
        """
        print(f"\n🔍 Analyzing subdivision potential for {geography}...")

        # Create subdivision potential score (0-100)
        score = 0

        # Component 1: High detached house percentage (0-40 points)
        detached_score = np.minimum(data['pct_separate'] / 70 * 40, 40)

        # Component 2: Urban proximity (0-40 points)
        urban_score = data['urban_proximity_score'] * 0.4

        # Component 3: Population size penalty for very small areas (0-20 points)
        pop_score = np.minimum(data['total_population'] / 10000 * 20, 20)

        data['subdivision_potential_score'] = (detached_score + urban_score + pop_score).round(2)

        # Flag high potential areas
        data['high_subdivision_potential'] = (
            (data['pct_separate'] >= 70) &
            (data['urban_proximity_score'] >= 60) &
            (data['total_population'] >= 5000)
        )

        high_count = data['high_subdivision_potential'].sum()
        print(f"   ✓ Found {high_count} areas with high subdivision potential")

        return data

    def analyze_luxury_apartment_demand(self, data, geography='LGA'):
        """
        Identify areas with luxury apartment demand:
        - Low medium/high density % (<20% apartments)
        - High income (top 30%)
        - High education (top 30%)
        """
        print(f"\n🔍 Analyzing luxury apartment demand for {geography}...")

        # Calculate income and education percentiles
        income_percentile = data['median_household_income'].rank(pct=True) * 100
        education_percentile = data['pct_tertiary'].rank(pct=True) * 100

        # Create luxury apartment demand score (0-100)
        # Component 1: Low current apartment % = higher demand (0-30 points)
        # Inverse relationship: lower apartment % = higher score
        low_density_score = np.maximum(0, (30 - data['pct_apartment']) / 30 * 30)

        # Component 2: High income (0-35 points)
        income_score = income_percentile * 0.35

        # Component 3: High education (0-35 points)
        education_score = education_percentile * 0.35

        data['luxury_apartment_demand_score'] = (
            low_density_score + income_score + education_score
        ).round(2)

        # Flag high demand areas
        data['high_luxury_demand'] = (
            (data['pct_apartment'] < 20) &
            (income_percentile >= 70) &
            (education_percentile >= 70)
        )

        high_count = data['high_luxury_demand'].sum()
        print(f"   ✓ Found {high_count} areas with high luxury apartment demand")

        return data

    def analyze_downsizing_wave(self, data, geography='LGA'):
        """
        Identify areas with downsizing wave incoming:
        - Aging population (>30% aged 55+)
        - High % of separate houses (>60%)
        - Good income (to afford downsizing)
        """
        print(f"\n🔍 Analyzing downsizing wave potential for {geography}...")

        # Create downsizing wave score (0-100)
        # Component 1: High % aged 55+ (0-40 points)
        aging_score = np.minimum(data['pct_age_55_plus'] / 40 * 40, 40)

        # Component 2: High % in large houses (0-30 points)
        large_house_score = np.minimum(data['pct_separate'] / 70 * 30, 30)

        # Component 3: Income to afford downsizing (0-30 points)
        income_percentile = data['median_household_income'].rank(pct=True) * 100
        income_score = income_percentile * 0.3

        data['downsizing_wave_score'] = (
            aging_score + large_house_score + income_score
        ).round(2)

        # Flag high downsizing areas
        data['high_downsizing_potential'] = (
            (data['pct_age_55_plus'] >= 30) &
            (data['pct_separate'] >= 60) &
            (data['median_household_income'] >= data['median_household_income'].median())
        )

        high_count = data['high_downsizing_potential'].sum()
        print(f"   ✓ Found {high_count} areas with high downsizing potential")

        return data

    def build_time_decay_model(self, data, geography='LGA'):
        """
        Build time-decay model for housing stock transformation
        Estimates likelihood of change over 5, 10, 15 years
        """
        print(f"\n📈 Building time-decay transformation models for {geography}...")

        # Base transformation probability based on current conditions
        # Higher scores = faster transformation expected

        # Calculate base transformation rate (0-1)
        # Average of all three major scores
        base_rate = (
            data['subdivision_potential_score'] / 100 * 0.4 +
            data['luxury_apartment_demand_score'] / 100 * 0.3 +
            data['downsizing_wave_score'] / 100 * 0.3
        )

        # Time decay function: probability of transformation over time
        # Using exponential growth model: P(t) = 1 - e^(-λt)
        # where λ is the transformation rate

        lambda_param = base_rate * 0.15  # Calibration factor

        # Transformation probability over different time horizons
        data['transform_prob_5yr'] = (1 - np.exp(-lambda_param * 5)) * 100
        data['transform_prob_10yr'] = (1 - np.exp(-lambda_param * 10)) * 100
        data['transform_prob_15yr'] = (1 - np.exp(-lambda_param * 15)) * 100

        # Round to 2 decimal places
        data['transform_prob_5yr'] = data['transform_prob_5yr'].round(2)
        data['transform_prob_10yr'] = data['transform_prob_10yr'].round(2)
        data['transform_prob_15yr'] = data['transform_prob_15yr'].round(2)

        print(f"   ✓ Built time-decay models for 5, 10, and 15 year horizons")

        return data

    def calculate_redevelopment_readiness_score(self, data, geography='LGA'):
        """
        Calculate comprehensive redevelopment readiness score
        Combines all factors into a single 0-100 score
        """
        print(f"\n🎯 Calculating comprehensive redevelopment readiness scores for {geography}...")

        # Weighted combination of all scores
        weights = {
            'subdivision': 0.30,
            'luxury_demand': 0.25,
            'downsizing': 0.25,
            'urban_proximity': 0.20
        }

        data['redevelopment_readiness_score'] = (
            data['subdivision_potential_score'] * weights['subdivision'] +
            data['luxury_apartment_demand_score'] * weights['luxury_demand'] +
            data['downsizing_wave_score'] * weights['downsizing'] +
            data['urban_proximity_score'] * weights['urban_proximity']
        ).round(2)

        # Calculate percentile rank
        data['readiness_percentile'] = data['redevelopment_readiness_score'].rank(pct=True) * 100
        data['readiness_percentile'] = data['readiness_percentile'].round(2)

        # Categorize readiness levels
        data['readiness_category'] = pd.cut(
            data['redevelopment_readiness_score'],
            bins=[0, 40, 60, 75, 100],
            labels=['Low', 'Medium', 'High', 'Very High']
        )

        print(f"   ✓ Calculated comprehensive redevelopment readiness scores")

        # Print summary statistics
        category_counts = data['readiness_category'].value_counts().sort_index()
        print("\n   📊 Readiness Category Distribution:")
        for cat, count in category_counts.items():
            print(f"      {cat}: {count} areas ({count/len(data)*100:.1f}%)")

        return data

    def run_full_analysis(self, geography='LGA', sample_size=None):
        """Run the complete analysis pipeline for a geography level"""
        print(f"\n{'='*80}")
        print(f"🚀 STARTING FULL ANALYSIS FOR {geography}")
        print(f"{'='*80}")

        # Step 1: Load all data
        dwelling_data = self.load_dwelling_data(geography)
        age_data = self.load_age_data(geography)
        income_data = self.load_income_data(geography)
        education_data = self.load_education_data(geography)

        # Step 2: Merge all data
        code_col = f"{geography}_CODE_2021"
        print(f"\n🔗 Merging all data sources...")

        combined = dwelling_data.merge(age_data, on=code_col, how='inner')
        combined = combined.merge(income_data, on=code_col, how='inner')
        combined = combined.merge(education_data, on=code_col, how='inner')

        print(f"   ✓ Merged data for {len(combined)} {geography} areas")

        # Optional: Sample for faster testing
        if sample_size and sample_size < len(combined):
            print(f"\n   ⚠️  Sampling {sample_size} areas for testing...")
            combined = combined.sample(n=sample_size, random_state=42)

        # Step 3: Calculate scores
        combined = self.calculate_urban_proximity_score(combined, geography)
        combined = self.analyze_subdivision_potential(combined, geography)
        combined = self.analyze_luxury_apartment_demand(combined, geography)
        combined = self.analyze_downsizing_wave(combined, geography)
        combined = self.build_time_decay_model(combined, geography)
        combined = self.calculate_redevelopment_readiness_score(combined, geography)

        # Step 4: Store results
        if geography == 'LGA':
            self.lga_data = combined
        elif geography == 'SA1':
            self.sa1_data = combined

        print(f"\n{'='*80}")
        print(f"✅ ANALYSIS COMPLETE FOR {geography}")
        print(f"{'='*80}\n")

        return combined

    def export_results(self, data, geography='LGA', top_n=100):
        """Export analysis results to CSV files"""
        print(f"\n💾 Exporting results for {geography}...")

        # Export full results
        output_file = f"transformation_analysis_{geography.lower()}_full.csv"
        data.to_csv(output_file, index=False)
        print(f"   ✓ Exported full results to {output_file}")

        # Export top redevelopment opportunities
        top_file = f"transformation_analysis_{geography.lower()}_top{top_n}.csv"
        top_data = data.nlargest(top_n, 'redevelopment_readiness_score')
        top_data.to_csv(top_file, index=False)
        print(f"   ✓ Exported top {top_n} opportunities to {top_file}")

        # Export high potential areas by category
        # Subdivision potential
        subdivision_file = f"subdivision_potential_{geography.lower()}.csv"
        subdivision_data = data[data['high_subdivision_potential']].sort_values(
            'subdivision_potential_score', ascending=False
        )
        subdivision_data.to_csv(subdivision_file, index=False)
        print(f"   ✓ Exported {len(subdivision_data)} high subdivision potential areas to {subdivision_file}")

        # Luxury apartment demand
        luxury_file = f"luxury_apartment_demand_{geography.lower()}.csv"
        luxury_data = data[data['high_luxury_demand']].sort_values(
            'luxury_apartment_demand_score', ascending=False
        )
        luxury_data.to_csv(luxury_file, index=False)
        print(f"   ✓ Exported {len(luxury_data)} high luxury demand areas to {luxury_file}")

        # Downsizing wave
        downsizing_file = f"downsizing_wave_{geography.lower()}.csv"
        downsizing_data = data[data['high_downsizing_potential']].sort_values(
            'downsizing_wave_score', ascending=False
        )
        downsizing_data.to_csv(downsizing_file, index=False)
        print(f"   ✓ Exported {len(downsizing_data)} high downsizing potential areas to {downsizing_file}")

        return {
            'full': output_file,
            'top': top_file,
            'subdivision': subdivision_file,
            'luxury': luxury_file,
            'downsizing': downsizing_file
        }

    def generate_summary_report(self, data, geography='LGA'):
        """Generate a summary report of the analysis"""
        print(f"\n📋 SUMMARY REPORT FOR {geography}")
        print("=" * 80)

        print(f"\n🔢 OVERALL STATISTICS:")
        print(f"   Total areas analyzed: {len(data)}")
        print(f"   Average redevelopment readiness score: {data['redevelopment_readiness_score'].mean():.2f}")
        print(f"   Median redevelopment readiness score: {data['redevelopment_readiness_score'].median():.2f}")

        print(f"\n🏆 TOP 10 REDEVELOPMENT OPPORTUNITIES:")
        top10 = data.nlargest(10, 'redevelopment_readiness_score')
        for idx, row in top10.iterrows():
            code_col = f"{geography}_CODE_2021"
            print(f"   {row[code_col]}: Score {row['redevelopment_readiness_score']:.2f} "
                  f"({row['readiness_category']}) - "
                  f"{row['pct_separate']:.1f}% detached, "
                  f"Income ${row['median_household_income']:.0f}, "
                  f"{row['pct_age_55_plus']:.1f}% aged 55+")

        print(f"\n📊 SUBDIVISION POTENTIAL:")
        print(f"   High potential areas: {data['high_subdivision_potential'].sum()}")
        print(f"   Average score: {data['subdivision_potential_score'].mean():.2f}")
        print(f"   Top area score: {data['subdivision_potential_score'].max():.2f}")

        print(f"\n🏢 LUXURY APARTMENT DEMAND:")
        print(f"   High demand areas: {data['high_luxury_demand'].sum()}")
        print(f"   Average score: {data['luxury_apartment_demand_score'].mean():.2f}")
        print(f"   Top area score: {data['luxury_apartment_demand_score'].max():.2f}")

        print(f"\n👴 DOWNSIZING WAVE:")
        print(f"   High downsizing areas: {data['high_downsizing_potential'].sum()}")
        print(f"   Average score: {data['downsizing_wave_score'].mean():.2f}")
        print(f"   Top area score: {data['downsizing_wave_score'].max():.2f}")
        print(f"   Average % aged 55+: {data['pct_age_55_plus'].mean():.2f}%")

        print(f"\n⏰ TIME DECAY PROJECTIONS:")
        print(f"   Average 5-year transformation probability: {data['transform_prob_5yr'].mean():.2f}%")
        print(f"   Average 10-year transformation probability: {data['transform_prob_10yr'].mean():.2f}%")
        print(f"   Average 15-year transformation probability: {data['transform_prob_15yr'].mean():.2f}%")

        print("\n" + "=" * 80)


def main():
    """Main execution function"""
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                                                                            ║
    ║           SUBURBAN TRANSFORMATION PREDICTION ENGINE                        ║
    ║                                                                            ║
    ║  Analyzing dwelling types, demographics, income, and education to          ║
    ║  predict redevelopment opportunities across Australian suburbs             ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize engine
    engine = SuburbanTransformationEngine()

    # Identify urban centers
    engine.identify_urban_centers()

    # Run analysis for LGA level (Local Government Areas)
    print("\n\n" + "🏙️  " * 20)
    print("ANALYZING LGA (LOCAL GOVERNMENT AREAS)")
    print("🏙️  " * 20 + "\n")

    lga_results = engine.run_full_analysis(geography='LGA')
    lga_files = engine.export_results(lga_results, geography='LGA', top_n=100)
    engine.generate_summary_report(lga_results, geography='LGA')

    # Run analysis for SA1 level (Statistical Area Level 1)
    # SA1 is very granular (~60,000 areas) so this will be compute-intensive!
    print("\n\n" + "🏘️  " * 20)
    print("ANALYZING SA1 (STATISTICAL AREA LEVEL 1)")
    print("🏘️  " * 20 + "\n")
    print("⚠️  WARNING: SA1 has ~60,000+ areas - this will take significant time!")
    print("⚠️  Processing all SA1 areas for maximum compute intensity...\n")

    sa1_results = engine.run_full_analysis(geography='SA1')
    sa1_files = engine.export_results(sa1_results, geography='SA1', top_n=500)
    engine.generate_summary_report(sa1_results, geography='SA1')

    # Final summary
    print("\n\n" + "🎉 " * 20)
    print("ANALYSIS COMPLETE!")
    print("🎉 " * 20 + "\n")

    print("📁 Generated files:")
    print("\nLGA Files:")
    for key, file in lga_files.items():
        print(f"   - {file}")

    print("\nSA1 Files:")
    for key, file in sa1_files.items():
        print(f"   - {file}")

    print("\n✨ Suburban Transformation Prediction Engine completed successfully!")
    print("💰 Free credits well spent on compute-intensive analysis! 💰\n")


if __name__ == "__main__":
    main()
