"""
Cybersecurity Analysis Engine - Professional Edition
Dual-algorithm anomaly detection (Isolation Forest + LOF) with English reporting.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, Any
from src.core.exceptions import AnalysisError

class SecurityEngine:
    def __init__(self, data: pd.DataFrame, contamination: float = 0.1):
        if data is None or data.empty:
            raise AnalysisError("No data provided for security scan.")
        self.data = data
        self.contamination = contamination

    def run_scan(self) -> Dict[str, Any]:
        """Runs security algorithms and finds consensus high-risk IDs."""
        try:
            # Normalization using MinMaxScaler as per Cyber.pdf
            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(self.data)
            df_scaled = pd.DataFrame(X_scaled, columns=self.data.columns, index=self.data.index)

            # Isolation Forest
            iso = IsolationForest(contamination=self.contamination, random_state=42)
            y_iso = iso.fit_predict(df_scaled)
            
            # LOF
            lof = LocalOutlierFactor(n_neighbors=min(20, len(df_scaled)-1), contamination=self.contamination)
            y_lof = lof.fit_predict(df_scaled)
            
            # Contextual PCA for viz
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(df_scaled)
            
            # Consensus: flagged by both
            high_risk_idx = np.where((y_iso == -1) & (y_lof == -1))[0]
            
            # Get Station labels
            labels = [f"Station {i}" for i in self.data.index]
            high_risk_labels = [labels[idx] for idx in high_risk_idx]
            
            return {
                "y_iso": y_iso,
                "y_lof": y_lof,
                "X_pca": X_pca,
                "high_risk_ids": high_risk_labels,
                "iso_count": int((y_iso == -1).sum()),
                "lof_count": int((y_lof == -1).sum()),
                "risk_count": len(high_risk_idx),
                "labels": labels
            }
        except Exception as e:
            raise AnalysisError(f"Security scan failed: {str(e)}")
