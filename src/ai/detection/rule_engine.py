"""
Implements: 03_AI/00_AI_ARCHITECTURE.md (Rule Engine)
"""
import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Deterministic rule-based security heuristics evaluator.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.velocity_threshold = config.get("velocity_threshold", 5) # seconds
        self.failure_threshold = config.get("failure_threshold", 5)
    
    def evaluate(self, features: pd.DataFrame) -> pd.DataFrame:
        logger.info("Evaluating deterministic rules...")
        
        # Evaluate Rule: Excessive Failed Logins
        excessive_failures = features["rolling_failures_24h"] >= self.failure_threshold
        
        # Evaluate Rule: Login Velocity Threshold
        velocity_anomaly = features["time_since_last_login"] < self.velocity_threshold
        
        # Evaluate Rule: Off-hours Authentication
        off_hours = features["is_working_hour"] == 0
        
        # Generate base rule score
        rule_score = (excessive_failures.astype(int) * 30 + 
                      velocity_anomaly.astype(int) * 20 + 
                      off_hours.astype(int) * 10)
                      
        rule_score = rule_score.clip(upper=100)
        
        triggered_rules = []
        for i in range(len(features)):
            rules = []
            if excessive_failures.iloc[i]: rules.append("ExcessiveFailures")
            if velocity_anomaly.iloc[i]: rules.append("VelocityAnomaly")
            if off_hours.iloc[i]: rules.append("OffHours")
            triggered_rules.append(",".join(rules) if rules else "None")
            
        return pd.DataFrame({
            "event_id": features["event_id"],
            "rule_score": rule_score,
            "triggered_rules": triggered_rules
        })
