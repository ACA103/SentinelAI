import pytest
import pandas as pd
from src.ai.risk.fusion_engine import RiskFusionEngine

def test_risk_fusion_normalization():
    config = {
        "risk_weights": {
            "rule_contribution": 0.5,
            "stat_contribution": 0.0,
            "ml_contribution": 0.5,
            "behavioral_contribution": 0.0,
            "device_contribution": 0.0
        }
    }
    engine = RiskFusionEngine(config)
    
    # Inputs: rule_score max 100, if_score max 100
    df = pd.DataFrame({
        "event_id": [1, 2],
        "rule_score": [100, 50],
        "if_score": [100, 50]
    })
    
    result = engine.calculate_risk(df)
    
    assert len(result) == 2
    assert result.iloc[0]["risk_score"] == 100
    assert result.iloc[1]["risk_score"] == 50
    assert result.iloc[0]["risk_level"] == "Critical"
    assert result.iloc[1]["risk_level"] == "Elevated"

def test_risk_fusion_missing_columns():
    engine = RiskFusionEngine({})
    
    df = pd.DataFrame({
        "event_id": [1],
        "rule_score": [100]
        # Missing if_score, stat_score, etc.
    })
    
    result = engine.calculate_risk(df)
    
    assert len(result) == 1
    # Check that missing columns were handled as 0
    assert result.iloc[0]["ml_contribution"] == 0.0
    assert result.iloc[0]["rule_contribution"] > 0
    
def test_risk_level_boundaries():
    engine = RiskFusionEngine({})
    df = pd.DataFrame({
        "event_id": [1, 2, 3, 4, 5],
        "rule_score": [0, 20, 40, 60, 80], # Dummy values, we just want to test risk_level assignment indirectly
    })
    
    # Since weights are applied, let's just force the final score mathematically via weights 1.0 on rule_score for testing
    engine.weights = {"rule_contribution": 1.0}
    
    result = engine.calculate_risk(df)
    levels = result["risk_level"].tolist()
    
    # Expected: <=20: Low, <=40: Moderate, <=60: Elevated, <=80: High, >80: Critical
    assert levels[0] == "Low"
    assert levels[1] == "Low"
    assert levels[2] == "Moderate"
    assert levels[3] == "Elevated"
    assert levels[4] == "High"
