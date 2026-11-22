"""
STEP 2: Train ALL 12 ML Models and Compare with Baseline
=========================================================
Run: python 02_train_models.py

Configures and trains 12 ML algorithms (linear, regularized, tree, ensemble,
boosting, and deep learning), compares 1-day model selection metrics against a
Last-Observed-Price persistence baseline, and saves the best model artifact.
"""

import pandas as pd
import numpy as np
import psycopg2
import joblib, os, json, warnings
from datetime import datetime

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor,
    ExtraTreesRegressor, AdaBoostRegressor
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.base import BaseEstimator, RegressorMixin

warnings.filterwarnings('ignore')

class PyTorchMLPRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, lr=0.01, epochs=150, batch_size=32, random_state=42):
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_state = random_state
        self.model = None

    def fit(self, X, y):
        # Set seeds for reproducibility
        if self.random_state is not None:
            torch.manual_seed(self.random_state)
            np.random.seed(self.random_state)
            
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        
        input_dim = X.shape[1]
        self.model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        criterion = nn.MSELoss()
        
        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        self.model.train()
        for epoch in range(self.epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
        return self

    def predict(self, X):
        if self.model is None:
            raise ValueError("Model is not fitted yet.")
        self.model.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32)
        with torch.no_grad():
            preds = self.model(X_tensor).squeeze(1).numpy()
        return preds

DB_URL = os.environ.get("DB_URL")

MODELS_DIR = "./saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────
# LOAD DATA FROM SUPABASE
# ─────────────────────────────────────────────────────
def load_data(variety="Red New", market="Guntur APMC"):
    conn = psycopg2.connect(DB_URL)
    df = pd.read_sql("""
        SELECT arrival_date, 
               AVG(modal_price) as modal_price,
               AVG(min_price) as min_price,
               AVG(max_price) as max_price,
               COALESCE(SUM(arrival_qty), 0) as arrival_qty
        FROM mirchi_prices
        WHERE market = %s
          AND variety = %s
          AND modal_price > 0
        GROUP BY arrival_date
        ORDER BY arrival_date ASC
    """, conn, params=(market, variety))
    df['variety'] = variety
    df['grade'] = 'Aggregated'
    conn.close()
    return df


# ─────────────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────────────
def build_features(df):
    df = df.copy()
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df = df.sort_values('arrival_date').reset_index(drop=True)

    price = df['modal_price']

    # Lag features — previous prices
    for lag in [1, 2, 3, 5, 7, 14]:
        df[f'lag_{lag}'] = price.shift(lag)

    # Rolling statistics
    for window in [3, 7, 14, 30]:
        df[f'rolling_mean_{window}']   = price.shift(1).rolling(window).mean()
        df[f'rolling_std_{window}']    = price.shift(1).rolling(window).std()
        df[f'rolling_max_{window}']    = price.shift(1).rolling(window).max()
        df[f'rolling_min_{window}']    = price.shift(1).rolling(window).min()

    # Price momentum
    df['price_change_1d']  = price.shift(1) - price.shift(2)
    df['price_change_3d']  = price.shift(1) - price.shift(4)
    df['price_change_7d']  = price.shift(1) - price.shift(8)
    df['pct_change_1d']    = price.pct_change(1).shift(1)

    # Arrival features
    if 'arrival_qty' in df.columns:
        df['arrival_qty'] = df['arrival_qty'].fillna(0)
        df['arrival_lag1']       = df['arrival_qty'].shift(1)
        df['arrival_rolling7']   = df['arrival_qty'].shift(1).rolling(7).mean()

    # Date features
    df['day_of_week']   = df['arrival_date'].dt.dayofweek
    df['month']         = df['arrival_date'].dt.month
    df['week_of_year']  = df['arrival_date'].dt.isocalendar().week.astype(int)
    df['day_of_year']   = df['arrival_date'].dt.dayofyear

    # Season encoding
    # Mirchi harvest season: Nov-Feb (prices usually lower due to supply)
    # Off-season: May-Oct (prices higher)
    df['is_harvest_season'] = df['month'].isin([11, 12, 1, 2]).astype(int)
    df['is_peak_demand']    = df['month'].isin([5, 6, 7, 8]).astype(int)

    # Cyclical encoding for month and day
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['dow_sin']   = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['dow_cos']   = np.cos(2 * np.pi * df['day_of_week'] / 7)

    # Drop rows with NaN from lag features
    df = df.dropna()
    return df


# ─────────────────────────────────────────────────────
# EVALUATION METRICS (1-step-ahead model selection)
# ─────────────────────────────────────────────────────
def evaluate(y_true, y_pred, model_name):
    # Guard against zero/missing actuals in percentage error calculation
    valid_mask = (y_true != 0) & (~np.isnan(y_true))
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true[valid_mask] - y_pred[valid_mask]) / y_true[valid_mask])) * 100
    return {
        'model':    model_name,
        'MAE':      float(round(mae, 2)),
        'RMSE':     float(round(rmse, 2)),
        'R2':       float(round(r2, 4)),
        'MAPE (%)': float(round(mape, 2)),
    }


# ─────────────────────────────────────────────────────
# TRAIN ALL 12 MODELS + EVALUATE BASELINE
# ─────────────────────────────────────────────────────
def train_all_models(variety="Red New", market="Guntur APMC"):
    print(f"\n🌶  Training models for: {variety} @ {market}")
    print("=" * 60)

    # Load and prepare data
    df_raw = load_data(variety, market)
    print(f"  Rows loaded: {len(df_raw)}")

    if len(df_raw) < 30:
        print(f"  ⚠️  Not enough data for {variety} — need at least 30 rows")
        return None, None

    df = build_features(df_raw)
    print(f"  Rows after feature engineering: {len(df)}")

    # Feature columns
    feature_cols = [c for c in df.columns if c not in [
        'arrival_date', 'modal_price', 'variety', 'grade',
        'min_price', 'max_price'
    ]]

    X = df[feature_cols].values
    y = df['modal_price'].values

    # Time-series split — last 20% for test (don't shuffle time-series!)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    print(f"  Train: {len(X_train)} rows | Test: {len(X_test)} rows")

    # Reference Persistence Baseline: y_hat = previous observed price (lag_1)
    baseline_preds = df['lag_1'].values[split:]
    baseline_metrics = evaluate(y_test, baseline_preds, "Last Observed Price (Baseline)")

    # Scale for models that need it
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # ─── ALL 12 TRAINED ALGORITHMS ─────────────────────
    models = {
        # Simple / regularized linear models
        "Linear Regression":    (LinearRegression(),            False),
        "Ridge Regression":     (Ridge(alpha=1.0),              False),
        "Lasso Regression":     (Lasso(alpha=100),              False),
        # Tree & instance-based models
        "Decision Tree":        (DecisionTreeRegressor(
                                    max_depth=8,
                                    random_state=42),            False),
        "KNN":                  (KNeighborsRegressor(n_neighbors=5), True),
        "SVR":                  (SVR(kernel='rbf', C=1000,
                                    epsilon=500),               True),
        # Ensemble models
        "Random Forest":        (RandomForestRegressor(
                                    n_estimators=200,
                                    max_depth=12,
                                    random_state=42),            False),
        "Extra Trees":          (ExtraTreesRegressor(
                                    n_estimators=200,
                                    random_state=42),            False),
        "Gradient Boosting":    (GradientBoostingRegressor(
                                    n_estimators=200,
                                    learning_rate=0.05,
                                    max_depth=5,
                                    random_state=42),            False),
        # Advanced boosting models
        "XGBoost":              (xgb.XGBRegressor(
                                    n_estimators=300,
                                    learning_rate=0.05,
                                    max_depth=6,
                                    subsample=0.8,
                                    colsample_bytree=0.8,
                                    random_state=42,
                                    verbosity=0),               False),
        "LightGBM":             (lgb.LGBMRegressor(
                                    n_estimators=300,
                                    learning_rate=0.05,
                                    max_depth=6,
                                    num_leaves=31,
                                    random_state=42,
                                    verbose=-1),                False),
        # Deep learning MLP
        "PyTorch MLP":          (PyTorchMLPRegressor(epochs=150, lr=0.01), True),
    }

    results = []
    trained_models = {}

    for name, (model, needs_scale) in models.items():
        try:
            Xtr = X_train_sc if needs_scale else X_train
            Xte = X_test_sc  if needs_scale else X_test

            model.fit(Xtr, y_train)
            preds = model.predict(Xte)
            metrics = evaluate(y_test, preds, name)
            results.append(metrics)
            trained_models[name] = (model, scaler if needs_scale else None)
            print(f"  ✅ {name:<22} MAE: ₹{metrics['MAE']:>7,.0f} | R²: {metrics['R2']:.4f} | MAPE: {metrics['MAPE (%)']:.1f}%")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    # ─── COMPARISON TABLE ────────────────────────────
    results_df = pd.DataFrame(results).sort_values('MAE')
    print(f"\n{'='*75}")
    print(f"📊 MODEL COMPARISON — {variety} @ {market} (1-Day Model Selection)")
    print(f"{'='*75}")
    print(f"{'Rank':<5} {'Model':<28} {'MAE (₹/qtl)':>12} {'RMSE (₹/qtl)':>12} {'R²':>8} {'MAPE%':>8}")
    print(f"{'-'*75}")
    print(f"{'--':<5} {baseline_metrics['model']:<28} {baseline_metrics['MAE']:>12,.0f} {baseline_metrics['RMSE']:>12,.0f} {baseline_metrics['R2']:>8.4f} {baseline_metrics['MAPE (%)']:>8.1f} [REF]")
    print(f"{'-'*75}")
    for i, row in enumerate(results_df.itertuples(), 1):
        flag = " ⭐ BEST TRAINED" if i == 1 else ""
        print(f"{i:<5} {row.model:<28} {row.MAE:>12,.0f} {row.RMSE:>12,.0f} {row.R2:>8.4f} {getattr(row,'MAPE (%)',0):>8.1f}{flag}")
    print(f"{'='*75}")

    # ─── SAVE BEST MODEL ─────────────────────────────
    best_name = results_df.iloc[0]['model']
    best_model, best_scaler = trained_models[best_name]

    safe_variety = variety.replace(" ", "_").replace("/", "_")
    model_path  = f"{MODELS_DIR}/best_model_{safe_variety}.pkl"
    scaler_path = f"{MODELS_DIR}/scaler_{safe_variety}.pkl"
    meta_path   = f"{MODELS_DIR}/meta_{safe_variety}.json"
    cols_path   = f"{MODELS_DIR}/feature_cols_{safe_variety}.json"

    joblib.dump(best_model, model_path)
    if best_scaler:
        joblib.dump(best_scaler, scaler_path)

    meta = {
        'variety':            variety,
        'market':             market,
        'best_model':         best_name,
        'mae':                float(results_df.iloc[0]['MAE']),
        'rmse':               float(results_df.iloc[0]['RMSE']),
        'r2':                 float(results_df.iloc[0]['R2']),
        'mape':               float(results_df.iloc[0]['MAPE (%)']),
        'needs_scale':        best_scaler is not None,
        'trained_at':         datetime.now().isoformat(),
        'train_rows':         len(X_train),
        'test_rows':          len(X_test),
        'models_configured':  len(models),
        'models_evaluated':   len(results),
        'baseline_metrics':   baseline_metrics,
        'all_results':        results_df.to_dict('records'),
    }
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    with open(cols_path, 'w') as f:
        json.dump(feature_cols, f)

    print(f"\n✅ Best trained model saved: {best_name}")
    print(f"   MAE = ₹{meta['mae']:,.0f}/quintal  |  R² = {meta['r2']:.4f}")
    print(f"   Reference Baseline MAE = ₹{baseline_metrics['MAE']:,.0f}/quintal")
    print(f"   File: {model_path}")

    # ─── SAVE RESULTS TO SUPABASE ────────────────────
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("DELETE FROM ml_model_results WHERE variety = %s", (variety,))
        for r in results:
            cur.execute("""
                INSERT INTO ml_model_results
                    (model_name, variety, mae, rmse, r2, mape, is_best)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                r['model'], variety,
                r['MAE'], r['RMSE'], r['R2'], r['MAPE (%)'],
                r['model'] == best_name
            ))
        conn.commit()
        cur.close()
        conn.close()
        print("   Results saved to Supabase ✅")
    except Exception as e:
        print(f"   Could not save to DB: {e}")

    return best_model, feature_cols


# ─────────────────────────────────────────────────────
# PREDICT NEXT 7 DAYS
# ─────────────────────────────────────────────────────
def predict_next_7_days(variety="Red New", market="Guntur APMC"):
    safe_variety = variety.replace(" ", "_").replace("/", "_")
    model_path   = f"{MODELS_DIR}/best_model_{safe_variety}.pkl"
    meta_path    = f"{MODELS_DIR}/meta_{safe_variety}.json"
    cols_path    = f"{MODELS_DIR}/feature_cols_{safe_variety}.json"

    if not os.path.exists(model_path):
        print(f"⚠️  No model found for {variety}. Run training first.")
        return []

    model = joblib.load(model_path)
    with open(meta_path) as f:
        meta = json.load(f)
    with open(cols_path) as f:
        feature_cols = json.load(f)

    scaler = None
    scaler_path = f"{MODELS_DIR}/scaler_{safe_variety}.pkl"
    if meta['needs_scale'] and os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)

    # Load recent data
    df_raw = load_data(variety, market)
    df     = build_features(df_raw)

    if len(df) == 0:
        return []

    # Use last row features as base for rolling prediction
    last_prices = list(df['modal_price'].values[-30:])
    predictions = []

    for day in range(1, 8):
        # Rebuild features using latest known + predicted prices
        temp_df = df_raw.copy()
        # Add predicted prices as future rows
        from datetime import timedelta
        last_date = pd.to_datetime(temp_df['arrival_date'].max())
        for i, p in enumerate(predictions):
            new_row = temp_df.iloc[-1].copy()
            new_row['arrival_date'] = (last_date + timedelta(days=i+1)).strftime('%Y-%m-%d')
            new_row['modal_price'] = p
            temp_df = pd.concat([temp_df, pd.DataFrame([new_row])], ignore_index=True)

        df_feat = build_features(temp_df)
        if len(df_feat) == 0:
            break

        last_feat = df_feat[feature_cols].iloc[-1].values.reshape(1, -1)
        if scaler:
            last_feat = scaler.transform(last_feat)

        pred = model.predict(last_feat)[0]
        predictions.append(round(pred, 2))

    print(f"\n📈 7-Day Price Forecast — {variety} @ {market}")
    today = df_raw['modal_price'].iloc[-1]
    print(f"   Today's price : ₹{today:,.0f}/qtl")
    for i, p in enumerate(predictions, 1):
        change = p - today
        arrow = "↑" if change > 0 else "↓"
        print(f"   Day +{i}        : ₹{p:,.0f}/qtl  ({arrow} ₹{abs(change):,.0f})")

    return predictions


# ─────────────────────────────────────────────────────
# MAIN — train all varieties
# ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌶  MirchiMandi — Step 2: Train ML Models")
    print("=" * 60)

    # Varieties to train including Guntur Sheets commercial varieties
    varieties_to_train = [
        "Red New", "Red", "Guntur", "Red Top",
        "Teja S17", "334 Sannam", "Byadgi", "341", "DD Deluxe", "Armoor"
    ]

    all_results = {}
    for variety in varieties_to_train:
        result = train_all_models(variety=variety, market="Guntur APMC")
        if result and result[0] is not None:
            all_results[variety] = result

    # Show predictions for best varieties
    print("\n" + "="*60)
    print("📈 SAMPLE PREDICTIONS")
    print("="*60)
    predict_next_7_days("Teja S17", "Guntur APMC")
    predict_next_7_days("334 Sannam", "Guntur APMC")
    predict_next_7_days("Red New", "Guntur APMC")

    print("\n✅ All models trained and saved to ./saved_models/")
    print("   Next step: python 03_run_backend.py")
