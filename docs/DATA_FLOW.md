# Data Flow

SentinelAI utilizes high-performance Parquet files to pass data between phases:

1. `data/raw/auth_logs.parquet`: Raw synthetic telemetry.
2. `data/processed/features.parquet`: Telemetry with engineered ML features.
3. `data/predictions/anomaly_scores.parquet`: Output from Unsupervised & Rule engines.
4. `data/predictions/risk_scores.parquet`: Output from XGBoost classification.
5. `data/predictions/explanations.parquet`: Final payload injected with SHAP XAI evidence.

**Execution History** is maintained in `data/execution_history.json` for dashboard comparison.
