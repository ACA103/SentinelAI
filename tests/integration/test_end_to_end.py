import pytest
import os
from pathlib import Path
from src.runtime.orchestrator import PipelineRunner

def test_end_to_end_pipeline():
    # Setup
    runner = PipelineRunner()
    
    # Run the pipeline (limiting events if possible through config)
    # Using small config overrides to speed up tests if applicable
    config_overrides = {"num_synthetic_events": 100}
    runner.run_all(config_overrides=config_overrides)
    
    # Assert artifacts generated
    assert Path("data/raw/auth_logs.parquet").exists()
    assert Path("data/processed/features.parquet").exists()
    assert Path("data/predictions/anomaly_scores.parquet").exists()
    assert Path("data/predictions/risk_scores.parquet").exists()
    assert Path("data/predictions/explanations.parquet").exists()
    assert Path("models/isolation_forest").exists()
    assert Path("artifacts/user_profiles.pkl").exists()
    assert Path("artifacts/device_profiles.pkl").exists()
