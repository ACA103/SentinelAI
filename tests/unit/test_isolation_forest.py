import pytest
import pandas as pd
import os
from src.ai.detection.isolation_forest import IsolationForestEngine

@pytest.fixture
def sample_features():
    return pd.DataFrame({
        "event_id": range(100),
        "hour_of_day": [9] * 99 + [3],
        "day_of_week": [1] * 100,
        "is_weekend": [0] * 100,
        "is_working_hour": [1] * 99 + [0],
        "is_failure": [0] * 99 + [1],
        "country_encoded": [1] * 100,
        "is_mfa": [1] * 100,
        "time_since_last_login": [3600] * 99 + [1],
        "rolling_failures_24h": [0] * 99 + [10]
    })

def test_isolation_forest_train_and_predict(sample_features, tmp_path):
    engine = IsolationForestEngine(str(tmp_path))
    
    # Train
    engine.train(sample_features)
    
    # Check persistence
    assert list(tmp_path.glob("*.pkl"))
    assert list(tmp_path.glob("*.json"))
    
    # Reload and predict
    engine2 = IsolationForestEngine(str(tmp_path))
    assert engine2.load() == True
    
    preds = engine2.predict(sample_features)
    
    # The last event is highly anomalous
    assert preds.loc[99, "if_prediction"] == 1
    assert preds.loc[99, "if_score"] > preds.loc[0, "if_score"]
