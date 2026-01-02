"""
DataScope Core Exceptions
Standardized error handling for the entire application.
"""

class DataScopeError(Exception):
    """Base exception for all DataScope errors."""
    pass

class DataLoadError(DataScopeError):
    """Raised when data loading fails."""
    pass

class AnalysisError(DataScopeError):
    """Raised when an analysis engine fails."""
    pass

class ValidationError(DataScopeError):
    """Raised when data validation fails."""
    pass
