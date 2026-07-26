"""
Implements: 01_Project/04_INTERFACE_CONTRACTS.md
Implements: 05_Implementation/00_IMPLEMENTATION_GUIDE.md
"""
import logging
import json
from pathlib import Path
import pandas as pd
from src.data.loaders.generator import SyntheticDataGenerator
from src.data.validation.validator import DataValidator
from src.ai.feature_engineering.features import FeatureEngineer
from src.ai.behavior.profiling import BehaviorProfiler
from src.ai.detection.rule_engine import RuleEngine
from src.ai.detection.statistical_engine import StatisticalEngine
from src.ai.detection.isolation_forest import IsolationForestEngine
from src.ai.detection.aggregator import DetectionAggregator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from src.runtime.phase4_pipeline import Phase4Pipeline
from src.runtime.phase5_pipeline import Phase5Pipeline
from src.utils.config import ConfigManager

class PipelineRunner:
    """
    Orchestrates the entire SentinelAI Pipeline.
    """
    def run_phase2(self, config_overrides=None):
        logger.info("Starting Phase 2 Pipeline execution...")
        
        # Stage 1-8: Synthetic Data Generation
        generator = SyntheticDataGenerator(config_overrides=config_overrides)
        datasets = generator.generate()
        df_raw = datasets["authentication_events"]
        
        # Stage 9: Data Validation
        logger.info("Stage 9: Validate")
        validator = DataValidator()
        if not validator.validate_all(datasets):
            logger.error("Pipeline aborted due to validation failure.")
            raise ValueError("Data validation failed.")
            
        # Stage 10: Export (as per INTERFACE CONTRACTS - auth_logs.parquet)
        logger.info("Stage 10: Export")
        out_path = Path("data/raw/auth_logs.parquet")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(out_path, index=False)
        
        # Also export raw tables as CSVs as per 02_Data/06_SYNTHETIC_DATA_GENERATION.md
        for name, df in datasets.items():
            csv_path = Path(f"data/raw/{name}.csv")
            df.to_csv(csv_path, index=False)
        
        # Export Metadata and Logs (as per SYNTHETIC_DATA_GENERATION.md)
        meta_path = Path("exports/generation_summary.json")
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        summary = {
            "num_events": len(df_raw),
            "num_attacks": int(df_raw["is_attack"].sum()),
            "status": "success"
        }
        with open(meta_path, "w") as f:
            json.dump(summary, f)
            
        logger.info(f"Exported auth_logs.parquet with {len(df_raw)} records.")
        
        # Phase 2: Feature Engineering
        engineer = FeatureEngineer()
        df_features = engineer.process(
            input_path="data/raw/auth_logs.parquet",
            output_path="data/processed/features.parquet"
        )
        
        # Phase 2: Behavior Profiling
        profiler = BehaviorProfiler()
        profiler.generate_profiles(
            input_path="data/processed/features.parquet",
            user_out="artifacts/user_profiles.pkl",
            device_out="artifacts/device_profiles.pkl"
        )
        
        logger.info("Phase 2 Pipeline completed successfully.")

    def run_phase3(self, config_overrides=None):
        logger.info("Starting Phase 3 Detection Core Pipeline execution...")
        
        features_path = "data/processed/features.parquet"
        user_profiles_path = "artifacts/user_profiles.pkl"
        device_profiles_path = "artifacts/device_profiles.pkl"
        
        features = pd.read_parquet(features_path)
        
        # 1. Rule Engine
        rule_engine = RuleEngine(config=config_overrides or {})
        rules_df = rule_engine.evaluate(features)
        
        # 2. Statistical Engine
        stat_engine = StatisticalEngine(user_profiles_path, device_profiles_path)
        stat_df = stat_engine.evaluate(features)
        
        # 3. Isolation Forest
        if_engine = IsolationForestEngine(model_dir="models/isolation_forest")
        if config_overrides and config_overrides.get("force_retrain"):
            if_engine.train(features)
        if_df = if_engine.predict(features)
        
        # 4. Aggregator
        aggregator = DetectionAggregator()
        aggregated_df = aggregator.aggregate(rules_df, stat_df, if_df)
        
        # 5. Persist Detection Results
        out_path = Path("data/predictions/anomaly_scores.parquet")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        aggregated_df.to_parquet(out_path, index=False)
        
        logger.info(f"Phase 3 Pipeline completed. Persisted {len(aggregated_df)} detection results.")

    def run_phase4(self, config_overrides=None):
        logger.info("Starting Phase 4 Pipeline...")
        config = ConfigManager()._config.copy()
        if config_overrides:
            config.update(config_overrides)
        pipeline = Phase4Pipeline(config, "models", "data/predictions")
        pipeline.execute("data/predictions/anomaly_scores.parquet", "data/processed/features.parquet")
        logger.info("Phase 4 Pipeline completed.")
        
    def run_phase5(self, config_overrides=None):
        logger.info("Starting Phase 5 Pipeline...")
        config = ConfigManager()._config.copy()
        if config_overrides:
            config.update(config_overrides)
        pipeline = Phase5Pipeline(config, "models", "data/predictions")
        pipeline.execute("data/processed/features.parquet", "data/predictions/risk_scores.parquet")
        logger.info("Phase 5 Pipeline completed.")
        
    def run_all(self, config_overrides=None):
        logger.info("--- Starting End-to-End Pipeline Execution ---")
        self.run_phase2(config_overrides)
        self.run_phase3(config_overrides)
        self.run_phase4(config_overrides)
        self.run_phase5(config_overrides)
        logger.info("--- End-to-End Pipeline Execution Complete ---")

if __name__ == "__main__":
    runner = PipelineRunner()
    runner.run_all()
