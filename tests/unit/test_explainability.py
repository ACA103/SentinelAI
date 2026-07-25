import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path
from src.ai.explainability.explainer import RuleExplanationEngine, BehaviorExplanationEngine, NaturalLanguageGenerator
from src.ai.explainability.evidence import RecommendationEngine, EvidencePackageGenerator
from src.runtime.phase5_pipeline import Phase5Pipeline

def test_rule_explanation():
    engine = RuleExplanationEngine()
    result = engine.explain("ImpossibleTravel,VelocityAnomaly", {"country": "USA", "time_since_last_login": 10})
    assert len(result) == 2
    assert result[0]["Rule Name"] == "Impossible Travel"
    assert result[1]["Rule Name"] == "Velocity Anomaly"

def test_behavior_explanation():
    engine = BehaviorExplanationEngine()
    result = engine.explain(60.0, {"is_working_hour": 0, "is_weekend": 1})
    assert len(result) == 3 # Should trigger working hour, weekend, and behavior score deviations
    assert result[0]["Deviation"] == "Temporal Anomaly"
    
def test_nl_generator():
    gen = NaturalLanguageGenerator()
    package = {
        "Risk Level": "High",
        "Attack Classification": "Credential Stuffing",
        "Confidence": 0.95,
        "Triggered Rules": [{"Rule Name": "Impossible Travel"}],
        "Behavior Deviations": [{"Observed": "Login outside normal working hours"}],
        "Audit Metadata": {"Classification_Model_Version": "1.0.0"},
        "Feature Values": {"f1": 1}
    }
    nl = gen.generate(package)
    assert "High Risk" in nl["Executive_Summary"]
    assert "Credential Stuffing" in nl["Executive_Summary"]
    assert "outside normal working hours" in nl["Executive_Summary"]
    
    assert "Model Version: 1.0.0" in nl["Technical_Analysis"]
    assert "95.00%" in nl["Technical_Analysis"]
    assert "Impossible Travel" in nl["Technical_Analysis"]
    assert "f1" in nl["Technical_Analysis"]

def test_recommendation_engine():
    config = {"recommendations": {"Critical": "Lock account"}}
    recommender = RecommendationEngine(config)
    assert recommender.recommend("Critical") == "Lock account"
    assert recommender.recommend("Unknown") == "Monitor"

def test_phase5_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        
        # Mock features
        features = pd.DataFrame({
            "event_id": [1],
            "hour_of_day": [1], "day_of_week": [1], "is_weekend": [0], "is_working_hour": [1],
            "is_failure": [0], "country_encoded": [0], "is_mfa": [1], "time_since_last_login": [3600],
            "rolling_failures_24h": [0]
        })
        
        # Mock risk output
        risks = pd.DataFrame({
            "event_id": [1],
            "risk_score": [85.0],
            "risk_level": ["Critical"],
            "attack_category": ["Insider Threat"],
            "prediction_confidence": [0.88],
            "rule_contribution": [20.0],
            "stat_contribution": [10.0],
            "ml_contribution": [35.0],
            "behavioral_contribution": [10.0],
            "device_contribution": [10.0],
            "triggered_rules": ["VelocityAnomaly"],
            "detection_engine_version": ["1.0"],
            "risk_engine_version": ["1.0"],
            "classification_model_version": ["1.0"]
        })
        
        f_path = tmp_path / "features.parquet"
        r_path = tmp_path / "risk_scores.parquet"
        features.to_parquet(f_path)
        risks.to_parquet(r_path)
        
        config = {"classification_labels": ["Normal Authentication", "Insider Threat"]}
        pipeline = Phase5Pipeline(config, tmp, tmp)
        
        # Execute
        out_df = pipeline.execute(str(f_path), str(r_path))
        
        assert len(out_df) == 1
        assert "Explanation" in out_df.columns
        assert "Recommended_Action" in out_df.columns
        assert "Audit_Metadata" in out_df.columns
        
        audit_meta = json.loads(out_df.iloc[0]["Audit_Metadata"])
        assert audit_meta["Event_ID"] == 1
        assert "Processing_Timestamp" in audit_meta
