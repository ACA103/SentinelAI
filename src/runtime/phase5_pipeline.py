import pandas as pd
import json
import logging
import time
from pathlib import Path

from src.ai.classification.xgboost_classifier import XGBoostClassifier
from src.ai.explainability.shap_engine import SHAPEngine
from src.ai.explainability.explainer import RuleExplanationEngine, BehaviorExplanationEngine, RiskExplanationEngine, NaturalLanguageGenerator
from src.ai.explainability.evidence import EvidencePackageGenerator

logger = logging.getLogger(__name__)

class Phase5Pipeline:
    """
    Phase 5 Orchestrator: Explainability (XAI), Evidence Generation & Audit Trail.
    """
    def __init__(self, config: dict, model_dir: str, output_dir: str):
        self.config = config
        self.model_dir = Path(model_dir)
        self.output_dir = Path(output_dir)
        
        # Initializing sub-engines
        self.rule_explainer = RuleExplanationEngine()
        self.behavior_explainer = BehaviorExplanationEngine()
        self.risk_explainer = RiskExplanationEngine()
        self.nl_generator = NaturalLanguageGenerator()
        self.evidence_gen = EvidencePackageGenerator(config)
        
        # Load classification model for SHAP
        self.classifier = XGBoostClassifier(str(model_dir), config)
        self.classifier.load()
        self.shap_engine = SHAPEngine(self.classifier.model) if self.classifier.model else None

    def execute(self, features_path: str, risk_scores_path: str) -> pd.DataFrame:
        logger.info("Starting Phase 5 Explainability Pipeline...")
        
        features_df = pd.read_parquet(features_path)
        risk_df = pd.read_parquet(risk_scores_path)
        
        # Sync indices using event_id
        df = pd.merge(risk_df, features_df, on="event_id", how="inner")
        
        # Extract predictions for SHAP
        # Note: mapping category back to label index if possible, else default 1
        predicted_classes = []
        for cat in df["attack_category"]:
            try:
                idx = self.classifier.labels.index(cat)
                predicted_classes.append(idx)
            except ValueError:
                predicted_classes.append(1)
        
        # 1. SHAP Feature Importance
        # Limit background data for performance in SHAP (just an assumption)
        X_shap = df[self.classifier.features_used] if self.classifier else pd.DataFrame()
        if self.shap_engine and not X_shap.empty:
            shap_explanations = self.shap_engine.explain(X_shap, predicted_classes)
        else:
            shap_explanations = {i: [] for i in range(len(df))}
            
        output_records = []
        
        for i, row in df.iterrows():
            event_id = row["event_id"]
            
            # 2. Rule Explanations
            triggered_rules = row.get("triggered_rules", "")
            rule_exp = self.rule_explainer.explain(triggered_rules, row.to_dict())
            
            # 3. Behavior Explanations
            behavior_score = row.get("behavioral_contribution", 0)
            behavior_exp = self.behavior_explainer.explain(behavior_score, row.to_dict())
            
            # 4. Risk Breakdown
            risk_exp = self.risk_explainer.explain(row.to_dict())
            
            # 5. Build Evidence Package First
            feature_values = row[self.classifier.features_used].to_dict() if self.classifier else {}
            
            package = {
                "Event Metadata": {"Event ID": event_id},
                "Triggered Rules": rule_exp,
                "Behavior Deviations": behavior_exp,
                "Feature Contributions": shap_explanations.get(i, []),
                "Feature Values": feature_values,
                "Risk Breakdown": risk_exp,
                "Attack Classification": row.get("attack_category", "Unknown"),
                "Risk Level": row.get("risk_level", "Unknown"),
                "Confidence": row.get("prediction_confidence", 0.0),
                "Recommended Action": self.evidence_gen.recommender.recommend(row.get("risk_level", "Unknown")),
                "Audit Metadata": self.evidence_gen.audit.generate_audit_metadata(
                    event_id,
                    row.get("detection_engine_version", "1.0"),
                    row.get("risk_engine_version", "1.0"),
                    row.get("classification_model_version", "1.0")
                )
            }
            
            # 6. Natural Language Generation
            nl_exp = self.nl_generator.generate(package)
            package["Explanation"] = nl_exp
            
            # Map back to flat schema per Output Contract
            output_records.append({
                "event_id": event_id,
                "Explanation": json.dumps(nl_exp),
                "SHAP_Values": json.dumps(package["Feature Contributions"]),
                "Triggered_Rules": json.dumps(package["Triggered Rules"]),
                "Risk_Breakdown": json.dumps(package["Risk Breakdown"]),
                "Recommended_Action": package["Recommended Action"],
                "Audit_Metadata": json.dumps(package["Audit Metadata"])
            })
            
        out_df = pd.DataFrame(output_records)
        
        # Persist Output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "explanations.parquet"
        out_df.to_parquet(out_path, index=False)
        
        logger.info(f"Phase 5 Complete. Explanations persisted to {out_path}")
        return out_df
