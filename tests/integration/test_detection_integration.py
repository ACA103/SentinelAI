import pytest
import os
import pandas as pd
from src.runtime.orchestrator import PipelineRunner

def test_integration_detection_core():
    """
    Integration test validating that the Detection Core correctly consumes Phase 2 outputs.
    """
    test_config = {
        "num_users": 5,
        "num_devices": 10,
        "num_events": 20,
        "attack_percentage": 0.1,
        "seed": 42,
        "force_retrain": True
    }
    
    runner = PipelineRunner()
    
    # Generate Phase 2 dependencies
    runner.run_phase2(config_overrides=test_config)
    
    # Run Phase 3
    runner.run_phase3(config_overrides=test_config)
    
    # Assert Phase 3 outputs are valid and integrate seamlessly
    output_path = "data/predictions/anomaly_scores.parquet"
    assert os.path.exists(output_path)
    
    df = pd.read_parquet(output_path)
    assert len(df) == 20
    assert "event_id" in df.columns
    assert "rule_score" in df.columns
    assert "stat_score" in df.columns
    assert "if_score" in df.columns
    assert "detection_timestamp" in df.columns
    
    # Check that Isolation Forest persistence is sound
    assert os.path.exists("models/isolation_forest/trained_isolation_forest.pkl")
