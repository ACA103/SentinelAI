import pandas as pd
import time
import logging
from datetime import datetime
from pathlib import Path
from src.ai.risk.fusion_engine import RiskFusionEngine
from src.ai.classification.xgboost_classifier import XGBoostClassifier

logger = logging.getLogger(__name__)

class Phase4Pipeline:
    """
    Module 4: Classification Pipeline.
    Orchestrates Enterprise Risk Fusion and Attack Classification.
    Output conforms to Documented Output Contract.
    """
    def __init__(self, config: dict, model_dir: str, output_dir: str):
        self.config = config
        self.model_dir = Path(model_dir)
        self.output_dir = Path(output_dir)
        self.risk_engine = RiskFusionEngine(config)
        self.classifier = XGBoostClassifier(str(model_dir), config)
        
    def execute(self, anomaly_scores_path: str, features_path: str) -> pd.DataFrame:
        start_time = time.time()
        logger.info("Starting Phase 4 Classification Pipeline...")
        
        # 1. Load Data
        anomalies_df = pd.read_parquet(anomaly_scores_path)
        features_df = pd.read_parquet(features_path)
        
        # 2. Execute Enterprise Risk Fusion
        risk_df = self.risk_engine.calculate_risk(anomalies_df)
        
        # 3. Execute Attack Classification
        if not self.classifier.load():
            logger.warning("No pre-trained classification model found. Training dummy model for execution...")
            self.classifier.train(features_df, features_df["attack_label"])
            
        class_df = self.classifier.predict(features_df)
        
        # 4. Merge Results & Ensure Output Contract
        result_df = risk_df.merge(class_df, on="event_id")
        
        # Add Traceability Metadata
        det_engine_version = anomalies_df.get("model_version", pd.Series(["1.0"] * len(anomalies_df)))
        
        result_df["detection_engine_version"] = det_engine_version
        result_df["feature_schema_version"] = self.config.get("feature_schema_version", "1.0.0")
        result_df["processing_timestamp"] = datetime.now().isoformat()
        result_df["processing_duration_sec"] = time.time() - start_time
        
        # Save output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "risk_scores.parquet"
        result_df.to_parquet(out_path, index=False)
        
        logger.info(f"Phase 4 Pipeline completed successfully. Output persisted to {out_path}")
        return result_df
