import pandas as pd
import xgboost as xgb
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class XGBoostClassifier:
    """
    Module 3: Attack Classification.
    Supervised XGBoost model to classify authentication events into specific attack categories.
    """
    def __init__(self, model_dir: str, config: Dict[str, Any]):
        self.model_dir = Path(model_dir)
        self.model = None
        self.config = config
        self.version = "1.0.0"
        
        self.labels = self.config.get("classification_labels", [
            "Normal Authentication",
            "Credential Stuffing",
            "Password Spray",
            "Brute Force",
            "Impossible Travel",
            "Insider Threat",
            "Privilege Abuse",
            "Suspicious Device"
        ])
        
        self.features_used = config.get("classifier_features", [
            "hour_of_day", "day_of_week", "is_weekend", "is_working_hour",
            "is_failure", "country_encoded", "is_mfa", "time_since_last_login",
            "rolling_failures_24h"
        ])

    def train(self, X: pd.DataFrame, y: pd.Series):
        logger.info(f"Training Attack Classification model on {len(X)} samples...")
        missing_cols = [c for c in self.features_used if c not in X.columns]
        for c in missing_cols:
            X[c] = 0
            
        X_train = X[self.features_used].fillna(0)
        
        self.model = xgb.XGBClassifier(
            objective="multi:softprob",
            num_class=len(self.labels),
            eval_metric="mlogloss",
            random_state=42
        )
        self.model.fit(X_train, y)
        self.persist()

    def persist(self):
        import hashlib
        self.model_dir.mkdir(parents=True, exist_ok=True)
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_path = self.model_dir / f"xgboost_attack_classifier_{version_id}.json"
        meta_path = self.model_dir / f"classifier_metadata_{version_id}.json"
        
        if self.model is not None:
            self.model.save_model(model_path)
            
        with open(model_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
            
        metadata = {
            "model_version": version_id,
            "training_dataset_version": "1.0",
            "feature_schema_version": "1.0",
            "training_date": datetime.now().isoformat(),
            "feature_schema": self.features_used,
            "labels": self.labels,
            "hyperparameters": self.model.get_params() if self.model else {},
            "performance_metrics": {"mlogloss": "computed_during_eval"}, 
            "model_checksum": checksum,
            "model_file": model_path.name
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f)
        self.version = version_id
        logger.info(f"Classifier model {version_id} and metadata persisted to {self.model_dir}")

    def load(self) -> bool:
        meta_files = sorted(self.model_dir.glob("classifier_metadata_*.json"))
        if not meta_files:
            return False
            
        latest_meta = meta_files[-1]
        with open(latest_meta, "r") as f:
            meta = json.load(f)
            self.labels = meta.get("labels", self.labels)
            self.version = meta.get("model_version", "1.0.0")
            model_file = meta.get("model_file")
            
        model_path = self.model_dir / model_file
        if model_path.exists():
            self.model = xgb.XGBClassifier()
            self.model.load_model(model_path)
            logger.info(f"Pre-trained XGBoost classifier {self.version} loaded successfully.")
            return True
        return False

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            if not self.load():
                raise RuntimeError("Classifier model is not loaded. Train or load first.")
                
        logger.info("Executing XGBoost Attack Classification inference...")
        
        # Prepare inference data
        missing_cols = [c for c in self.features_used if c not in features.columns]
        for c in missing_cols:
            features[c] = 0
            
        X = features[self.features_used].fillna(0)
        
        probs = self.model.predict_proba(X)
        preds = probs.argmax(axis=1)
        
        confidences = probs.max(axis=1)
        predicted_labels = [self.labels[p] if p < len(self.labels) else "Unknown" for p in preds]
        
        return pd.DataFrame({
            "event_id": features["event_id"],
            "attack_category": predicted_labels,
            "prediction_confidence": confidences,
            "classification_model_version": self.version
        })
