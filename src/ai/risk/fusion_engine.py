import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RiskFusionEngine:
    """
    Module 1 & 2: Enterprise Risk Fusion Engine and Risk Contribution Breakdown.
    Consumes Detection Engine anomaly scores and aggregates them into a normalized
    Enterprise Risk Score [0-100]. Also categorizes risk into severity levels.
    """
    def __init__(self, config: Dict[str, Any]):
        self.weights = config.get("risk_weights", {
            "rule_contribution": 0.30,
            "stat_contribution": 0.10,
            "ml_contribution": 0.40,
            "behavioral_contribution": 0.10,
            "device_contribution": 0.10
        })
        self.version = "1.0.0"

    def calculate_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Executing Enterprise Risk Fusion...")
        
        # 1. Extract raw scores, defaulting to 0 if not present in upstream results
        # Assuming rule_score, if_score, etc. might exist in detection df
        rule_score = df.get("rule_score", pd.Series(0, index=df.index))
        stat_score = df.get("stat_score", pd.Series(0, index=df.index))
        if_score = df.get("if_score", pd.Series(0, index=df.index))
        behavior_score = df.get("behavior_score", pd.Series(0, index=df.index))
        device_score = df.get("device_score", pd.Series(0, index=df.index))
        
        # 2. Normalize and apply weights
        rule_contrib = rule_score * self.weights.get("rule_contribution", 0.3)
        stat_contrib = stat_score * self.weights.get("stat_contribution", 0.1)
        ml_contrib = if_score * self.weights.get("ml_contribution", 0.4)
        behavior_contrib = behavior_score * self.weights.get("behavioral_contribution", 0.1)
        device_contrib = device_score * self.weights.get("device_contribution", 0.1)
        
        # 3. Sum Risk Score and Normalize to 0-100
        raw_risk_score = (rule_contrib + stat_contrib + ml_contrib + 
                          behavior_contrib + device_contrib)
        
        final_risk_score = raw_risk_score.clip(lower=0, upper=100)
        
        # 4. Determine Risk Levels
        def assign_level(score):
            if score <= 15: return "Low"
            elif score <= 25: return "Moderate"
            elif score <= 30: return "High"
            else: return "Critical"
            
        risk_levels = final_risk_score.apply(assign_level)
        
        # 5. Output Preserving Intermediate Contributions
        return pd.DataFrame({
            "event_id": df["event_id"],
            "rule_contribution": rule_contrib,
            "stat_contribution": stat_contrib,
            "ml_contribution": ml_contrib,
            "behavioral_contribution": behavior_contrib,
            "device_contribution": device_contrib,
            "risk_score": final_risk_score,
            "risk_level": risk_levels,
            "risk_engine_version": self.version,
            "triggered_rules": df.get("triggered_rules", "")
        })
