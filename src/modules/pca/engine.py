"""
PCA Analysis Engine - Professional Edition
Pure logic for Principal Component Analysis with full metrics suite.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from typing import Dict, Any, List
from src.core.exceptions import AnalysisError

class PCAEngine:
    def __init__(self, raw_data: pd.DataFrame, scaled_data: pd.DataFrame):
        if raw_data is None or scaled_data is None:
            raise AnalysisError("No data provided for PCA.")
        self.raw_data = raw_data
        self.scaled_data = scaled_data
        self._pca = PCA()
        self.results: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        """Performs full PCA and returns comprehensive metrics."""
        try:
            # Fit/Transform on scaled data
            components = self._pca.fit_transform(self.scaled_data)
            
            # Basic metrics
            eigenvalues = self._pca.explained_variance_
            inertia = self._pca.explained_variance_ratio_ * 100
            loadings = self._pca.components_.T * np.sqrt(eigenvalues)
            
            # Quality and Contributions
            # Cos2: Quality of representation on first 2 dims
            cos2 = components[:, :2] ** 2 / np.sum(components ** 2, axis=1, keepdims=True)
            # Contrib: Percentage of contribution to first 2 dims
            contrib = (components[:, :2] ** 2 / np.sum(components[:, :2] ** 2, axis=0)) * 100

            self.results = {
                "components": components,
                "eigenvalues": eigenvalues,
                "inertia": inertia,
                "loadings": loadings,
                "cos2": cos2,
                "contrib": contrib,
                "features": self.scaled_data.columns.tolist(),
                "index": self.scaled_data.index.tolist(),
                "scaled_data": self.scaled_data,
                "corr_matrix": self.raw_data.corr(),
                "desc_stats": self.raw_data.describe().loc[['mean', 'std']]
            }
            return self.results
        except Exception as e:
            raise AnalysisError(f"PCA Analysis failed: {str(e)}")

    def get_tab_data(self) -> Dict[str, Any]:
        if not self.results:
            self.run()
        return self.results
