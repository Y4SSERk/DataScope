"""
CA Analysis Engine - Professional Edition
Logic for Correspondence Analysis and Chi-squared independence testing.
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from typing import Dict, Any
from src.core.exceptions import AnalysisError

class CAEngine:
    def __init__(self, df: pd.DataFrame):
        if df.empty or df.shape[0] < 2 or df.shape[1] < 2:
            raise AnalysisError("Table must be at least 2x2 with numeric data.")
        self.df = df

    def run(self) -> Dict[str, Any]:
        """Performs full CA computation."""
        try:
            # Chi-squared test
            chi2, p_value, dof, expected = chi2_contingency(self.df)
            
            # Standardized residuals/Inertia
            data = self.df.values.astype(float)
            total_n = data.sum()
            P = data / total_n
            r, c = P.sum(axis=1), P.sum(axis=0)
            S = (P - np.outer(r, c)) / np.sqrt(np.outer(r, c))
            
            # SVD for coordinates
            U, s, Vt = np.linalg.svd(S, full_matrices=False)
            inertia = s ** 2
            
            n_dims = min(2, len(s))
            row_coords = U[:, :n_dims] * s[:n_dims] / np.sqrt(r)[:, None]
            col_coords = Vt.T[:, :n_dims] * s[:n_dims] / np.sqrt(c)[:, None]

            # Contribution to Chi2 (Residuals)
            residuals = (data - expected) ** 2 / expected
            res_df = pd.DataFrame(residuals, index=self.df.index, columns=self.df.columns).round(3)

            return {
                "chi2": chi2,
                "p_value": p_value,
                "dof": dof,
                "expected": expected,
                "inertia": inertia,
                "total_inertia": np.sum(inertia),
                "row_coords": row_coords,
                "col_coords": col_coords,
                "row_names": self.df.index.tolist(),
                "col_names": self.df.columns.tolist(),
                "res_df": res_df
            }
        except Exception as e:
            raise AnalysisError(f"CA Failed: {str(e)}")
