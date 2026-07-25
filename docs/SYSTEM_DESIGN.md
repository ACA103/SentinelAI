# System Design

## Modularity
SentinelAI is strictly modular. Each phase operates independently, passing immutable `.parquet` state files.

### Components
* **Data Generator**: Bootstraps realistic Active Directory and Authentication logs.
* **Feature Engineer**: Computes velocity, behavioral, and spatial features.
* **Risk Fusion**: Aggregates disparate model outputs into a unified 0-100 Risk Score.
* **XGBoost Classifier**: Translates risk scores into actionable Threat Contexts.
* **Streamlit UI**: Renders real-time investigations using caching and session state.
