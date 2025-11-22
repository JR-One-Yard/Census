"""
Visualization module for migration analysis results
Creates maps, charts, and visual reports
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import logging
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style(config.VIZ_SETTINGS['map_style'])
plt.rcParams['figure.figsize'] = config.VIZ_SETTINGS['figure_size']
plt.rcParams['figure.dpi'] = config.VIZ_SETTINGS['dpi']


class MigrationVisualizer:
    """
    Creates visualizations for migration analysis results
    """

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or config.OUTPUT_DIR
        logger.info(f"Initialized visualizer, output: {self.output_dir}")

    def plot_country_distribution(self, analysis_results: Dict, top_n: int = 20):
        """
        Plot population distribution for top countries

        Args:
            analysis_results: Results from country analysis
            top_n: Number of top countries to show
        """
        logger.info(f"Creating country distribution plot (top {top_n})")

        # Extract country populations
        countries = []
        populations = []
        clusters = []
        anchors = []

        for country, data in analysis_results.items():
            countries.append(country)
            populations.append(data['total_population'])
            clusters.append(data['total_clusters'])
            anchors.append(data['total_anchors'])

        df = pd.DataFrame({
            'Country': countries,
            'Population': populations,
            'Clusters': clusters,
            'Anchor_Points': anchors
        })

        df = df.sort_values('Population', ascending=False).head(top_n)

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))

        # 1. Total population by country
        ax1 = axes[0, 0]
        bars1 = ax1.barh(df['Country'], df['Population'], color='steelblue')
        ax1.set_xlabel('Total Population', fontsize=12, fontweight='bold')
        ax1.set_title(f'Top {top_n} Countries by Total Population', fontsize=14, fontweight='bold')
        ax1.invert_yaxis()

        # Add values on bars
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2,
                    f'{int(width):,}',
                    ha='left', va='center', fontsize=9)

        # 2. Number of clusters by country
        ax2 = axes[0, 1]
        bars2 = ax2.barh(df['Country'], df['Clusters'], color='coral')
        ax2.set_xlabel('Number of Clusters', fontsize=12, fontweight='bold')
        ax2.set_title(f'Cultural Clusters by Country', fontsize=14, fontweight='bold')
        ax2.invert_yaxis()

        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=9)

        # 3. Anchor points by country
        ax3 = axes[1, 0]
        bars3 = ax3.barh(df['Country'], df['Anchor_Points'], color='darkgreen')
        ax3.set_xlabel('Number of Anchor Points', fontsize=12, fontweight='bold')
        ax3.set_title(f'Cultural Anchor Points by Country', fontsize=14, fontweight='bold')
        ax3.invert_yaxis()

        for i, bar in enumerate(bars3):
            width = bar.get_width()
            ax3.text(width, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=9)

        # 4. Scatter: Population vs Clusters
        ax4 = axes[1, 1]
        scatter = ax4.scatter(df['Population'], df['Clusters'],
                             s=df['Anchor_Points']*20, alpha=0.6, c=range(len(df)),
                             cmap='viridis')
        ax4.set_xlabel('Total Population', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Number of Clusters', fontsize=12, fontweight='bold')
        ax4.set_title('Population vs Clusters (size = anchor points)', fontsize=14, fontweight='bold')

        # Add country labels
        for idx, row in df.iterrows():
            ax4.annotate(row['Country'], (row['Population'], row['Clusters']),
                        fontsize=8, alpha=0.7)

        plt.tight_layout()
        output_path = f"{self.output_dir}/country_distribution.png"
        plt.savefig(output_path, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()

    def plot_housing_affordability(self, clusters_with_housing: pd.DataFrame, country: str):
        """
        Plot housing affordability analysis for a country

        Args:
            clusters_with_housing: DataFrame with housing data
            country: Country name
        """
        logger.info(f"Creating housing affordability plot for {country}")

        if clusters_with_housing.empty:
            logger.warning(f"No housing data for {country}")
            return

        # Filter valid data
        df = clusters_with_housing[
            clusters_with_housing['Median_rent_weekly'].notna() |
            clusters_with_housing['Median_mortgage_repay_monthly'].notna()
        ].copy()

        if df.empty:
            logger.warning(f"No valid housing data for {country}")
            return

        fig, axes = plt.subplots(2, 2, figsize=(20, 16))

        # 1. Rent affordability distribution
        ax1 = axes[0, 0]
        rent_afford = df['rent_affordability'].value_counts()
        colors1 = ['green', 'yellowgreen', 'orange', 'red']
        ax1.pie(rent_afford.values, labels=rent_afford.index, autopct='%1.1f%%',
               colors=colors1[:len(rent_afford)], startangle=90)
        ax1.set_title(f'{country} Communities - Rent Affordability', fontsize=14, fontweight='bold')

        # 2. Mortgage affordability distribution
        ax2 = axes[0, 1]
        mortgage_afford = df['mortgage_affordability'].value_counts()
        ax2.pie(mortgage_afford.values, labels=mortgage_afford.index, autopct='%1.1f%%',
               colors=colors1[:len(mortgage_afford)], startangle=90)
        ax2.set_title(f'{country} Communities - Mortgage Affordability', fontsize=14, fontweight='bold')

        # 3. Scatter: Rent vs Income
        ax3 = axes[1, 0]
        valid_rent = df[df['Median_rent_weekly'].notna() & df['Median_tot_hhd_inc_weekly'].notna()]
        if not valid_rent.empty:
            scatter = ax3.scatter(valid_rent['Median_tot_hhd_inc_weekly'],
                                 valid_rent['Median_rent_weekly'],
                                 s=valid_rent[f'{country}_population']*2,
                                 alpha=0.6, c=valid_rent['concentration_ratio'],
                                 cmap='YlOrRd')
            ax3.set_xlabel('Median Household Income ($/week)', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Median Rent ($/week)', fontsize=12, fontweight='bold')
            ax3.set_title('Rent vs Income (size=population, color=concentration)',
                         fontsize=14, fontweight='bold')
            plt.colorbar(scatter, ax=ax3, label='Concentration Ratio')

        # 4. Distribution of rent-to-income ratio
        ax4 = axes[1, 1]
        # Filter out NaN and infinite values
        valid_ratio = df[df['rent_to_income_ratio'].notna() & np.isfinite(df['rent_to_income_ratio'])]
        if not valid_ratio.empty and len(valid_ratio) > 0:
            # Also cap at reasonable maximum (e.g., 2.0 = 200%)
            ratio_data = valid_ratio['rent_to_income_ratio']
            ratio_data = ratio_data[ratio_data <= 2.0]  # Cap at 200%

            if len(ratio_data) > 0:
                ax4.hist(ratio_data, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
                ax4.axvline(0.3, color='green', linestyle='--', linewidth=2, label='Affordable (30%)')
                ax4.axvline(0.4, color='orange', linestyle='--', linewidth=2, label='Moderate (40%)')
                ax4.set_xlabel('Rent-to-Income Ratio', fontsize=12, fontweight='bold')
                ax4.set_ylabel('Number of Areas', fontsize=12, fontweight='bold')
                ax4.set_title('Distribution of Rent-to-Income Ratios (capped at 200%)', fontsize=14, fontweight='bold')
                ax4.legend()
            else:
                ax4.text(0.5, 0.5, 'No valid ratio data', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Distribution of Rent-to-Income Ratios', fontsize=14, fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'No valid ratio data', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Distribution of Rent-to-Income Ratios', fontsize=14, fontweight='bold')

        plt.tight_layout()
        output_path = f"{self.output_dir}/housing_affordability_{country}.png"
        plt.savefig(output_path, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()

    def plot_growth_projections(self, growth_data: Dict, country: str, top_n: int = 20):
        """
        Plot growth projections for a country

        Args:
            growth_data: Growth projection data
            country: Country name
            top_n: Number of top areas to show
        """
        logger.info(f"Creating growth projection plot for {country}")

        if not growth_data or 'data' not in growth_data:
            logger.warning(f"No growth data for {country}")
            return

        df = growth_data['data'].head(top_n).copy()

        if df.empty:
            logger.warning(f"Empty growth data for {country}")
            return

        fig, axes = plt.subplots(2, 2, figsize=(20, 16))

        # 1. Top areas by projected additional demand
        ax1 = axes[0, 0]
        geo_col = df.columns[0]
        bars1 = ax1.barh(range(len(df)), df['projected_additional_demand'], color='darkblue')
        ax1.set_yticks(range(len(df)))
        ax1.set_yticklabels(df[geo_col], fontsize=8)
        ax1.set_xlabel('Projected Additional Population', fontsize=12, fontweight='bold')
        ax1.set_title(f'Top {top_n} Areas by Projected {country} Population Growth',
                     fontsize=14, fontweight='bold')
        ax1.invert_yaxis()

        # 2. Current vs Projected population
        ax2 = axes[0, 1]
        x = np.arange(len(df))
        width = 0.35
        bars1 = ax2.bar(x - width/2, df[f'{country}_population'], width, label='Current', color='steelblue')
        bars2 = ax2.bar(x + width/2, df['projected_population'], width, label='Projected', color='coral')
        ax2.set_xlabel('Area', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Population', fontsize=12, fontweight='bold')
        ax2.set_title(f'Current vs Projected {country} Population',
                     fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df[geo_col], rotation=45, ha='right', fontsize=8)
        ax2.legend()

        # 3. Growth rate distribution
        ax3 = axes[1, 0]
        # Filter out NaN and infinite values
        valid_growth = df[df['growth_rate'].notna() & np.isfinite(df['growth_rate'])]
        if not valid_growth.empty and len(valid_growth) > 0:
            # Cap at reasonable growth rate (-50% to +500%)
            growth_data = valid_growth['growth_rate'] * 100
            growth_data = growth_data[(growth_data >= -50) & (growth_data <= 500)]

            if len(growth_data) > 0:
                ax3.hist(growth_data, bins=20, color='green', alpha=0.7, edgecolor='black')
                ax3.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')
                ax3.set_ylabel('Number of Areas', fontsize=12, fontweight='bold')
                ax3.set_title(f'{country} Community Growth Rate Distribution',
                             fontsize=14, fontweight='bold')
            else:
                ax3.text(0.5, 0.5, 'No valid growth data', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title(f'{country} Community Growth Rate Distribution', fontsize=14, fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'No valid growth data', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title(f'{country} Community Growth Rate Distribution', fontsize=14, fontweight='bold')

        # 4. Overall summary
        ax4 = axes[1, 1]
        ax4.axis('off')

        summary_text = f"""
        {country} GROWTH PROJECTION SUMMARY
        {'=' * 50}

        Current Total Population: {growth_data['total_current_population']:,.0f}

        Projected Total Population: {growth_data['total_projected_population']:,.0f}

        Total Projected Growth: {growth_data['total_projected_growth']:,.0f}

        Growth Percentage: {(growth_data['total_projected_growth'] / growth_data['total_current_population'] * 100):.1f}%

        Projection Period: {config.ANALYSIS_PARAMS['growth_trajectory_years']} years

        Number of Growth Areas: {len(df)}
        """

        ax4.text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
                verticalalignment='center')

        plt.tight_layout()
        output_path = f"{self.output_dir}/growth_projections_{country}.png"
        plt.savefig(output_path, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()

    def plot_anchor_points_heatmap(self, analysis_results: Dict, top_n: int = 15):
        """
        Create heatmap of anchor point concentrations

        Args:
            analysis_results: Results from country analysis
            top_n: Number of top countries to show
        """
        logger.info("Creating anchor points heatmap")

        # Get top countries by anchor points
        countries_data = [(c, d['total_anchors'], d['anchor_points'])
                         for c, d in analysis_results.items()
                         if d['total_anchors'] > 0]

        countries_data = sorted(countries_data, key=lambda x: x[1], reverse=True)[:top_n]

        if not countries_data:
            logger.warning("No anchor points data available")
            return

        # Create concentration matrix
        # For each country, get top anchor points and their concentrations
        matrix_data = []
        country_names = []

        for country, total, anchor_df in countries_data:
            country_names.append(country)
            top_anchors = anchor_df.head(10)  # Top 10 anchors per country
            concentrations = top_anchors['concentration_ratio'].values
            # Pad to 10 values
            if len(concentrations) < 10:
                concentrations = np.pad(concentrations, (0, 10 - len(concentrations)), constant_values=0)
            matrix_data.append(concentrations)

        matrix = np.array(matrix_data)

        # Create heatmap
        fig, ax = plt.subplots(figsize=(16, 12))
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')

        # Set ticks
        ax.set_xticks(np.arange(10))
        ax.set_yticks(np.arange(len(country_names)))
        ax.set_xticklabels([f'Anchor {i+1}' for i in range(10)])
        ax.set_yticklabels(country_names)

        # Rotate the tick labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Concentration Ratio', rotation=270, labelpad=20, fontsize=12, fontweight='bold')

        # Add values in cells
        for i in range(len(country_names)):
            for j in range(10):
                value = matrix[i, j]
                if value > 0:
                    text = ax.text(j, i, f'{value:.2f}',
                                  ha="center", va="center", color="black" if value < 0.5 else "white",
                                  fontsize=8)

        ax.set_title('Cultural Anchor Points - Concentration Heatmap\n(Top Areas by Country)',
                    fontsize=14, fontweight='bold')

        plt.tight_layout()
        output_path = f"{self.output_dir}/anchor_points_heatmap.png"
        plt.savefig(output_path, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()

    def create_summary_dashboard(self, report: Dict):
        """
        Create a comprehensive summary dashboard

        Args:
            report: Comprehensive analysis report
        """
        logger.info("Creating summary dashboard")

        overview = report['overview']

        fig = plt.figure(figsize=(24, 16))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. Total populations by country (top 15)
        ax1 = fig.add_subplot(gs[0, :2])
        countries = []
        populations = []
        for country, data in sorted(overview.items(), key=lambda x: x[1]['total_population'], reverse=True)[:15]:
            countries.append(country)
            populations.append(data['total_population'])

        ax1.bar(range(len(countries)), populations, color='steelblue', alpha=0.8)
        ax1.set_xticks(range(len(countries)))
        ax1.set_xticklabels(countries, rotation=45, ha='right')
        ax1.set_ylabel('Total Population', fontsize=12, fontweight='bold')
        ax1.set_title('Top 15 Countries by Total Population in Australia', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # 2. Key statistics
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')

        total_pop = sum(d['total_population'] for d in overview.values())
        total_clusters = sum(d['total_clusters'] for d in overview.values())
        total_anchors = sum(d['total_anchors'] for d in overview.values())
        countries_analyzed = len(overview)

        stats_text = f"""
        ANALYSIS SUMMARY
        {'=' * 30}

        Countries Analyzed: {countries_analyzed}

        Total Population: {total_pop:,.0f}

        Total Clusters: {total_clusters:,}

        Total Anchor Points: {total_anchors:,}

        Geographic Level: {report['metadata']['geo_level']}

        Analysis Date: {report['metadata']['analysis_date'][:10]}
        """

        ax2.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                verticalalignment='center')

        # 3. Clusters per country
        ax3 = fig.add_subplot(gs[1, 0])
        cluster_counts = [d['total_clusters'] for country, d in sorted(overview.items(),
                         key=lambda x: x[1]['total_clusters'], reverse=True)[:10]]
        cluster_countries = [country for country, d in sorted(overview.items(),
                            key=lambda x: x[1]['total_clusters'], reverse=True)[:10]]

        ax3.barh(range(len(cluster_countries)), cluster_counts, color='coral')
        ax3.set_yticks(range(len(cluster_countries)))
        ax3.set_yticklabels(cluster_countries, fontsize=9)
        ax3.set_xlabel('Number of Clusters', fontsize=11, fontweight='bold')
        ax3.set_title('Top 10 Countries by Number of Clusters', fontsize=12, fontweight='bold')
        ax3.invert_yaxis()

        # 4. Anchor points per country
        ax4 = fig.add_subplot(gs[1, 1])
        anchor_counts = [d['total_anchors'] for country, d in sorted(overview.items(),
                        key=lambda x: x[1]['total_anchors'], reverse=True)[:10]]
        anchor_countries = [country for country, d in sorted(overview.items(),
                           key=lambda x: x[1]['total_anchors'], reverse=True)[:10]]

        ax4.barh(range(len(anchor_countries)), anchor_counts, color='darkgreen')
        ax4.set_yticks(range(len(anchor_countries)))
        ax4.set_yticklabels(anchor_countries, fontsize=9)
        ax4.set_xlabel('Number of Anchor Points', fontsize=11, fontweight='bold')
        ax4.set_title('Top 10 Countries by Anchor Points', fontsize=12, fontweight='bold')
        ax4.invert_yaxis()

        # 5. Cluster to anchor ratio
        ax5 = fig.add_subplot(gs[1, 2])
        ratios = []
        ratio_countries = []
        for country, d in overview.items():
            if d['total_clusters'] > 0:
                ratio = d['total_anchors'] / d['total_clusters']
                ratios.append(ratio)
                ratio_countries.append(country)

        top_ratios = sorted(zip(ratio_countries, ratios), key=lambda x: x[1], reverse=True)[:10]
        ratio_countries = [c for c, r in top_ratios]
        ratios = [r for c, r in top_ratios]

        ax5.barh(range(len(ratio_countries)), ratios, color='purple')
        ax5.set_yticks(range(len(ratio_countries)))
        ax5.set_yticklabels(ratio_countries, fontsize=9)
        ax5.set_xlabel('Anchor/Cluster Ratio', fontsize=11, fontweight='bold')
        ax5.set_title('Top 10 Countries by Concentration\n(Anchor-to-Cluster Ratio)',
                     fontsize=12, fontweight='bold')
        ax5.invert_yaxis()

        # 6. Projected growth for detailed analysis countries
        ax6 = fig.add_subplot(gs[2, :])
        if 'detailed_analysis' in report:
            growth_countries = []
            growth_values = []

            for country, data in report['detailed_analysis'].items():
                if 'summary' in data and 'projected_growth' in data['summary']:
                    growth = data['summary']['projected_growth']
                    if growth > 0:
                        growth_countries.append(country)
                        growth_values.append(growth)

            if growth_countries:
                ax6.bar(range(len(growth_countries)), growth_values, color='darkblue', alpha=0.8)
                ax6.set_xticks(range(len(growth_countries)))
                ax6.set_xticklabels(growth_countries, rotation=45, ha='right')
                ax6.set_ylabel('Projected Additional Population', fontsize=12, fontweight='bold')
                ax6.set_title(f'Projected Population Growth ({config.ANALYSIS_PARAMS["growth_trajectory_years"]} years)',
                             fontsize=14, fontweight='bold')
                ax6.grid(axis='y', alpha=0.3)

        plt.suptitle('NATIONAL MIGRATION PATTERN & PROPERTY DEMAND FLOW ANALYSIS\nAustralian Census 2021',
                    fontsize=18, fontweight='bold', y=0.995)

        output_path = f"{self.output_dir}/summary_dashboard.png"
        plt.savefig(output_path, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()
