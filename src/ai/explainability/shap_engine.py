import shap
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

_GLOBAL_SHAP_EXPLAINER = None

class SHAPEngine:
    """
    Module 1: SHAP Explainability Engine
    Computes SHAP values and feature importance for XGBoost Attack Classification.
    """
    def __init__(self, model):
        self.model = model
        self.explainer = None
        
    def fit(self, background_data: pd.DataFrame):
        global _GLOBAL_SHAP_EXPLAINER
        if _GLOBAL_SHAP_EXPLAINER is not None:
            logger.info("Using globally cached SHAP TreeExplainer.")
            self.explainer = _GLOBAL_SHAP_EXPLAINER
            return
            
        logger.info("Initializing SHAP TreeExplainer...")
        try:
            self.explainer = shap.TreeExplainer(self.model)
            _GLOBAL_SHAP_EXPLAINER = self.explainer
        except Exception as e:
            logger.error(f"Failed to initialize TreeExplainer: {e}")
            self.explainer = None
            
    def explain(self, X: pd.DataFrame, predicted_classes: list = None) -> dict:
        """
        Generates local explanations for every prediction.
        Returns a dictionary mapping index/event_id to top contributing features.
        """
        if self.explainer is None:
            self.fit(X)
            
        if self.explainer is None:
            logger.warning("SHAP Explainer unavailable, returning dummy explanations.")
            return {i: [("unknown", 0.0)] for i in range(len(X))}
            
        logger.info(f"Computing SHAP values for {len(X)} records...")
        
        try:
            shap_values = self.explainer.shap_values(X)
            
            explanations = {}
            for i in range(len(X)):
                event_id = X.iloc[i].name if X.index.name == 'event_id' else i
                
                # Multi-class SHAP returns list of arrays
                if isinstance(shap_values, list):
                    # Default to class 1 if predicted_classes not provided
                    pred_class = int(predicted_classes[i]) if predicted_classes else 1
                    if pred_class >= len(shap_values): pred_class = 0
                    vals = shap_values[pred_class][i]
                elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
                    pred_class = int(predicted_classes[i]) if predicted_classes else 1
                    if pred_class >= shap_values.shape[2]: pred_class = 0
                    vals = shap_values[i, :, pred_class]
                else:
                    vals = shap_values[i]
                    
                feature_contributions = dict(zip(X.columns, vals))
                sorted_features = sorted(feature_contributions.items(), key=lambda item: abs(item[1]), reverse=True)
                
                # Format into string mapping for easy reporting
                top_features = [{"feature": k, "contribution": float(v)} for k, v in sorted_features[:3]]
                explanations[event_id] = top_features
                
            return explanations
        except Exception as e:
            logger.error(f"SHAP explanation generation failed: {e}")
            return {i: [{"feature": "error", "contribution": 0.0}] for i in range(len(X))}
