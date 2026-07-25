import pytest
import pandas as pd
import tempfile
import os
from src.runtime.phase4_pipeline import Phase4Pipeline

def test_phase4_pipeline_execution():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            "classification_labels": ["Normal", "Attack"],
            "classifier_features": ["f1"]
        }
        
        # Create mock inputs
        anomalies_df = pd.DataFrame({
            "event_id": [1, 2],
            "rule_score": [50, 100],
            "model_version": ["1.0", "1.0"]
        })
        
        features_df = pd.DataFrame({
            "event_id": [1, 2],
            "f1": [0, 1],
            "is_failure": [0, 1]
        })
        
        anomalies_path = os.path.join(temp_dir, "anomaly_scores.parquet")
        features_path = os.path.join(temp_dir, "features.parquet")
        
        anomalies_df.to_parquet(anomalies_path)
        features_df.to_parquet(features_path)
        
        pipeline = Phase4Pipeline(config, temp_dir, temp_dir)
        
        # Execute pipeline
        result_df = pipeline.execute(anomalies_path, features_path)
        
        # Validate output
        assert len(result_df) == 2
        assert "risk_score" in result_df.columns
        assert "attack_category" in result_df.columns
        assert "detection_engine_version" in result_df.columns
        assert "processing_timestamp" in result_df.columns
        assert "processing_duration_sec" in result_df.columns
        
        # Validate persistence
        assert os.path.exists(os.path.join(temp_dir, "risk_scores.parquet"))
