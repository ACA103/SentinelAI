"""
Implements: 03_AI/00_AI_ARCHITECTURE.md (Detection Result Aggregation)
"""
import pandas as pd
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class DetectionAggregator:
    """
    Combines rule-based, statistical, and ML anomaly signals into a unified detection assessment.
    """
    def aggregate(self, rules_df: pd.DataFrame, stat_df: pd.DataFrame, if_df: pd.DataFrame,
                  model_version: str = "1.0", rule_engine_version: str = "1.0", feature_schema_version: str = "1.0") -> pd.DataFrame:
        
        start_time = time.time()
        logger.info("Aggregating hybrid detection results...")
        
        df = rules_df.merge(stat_df, on="event_id")
        df = df.merge(if_df, on="event_id")
        
        df["detection_timestamp"] = datetime.now().isoformat()
        
        # Calculate processing duration
        duration_sec = time.time() - start_time
        
        # Add traceability metadata
        df["model_version"] = model_version
        df["rule_engine_version"] = rule_engine_version
        df["feature_schema_version"] = feature_schema_version
        df["processing_duration_sec"] = duration_sec
        
        logger.info(f"Aggregation complete. Output format contains {len(df.columns)} columns.")
        return df
