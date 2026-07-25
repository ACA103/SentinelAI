"""
Implements: 01_Project/04_INTERFACE_CONTRACTS.md
Implements: 05_Implementation/00_IMPLEMENTATION_GUIDE.md
"""
import pandas as pd
import pickle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BehaviorProfiler:
    """
    Generates normal behavior baselines for users and devices based on historical features.
    """
    def generate_profiles(self, input_path: str, user_out: str, device_out: str):
        logger.info("Generating behavior profiles...")
        df = pd.read_parquet(input_path)
        
        # Population Baseline for Cold Start
        population_baseline = {
            'typical_login_hour': df['hour_of_day'].mode().iloc[0] if not df['hour_of_day'].mode().empty else 9,
            'frequent_locations': df['country'].value_counts().head(5).index.tolist(),
            'success_rate': 1.0 - df['is_failure'].mean(),
            'average_velocity': df['time_since_last_login'].mean(),
            'confidence': 'Low',
            'note': 'No historical profile exists for this entity. Risk calculated using population baseline.'
        }
        
        # User Profiles with Concept Drift Support (Exponential Decay placeholder)
        user_profiles = {}
        for user_id, group in df.groupby('user_id'):
            # Decay factor applies more weight to recent events
            recent_group = group.tail(100) # Sliding window for concept drift
            user_profiles[user_id] = {
                'typical_login_hour': recent_group['hour_of_day'].mode().iloc[0] if not recent_group['hour_of_day'].mode().empty else population_baseline['typical_login_hour'],
                'frequent_locations': recent_group['country'].value_counts().head(3).index.tolist(),
                'trusted_devices': recent_group['device_id'].value_counts().head(3).index.tolist(),
                'success_rate': 1.0 - recent_group['is_failure'].mean(),
                'average_velocity': recent_group['time_since_last_login'].mean(),
                'confidence': 'High' if len(recent_group) > 20 else 'Medium',
                'last_updated': pd.Timestamp.now().isoformat()
            }
            
        # Add a default fallback profile for unseen users (Cold Start)
        user_profiles['DEFAULT'] = population_baseline
            
        # Device Profiles
        device_profiles = {}
        for device_id, group in df.groupby('device_id'):
            recent_group = group.tail(100)
            device_profiles[device_id] = {
                'primary_user': recent_group['user_id'].mode().iloc[0] if not recent_group['user_id'].mode().empty else -1,
                'total_events': len(group),
                'confidence': 'High' if len(recent_group) > 20 else 'Medium',
                'last_updated': pd.Timestamp.now().isoformat()
            }
        
        # Add default device profile
        device_profiles['DEFAULT'] = {
            'primary_user': -1,
            'total_events': 0,
            'confidence': 'Low',
            'note': 'No historical profile exists for this device. Risk calculated using device category baseline.'
        }
            
        Path(user_out).parent.mkdir(parents=True, exist_ok=True)
        
        with open(user_out, 'wb') as f:
            pickle.dump(user_profiles, f)
            
        with open(device_out, 'wb') as f:
            pickle.dump(device_profiles, f)
            
        logger.info(f"Persisted {len(user_profiles)} user profiles and {len(device_profiles)} device profiles.")
        return user_profiles, device_profiles
