"""Report generator services for configuration analysis."""

from .protocols import ReportGeneratorService
from .service import DefaultReportGenerator

__all__ = [
    "DefaultReportGenerator",
    "ReportGeneratorService",
]
