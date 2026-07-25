import pytest
import pandas as pd
from src.ai.detection.rule_engine import RuleEngine

def test_rule_engine_excessive_failures():
    engine = RuleEngine({"failure_threshold": 3, "velocity_threshold": 5})
    df = pd.DataFrame({
        "event_id": [1, 2],
        "rolling_failures_24h": [1, 5],
        "time_since_last_login": [100, 100],
        "is_working_hour": [1, 1]
    })
    
    result = engine.evaluate(df)
    assert result.loc[result["event_id"] == 1, "rule_score"].values[0] == 0
    assert result.loc[result["event_id"] == 2, "rule_score"].values[0] == 30
    assert "ExcessiveFailures" in result.loc[result["event_id"] == 2, "triggered_rules"].values[0]

def test_rule_engine_velocity_and_offhours():
    engine = RuleEngine({"velocity_threshold": 5})
    df = pd.DataFrame({
        "event_id": [1],
        "rolling_failures_24h": [0],
        "time_since_last_login": [2],
        "is_working_hour": [0]
    })
    
    result = engine.evaluate(df)
    assert result.loc[0, "rule_score"] == 30 # 20 for velocity + 10 for off-hours
    assert "VelocityAnomaly" in result.loc[0, "triggered_rules"]
    assert "OffHours" in result.loc[0, "triggered_rules"]
