import pytest
import pandas as pd
from src.ai.detection.aggregator import DetectionAggregator

def test_aggregator():
    rules_df = pd.DataFrame({"event_id": [1, 2], "rule_score": [10, 20]})
    stat_df = pd.DataFrame({"event_id": [1, 2], "stat_score": [15, 25]})
    if_df = pd.DataFrame({"event_id": [1, 2], "if_score": [80, 90], "if_prediction": [1, 1]})
    
    aggregator = DetectionAggregator()
    result = aggregator.aggregate(rules_df, stat_df, if_df)
    
    assert len(result) == 2
    assert "detection_timestamp" in result.columns
    assert result.loc[0, "rule_score"] == 10
    assert result.loc[1, "stat_score"] == 25
    assert result.loc[0, "if_prediction"] == 1
