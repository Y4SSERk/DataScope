"""
DataScope Data Loaders
Implementation of robust data ingestion logic.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple
from src.core.exceptions import DataLoadError

def load_excel_dataset(filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads an Excel file and returns (raw_df, scaled_df).
    
    Raises:
        DataLoadError: If loading or processing fails.
    """
    try:
        if not os.path.exists(filepath):
            raise DataLoadError(f"File not found: {filepath}")

        # Load data (do not use first column as index, we want row-based IDs)
        df = pd.read_excel(filepath, index_col=None)
        
        # Filter numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            raise DataLoadError("Dataset contains no numeric columns.")
            
        if len(numeric_df) < 2:
            raise DataLoadError("Dataset must have at least 2 rows for analysis.")

        # Set 1-based index (Row 2 in Excel becomes ID 1)
        numeric_df.index = range(1, len(numeric_df) + 1)

        # Handle NaNs
        if numeric_df.isnull().any().any():
            numeric_df = numeric_df.fillna(numeric_df.mean())

        # Scale data
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(numeric_df)
        scaled_df = pd.DataFrame(
            scaled_values, 
            columns=numeric_df.columns, 
            index=numeric_df.index
        )
        
        return numeric_df, scaled_df

    except Exception as e:
        if isinstance(e, DataLoadError):
            raise e
        raise DataLoadError(f"Unexpected error loading data: {str(e)}")
