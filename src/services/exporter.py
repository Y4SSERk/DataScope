"""
DataScope Exporter Service
Handles results export to Excel and other formats.
"""

import pandas as pd
from typing import Dict
from src.core.exceptions import DataScopeError

class Exporter:
    @staticmethod
    def to_excel(filepath: str, sheets: Dict[str, pd.DataFrame]) -> None:
        """Exports multiple dataframes to different sheets in an Excel file."""
        try:
            with pd.ExcelWriter(filepath) as writer:
                for sheet_name, df in sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name)
        except Exception as e:
            raise DataScopeError(f"Failed to export Excel: {str(e)}")
