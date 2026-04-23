"""
Smart Energy Consumption Optimizer — ML Model Training
Trains a Random Forest Regressor to predict daily energy consumption.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json


def train_model(data_path=None, model_path=None):
    """
    Train a Random Forest model on the energy dataset.
    
    Returns:
        dict: Training metrics (MAE, RMSE, R²)
    """
    # --- Resolve paths ---
    base_dir = os.path.dirname(__file__)
    if data_path is None:
        data_path = os.path.join(base_dir, '..', 'data', 'energy_data.csv')
    if model_path is None:
        model_path = os.path.join(base_dir, 'energy_model.pkl')
    
    # --- Load data ---
    print("[1/4] Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df)} samples with {len(df.columns)} features")
    
    # --- Feature engineering ---
    feature_cols = [
        'rooms', 'occupants', 'num_appliances', 
        'total_usage_hours', 'avg_temperature',
        'has_ac', 'has_heavy_appliances'
    ]
    target_col = 'energy_kwh'
    
    X = df[feature_cols].values
    y = df[target_col].values
    
    # --- Train/test split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
    
    # --- Scale features ---
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # --- Train Random Forest ---
    print("[2/4] Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # --- Evaluate ---
    y_pred = model.predict(X_test_scaled)
    
    metrics = {
        'mae': round(mean_absolute_error(y_test, y_pred), 4),
        'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        'r2': round(r2_score(y_test, y_pred), 4)
    }
    
    print(f"\n[3/4] Model Performance:")
    print(f"   MAE:  {metrics['mae']} kWh")
    print(f"   RMSE: {metrics['rmse']} kWh")
    print(f"   R2:   {metrics['r2']}")
    
    # --- Feature importance ---
    importances = model.feature_importances_
    feature_importance = dict(zip(feature_cols, [round(float(x), 4) for x in importances]))
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n[3/4] Feature Importance:")
    for feat, imp in sorted_features:
        bar = '#' * int(imp * 50)
        print(f"   {feat:25s} {imp:.4f} {bar}")
    
    # --- Save model, scaler, and metadata ---
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_cols': feature_cols,
        'metrics': metrics,
        'feature_importance': feature_importance
    }
    
    joblib.dump(model_data, model_path)
    print(f"\n[4/4] Model saved to {model_path}")
    
    # Also save metrics as JSON for the frontend
    metrics_path = os.path.join(base_dir, 'model_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump({
            'metrics': metrics,
            'feature_importance': feature_importance
        }, f, indent=2)
    
    return metrics


if __name__ == '__main__':
    train_model()
