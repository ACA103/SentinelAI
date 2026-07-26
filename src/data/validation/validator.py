"""
Implements: 02_Data/06_SYNTHETIC_DATA_GENERATION.md
"""
import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates synthetic datasets against interface contracts.
    Implements Stage 9 of the Data Generation Pipeline.
    """
    def validate_auth_logs(self, df: pd.DataFrame) -> bool:
        required_columns = [
            "event_id", "timestamp", "user_id", "device_id", 
            "session_id", "resource_id", "ip_address", "country", 
            "city", "latitude", "longitude", "authentication_method", 
            "authentication_result", "is_attack"
        ]
        
        missing_cols = [c for c in required_columns if c not in df.columns]
        if missing_cols:
            logger.error(f"Missing columns: {missing_cols}")
            return False
            
        required_no_nulls = [c for c in required_columns if c != "failure_reason"]
        if df[required_no_nulls].isnull().any().any():
            logger.error("Missing values in required columns.")
            return False
            
        if not df["ip_address"].str.match(r"^\d{1,3}(\.\d{1,3}){3}$").all():
            logger.error("Invalid IP addresses found.")
            return False
            
        if not df["timestamp"].is_monotonic_increasing:
            logger.error("Timestamps are not strictly chronological.")
            return False
            
        logger.info("Validation passed successfully.")
        return True

    def validate_all(self, datasets: Dict[str, pd.DataFrame]) -> bool:
        if "authentication_events" not in datasets:
            return False
        return self.validate_auth_logs(datasets["authentication_events"])

    def generate_validation_report(self, datasets: Dict[str, pd.DataFrame], features_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Generates a comprehensive pipeline validation report containing:
        - Generated artifacts
        - Schema validation results
        - Record counts
        - Feature counts
        - Data quality summary
        - Validation errors
        - Assumptions made
        """
        report = {
            "generated_artifacts": list(datasets.keys()),
            "schema_validation": {},
            "record_counts": {name: len(df) for name, df in datasets.items()},
            "feature_counts": len(features_df.columns) if features_df is not None else 0,
            "data_quality_summary": {},
            "validation_errors": [],
            "assumptions_made": [
                "Synthetic data simulates enterprise behavior and represents chronological order.",
                "Nulls in 'failure_reason' are structurally valid for successful logins.",
                "Feature generation correctly maps historical aggregates for profiling."
            ]
        }
        
        for name, df in datasets.items():
            if name == "authentication_events":
                is_valid = self.validate_auth_logs(df)
                report["schema_validation"][name] = "Passed" if is_valid else "Failed"
                if not is_valid:
                    report["validation_errors"].append("authentication_events failed schema validation.")
            else:
                report["schema_validation"][name] = "Not Evaluated (No strict schema enforced)"
                
            report["data_quality_summary"][name] = {
                "missing_values": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum())
            }
            
        if features_df is not None:
            report["generated_artifacts"].append("engineered_features")
            report["record_counts"]["engineered_features"] = len(features_df)
            
        return report
