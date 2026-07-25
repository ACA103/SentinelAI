import pytest
import pandas as pd
import tempfile
import os
from src.ai.classification.xgboost_classifier import XGBoostClassifier

@pytest.fixture
def classifier_setup():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            "classification_labels": ["Normal", "Attack"],
            "classifier_features": ["f1", "f2"]
        }
        classifier = XGBoostClassifier(model_dir=temp_dir, config=config)
        yield classifier, temp_dir

def test_xgboost_train_and_predict(classifier_setup):
    classifier, model_dir = classifier_setup
    
    # Dummy data
    X_train = pd.DataFrame({
        "event_id": [1, 2, 3, 4],
        "f1": [0, 0, 1, 1],
        "f2": [0, 0, 1, 1]
    })
    y_train = pd.Series([0, 0, 1, 1])
    
    classifier.train(X_train, y_train)
    
    # Check persistence
    import glob
    model_files = glob.glob(os.path.join(model_dir, "xgboost_attack_classifier_*.json"))
    meta_files = glob.glob(os.path.join(model_dir, "classifier_metadata_*.json"))
    assert len(model_files) > 0
    assert len(meta_files) > 0
    
    # Predict
    X_test = pd.DataFrame({
        "event_id": [5],
        "f1": [1],
        "f2": [1]
    })
    
    result = classifier.predict(X_test)
    assert len(result) == 1
    assert "attack_category" in result.columns
    assert "prediction_confidence" in result.columns
    assert result.iloc[0]["attack_category"] == "Attack"

def test_xgboost_load_model(classifier_setup):
    classifier, model_dir = classifier_setup
    
    X_train = pd.DataFrame({
        "event_id": [1, 2], 
        "f1": [0, 1], 
        "f2": [0, 1]
    })
    y_train = pd.Series([0, 1])
    
    classifier.train(X_train, y_train)
    
    # Create new instance to test loading
    new_classifier = XGBoostClassifier(model_dir=model_dir, config=classifier.config)
    success = new_classifier.load()
    
    assert success is True
    assert new_classifier.model is not None
