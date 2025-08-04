"""Search engine services for process scripts."""

from kp_analysis_toolkit.process_scripts.services.search_engine.field_extractor import (
    DefaultFieldExtractor,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.pattern_compiler import (
    DefaultPatternCompiler,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.protocols import (
    FieldExtractor,
    PatternCompiler,
    ResultProcessor,
    SearchEngineService,
    SystemFilterService,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.result_processor import (
    DefaultResultProcessor,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.service import (
    DefaultSearchEngineService,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.system_filter import (
    DefaultSystemFilterService,
)

__version__ = "0.1.0"

__all__ = [
    "DefaltSearchEngineService",
    "DefaultFieldExtractor",
    "DefaultPatternCompiler",
    "DefaultResultProcessor",
    "DefaultSystemFilterService",
    "FieldExtractor",
    "PatternCompiler",
    "ResultProcessor",
    "SearchEngineService",
    "SystemFilterService",
]

"""Change History
0.1.0  2025-08-03: Initial implementation using Dependency Injection patterns
"""
