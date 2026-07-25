# Interface Reference

SentinelAI operates on internal Python interfaces rather than REST APIs.

## Core Classes
* `PipelineRunner`: `run_phase2()`, `run_phase3()`, `run_phase4()`, `run_phase5()`, `run_all()`
* `SyntheticDataGenerator`: `generate()` -> Returns Dict[str, pd.DataFrame]
* `XGBoostClassifier`: `predict(features)` -> Returns threat labels.
* `SHAPExplainer`: `explain(features, model)` -> Returns JSON strings of feature importance.
* `ConfigManager`: Manages immutable configuration states.
