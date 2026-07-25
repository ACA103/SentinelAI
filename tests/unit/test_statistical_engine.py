import pytest
import pandas as pd
import pickle
import os
from src.ai.detection.statistical_engine import StatisticalEngine

@pytest.fixture
def mock_profiles(tmp_path):
    user_profiles = {1: {"typical_login_hour": 9, "success_rate": 1.0}}
    device_profiles = {101: {"primary_user": 1}, 102: {"primary_user": 999}}
    
    u_path = tmp_path / "user_profiles.pkl"
    d_path = tmp_path / "device_profiles.pkl"
    
    with open(u_path, "wb") as f:
        pickle.dump(user_profiles, f)
    with open(d_path, "wb") as f:
        pickle.dump(device_profiles, f)
        
    return str(u_path), str(d_path)

def test_statistical_engine_normal(mock_profiles):
    engine = StatisticalEngine(mock_profiles[0], mock_profiles[1])
    df = pd.DataFrame({
        "event_id": [1],
        "user_id": [1],
        "device_id": [101],
        "hour_of_day": [10],
        "is_failure": [0]
    })
    
    result = engine.evaluate(df)
    assert result.loc[0, "stat_score"] == 0
    assert result.loc[0, "stat_metrics"] == "None"

def test_statistical_engine_anomalous(mock_profiles):
    engine = StatisticalEngine(mock_profiles[0], mock_profiles[1])
    df = pd.DataFrame({
        "event_id": [1, 2],
        "user_id": [1, 1],
        "device_id": [101, 102], # 102 is device mismatch
        "hour_of_day": [3, 9], # 3 is hour deviation (diff 6)
        "is_failure": [1, 0] # anomalous failure
    })
    
    result = engine.evaluate(df)
    
    # Event 1: Hour deviation (20) + Anomalous failure (15) = 35
    assert result.loc[0, "stat_score"] == 35
    assert "HighHourDeviation" in result.loc[0, "stat_metrics"]
    assert "AnomalousFailure" in result.loc[0, "stat_metrics"]
    
    # Event 2: Device mismatch (30)
    assert result.loc[1, "stat_score"] == 30
    assert "DeviceMismatch" in result.loc[1, "stat_metrics"]
