import os
import pytest
import pandas as pd
from src.runtime.orchestrator import PipelineRunner

def test_phase3_detection_core():
    # Setup test configuration
    test_config = {
        "num_users": 10,
        "num_devices": 20,
        "num_events": 50,
        "attack_percentage": 0.1,
        "seed": 42,
        "force_retrain": True
    }
    
    runner = PipelineRunner()
    
    # We must run phase 2 first to generate inputs
    runner.run_phase2(config_overrides=test_config)
    
    # Run Phase 3
    runner.run_phase3(config_overrides=test_config)
    
    # 1. Verify model persistence
    assert os.path.exists("models/isolation_forest/trained_isolation_forest.pkl")
    assert os.path.exists("models/isolation_forest/model_metadata.json")
    
    # 2. Verify detection output
    assert os.path.exists("data/predictions/anomaly_scores.parquet")
    
    # 3. Check data constraints
    df_scores = pd.read_parquet("data/predictions/anomaly_scores.parquet")
    assert len(df_scores) == 50
    
    # Ensure expected columns from Rule Engine, Stat Engine, and Isolation Forest
    expected_cols = [
        "event_id", "rule_score", "triggered_rules", 
        "stat_score", "stat_metrics", 
        "if_score", "if_prediction", "detection_timestamp"
    ]
    for col in expected_cols:
        assert col in df_scores.columns
