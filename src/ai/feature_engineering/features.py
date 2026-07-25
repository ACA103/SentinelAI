"""
Implements: 02_Data/06_SYNTHETIC_DATA_GENERATION.md
Implements: 01_Project/04_INTERFACE_CONTRACTS.md
"""
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Transforms raw authentication telemetry into engineered ML feature vectors.
    """
    def process(self, input_path: str, output_path: str) -> pd.DataFrame:
        logger.info(f"Loading raw logs from {input_path}")
        df = pd.read_parquet(input_path)
        
        # Temporal Features
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_working_hour'] = ((df['hour_of_day'] >= 8) & (df['hour_of_day'] <= 18)).astype(int)
        
        # Behavior Features
        df['is_failure'] = (df['authentication_result'] == 'Failure').astype(int)
        
        # Geographic Features
        df['country_encoded'] = df['country'].astype('category').cat.codes
        
        # Device Features
        df['is_mfa'] = (df['authentication_method'] == 'MFA').astype(int)
        
        # Velocity / Historical Features
        df = df.sort_values(['user_id', 'timestamp'])
        df['time_since_last_login'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds().fillna(0)
        df['rolling_failures_24h'] = df.groupby('user_id')['is_failure'].transform(
            lambda x: x.rolling(10, min_periods=1).sum()
        )
        
        # Sort back to original chronological event ID order
        df = df.sort_values('event_id').reset_index(drop=True)
        
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_path, index=False)
        logger.info(f"Persisted feature vectors to {output_path}")
        return df
