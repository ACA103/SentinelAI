import logging
import json
import pandas as pd
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RuleExplanationEngine:
    """Module 2: Rule Explanation Engine"""
    def explain(self, triggered_rules: str, event_data: dict) -> List[dict]:
        if not triggered_rules or triggered_rules == "None" or pd.isna(triggered_rules):
            return []
            
        explanations = []
        rules = triggered_rules.split(",")
        for rule in rules:
            if rule == "ImpossibleTravel":
                explanations.append({
                    "Rule Name": "Impossible Travel",
                    "Rule Description": "Login originated from geographically distant location",
                    "Evidence": f"Country: {event_data.get('country', 'Unknown')}",
                    "Severity": "High",
                    "Status": "Triggered"
                })
            elif rule == "VelocityAnomaly":
                explanations.append({
                    "Rule Name": "Velocity Anomaly",
                    "Rule Description": "Abnormal volume of authentication requests in short window",
                    "Evidence": f"Time since last: {event_data.get('time_since_last_login', 'Unknown')}s",
                    "Severity": "Moderate",
                    "Status": "Triggered"
                })
            else:
                explanations.append({
                    "Rule Name": rule,
                    "Rule Description": f"Triggered standard rule {rule}",
                    "Evidence": "Detected during deterministic rule evaluation",
                    "Severity": "Elevated",
                    "Status": "Triggered"
                })
        return explanations

class BehaviorExplanationEngine:
    """Module 3: Behavior Explanation Engine"""
    def explain(self, behavior_score: float, event_data: dict) -> List[dict]:
        deviations = []
        if event_data.get("is_working_hour") == 0:
            deviations.append({
                "Expected": "Login within working hours (8AM-6PM)",
                "Observed": "Login outside normal working hours",
                "Deviation": "Temporal Anomaly",
                "Impact": "Increased Risk"
            })
        if event_data.get("is_weekend") == 1:
            deviations.append({
                "Expected": "Weekday authentication",
                "Observed": "Weekend authentication",
                "Deviation": "Temporal Anomaly",
                "Impact": "Increased Risk"
            })
        if behavior_score > 50:
            deviations.append({
                "Expected": "Normal profile execution",
                "Observed": "Significant divergence from learned profile",
                "Deviation": "Behavioral Shift",
                "Impact": "High Risk"
            })
        return deviations

class RiskExplanationEngine:
    """Module 4: Risk Explanation Engine"""
    def explain(self, risk_record: dict) -> dict:
        return {
            "Final Risk Score": float(risk_record.get("risk_score", 0.0)),
            "Rule Contribution": float(risk_record.get("rule_contribution", 0.0)),
            "Statistical Contribution": float(risk_record.get("stat_contribution", 0.0)),
            "ML Contribution": float(risk_record.get("ml_contribution", 0.0)),
            "Behavioral Contribution": float(risk_record.get("behavioral_contribution", 0.0)),
            "Device Trust Contribution": float(risk_record.get("device_contribution", 0.0)),
            "Reasoning": "Aggregated normalized risk driven by explicit sub-engines."
        }

class NaturalLanguageGenerator:
    """Module 5: Natural Language Explanation"""
    def generate(self, evidence_package: dict) -> dict:
        risk_level = evidence_package.get("Risk Level", "Unknown")
        attack_category = evidence_package.get("Attack Classification", "Unknown")
        deviations = evidence_package.get("Behavior Deviations", [])
        rules = evidence_package.get("Triggered Rules", [])
        conf = evidence_package.get("Confidence", 0.0)
        
        # 1. Executive Summary
        exec_summary = f"The authentication event was classified as {risk_level} Risk. "
        if deviations:
            reasons = [d['Observed'].lower() for d in deviations]
            exec_summary += f"This was primarily because {', '.join(reasons)}. "
        if rules:
            r_names = [r['Rule Name'] for r in rules]
            exec_summary += f"Additionally, the following rules triggered: {', '.join(r_names)}. "
            
        if attack_category and attack_category != "Normal Authentication":
            exec_summary += f"The AI classifier predicted {attack_category}."
        else:
            exec_summary += "The activity was categorized as Normal Authentication."
            
        # 2. Technical Analysis
        features = evidence_package.get("Feature Contributions", [])
        feat_str = ", ".join([f"{f['feature']} ({f['contribution']:.2f})" for f in features]) if features else "None"
        stat_score = evidence_package.get("Risk Breakdown", {}).get("Statistical Contribution", 0.0)
        model_version = evidence_package.get("Audit Metadata", {}).get("Classification_Model_Version", "Unknown")
        feature_values = evidence_package.get("Feature Values", {})
        
        tech_analysis = (
            f"Model Version: {model_version}\n"
            f"Prediction Confidence: {conf*100:.2f}%\n"
            f"SHAP Contributions: {feat_str}\n"
            f"Triggered Rules: {', '.join([r['Rule Name'] for r in rules]) if rules else 'None'}\n"
            f"Statistical Deviation Score: {stat_score:.2f}\n"
            f"Input Feature Values: {feature_values}\n"
            f"Recommended Action: {evidence_package.get('Recommended Action', 'None')}"
        )
        
        return {
            "Executive_Summary": exec_summary,
            "Technical_Analysis": tech_analysis
        }
