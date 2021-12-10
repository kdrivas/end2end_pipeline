"""
    This file contains functions for model training and validation
"""
import os
import joblib
import json
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.feature_selection import SelectKBest, mutual_info_regression

from dags.pipelines.food_model.constants import TARGET_COL, PARAM_GRID

def hypertune_model(data_path: str, artifact_path: str) -> None:
    """
        This function will train the model using the preprocessed data (train and test sets)
        Once the model is trained, the metrics and the serialized model is stored in the artifact_path
    """
    train = pd.read_csv(os.path.join(data_path, 'preprocessed/train.csv'))

    pipe =  Pipeline([
        # Moving the standardScaler to the data processing pipeline causes problems of reproducibility
        ('scale', StandardScaler()),
        ('selector', SelectKBest(mutual_info_regression)),
        ('poly', PolynomialFeatures()),
        ('model', Ridge()),
    ])

    X_train, y_train = train.drop(TARGET_COL, axis=1), train[TARGET_COL]

    grid = GridSearchCV(
        estimator=pipe,
        param_grid=PARAM_GRID,
        cv = 3,
        scoring='r2'
    )
    grid.fit(X_train, y_train)
    best_params = grid.best_params_

    print('Best params:', best_params)
    with open(os.path.join(artifact_path, 'best_params.json'), 'w') as f:
        json.dump(best_params, f, indent=4)

def training_model(data_path: str, artifact_path: str) -> None:
    """
        This function will train the model using the preprocessed data (train and test sets)
        Once the model is trained, the metrics and the serialized model is stored in the artifact_path
    """
    train = pd.read_csv(os.path.join(data_path, 'preprocessed/train.csv'))
    test = pd.read_csv(os.path.join(data_path, 'preprocessed/test.csv'))

    with open(os.path.join(artifact_path, 'best_params.json')) as f:
        params = json.load(f)

    # Prediction pipeline
    # I'd prefer to keep just the model
    pipe =  Pipeline([
        # Moving the standardScaler to the data processing pipeline causes problems of reproducibility
        ('scale', StandardScaler()),
        ('selector', SelectKBest(mutual_info_regression, k=params['selector__k'])),
        ('poly', PolynomialFeatures(degree=params['poly__degree'])),
        ('model', Ridge(alpha=params['model__alpha'])),
    ])

    X_train, y_train = train.drop(TARGET_COL, axis=1), train[TARGET_COL]
    X_test, y_test = test.drop(TARGET_COL, axis=1), test[TARGET_COL]

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    rmse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print('RMSE:', rmse)
    print('r2:', r2)
    
    metrics = { 
        'RMSE': rmse,
        'r2': r2,
    }
    with open(os.path.join(artifact_path, 'model_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)

    joblib.dump(pipe, os.path.join(artifact_path, 'model_staging.pkl'))
    

def validate_promote_model(artifact_path: str) -> None:
    """
        Implements a set of validation for the model to promote it 
    """
    with open(os.path.join(artifact_path, 'model_metrics.json')) as json_file:
        metrics = json.load(json_file)

    model = joblib.load(os.path.join(artifact_path, 'model_staging.pkl'))

    # Dummy validation for RMSE and R2
    assert metrics['RMSE'] > 0 and metrics['r2'] > 0

    # TO-DO: Validate the last model perform better than the previous model
    print("Everythin Ok :D")

    joblib.dump(model, os.path.join(artifact_path, 'model_prod.pkl'))

def batch_prediction_model(artifact_path: str, data_path: str) -> None:
    """
        Predict batch data
    """

    # Read historic features from our feature store
    features = pd.read_csv(os.path.join(data_path, 'feature_store', 'super_efficient_feature_store.csv'))

    model = joblib.load(os.path.join(artifact_path, 'model_prod.pkl'))

    pred = model.predict(features.drop('Periodo', axis=1))
    features['preds'] = pred

    features[['Periodo', 'preds']].to_csv(os.path.join(data_path, 'batch_predictions', 'predictions.csv'), index=False)

