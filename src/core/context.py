"""
DataScope App Context
Central state management and dependency injection container.
"""

from typing import Optional, Dict, Any
import pandas as pd

class AppContext:
    """
    Holds application state and shared services.
    Eliminates the need for global singletons.
    """
    
    def __init__(self) -> None:
        self.raw_data: Optional[pd.DataFrame] = None
        self.scaled_data: Optional[pd.DataFrame] = None
        self.features: list[str] = []
        self.individual_prefix: str = "Individual"
        self.settings: Dict[str, Any] = {
            "theme_mode": "dark"
        }
        self.metadata: Dict[str, Any] = {}

    def set_data(self, df: pd.DataFrame, scaled_df: Optional[pd.DataFrame] = None) -> None:
        self.raw_data = df
        self.scaled_data = scaled_df
        self.features = df.columns.tolist() if df is not None else []

    def set_individual_prefix(self, prefix: str) -> None:
        self.individual_prefix = prefix

    def get_individual_labels(self) -> list[str]:
        if self.raw_data is None: return []
        return [f"{self.individual_prefix}_{i}" for i in self.raw_data.index]

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
