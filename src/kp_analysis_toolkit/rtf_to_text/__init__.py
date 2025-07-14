"""RTF to text converter module."""

from .protocols import RtfConverter, RtfToTextService
from .service import RtfToTextService as RtfToTextServiceImpl

__version__ = "0.2.0"

__all__ = [
    "RtfConverter",
    "RtfToTextService",
    "RtfToTextServiceImpl",
]

"""Change History
0.1    Initial version
0.2.0  2025-07-12: Refactor to use Dependency Injection patterns
"""
