# AI Pipeline

The pipeline processes data sequentially to ensure maximum fidelity:

1. **Synthetic Data Generation**: Injects precise threat scenarios (e.g. Impossible Travel).
2. **Feature Engineering**: Extracts time-series and spatial characteristics.
3. **Behavior Profiling**: Builds continuous mathematical baselines for users/devices.
4. **Isolation Forest**: Identifies multi-dimensional spatial anomalies.
5. **Rule Engine**: Flags known enterprise signatures.
6. **Risk Fusion**: Normalizes inputs into an enterprise 0-100 risk score.
7. **XGBoost**: Supervised learning categorizes the specific threat context.
8. **SHAP (XAI)**: Generates interpretable feature importance evidence.
