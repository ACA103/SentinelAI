"""
Implements: 03_AI/00_AI_ARCHITECTURE.md (Behavioral Deviation)
"""
import pandas as pd
import pickle
import logging

logger = logging.getLogger(__name__)

class StatisticalEngine:
    """
    Computes statistical deviations against historical baselines for users and devices.
    """
    def __init__(self, user_profiles_path: str, device_profiles_path: str):
        logger.info(f"Loading user profiles from {user_profiles_path}")
        with open(user_profiles_path, "rb") as f:
            self.user_profiles = pickle.load(f)
            
        logger.info(f"Loading device profiles from {device_profiles_path}")
        with open(device_profiles_path, "rb") as f:
            self.device_profiles = pickle.load(f)
            
    def evaluate(self, features: pd.DataFrame) -> pd.DataFrame:
        logger.info("Evaluating statistical deviations...")
        
        stat_scores = []
        metrics_list = []
        
        for _, row in features.iterrows():
            user_id = row["user_id"]
            device_id = row["device_id"]
            
            score = 0
            metrics = []
            
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                
                # Login hour deviation
                hour = row["hour_of_day"]
                typical_hour = profile.get("typical_login_hour", 9)
                hour_diff = min(abs(hour - typical_hour), 24 - abs(hour - typical_hour))
                if hour_diff > 4:
                    score += 20
                    metrics.append("HighHourDeviation")
                    
                # Success rate deviation
                if row["is_failure"] == 1 and profile.get("success_rate", 1.0) > 0.95:
                    score += 15
                    metrics.append("AnomalousFailure")
            
            if device_id in self.device_profiles:
                device_profile = self.device_profiles[device_id]
                if device_profile.get("primary_user", -1) != user_id:
                    score += 30
                    metrics.append("DeviceMismatch")
                    
            stat_scores.append(min(score, 100))
            metrics_list.append(",".join(metrics) if metrics else "None")
            
        return pd.DataFrame({
            "event_id": features["event_id"],
            "stat_score": stat_scores,
            "stat_metrics": metrics_list
        })
