"""
Report generation module
Creates text reports and exports data to CSV
"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Dict
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates text reports and exports analysis results
    """

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or config.OUTPUT_DIR
        logger.info(f"Initialized report generator, output: {self.output_dir}")

    def generate_text_report(self, report: Dict):
        """
        Generate comprehensive text report

        Args:
            report: Analysis report dictionary
        """
        logger.info("Generating comprehensive text report")

        output_path = os.path.join(self.output_dir, "comprehensive_report.txt")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 100 + "\n")
            f.write("NATIONAL MIGRATION PATTERN & PROPERTY DEMAND FLOW ANALYSIS\n")
            f.write("Australian Census 2021 Data\n")
            f.write("=" * 100 + "\n\n")

            # Metadata
            f.write("ANALYSIS METADATA\n")
            f.write("-" * 100 + "\n")
            f.write(f"Geographic Level: {report['metadata']['geo_level']}\n")
            f.write(f"Analysis Date: {report['metadata']['analysis_date']}\n")
            f.write(f"Parameters:\n")
            for key, value in report['metadata']['parameters'].items():
                f.write(f"  - {key}: {value}\n")
            f.write("\n")

            # Overview statistics
            f.write("=" * 100 + "\n")
            f.write("OVERVIEW STATISTICS\n")
            f.write("=" * 100 + "\n\n")

            overview = report['overview']
            total_pop = sum(d['total_population'] for d in overview.values())
            total_clusters = sum(d['total_clusters'] for d in overview.values())
            total_anchors = sum(d['total_anchors'] for d in overview.values())

            f.write(f"Countries Analyzed: {len(overview)}\n")
            f.write(f"Total Population (from analyzed countries): {total_pop:,.0f}\n")
            f.write(f"Total Cultural Clusters Identified: {total_clusters:,}\n")
            f.write(f"Total Cultural Anchor Points: {total_anchors:,}\n")
            f.write(f"Average Clusters per Country: {total_clusters / len(overview):.1f}\n")
            f.write(f"Average Anchor Points per Country: {total_anchors / len(overview):.1f}\n")
            f.write("\n")

            # Top countries by population
            f.write("=" * 100 + "\n")
            f.write("TOP 20 COUNTRIES BY POPULATION\n")
            f.write("=" * 100 + "\n\n")

            sorted_countries = sorted(overview.items(),
                                    key=lambda x: x[1]['total_population'],
                                    reverse=True)[:20]

            f.write(f"{'Rank':<6}{'Country':<25}{'Population':<15}{'Clusters':<12}{'Anchors':<12}{'Avg Conc.':<12}\n")
            f.write("-" * 100 + "\n")

            for rank, (country, data) in enumerate(sorted_countries, 1):
                pop = data['total_population']
                clusters = data['total_clusters']
                anchors = data['total_anchors']

                # Calculate average concentration
                if not data['clusters'].empty:
                    avg_conc = data['clusters']['concentration_ratio'].mean()
                else:
                    avg_conc = 0

                f.write(f"{rank:<6}{country:<25}{pop:>14,}{clusters:>12}{anchors:>12}{avg_conc:>11.2%}\n")

            f.write("\n")

            # Detailed analysis for top countries
            if 'detailed_analysis' in report:
                f.write("=" * 100 + "\n")
                f.write("DETAILED ANALYSIS BY COUNTRY\n")
                f.write("=" * 100 + "\n\n")

                for country, data in report['detailed_analysis'].items():
                    f.write(f"\n{'=' * 100}\n")
                    f.write(f"{country.upper()}\n")
                    f.write(f"{'=' * 100}\n\n")

                    # Summary
                    summary = data.get('summary', {})
                    f.write("SUMMARY:\n")
                    f.write("-" * 100 + "\n")
                    f.write(f"Total Population: {summary.get('total_population', 0):,.0f}\n")
                    f.write(f"Number of Clusters: {summary.get('num_clusters', 0):,}\n")
                    f.write(f"Number of Anchor Points: {summary.get('num_anchor_points', 0):,}\n")
                    f.write(f"Projected Growth ({config.ANALYSIS_PARAMS['growth_trajectory_years']} years): "
                           f"{summary.get('projected_growth', 0):,.0f}\n")
                    f.write("\n")

                    # Top 10 anchor points
                    if 'anchor_points' in data and not data['anchor_points'].empty:
                        f.write("TOP 10 ANCHOR POINTS:\n")
                        f.write("-" * 100 + "\n")

                        anchors = data['anchor_points'].head(10)
                        geo_col = anchors.columns[0]

                        f.write(f"{'Rank':<6}{geo_col:<15}{'Population':<12}{'Total Pop':<12}"
                               f"{'Concentration':<15}{'Anchor Strength':<15}\n")
                        f.write("-" * 100 + "\n")

                        for idx, (i, row) in enumerate(anchors.iterrows(), 1):
                            f.write(f"{idx:<6}{row[geo_col]:<15}"
                                   f"{row[f'{country}_population']:>11,.0f}"
                                   f"{row['total_population']:>12,.0f}"
                                   f"{row['concentration_ratio']:>14.1%}"
                                   f"{row['anchor_strength']:>15.2f}\n")
                        f.write("\n")

                    # Housing affordability summary
                    if 'clusters_with_housing' in data and not data['clusters_with_housing'].empty:
                        f.write("HOUSING AFFORDABILITY SUMMARY:\n")
                        f.write("-" * 100 + "\n")

                        housing = data['clusters_with_housing']

                        # Median values
                        median_rent = housing['Median_rent_weekly'].median()
                        median_income = housing['Median_tot_hhd_inc_weekly'].median()
                        median_mortgage = housing['Median_mortgage_repay_monthly'].median()

                        f.write(f"Median Weekly Rent: ${median_rent:,.0f}\n")
                        f.write(f"Median Weekly Household Income: ${median_income:,.0f}\n")
                        f.write(f"Median Monthly Mortgage: ${median_mortgage:,.0f}\n")

                        # Affordability distribution
                        if 'rent_affordability' in housing.columns:
                            f.write("\nRent Affordability Distribution:\n")
                            rent_dist = housing['rent_affordability'].value_counts()
                            for category, count in rent_dist.items():
                                pct = count / len(housing) * 100
                                f.write(f"  {category}: {count} areas ({pct:.1f}%)\n")

                        f.write("\n")

                    # Growth projections
                    if 'growth_projections' in data and data['growth_projections']:
                        growth = data['growth_projections']
                        f.write("GROWTH PROJECTIONS:\n")
                        f.write("-" * 100 + "\n")
                        f.write(f"Current Total Population: {growth['total_current_population']:,.0f}\n")
                        f.write(f"Projected Total Population: {growth['total_projected_population']:,.0f}\n")
                        f.write(f"Total Projected Growth: {growth['total_projected_growth']:,.0f}\n")
                        growth_pct = (growth['total_projected_growth'] /
                                    growth['total_current_population'] * 100)
                        f.write(f"Growth Percentage: {growth_pct:.1f}%\n")
                        f.write(f"Projection Period: {config.ANALYSIS_PARAMS['growth_trajectory_years']} years\n")
                        f.write("\n")

                        # Top growth areas
                        if 'data' in growth and not growth['data'].empty:
                            f.write("TOP 10 AREAS BY PROJECTED GROWTH:\n")
                            f.write("-" * 100 + "\n")

                            growth_df = growth['data'].head(10)
                            geo_col = growth_df.columns[0]

                            f.write(f"{'Rank':<6}{geo_col:<15}{'Current':<12}{'Projected':<12}"
                                   f"{'Growth':<12}{'Growth Rate':<12}\n")
                            f.write("-" * 100 + "\n")

                            for idx, (i, row) in enumerate(growth_df.iterrows(), 1):
                                current = row[f'{country}_population']
                                projected = row['projected_population']
                                growth_amt = row['projected_additional_demand']
                                growth_rate = row['growth_rate'] * 100 if pd.notna(row['growth_rate']) else 0

                                f.write(f"{idx:<6}{row[geo_col]:<15}"
                                       f"{current:>11,.0f}"
                                       f"{projected:>12,.0f}"
                                       f"{growth_amt:>12,.0f}"
                                       f"{growth_rate:>11.1f}%\n")

                            f.write("\n")

            # Key insights
            f.write("\n" + "=" * 100 + "\n")
            f.write("KEY INSIGHTS\n")
            f.write("=" * 100 + "\n\n")

            f.write("CULTURAL CLUSTERING PATTERNS:\n")
            f.write("-" * 100 + "\n")

            # Countries with highest concentration
            high_conc_countries = []
            for country, data in overview.items():
                if not data['clusters'].empty:
                    max_conc = data['clusters']['concentration_ratio'].max()
                    high_conc_countries.append((country, max_conc))

            high_conc_countries = sorted(high_conc_countries, key=lambda x: x[1], reverse=True)[:10]

            f.write("Countries with Highest Peak Concentrations:\n")
            for country, conc in high_conc_countries:
                f.write(f"  - {country}: {conc:.1%} maximum concentration\n")

            f.write("\n")

            # Countries with most dispersed populations
            f.write("Countries with Most Widespread Settlement:\n")
            dispersed = sorted(overview.items(), key=lambda x: x[1]['total_clusters'], reverse=True)[:10]
            for country, data in dispersed:
                f.write(f"  - {country}: {data['total_clusters']:,} clusters across Australia\n")

            f.write("\n")

            f.write("PROPERTY DEMAND IMPLICATIONS:\n")
            f.write("-" * 100 + "\n")
            f.write("The analysis reveals several key patterns relevant to property demand:\n\n")

            f.write("1. ANCHOR POINTS represent established communities with strong cultural presence\n")
            f.write("   - These areas show stable, ongoing demand from specific demographic groups\n")
            f.write("   - Property investors can expect sustained interest in these locations\n\n")

            f.write("2. EMERGING CLUSTERS indicate areas of recent settlement growth\n")
            f.write("   - Higher growth rates suggest expanding demand\n")
            f.write("   - Early investment opportunities in these areas\n\n")

            f.write("3. HOUSING AFFORDABILITY varies significantly across cultural communities\n")
            f.write("   - Some communities concentrate in expensive areas (established residents)\n")
            f.write("   - Others in more affordable areas (recent arrivals)\n")
            f.write("   - This creates diverse investment opportunities at different price points\n\n")

            f.write("\n" + "=" * 100 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 100 + "\n")

        logger.info(f"Text report saved to: {output_path}")

    def export_results_to_csv(self, report: Dict):
        """
        Export analysis results to CSV files

        Args:
            report: Analysis report dictionary
        """
        logger.info("Exporting results to CSV")

        # Export overview summary
        overview_data = []
        for country, data in report['overview'].items():
            overview_data.append({
                'Country': country,
                'Total_Population': data['total_population'],
                'Num_Clusters': data['total_clusters'],
                'Num_Anchor_Points': data['total_anchors'],
            })

        overview_df = pd.DataFrame(overview_data)
        overview_df = overview_df.sort_values('Total_Population', ascending=False)
        overview_path = os.path.join(self.output_dir, "overview_by_country.csv")
        overview_df.to_csv(overview_path, index=False)
        logger.info(f"Exported: {overview_path}")

        # Export detailed data for each top country
        if 'detailed_analysis' in report:
            for country, data in report['detailed_analysis'].items():
                safe_country = country.replace(' ', '_').replace('/', '_')

                # Export clusters
                if 'clusters' in data and not data['clusters'].empty:
                    clusters_path = os.path.join(self.output_dir, f"clusters_{safe_country}.csv")
                    data['clusters'].to_csv(clusters_path, index=False)
                    logger.info(f"Exported: {clusters_path}")

                # Export anchor points
                if 'anchor_points' in data and not data['anchor_points'].empty:
                    anchors_path = os.path.join(self.output_dir, f"anchor_points_{safe_country}.csv")
                    data['anchor_points'].to_csv(anchors_path, index=False)
                    logger.info(f"Exported: {anchors_path}")

                # Export housing data
                if 'clusters_with_housing' in data and not data['clusters_with_housing'].empty:
                    housing_path = os.path.join(self.output_dir, f"housing_analysis_{safe_country}.csv")
                    data['clusters_with_housing'].to_csv(housing_path, index=False)
                    logger.info(f"Exported: {housing_path}")

                # Export growth projections
                if 'growth_projections' in data and data['growth_projections']:
                    if 'data' in data['growth_projections'] and not data['growth_projections']['data'].empty:
                        growth_path = os.path.join(self.output_dir, f"growth_projections_{safe_country}.csv")
                        data['growth_projections']['data'].to_csv(growth_path, index=False)
                        logger.info(f"Exported: {growth_path}")

        logger.info("CSV export complete")

    def generate_executive_summary(self, report: Dict):
        """
        Generate executive summary

        Args:
            report: Analysis report dictionary
        """
        logger.info("Generating executive summary")

        output_path = os.path.join(self.output_dir, "executive_summary.txt")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("EXECUTIVE SUMMARY\n")
            f.write("National Migration Pattern & Property Demand Flow Analysis\n")
            f.write("=" * 100 + "\n\n")

            # Key findings
            overview = report['overview']

            f.write("KEY FINDINGS:\n")
            f.write("-" * 100 + "\n\n")

            # 1. Scale of analysis
            total_pop = sum(d['total_population'] for d in overview.values())
            total_clusters = sum(d['total_clusters'] for d in overview.values())
            total_anchors = sum(d['total_anchors'] for d in overview.values())

            f.write(f"1. SCALE OF ANALYSIS\n\n")
            f.write(f"   - Analyzed {len(overview)} countries/regions of origin\n")
            f.write(f"   - Total population studied: {total_pop:,.0f} people\n")
            f.write(f"   - Identified {total_clusters:,} cultural clusters across Australia\n")
            f.write(f"   - Found {total_anchors:,} strong anchor points (high concentration areas)\n")
            f.write(f"   - Geographic resolution: {report['metadata']['geo_level']} level "
                   f"(finest available granularity)\n\n")

            # 2. Top communities
            f.write(f"2. MAJOR CULTURAL COMMUNITIES\n\n")
            top_5 = sorted(overview.items(), key=lambda x: x[1]['total_population'], reverse=True)[:5]
            for rank, (country, data) in enumerate(top_5, 1):
                f.write(f"   {rank}. {country}:\n")
                f.write(f"      Population: {data['total_population']:,}\n")
                f.write(f"      Clusters: {data['total_clusters']:,} areas\n")
                f.write(f"      Anchor Points: {data['total_anchors']:,} locations\n")
                f.write(f"\n")

            # 3. Growth projections
            if 'detailed_analysis' in report:
                f.write(f"3. GROWTH PROJECTIONS ({config.ANALYSIS_PARAMS['growth_trajectory_years']} YEARS)\n\n")

                growth_summary = []
                for country, data in report['detailed_analysis'].items():
                    if 'summary' in data and 'projected_growth' in data['summary']:
                        growth = data['summary']['projected_growth']
                        current = data['summary']['total_population']
                        if current > 0:
                            growth_pct = (growth / current) * 100
                            growth_summary.append((country, growth, growth_pct))

                growth_summary = sorted(growth_summary, key=lambda x: x[1], reverse=True)[:5]

                for country, growth, growth_pct in growth_summary:
                    f.write(f"   - {country}: +{growth:,.0f} people ({growth_pct:.1f}% growth)\n")

                f.write("\n")

            # 4. Property demand implications
            f.write("4. PROPERTY DEMAND IMPLICATIONS\n\n")

            f.write("   ANCHOR POINT OPPORTUNITIES:\n")
            f.write("   - Established communities with stable, ongoing demand\n")
            f.write("   - Lower risk, predictable rental/purchase patterns\n")
            f.write("   - Premium pricing potential in well-established ethnic enclaves\n\n")

            f.write("   EMERGING CLUSTER OPPORTUNITIES:\n")
            f.write("   - Areas with recent rapid growth in specific demographics\n")
            f.write("   - Higher growth potential but more volatile\n")
            f.write("   - Early investment opportunities before full establishment\n\n")

            f.write("   AFFORDABILITY PATTERNS:\n")
            f.write("   - Different communities show distinct affordability profiles\n")
            f.write("   - Recent arrivals concentrate in more affordable areas\n")
            f.write("   - Established communities often in premium locations\n")
            f.write("   - Opportunities at multiple price points\n\n")

            # 5. Recommendations
            f.write("5. STRATEGIC RECOMMENDATIONS\n\n")

            f.write("   FOR PROPERTY INVESTORS:\n")
            f.write("   a) Target anchor points for stable, long-term investments\n")
            f.write("   b) Monitor emerging clusters for high-growth opportunities\n")
            f.write("   c) Consider community-specific amenities (shops, places of worship)\n")
            f.write("   d) Track migration trends for forward-looking investments\n\n")

            f.write("   FOR DEVELOPERS:\n")
            f.write("   a) Design culturally appropriate housing (size, layout)\n")
            f.write("   b) Focus on areas with projected population growth\n")
            f.write("   c) Consider multi-generational housing in established communities\n")
            f.write("   d) Plan for evolving demographic needs\n\n")

            f.write("   FOR URBAN PLANNERS:\n")
            f.write("   a) Ensure infrastructure supports growing communities\n")
            f.write("   b) Plan for culturally diverse amenities\n")
            f.write("   c) Monitor housing affordability in high-concentration areas\n")
            f.write("   d) Support community integration and cohesion\n\n")

            # Conclusion
            f.write("-" * 100 + "\n")
            f.write("CONCLUSION\n")
            f.write("-" * 100 + "\n\n")

            f.write("This analysis reveals complex patterns of settlement and community formation across\n")
            f.write("Australia. The identification of cultural anchor points and emerging clusters provides\n")
            f.write("actionable insights for property investment, development, and urban planning.\n\n")

            f.write("The projected growth trajectories suggest continued diversification of Australian\n")
            f.write("communities, with specific opportunities in areas experiencing demographic transition.\n\n")

            f.write("For detailed data and visualizations, refer to:\n")
            f.write("  - comprehensive_report.txt (full analysis)\n")
            f.write("  - summary_dashboard.png (visual overview)\n")
            f.write("  - Individual country CSV files (detailed data)\n")
            f.write("  - Country-specific visualizations (housing, growth)\n\n")

            f.write("=" * 100 + "\n")
            f.write(f"Report generated: {report['metadata']['analysis_date']}\n")
            f.write("=" * 100 + "\n")

        logger.info(f"Executive summary saved to: {output_path}")
