"""
Implements: 03_AI/00_AI_ARCHITECTURE.md (Isolation Forest)
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class IsolationForestEngine:
    """
    Unsupervised ML model for unknown anomaly detection using engineered features.
    """
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.model = None
        self.version = "1.0.0"
        self.features_used = [
            "hour_of_day", "day_of_week", "is_weekend", "is_working_hour",
            "is_failure", "country_encoded", "is_mfa", "time_since_last_login",
            "rolling_failures_24h"
        ]
        
    def train(self, features: pd.DataFrame):
        logger.info(f"Training Isolation Forest model with {len(features)} samples...")
        X = features[self.features_used].fillna(0)
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.model.fit(X)
        self.persist()
        
    def persist(self):
        import hashlib
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.model_dir / f"trained_isolation_forest_{version_id}.pkl"
        meta_path = self.model_dir / f"model_metadata_{version_id}.json"
        
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)
            
        with open(model_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
            
        metadata = {
            "model_version": version_id,
            "training_dataset_version": "1.0",
            "feature_schema_version": "1.0",
            "training_date": datetime.now().isoformat(),
            "feature_schema": self.features_used,
            "hyperparameters": {"n_estimators": self.model.n_estimators, "contamination": self.model.contamination},
            "performance_metrics": {"estimated_anomaly_rate": self.model.contamination},
            "model_checksum": checksum,
            "model_file": model_path.name
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f)
        self.version = version_id
        logger.info(f"Isolation Forest model {version_id} persisted to {model_path}")
        
    def load(self) -> bool:
        meta_files = sorted(self.model_dir.glob("model_metadata_*.json"))
        if not meta_files:
            return False
            
        latest_meta = meta_files[-1]
        with open(latest_meta, "r") as f:
            metadata = json.load(f)
            
        model_path = self.model_dir / metadata["model_file"]
        if model_path.exists():
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            self.version = metadata["model_version"]
            logger.info(f"Pre-trained Isolation Forest model {self.version} loaded successfully.")
            return True
        return False
        
    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            if not self.load():
                logger.warning("No saved model found. Initiating dynamic training...")
                self.train(features)
                
        logger.info("Executing Isolation Forest inference...")
        X = features[self.features_used].fillna(0)
        
        preds = self.model.predict(X)
        scores = self.model.decision_function(X)
        
        normalized_scores = (-scores + 0.5) * 100
        normalized_scores = normalized_scores.clip(min=0, max=100)
        
        return pd.DataFrame({
            "event_id": features["event_id"],
            "if_score": normalized_scores,
            "if_prediction": (preds == -1).astype(int)
        })
