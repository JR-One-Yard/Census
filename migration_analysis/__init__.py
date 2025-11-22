"""
National Migration Pattern & Property Demand Flow Analysis
Australian Census 2021 Data

A comprehensive analysis toolkit for identifying migration patterns,
cultural clusters, and predicting future property demand.
"""

__version__ = "1.0.0"
__author__ = "Census Analysis Team"

from .data_loader import CensusDataLoader
from .migration_analyzer import MigrationAnalyzer
from .visualizer import MigrationVisualizer
from .report_generator import ReportGenerator

__all__ = [
    'CensusDataLoader',
    'MigrationAnalyzer',
    'MigrationVisualizer',
    'ReportGenerator',
]
