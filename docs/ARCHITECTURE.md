# SentinelAI Architecture

## Overview
SentinelAI is a multi-layered, hybrid AI cybersecurity platform designed for Enterprise SOCs. 

## Core Layers
1. **Presentation Layer (Streamlit)**: Interactive dashboard for analysts.
2. **Orchestration Layer**: Python-based pipeline runner managing execution phases.
3. **Machine Learning Layer**:
   - *Unsupervised*: Isolation Forest for spatial anomaly detection.
   - *Deterministic*: Rule Engine for known enterprise signatures.
   - *Supervised*: XGBoost for multi-class threat classification.
   - *Explainability*: SHAP values for AI transparency.
4. **Data Layer**: High-performance Parquet storage (PyArrow) for telemetry.
