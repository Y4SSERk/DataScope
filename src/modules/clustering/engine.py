"""
Clustering Analysis Engine - Professional Edition
Logic for K-Means and Random Forest classification with feature support.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from typing import Dict, Any, Tuple, Optional
from src.core.exceptions import AnalysisError

class ClusteringEngine:
    def __init__(self, scaled_data: pd.DataFrame):
        self.data = scaled_data
        self.clf: Optional[RandomForestClassifier] = None
        self.accuracy: float = 0.0
        self.report: str = ""
        self.labels: Optional[pd.Series] = None

    def run_clustering_flow(self, n_clusters: int = 4) -> Dict[str, Any]:
        """Runs the standard K-Means -> RF Training flow."""
        try:
            # 1. K-Means
            kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
            self.labels = pd.Series(kmeans.fit_predict(self.data), index=self.data.index, name="Cluster")
            
            # 2. Train Classifier
            X_train, X_test, y_train, y_test = train_test_split(
                self.data, self.labels, test_size=0.3, random_state=42
            )
            self.clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            self.clf.fit(X_train, y_train)
            
            y_pred = self.clf.predict(X_test)
            self.accuracy = accuracy_score(y_test, y_pred)
            self.report = classification_report(y_test, y_pred, zero_division=0)
            
            return {
                "accuracy": self.accuracy,
                "report": self.report,
                "labels": self.labels,
                "distribution": self.labels.value_counts().sort_index(),
                "n_clusters": n_clusters
            }
        except Exception as e:
            raise AnalysisError(f"Clustering flow failed: {str(e)}")

    def predict(self, feature_values: list) -> int:
        """Predicts cluster for raw feature inputs."""
        if not self.clf:
            raise AnalysisError("Classifier is not trained.")
        try:
            # Wrap in DataFrame to avoid feature name warning
            input_df = pd.DataFrame([feature_values], columns=self.data.columns)
            return int(self.clf.predict(input_df)[0])
        except Exception as e:
            raise AnalysisError(f"Prediction failed: {str(e)}")
