"""
STEP 3: FastAPI Backend
========================
Run: uvicorn main:app --reload --port 8000

All API endpoints for MirchiMandi website.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import psycopg2, psycopg2.extras
import pandas as pd
import numpy as np
import joblib, json, os
import requests
import math
from datetime import date, datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

app = FastAPI(
    title="MirchiMandi API",
    description="Real-time Mirchi Price Intelligence for Andhra Pradesh",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL     = "postgresql://postgres.akdzzsfhvcuvzpjxmscs:8pohdOKVFAZHJ0VJ@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
MODELS_DIR = "../saved_models"

# Add scripts directory to path to import PyTorchMLPRegressor for unpickling
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
from train_models import PyTorchMLPRegressor

# ─────────────────────────────────────────────────────
# DB HELPER
# ─────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)

def query(sql, params=None):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

def execute(sql, params=None):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────────────────────────────────
# LOAD ML MODEL
# ─────────────────────────────────────────────────────
def load_model(variety):
    safe = variety.replace(" ", "_").replace("/", "_")
    mp   = f"{MODELS_DIR}/best_model_{safe}.pkl"
    if not os.path.exists(mp):
        return None, None, None, None
    model  = joblib.load(mp)
    scaler = None
    sp = f"{MODELS_DIR}/scaler_{safe}.pkl"
    if os.path.exists(sp):
        scaler = joblib.load(sp)
    with open(f"{MODELS_DIR}/meta_{safe}.json") as f:
        meta = json.load(f)
    with open(f"{MODELS_DIR}/feature_cols_{safe}.json") as f:
        cols = json.load(f)
    return model, scaler, meta, cols


# ─────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "MirchiMandi API is running 🌶", "version": "1.0.0"}


# ── 1. GET TODAY'S PRICE ─────────────────────────────
@app.get("/api/price/today")
def get_today_price(
    market:  str = Query("Guntur APMC",  description="Market name"),
    variety: str = Query("Red New",       description="Variety: Red New / Red / Guntur / Red Top / White")
):
    is_user_reported = False
    rows = query("""
        SELECT arrival_date, 
               AVG(modal_price)::float as modal_price,
               MIN(min_price)::float as min_price,
               MAX(max_price)::float as max_price,
               SUM(arrival_qty)::float as arrival_qty
        FROM mirchi_prices
        WHERE market = %s AND variety = %s
        GROUP BY arrival_date
        ORDER BY arrival_date DESC LIMIT 2
    """, (market, variety))

    if not rows:
        # Fallback to verified user-submitted prices
        rows = query("""
            SELECT arrival_date, 
                   AVG(modal_price)::float as modal_price,
                   MIN(min_price)::float as min_price,
                   MAX(max_price)::float as max_price,
                   SUM(arrival_qty)::float as arrival_qty
            FROM user_variety_prices
            WHERE market = %s AND variety = %s AND is_verified = TRUE
            GROUP BY arrival_date
            ORDER BY arrival_date DESC LIMIT 2
        """, (market, variety))
        if rows:
            is_user_reported = True

    if not rows:
        raise HTTPException(404, f"No data for {variety} at {market}")

    today_row = rows[0]
    prev_row  = rows[1] if len(rows) > 1 else None

    change       = None
    change_pct   = None
    if prev_row and today_row['modal_price'] and prev_row['modal_price']:
        change     = today_row['modal_price'] - prev_row['modal_price']
        change_pct = round(change / prev_row['modal_price'] * 100, 2)

    return {
        "date":        str(today_row['arrival_date']),
        "market":      market,
        "variety":     variety,
        "grade":       "User Reported (Avg)" if is_user_reported else "All Grades (Avg)",
        "modal_price": round(today_row['modal_price'], 2) if today_row['modal_price'] else None,
        "min_price":   round(today_row['min_price'], 2) if today_row['min_price'] else None,
        "max_price":   round(today_row['max_price'], 2) if today_row['max_price'] else None,
        "arrival_qty": today_row['arrival_qty'],
        "change":      round(change, 2) if change else None,
        "change_pct":  change_pct,
        "unit":        "Rs. per Quintal (100 kg)",
        "is_user_reported": is_user_reported,
    }


# ── 2. PRICE HISTORY CHART ───────────────────────────
@app.get("/api/price/history")
def get_price_history(
    market:  str = Query("Guntur APMC"),
    variety: str = Query("Red New"),
    days:    int = Query(90, ge=7, le=365)
):
    rows = query("""
        SELECT arrival_date, modal_price, min_price, max_price, arrival_qty
        FROM mirchi_prices
        WHERE market = %s AND variety = %s
          AND arrival_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY arrival_date ASC
    """, (market, variety, days))

    return {
        "market":  market,
        "variety": variety,
        "days":    days,
        "data":    rows,
        "count":   len(rows),
    }


# ── 3. 7-DAY FORECAST ────────────────────────────────
@app.get("/api/forecast")
def get_forecast(
    market:  str = Query("Guntur APMC"),
    variety: str = Query("Red New")
):
    model, scaler, meta, feat_cols = load_model(variety)

    if model is None:
        # Fallback: simple moving average if no ML model (aggregate grades by date first)
        rows = query("""
            SELECT arrival_date, AVG(modal_price)::float as modal_price 
            FROM mirchi_prices
            WHERE market = %s AND variety = %s
            GROUP BY arrival_date
            ORDER BY arrival_date DESC LIMIT 14
        """, (market, variety))
        
        if not rows:
            # Fallback to verified user-submitted prices
            rows = query("""
                SELECT arrival_date, AVG(modal_price)::float as modal_price 
                FROM user_variety_prices
                WHERE market = %s AND variety = %s AND is_verified = TRUE
                GROUP BY arrival_date
                ORDER BY arrival_date DESC LIMIT 14
            """, (market, variety))
            
        if not rows:
            raise HTTPException(404, "No data available")
        prices = [r['modal_price'] for r in rows if r['modal_price'] is not None]
        avg    = np.mean(prices)
        preds  = [round(avg, 0)] * 7
        today_price = float(prices[0])
        trend       = "RISING" if preds and preds[-1] > today_price else "FALLING"
        best_day    = preds.index(max(preds)) + 1 if preds else 1
        max_gain    = round(max(preds) - today_price, 0) if preds else 0
        return {
            "market":       market,
            "variety":      variety,
            "today_price":  today_price,
            "forecast":     preds,
            "trend":        trend,
            "best_day":     best_day,
            "max_gain":     max_gain,
            "model_used":   "Moving Average (fallback)",
            "accuracy_mae": None,
            "accuracy_r2":  None
        }

    # Load recent data and build features - aggregate grades by date to avoid duplicates
    raw_rows = query("""
        SELECT arrival_date::text, 
               AVG(modal_price) as modal_price,
               AVG(min_price) as min_price,
               AVG(max_price) as max_price,
               COALESCE(SUM(arrival_qty), 0) as arrival_qty
        FROM mirchi_prices
        WHERE market = %s AND variety = %s
        GROUP BY arrival_date
        ORDER BY arrival_date ASC
    """, (market, variety))

    df_raw = pd.DataFrame(raw_rows)
    df_raw['arrival_date'] = pd.to_datetime(df_raw['arrival_date'])

    # Import feature building inline
    import sys; sys.path.insert(0, '../scripts')
    from train_models import build_features  # noqa
    # Rebuild features same way as training
    predictions = []
    current_df  = df_raw.copy()

    for day in range(1, 8):
        df_feat = build_features(current_df)
        if len(df_feat) == 0 or not all(c in df_feat.columns for c in feat_cols):
            break
        last = df_feat[feat_cols].iloc[-1].values.reshape(1, -1)
        if scaler:
            last = scaler.transform(last)
        pred = float(model.predict(last)[0])
        predictions.append(round(pred, 2))

        # Add this prediction as next row
        new_row = current_df.iloc[-1].copy()
        last_dt = current_df['arrival_date'].max()
        new_row['arrival_date'] = last_dt + timedelta(days=1)
        new_row['modal_price']  = pred
        current_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)

    today_price = float(df_raw['modal_price'].iloc[-1])
    trend       = "RISING" if predictions and predictions[-1] > today_price else "FALLING"
    best_day    = predictions.index(max(predictions)) + 1 if predictions else 1
    max_gain    = round(max(predictions) - today_price, 0) if predictions else 0

    return {
        "market":       market,
        "variety":      variety,
        "today_price":  today_price,
        "forecast":     predictions,
        "trend":        trend,
        "best_day":     best_day,
        "max_gain":     max_gain,
        "model_used":   meta['best_model'],
        "accuracy_mae": meta['mae'],
        "accuracy_r2":  meta['r2'],
    }


# ── 4. RECOMMENDATION ────────────────────────────────
@app.get("/api/recommendation")
def get_recommendation(
    market:       str   = Query("Guntur APMC"),
    variety:      str   = Query("Red New"),
    quintals:     float = Query(50, description="How many quintals you have"),
    broker_price: float = Query(None, description="Broker's offered price per quintal")
):
    # Get forecast
    forecast_data = get_forecast(market, variety)
    today_price   = forecast_data['today_price']
    predictions   = forecast_data['forecast']

    if not predictions:
        return {"action": "SELL_TODAY", "reason": "No forecast available"}

    # Storage cost = approx Rs 30 per quintal per day (cold storage + transport risk)
    STORAGE_COST_PER_DAY = 30

    best_action = "SELL_TODAY"
    best_gain   = 0
    best_day    = 0
    best_price  = today_price

    for day_idx, pred_price in enumerate(predictions, 1):
        storage_cost   = day_idx * STORAGE_COST_PER_DAY
        net_gain_per_q = pred_price - today_price - storage_cost
        if net_gain_per_q > best_gain and net_gain_per_q > 200:
            best_gain   = net_gain_per_q
            best_day    = day_idx
            best_price  = pred_price
            best_action = "WAIT"

    # Find the maximum predicted price in the next 7 days for explanation math
    max_forecast_price = float(max(predictions))
    max_forecast_day = predictions.index(max_forecast_price) + 1
    price_increase = max_forecast_price - today_price
    max_storage_cost = max_forecast_day * STORAGE_COST_PER_DAY
    
    # Crop scale calculations
    total_price_gain = price_increase * quintals
    total_storage_cost = max_storage_cost * quintals
    total_net_loss = total_storage_cost - total_price_gain

    # Wait scale calculations
    wait_storage_cost = best_day * STORAGE_COST_PER_DAY * quintals
    wait_price_gain = (best_price - today_price) * quintals
    wait_net_profit = wait_price_gain - wait_storage_cost

    if best_action == "WAIT":
        reason_en = f"Storing {quintals:,.0f} qtl for {best_day} days costs ₹{wait_storage_cost:,.0f}, while your total price gain is ₹{wait_price_gain:,.0f}, giving you an extra net profit of ₹{wait_net_profit:,.0f}."
        reason_te = f"{quintals:,.0f} క్వింటాళ్లను {best_day} రోజులు నిల్వ చేయడానికి ₹{wait_storage_cost:,.0f} ఖర్చవుతుంది, కానీ ధర పెరుగుదల వల్ల వచ్చే లాభం ₹{wait_price_gain:,.0f}. దీనివల్ల మీకు ₹{wait_net_profit:,.0f} అదనపు లాభం లభిస్తుంది."
        rec_te = f"{best_day} రోజుల తర్వాత {market}కి వెళ్ళండి"
        rec_en = f"Go to {market} after {best_day} days"
        expected_p = best_price
    else:
        # SELL_TODAY
        expected_p = max_forecast_price
        if price_increase > 0:
            reason_en = f"Storing {quintals:,.0f} qtl for {max_forecast_day} days costs ₹{total_storage_cost:,.0f}, whereas your price gain is only ₹{total_price_gain:,.0f}. Selling today avoids a net loss of ₹{total_net_loss:,.0f}."
            reason_te = f"{quintals:,.0f} క్వింటాళ్లను {max_forecast_day} రోజులు నిల్వ చేయడానికి ₹{total_storage_cost:,.0f} ఖర్చవుతుంది, కానీ ధర ద్వారా వచ్చే లాభం కేవలం ₹{total_price_gain:,.0f}. ఈరోజే అమ్మడం ద్వారా ₹{total_net_loss:,.0f} నష్టాన్ని నివారించవచ్చు."
            rec_en = "Sell today (Save on storage)"
            rec_te = "ఈరోజే అమ్మండి (స్టోరేజ్ ఖర్చులు ఆదా చేసుకోండి)"
        else:
            reason_en = "Prices are expected to drop or stay flat over the next 7 days. Sell today to avoid storage losses."
            reason_te = "రాబోయే 7 రోజుల్లో ధరలు తగ్గే అవకాశం ఉంది లేదా స్థిరంగా ఉంటాయి. నష్టాలను నివారించడానికి ఈరోజే అమ్మండి."
            rec_en = "Sell today"
            rec_te = "ఈరోజే అమ్మండి"

    # Broker comparison
    broker_loss = None
    if broker_price:
        broker_loss = (today_price - broker_price) * quintals

    total_gain  = round(best_gain * quintals, 0) if best_action == "WAIT" else 0

    return {
        "action":              best_action,
        "wait_days":           best_day,
        "today_price":         today_price,
        "expected_price":      round(expected_p, 0),
        "gain_per_quintal":    round(best_gain, 0) if best_action == "WAIT" else 0,
        "total_gain":          total_gain,
        "quintals":            quintals,
        "broker_price":        broker_price,
        "broker_loss_total":   round(broker_loss, 0) if broker_loss else None,
        "recommendation_te":   rec_te,
        "recommendation_en":   rec_en,
        "reason":              reason_en,
        "reason_te":           reason_te,
    }


# ── 5. COMPARE ALL MARKETS (Deprecated) ───────────────
@app.get("/api/markets/compare")
def compare_markets(variety: str = Query("Red New")):
    return {"variety": variety, "markets": []}


# ── 6. ALL VARIETIES — TODAY ──────────────────────────
@app.get("/api/varieties/today")
def get_all_varieties_today(market: str = Query("Guntur APMC")):
    rows = query("""
        SELECT variety, grade, modal_price, min_price, max_price,
               arrival_qty, arrival_date
        FROM mirchi_prices
        WHERE market = %s
          AND arrival_date = (
              SELECT MAX(arrival_date) FROM mirchi_prices WHERE market = %s
          )
        ORDER BY modal_price DESC
    """, (market, market))

    for r in rows:
        r['arrival_date'] = str(r['arrival_date'])

    return {"market": market, "varieties": rows, "count": len(rows)}


# ── 7. MODEL COMPARISON TABLE ────────────────────────
@app.get("/api/models/comparison")
def get_model_comparison(variety: str = Query("Red New")):
    rows = query("""
        SELECT model_name, variety, mae, rmse, r2, mape, is_best, trained_at
        FROM ml_model_results
        WHERE variety = %s
        ORDER BY mae ASC
    """, (variety,))
    for r in rows:
        if r.get('trained_at'):
            r['trained_at'] = str(r['trained_at'])
    return {"variety": variety, "models": rows}


# ── 8. PROFIT CALCULATOR ─────────────────────────────
@app.get("/api/calculator")
def profit_calculator(
    quintals:     float = Query(..., description="Number of quintals"),
    broker_price: float = Query(..., description="Broker offered price"),
    market:       str   = Query("Guntur APMC"),
    variety:      str   = Query("Red New")
):
    today = get_today_price(market, variety)
    mandi_price   = today['modal_price']
    mandi_total   = quintals * mandi_price
    broker_total  = quintals * broker_price
    loss          = mandi_total - broker_total
    loss_pct      = round(loss / mandi_total * 100, 1)

    return {
        "quintals":     quintals,
        "mandi_price":  mandi_price,
        "broker_price": broker_price,
        "mandi_total":  round(mandi_total, 0),
        "broker_total": round(broker_total, 0),
        "loss":         round(loss, 0),
        "loss_pct":     loss_pct,
        "message_te":   f"మీరు బ్రోకర్ దగ్గర ₹{loss:,.0f} పోగొట్టుకుంటున్నారు",
        "message_en":   f"You are losing ₹{loss:,.0f} by selling to broker",
    }


# ── 8b. TRANSPORT & ARBITRAGE CALCULATOR ──────────────────

# Static mapping for Andhra Pradesh pincodes for high-reliability lookup
AP_PINCODE_COORDS = {
    "523167": (15.8221, 80.1918),  # Pavulur / Inkollu (Farmer's village)
    "523169": (15.9364, 80.22906),  # Nuthalapadu
    "523187": (15.9388, 80.1206),  # Vetapalem / Chirala
    "Pavulur": (15.8221, 80.1918),
    "pavulur": (15.8221, 80.1918),
    "Nuthalapadu": (15.9364, 80.22906),
    "nuthalapadu": (15.9364, 80.22906),
    "522001": (16.3067, 80.4367),  # Guntur APMC (Guntur Main Yard)
    "522002": (16.3000, 80.4500),  # Guntur East
    "522004": (16.2922, 80.4491),  # Guntur APMC Yard Area
    "522529": (16.2625, 80.2500),  # Phirangipuram
    "522601": (16.1500, 80.0500),  # Narasaraopet
    "522616": (16.0833, 80.1667),  # Chilakaluripet
    "522403": (16.3833, 80.1500),  # Sattenapalli
    "522201": (16.2428, 80.6438),  # Tenali
    "522101": (15.9036, 80.4682),  # Bapatla
    "520001": (16.5083, 80.6417),  # Vijayawada
    "523001": (15.5058, 80.0494),  # Ongole
    "518001": (15.8281, 78.0372),  # Kurnool APMC
    "517501": (13.6288, 79.4192),  # Tirupati
    "524001": (14.4426, 79.9865),  # Nellore
}

MARKET_COORDS = {
    "Guntur APMC": (16.3067, 80.4367),
}

def get_coordinates(location: str):
    loc = str(location).strip()
    
    # 1. Check if it matches a known market name
    if loc in MARKET_COORDS:
        return MARKET_COORDS[loc]
        
    # 2. Check if it matches a known pincode in our static dictionary
    if loc in AP_PINCODE_COORDS:
        return AP_PINCODE_COORDS[loc]
        
    # 3. Check if it's a 6-digit numeric pincode
    if loc.isdigit() and len(loc) == 6:
        try:
            url = f"https://nominatim.openstreetmap.org/search?postalcode={loc}&country=India&format=json"
            headers = {'User-Agent': 'MirchiMandi-App/1.0'}
            r = requests.get(url, headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                if data:
                    return float(data[0]['lat']), float(data[0]['lon'])
        except Exception:
            pass
            
    # 4. Fallback: treat it as a village/town name and search in Andhra Pradesh, India
    try:
        from urllib.parse import quote
        search_query = f"{loc}, Andhra Pradesh, India"
        url = f"https://nominatim.openstreetmap.org/search?q={quote(search_query)}&format=json"
        headers = {'User-Agent': 'MirchiMandi-App/1.0'}
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
        
    return None


def fallback_distance(p1: str, p2: str):
    p1, p2 = str(p1).strip(), str(p2).strip()
    if p1 == p2:
        return 5.0
    if p1[:4] == p2[:4]:
        return 20.0
    if p1[:3] == p2[:3]:
        return 45.0
    if p1[:2] == p2[:2]:
        return 95.0
    return 220.0

@app.get("/api/transport/calculate")
def get_transport_costs(
    farmer_pincode: str = Query(..., description="Farmer village pincode"),
    market_pincode: str = Query("522001", description="APMC market pincode"),
    vehicle:        str = Query("Tractor", description="Tractor / Trolley / Truck"),
    quintals:       float = Query(50.0, description="Amount of crop in quintals")
):
    c1 = get_coordinates(farmer_pincode)
    c2 = get_coordinates(market_pincode)
    
    if c1 and c2:
        # Haversine distance
        lat1, lon1 = c1
        lat2, lon2 = c2
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        # Multiply by 1.47 to estimate actual road path distance from straight-line (more realistic for rural AP district roads)
        distance = round(distance * 1.47, 1)
    else:
        # Fallback estimation based on pincode prefix
        distance = fallback_distance(farmer_pincode, market_pincode)
        
    # Calculate vehicle expenses
    # Tractor: base ₹1500, ₹35/km (up to 100 quintals)
    # Trolley (Tata Ace): base ₹800, ₹25/km (up to 30 quintals)
    # Truck: base ₹3000, ₹45/km (up to 250 quintals)
    v = vehicle.lower().strip()
    if "trolley" in v or "ace" in v:
        base_fare = 800
        per_km = 25
        v_name = "Trolley (Tata Ace)"
    elif "truck" in v:
        base_fare = 3000
        per_km = 45
        v_name = "Truck"
    else: # Default: Tractor
        base_fare = 1500
        per_km = 35
        v_name = "Tractor"
        
    transport_fare = base_fare + (distance * per_km)
    
    # Labor (Hamali): Loading + Unloading = ₹40 per quintal (₹20 load + ₹20 unload)
    labor_cost = quintals * 40
    total_cost = transport_fare + labor_cost
    
    return {
        "farmer_pincode": farmer_pincode,
        "market_pincode": market_pincode,
        "distance_km": distance,
        "vehicle": v_name,
        "base_fare": base_fare,
        "per_km_rate": per_km,
        "transport_fare": round(transport_fare, 0),
        "labor_cost": round(labor_cost, 0),
        "total_cost": round(total_cost, 0),
    }

@app.get("/api/arbitrage")
def get_arbitrage_analysis(
    farmer_pincode: str = Query(..., description="Farmer village pincode"),
    market_pincode: str = Query("522001", description="APMC market pincode"),
    vehicle:        str = Query("Tractor", description="Tractor / Trolley / Truck"),
    quintals:       float = Query(50.0, description="Amount of crop in quintals"),
    broker_price:   float = Query(..., description="Local broker offer price per quintal"),
    variety:        str = Query("Teja S17", description="Variety name"),
    market:         str = Query("Guntur APMC", description="Market name")
):
    # Get today's market price
    # Query the latest average price for that variety in that market
    rows = query("""
        SELECT AVG(modal_price)::float as modal_price 
        FROM mirchi_prices
        WHERE market = %s AND variety = %s
        GROUP BY arrival_date
        ORDER BY arrival_date DESC LIMIT 1
    """, (market, variety))
    
    if not rows:
        raise HTTPException(404, f"No market price found for variety '{variety}' at '{market}'")
        
    mandi_price = rows[0]['modal_price']
    
    # Calculate transport cost
    tc = get_transport_costs(farmer_pincode, market_pincode, vehicle, quintals)
    transport_cost = tc['total_cost']
    distance_km = tc['distance_km']
    
    mandi_revenue = quintals * mandi_price
    broker_revenue = quintals * broker_price
    net_mandi_revenue = mandi_revenue - transport_cost
    
    arbitrage_gain = net_mandi_revenue - broker_revenue
    is_profitable = arbitrage_gain > 0
    
    # Get forecast trend
    trend = "STABLE"
    try:
        fc = get_forecast(market, variety)
        trend = fc['trend']
    except Exception:
        pass
        
    # Recommendation logic
    if is_profitable:
        rec_action = "MANDI"
        rec_te = f"మీరు గంటూరు యార్డుకు వెళితే ₹{arbitrage_gain:,.0f} అదనపు లాభం పొందుతారు. ట్రాక్టర్ ద్వారా రవాణా ఖర్చు ₹{transport_cost:,.0f} అవుతుంది."
        rec_en = f"Recommended: Sell at {market}! Even after transport costs, you will gain ₹{arbitrage_gain:,.0f} extra profit compared to the local broker."
    else:
        rec_action = "BROKER"
        rec_te = f"ఈరోజే బ్రోకర్‌కు అమ్మండి. గంటూరుకు వెళ్ళడానికి అయ్యే రవాణా ఖర్చు (₹{transport_cost:,.0f}) ధర వ్యత్యాసం కంటే ఎక్కువ."
        rec_en = f"Recommended: Sell to local broker. Transporting to {market} (₹{transport_cost:,.0f}) will exceed your price gain, causing a loss of ₹{abs(arbitrage_gain):,.0f}."
        
    return {
        "mandi_price": mandi_price,
        "broker_price": broker_price,
        "mandi_revenue": round(mandi_revenue, 0),
        "broker_revenue": round(broker_revenue, 0),
        "net_mandi_revenue": round(net_mandi_revenue, 0),
        "transport_cost": transport_cost,
        "distance_km": distance_km,
        "arbitrage_gain": round(arbitrage_gain, 0),
        "is_profitable": is_profitable,
        "trend": trend,
        "recommendation": {
            "action": rec_action,
            "message_te": rec_te,
            "message_en": rec_en
        },
        "transport_details": tc
    }


# ── 9. USER SUBMITS VARIETY PRICE ────────────────────
class UserPriceSubmit(BaseModel):
    arrival_date:  str   = Field(..., example="2026-06-04")
    market:        str   = Field(..., example="Guntur APMC")
    variety:       str   = Field(..., example="Teja S17")
    modal_price:   float = Field(..., example=22400)
    min_price:     Optional[float] = None
    max_price:     Optional[float] = None
    arrival_qty:   Optional[float] = None
    reporter_name: Optional[str]   = None
    notes:         Optional[str]   = None

@app.post("/api/user/submit-price")
def submit_user_price(data: UserPriceSubmit):
    """
    Farmers / users can submit prices for varieties
    not in agmarknet — like Teja, 334, Byadgi etc.
    """
    if data.modal_price <= 0 or data.modal_price > 100000:
        raise HTTPException(400, "Invalid price. Must be between 0 and 100,000")

    # Get recent official prices to check if the submission is a massive outlier
    ref_prices = query("""
        SELECT modal_price FROM mirchi_prices
        WHERE market = %s
        ORDER BY arrival_date DESC LIMIT 10
    """, (data.market,))
    
    if ref_prices:
        avg_ref = np.mean([r['modal_price'] for r in ref_prices])
        lower_bound = avg_ref * 0.75
        upper_bound = avg_ref * 1.25
        if data.modal_price < lower_bound or data.modal_price > upper_bound:
            raise HTTPException(
                400, 
                f"Submitted price is too far from current market rates (average is ₹{avg_ref:,.0f}). "
                f"Allowable range: ₹{lower_bound:,.0f} to ₹{upper_bound:,.0f}."
            )

    execute("""
        INSERT INTO user_variety_prices
            (arrival_date, market, variety, modal_price,
             min_price, max_price, arrival_qty,
             reporter_name, notes, is_verified)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, FALSE)
    """, (
        data.arrival_date, data.market, data.variety,
        data.modal_price, data.min_price, data.max_price,
        data.arrival_qty, data.reporter_name, data.notes
    ))

    return {
        "success": True,
        "message": "Price submitted! Thank you for contributing. It will appear on the site after admin verification.",
        "message_te": "ధర నమోదు చేశారు! మీ సహకారానికి ధన్యవాదాలు. అడ్మిన్ పరిశీలించిన తర్వాత వెబ్‌సైట్‌లో కనిపిస్తుంది.",
        "data": data.dict()
    }


# ── 10. GET USER-SUBMITTED VARIETIES ─────────────────
@app.get("/api/user/varieties")
def get_user_varieties(
    market:  str = Query("Guntur APMC"),
    variety: Optional[str] = Query(None)
):
    if variety:
        rows = query("""
            SELECT id, variety, arrival_date, modal_price, reporter_name,
                   notes, upvotes, submitted_at
            FROM user_variety_prices
            WHERE market = %s AND variety ILIKE %s AND is_verified = TRUE
            ORDER BY arrival_date DESC, submitted_at DESC LIMIT 50
        """, (market, f"%{variety}%"))
    else:
        rows = query("""
            SELECT variety, COUNT(*) as submissions,
                   ROUND(AVG(modal_price)::numeric,0) as avg_price,
                   MAX(arrival_date) as latest_date
            FROM user_variety_prices
            WHERE market = %s AND is_verified = TRUE
            GROUP BY variety
            ORDER BY submissions DESC
        """, (market,))

    for r in rows:
        for k in ['arrival_date', 'submitted_at', 'latest_date']:
            if k in r and r[k]:
                r[k] = str(r[k])

    return {"market": market, "data": rows}


# ── 11. UPVOTE USER PRICE ─────────────────────────────
@app.post("/api/user/upvote/{price_id}")
def upvote_price(price_id: int):
    execute("""
        UPDATE user_variety_prices SET upvotes = upvotes + 1 WHERE id = %s
    """, (price_id,))
    return {"success": True, "message": "Upvoted!"}


# ── 11b. ADMIN CONTROL ENDPOINTS ──────────────────────
@app.get("/api/admin/unverified")
def get_unverified_prices(passcode: str = Query(...)):
    if passcode != "1234":
        raise HTTPException(401, "Invalid passcode")
    rows = query("""
        SELECT id, arrival_date, market, variety, modal_price, reporter_name, notes, submitted_at
        FROM user_variety_prices
        WHERE is_verified = FALSE
        ORDER BY submitted_at DESC
    """)
    for r in rows:
        for k in ['arrival_date', 'submitted_at']:
            if k in r and r[k]:
                r[k] = str(r[k])
    return rows

@app.post("/api/admin/verify/{price_id}")
def verify_price(price_id: int, passcode: str = Query(...)):
    if passcode != "1234":
        raise HTTPException(401, "Invalid passcode")
    execute("UPDATE user_variety_prices SET is_verified = TRUE WHERE id = %s", (price_id,))
    return {"success": True, "message": "Price verified successfully!"}

@app.delete("/api/admin/delete/{price_id}")
def delete_price(price_id: int, passcode: str = Query(...)):
    if passcode != "1234":
        raise HTTPException(401, "Invalid passcode")
    execute("DELETE FROM user_variety_prices WHERE id = %s", (price_id,))
    return {"success": True, "message": "Price deleted successfully!"}

@app.post("/api/admin/trigger-scraper")
def trigger_scraper(passcode: str = Query(...)):
    import sys
    import subprocess
    if passcode != "1234":
        raise HTTPException(401, "Invalid passcode")
    try:
        python_exec = sys.executable
        # Run daily_auto_sync.py in scripts folder to fetch latest daily prices
        cmd = [python_exec, "scripts/daily_auto_sync.py"]
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        subprocess.Popen(cmd, env=env, cwd=os.path.dirname(os.path.abspath(__file__)) + "/..")
        return {"success": True, "message": "Mandi data sync triggered successfully in the background!"}
    except Exception as e:
        raise HTTPException(500, f"Failed to trigger scraper: {str(e)}")


# ── 12. SEASONAL ANALYSIS ────────────────────────────
@app.get("/api/analysis/seasonal")
def seasonal_analysis(
    market:  str = Query("Guntur APMC"),
    variety: str = Query("Red New")
):
    rows = query("""
        SELECT
            EXTRACT(MONTH FROM arrival_date) as month,
            TO_CHAR(arrival_date, 'Mon') as month_name,
            ROUND(AVG(modal_price)::numeric, 0) as avg_price,
            ROUND(MIN(modal_price)::numeric, 0) as min_price,
            ROUND(MAX(modal_price)::numeric, 0) as max_price,
            COUNT(*) as data_points
        FROM mirchi_prices
        WHERE market = %s AND variety = %s
        GROUP BY month, month_name
        ORDER BY month
    """, (market, variety))
    return {"market": market, "variety": variety, "seasonal": rows}


# ── 13. HEALTH CHECK ─────────────────────────────────
@app.get("/api/health")
def health():
    try:
        rows = query("SELECT MAX(arrival_date) as latest FROM mirchi_prices")
        return {
            "status": "ok",
            "latest_data": str(rows[0]['latest']) if rows else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
