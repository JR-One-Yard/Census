#!/usr/bin/env python3
"""
Main script for National Migration Pattern & Property Demand Flow Analysis
Australian Census 2021 Data

This script orchestrates the complete analysis pipeline:
1. Load census data
2. Identify cultural clusters and anchor points
3. Analyze migration timing and patterns
4. Cross-reference with housing affordability
5. Calculate growth projections
6. Generate comprehensive visualizations and reports
"""

import pandas as pd
import numpy as np
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data_loader import CensusDataLoader
from migration_analyzer import MigrationAnalyzer
from visualizer import MigrationVisualizer
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.OUTPUT_DIR, 'analysis.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print analysis banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║     NATIONAL MIGRATION PATTERN & PROPERTY DEMAND FLOW ANALYSIS      ║
    ║                    Australian Census 2021 Data                      ║
    ║                                                                      ║
    ║                    Compute Load: ⭐⭐⭐⭐⭐                           ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    logger.info("Starting migration analysis pipeline")


def main():
    """Main analysis pipeline"""

    print_banner()

    start_time = datetime.now()
    logger.info(f"Analysis started at {start_time}")

    try:
        # ============================================================
        # PHASE 1: DATA LOADING
        # ============================================================
        logger.info("=" * 80)
        logger.info("PHASE 1: DATA LOADING")
        logger.info("=" * 80)

        analyzer = MigrationAnalyzer(geo_level=config.PRIMARY_GEO)
        analyzer.load_data(use_cache=True)

        logger.info(f"Data loaded for {config.PRIMARY_GEO} level")

        # ============================================================
        # PHASE 2: MIGRATION PATTERN ANALYSIS
        # ============================================================
        logger.info("=" * 80)
        logger.info("PHASE 2: MIGRATION PATTERN ANALYSIS")
        logger.info("=" * 80)

        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()

        logger.info("Migration analysis complete")
        logger.info(f"Countries analyzed: {len(report['overview'])}")
        logger.info(f"Detailed analysis for: {', '.join(report['top_countries'][:5])}")

        # ============================================================
        # PHASE 3: VISUALIZATION
        # ============================================================
        logger.info("=" * 80)
        logger.info("PHASE 3: VISUALIZATION")
        logger.info("=" * 80)

        visualizer = MigrationVisualizer()

        # Create summary dashboard
        visualizer.create_summary_dashboard(report)

        # Create country distribution plot
        visualizer.plot_country_distribution(report['overview'], top_n=20)

        # Create anchor points heatmap
        visualizer.plot_anchor_points_heatmap(report['overview'], top_n=15)

        # Create detailed visualizations for top countries
        for country in report['top_countries'][:10]:
            logger.info(f"Creating visualizations for {country}...")

            if country in report['detailed_analysis']:
                data = report['detailed_analysis'][country]

                # Housing affordability
                if 'clusters_with_housing' in data and not data['clusters_with_housing'].empty:
                    visualizer.plot_housing_affordability(
                        data['clusters_with_housing'],
                        country
                    )

                # Growth projections
                if 'growth_projections' in data and data['growth_projections']:
                    visualizer.plot_growth_projections(
                        data['growth_projections'],
                        country,
                        top_n=20
                    )

        logger.info("Visualizations complete")

        # ============================================================
        # PHASE 4: REPORT GENERATION
        # ============================================================
        logger.info("=" * 80)
        logger.info("PHASE 4: REPORT GENERATION")
        logger.info("=" * 80)

        report_gen = ReportGenerator()

        # Generate comprehensive text report
        report_gen.generate_text_report(report)

        # Export key datasets to CSV
        report_gen.export_results_to_csv(report)

        # Generate executive summary
        report_gen.generate_executive_summary(report)

        logger.info("Report generation complete")

        # ============================================================
        # COMPLETION
        # ============================================================
        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("=" * 80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Start time: {start_time}")
        logger.info(f"End time: {end_time}")
        logger.info(f"Duration: {duration}")
        logger.info(f"Output directory: {config.OUTPUT_DIR}")

        print("\n" + "=" * 80)
        print("✓ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nDuration: {duration}")
        print(f"\nResults saved to: {config.OUTPUT_DIR}")
        print("\nGenerated files:")
        print("  - summary_dashboard.png")
        print("  - country_distribution.png")
        print("  - anchor_points_heatmap.png")
        print("  - housing_affordability_*.png (for top countries)")
        print("  - growth_projections_*.png (for top countries)")
        print("  - comprehensive_report.txt")
        print("  - executive_summary.txt")
        print("  - *.csv (exported datasets)")
        print("\n" + "=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\n✗ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
