import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Module 7: Recommended Response"""
    def __init__(self, config: dict):
        self.mapping = config.get("recommendations", {
            "Low": "Monitor",
            "Moderate": "Review activity",
            "Elevated": "Step-up Authentication",
            "High": "Require MFA, Notify SOC",
            "Critical": "Lock account, Block authentication, Escalate incident"
        })
        
    def recommend(self, risk_level: str) -> str:
        return self.mapping.get(risk_level, "Monitor")

class AuditTrail:
    """Module 8: Audit Trail"""
    def __init__(self, config: dict):
        self.version_info = {
            "Feature_Schema_Version": config.get("feature_schema_version", "1.0"),
            "SHAP_Version": "1.0",
            "Audit_Engine_Version": "1.0"
        }
        
    def generate_audit_metadata(self, event_id, detection_v, risk_v, class_v) -> dict:
        metadata = {
            "Event_ID": event_id,
            "Detection_Engine_Version": detection_v,
            "Risk_Engine_Version": risk_v,
            "Classification_Model_Version": class_v,
            "Processing_Timestamp": datetime.now().isoformat(),
            "Explanation_Timestamp": datetime.now().isoformat()
        }
        metadata.update(self.version_info)
        return metadata

class EvidencePackageGenerator:
    """Module 6: Evidence Package"""
    def __init__(self, config: dict):
        self.recommender = RecommendationEngine(config)
        self.audit = AuditTrail(config)
        
    def build_package(self, event_id: int, nl_explanation: str, shap_features: list, 
                      rule_exp: list, behavior_exp: list, risk_exp: dict, 
                      attack_category: str, risk_level: str,
                      detection_v: str, risk_v: str, class_v: str) -> dict:
        
        recommended_action = self.recommender.recommend(risk_level)
        audit_metadata = self.audit.generate_audit_metadata(event_id, detection_v, risk_v, class_v)
        
        # Structure the payload per requirements
        package = {
            "Event Metadata": {"Event ID": event_id},
            "Triggered Rules": rule_exp,
            "Behavior Deviations": behavior_exp,
            "Feature Contributions": shap_features,
            "Risk Breakdown": risk_exp,
            "Attack Classification": attack_category,
            "Recommended Action": recommended_action,
            "Explanation": nl_explanation,
            "Audit Metadata": audit_metadata
        }
        
        return package
