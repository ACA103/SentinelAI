import pandas as pd
import json
import logging
import streamlit as st
from pathlib import Path

logger = logging.getLogger(__name__)

# Define absolute paths based on project structure
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXPLANATIONS_PATH = PROJECT_ROOT / "data" / "predictions" / "explanations.parquet"
RAW_LOGS_PATH = PROJECT_ROOT / "data" / "raw" / "auth_logs.parquet"

@st.cache_data(ttl=5)
def load_soc_telemetry(file_path: str = str(EXPLANATIONS_PATH)) -> pd.DataFrame:
    """
    Loads Parquet data and transforms JSON schema for Streamlit visualization.
    Implements separation of concerns (UI vs Data Layer).
    """
    try:
        exps = pd.read_parquet(file_path)
        
        # Transform logic extracted from app.py
        risk_levels = []
        attack_cats = []
        exec_summaries = []
        
        risk_scores = []
        for _, row in exps.iterrows():
            try:
                rb = json.loads(row["Risk_Breakdown"])
                score = rb.get("Final Risk Score", 0)
                risk_scores.append(round(score, 2))
                rl = "Critical" if score > 30 else "High" if score > 25 else "Moderate" if score > 15 else "Low"
                risk_levels.append(rl)
            except json.JSONDecodeError:
                risk_levels.append("Unknown")
                risk_scores.append(0.0)
            
            try:
                exp_dict = json.loads(row["Explanation"])
                exec_sum = exp_dict.get("Executive_Summary", "")
                exec_summaries.append(exec_sum)
                if "predicted" in exec_sum:
                    cat = exec_sum.split("predicted ")[-1].replace(".", "")
                else:
                    cat = "Normal Authentication"
                attack_cats.append(cat)
            except json.JSONDecodeError:
                attack_cats.append("Unknown")
                exec_summaries.append("")
        
        exps["Risk Level"] = risk_levels
        exps["Risk Score"] = risk_scores
        exps["Attack Classification"] = attack_cats
        exps["Executive Summary"] = exec_summaries
        
        # Merge rich analyst metadata from raw logs
        try:
            raw_logs = pd.read_parquet(RAW_LOGS_PATH)
            # We only need specific columns
            if not raw_logs.empty:
                meta_df = raw_logs[["event_id", "timestamp", "user_id", "device_id", "country", "ip_address", "authentication_method"]]
                exps = pd.merge(exps, meta_df, on="event_id", how="left")
                # If left merge causes NaNs because event_id didn't match
                exps["user_id"] = exps["user_id"].fillna("Unknown")
                exps["device_id"] = exps["device_id"].fillna("Unknown")
                exps["country"] = exps["country"].fillna("Unknown")
                exps["ip_address"] = exps["ip_address"].fillna("Unknown")
                exps["authentication_method"] = exps["authentication_method"].fillna("Unknown")
        except Exception as e:
            logger.error(f"Failed to merge raw logs: {e}")
            # If raw logs missing, provide graceful degradation
            exps["timestamp"] = ""
            exps["user_id"] = "Unknown"
            exps["device_id"] = "Unknown" 
            exps["country"] = "Unknown"
            exps["ip_address"] = "Unknown"
            exps["authentication_method"] = "Unknown"

        return exps
    except FileNotFoundError:
        logger.warning(f"Data file not found: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading data layer: {e}")
        return pd.DataFrame()
