import os
import pytest
import pandas as pd
from src.runtime.orchestrator import PipelineRunner

def test_phase2_pipeline():
    # Setup miniature pipeline configuration for fast testing
    test_config = {
        "num_users": 10,
        "num_devices": 20,
        "num_events": 50,
        "attack_percentage": 0.1,
        "seed": 42
    }
    
    runner = PipelineRunner()
    runner.run_phase2(config_overrides=test_config)
    
    # 1. Verify artifacts were generated at correct paths
    assert os.path.exists("data/raw/auth_logs.parquet")
    assert os.path.exists("data/processed/features.parquet")
    assert os.path.exists("artifacts/user_profiles.pkl")
    assert os.path.exists("artifacts/device_profiles.pkl")
    
    # 2. Verify data constraints
    df_raw = pd.read_parquet("data/raw/auth_logs.parquet")
    assert len(df_raw) == 50
    assert df_raw["timestamp"].is_monotonic_increasing
    
    df_features = pd.read_parquet("data/processed/features.parquet")
    assert len(df_features) == 50
    assert "is_weekend" in df_features.columns
    assert "hour_of_day" in df_features.columns
    assert "time_since_last_login" in df_features.columns
    assert "rolling_failures_24h" in df_features.columns

    # 3. Check behavior profiles generated
    import pickle
    with open("artifacts/user_profiles.pkl", "rb") as f:
        profiles = pickle.load(f)
        assert len(profiles) > 0
        user_id = list(profiles.keys())[0]
        assert "typical_login_hour" in profiles[user_id]
