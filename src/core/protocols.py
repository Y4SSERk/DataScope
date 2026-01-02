"""
DataScope Core Protocols
Formal interfaces for component decoupling and testability.
"""

from typing import Protocol, runtime_checkable, Any
import pandas as pd

@runtime_checkable
class AnalysisEngine(Protocol):
    """Interface for all analysis modules (PCA, CA, etc.)."""
    
    def run(self, data: pd.DataFrame, **kwargs: Any) -> Any:
        """Execute the analysis logic and return results."""
        ...

@runtime_checkable
class ViewComponent(Protocol):
    """Interface for UI view components."""
    
    def render(self) -> None:
        """Render the UI component."""
        ...
