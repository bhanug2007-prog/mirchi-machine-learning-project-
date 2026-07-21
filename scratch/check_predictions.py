import os
import sys
import pandas as pd
import numpy as np
import joblib
import json
from datetime import timedelta

# Add scripts folder to path
sys.path.insert(0, './scripts')
from train_models import load_data, build_features

MODELS_DIR = "./saved_models"

def check_forecast(variety="Teja S17", market="Guntur APMC"):
    safe_variety = variety.replace(" ", "_").replace("/", "_")
    model_path   = f"{MODELS_DIR}/best_model_{safe_variety}.pkl"
    meta_path    = f"{MODELS_DIR}/meta_{safe_variety}.json"
    cols_path    = f"{MODELS_DIR}/feature_cols_{safe_variety}.json"
    scaler_path  = f"{MODELS_DIR}/scaler_{safe_variety}.pkl"
    
    if not os.path.exists(model_path):
        print(f"No model found for {variety}")
        return
        
    model = joblib.load(model_path)
    with open(meta_path) as f:
        meta = json.load(f)
    with open(cols_path) as f:
        feat_cols = json.load(f)
        
    scaler = None
    if meta['needs_scale'] and os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        
    # Load recent data
    df_raw = load_data(variety, market)
    print(f"Loaded {len(df_raw)} rows for {variety}")
    
    df_feat = build_features(df_raw)
    print(f"Latest actual price: {df_raw['modal_price'].iloc[-1]} on {df_raw['arrival_date'].iloc[-1]}")
    
    # Let's run the forecast loop exactly as in backend
    predictions = []
    current_df  = df_raw.copy()

    for day in range(1, 8):
        df_feat = build_features(current_df)
        last = df_feat[feat_cols].iloc[-1].values.reshape(1, -1)
        if scaler:
            last = scaler.transform(last)
        pred = float(model.predict(last)[0])
        predictions.append(round(pred, 2))

        # Add this prediction as next row
        new_row = current_df.iloc[-1].copy()
        last_dt = pd.to_datetime(current_df['arrival_date'].max())
        new_row['arrival_date'] = (last_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        new_row['modal_price']  = pred
        current_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
        
    print(f"Forecast for next 7 days: {predictions}")

if __name__ == '__main__':
    for v in ["Teja S17", "Red New", "334 Sannam", "DD Deluxe", "Byadgi"]:
        print(f"\n--- Checking variety: {v} ---")
        check_forecast(v)
