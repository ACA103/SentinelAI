# Project Structure

```
SentinelAI/
├── src/                 # Core Source Code
│   ├── ai/              # Intelligence (Detection, Risk, Classification, XAI)
│   ├── data/            # Data Generation and Loaders
│   ├── runtime/         # Orchestration Pipelines
│   └── ui/              # Streamlit Dashboard components
├── docs/                # Documentation
├── data/                # Local Parquet Storage
│   ├── raw/
│   ├── processed/
│   └── predictions/
├── models/              # Serialized XGBoost & Isolation Forest Pickles
├── artifacts/           # Serialized User & Device Behavior Profiles
└── app.py               # Main Entrypoint
```
