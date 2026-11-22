"""Evaluate lagged market arrivals and archive weather on paired forecast dates."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
MARKET = "Guntur APMC"
GRADE = "FAQ"
COORDINATES = (16.3067, 80.4367)
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_CACHE = ROOT / "csv_data" / "guntur_weather_era5.json"
WEATHER_DELAY = 6  # Five-day publication delay plus one calendar day for the complete daily total.
PRICE_FEATURES = ["price", "price_change", "recent_mean_change"]
ARRIVAL_FEATURES = ["previous_arrival", "recent_arrival_mean"]
WEATHER_FEATURES = ["rain_7d", "max_temp_mean_7d"]
MODELS = {
    "price": PRICE_FEATURES,
    "arrivals": PRICE_FEATURES + ARRIVAL_FEATURES,
    "weather": PRICE_FEATURES + WEATHER_FEATURES,
    "combined": PRICE_FEATURES + ARRIVAL_FEATURES + WEATHER_FEATURES,
}


def load_market_reports(directory, variety):
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise ValueError(f"No market CSV files found in {directory}")
    rows = pd.concat([pd.read_csv(path, skiprows=1) for path in files], ignore_index=True)
    rows = rows.loc[
        (rows["Market"] == MARKET) & (rows["Variety"] == variety) & (rows["Grade"] == GRADE)
        & (rows["Commodity"] == "Dry Chillies") & (rows["Price Unit"] == "Rs./Quintal")
    ].copy()
    rows["date"] = pd.to_datetime(rows["Arrival Date"], format="%d-%m-%Y", errors="coerce")
    rows["price"] = pd.to_numeric(rows["Modal Price"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    arrivals = pd.to_numeric(rows["Arrival Quantity"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    rows["arrival"] = arrivals.where((arrivals >= 0) & (rows["Arrival Unit"] == "Metric Tonnes"))
    rows = rows.loc[rows["price"].gt(0)].dropna(subset=["date"])
    # Overlapping exports repeat quotes. Preserve missing volumes and avoid double-counting arrivals.
    prices = rows[["date", "price"]].drop_duplicates().groupby("date")["price"].median()
    quantities = rows[["date", "arrival"]].drop_duplicates().groupby("date")["arrival"].median()
    return pd.concat([prices, quantities], axis=1).sort_index()


def download_weather(path, first_date, last_date):
    response = requests.get(WEATHER_URL, params={
        "latitude": COORDINATES[0], "longitude": COORDINATES[1],
        "start_date": (first_date - pd.Timedelta(days=WEATHER_DELAY + 6)).date().isoformat(),
        "end_date": last_date.date().isoformat(), "daily": "precipitation_sum,temperature_2m_max",
        "timezone": "Asia/Kolkata", "models": "era5",
    }, timeout=30)
    response.raise_for_status()
    payload = response.json()
    parse_weather(payload)
    write_json(path, payload)


def parse_weather(payload):
    daily = payload["daily"]
    units = payload["daily_units"]
    if units["precipitation_sum"] != "mm" or units["temperature_2m_max"] != "°C" or payload["utc_offset_seconds"] != 19800:
        raise ValueError("Weather cache must use mm, °C and Asia/Kolkata daily dates")
    frame = pd.DataFrame({"rain": daily["precipitation_sum"], "max_temp": daily["temperature_2m_max"]},
                         index=pd.to_datetime(daily["time"]))
    if frame.empty or frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("Weather cache must contain ordered, unique daily dates")
    return frame.astype(float).asfreq("D")


def build_market_features(market, weather=None):
    prices = market["price"]
    previous_arrivals = market["arrival"].shift(1)
    frame = pd.DataFrame({
        "price": prices,
        "price_change": prices.diff(),
        "recent_mean_change": prices - prices.rolling(5).mean(),
        "previous_arrival": previous_arrivals,
        "recent_arrival_mean": previous_arrivals.rolling(5).mean(),
    })
    if weather is not None:
        # Label each aggregate with its first assumed availability date before joining market dates.
        lagged = pd.DataFrame({"rain_7d": weather["rain"].rolling(7).sum(),
                               "max_temp_mean_7d": weather["max_temp"].rolling(7).mean()})
        lagged.index += pd.Timedelta(days=WEATHER_DELAY)
        frame = frame.join(lagged)
    return frame


def predict_at_origin(features, target, origin, delay, feature_sets):
    history = target.loc[:origin - delay].dropna()
    if len(history) < 20:
        return None
    base = features.at[origin, "price"]
    predictions = {"persistence": float(base)}
    for name, columns in feature_sets.items():
        train = features.loc[history.index, columns]
        model = make_pipeline(StandardScaler(), Ridge(alpha=1))
        model.fit(train, history - features.loc[history.index, "price"])
        predictions[name] = float(base + model.predict(features.loc[[origin], columns])[0])
    return predictions


def evaluate(market, weather=None):
    if len(market) < 60:
        raise ValueError("At least 60 market quote dates are required")
    feature_sets = MODELS if weather is not None else {key: MODELS[key] for key in ("price", "arrivals")}
    required = list(dict.fromkeys(column for columns in feature_sets.values() for column in columns))
    features = build_market_features(market, weather).dropna(subset=required)
    cutoff = market.index[int(len(market) * 0.70)]
    origins = features.loc[cutoff:].index
    rows = []
    for day in range(1, 8):
        delay = pd.Timedelta(days=day)
        target = pd.Series(market["price"].reindex(features.index + delay).to_numpy(), index=features.index)
        predictions = []
        for origin in origins:
            actual = target.at[origin]
            if pd.isna(actual):
                continue
            prediction = predict_at_origin(features, target, origin, delay, feature_sets)
            if prediction is not None:
                predictions.append({"actual": float(actual), **prediction})
        scored = pd.DataFrame(predictions)
        metric = {}
        for name in ("persistence", *feature_sets):
            if scored.empty:
                metric[name] = {"mae": None, "rmse": None}
                continue
            errors = scored[name] - scored["actual"]
            metric[name] = {"mae": round(float(errors.abs().mean()), 2),
                            "rmse": round(float(np.sqrt((errors ** 2).mean())), 2)}
        rows.append({"day": day, "scored": len(scored), "metrics": metric})
    return cutoff, rows


def write_json(path, payload):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variety", choices=("Red New", "Red"), default="Red New")
    parser.add_argument("--csv-dir", type=Path, default=ROOT / "csv_data")
    parser.add_argument("--weather-cache", type=Path, default=WEATHER_CACHE)
    parser.add_argument("--download-weather", action="store_true")
    args = parser.parse_args()
    market = load_market_reports(args.csv_dir, args.variety)
    if market.empty:
        parser.error("No usable market observations for the selected variety")
    if args.download_weather:
        download_weather(args.weather_cache, market.index.min(), market.index.max())
    weather = parse_weather(json.loads(args.weather_cache.read_text(encoding="utf-8"))) if args.weather_cache.is_file() else None
    cutoff, rows = evaluate(market, weather)
    recent = market["arrival"].dropna().tail(10)
    report = {
        "market": MARKET, "variety": args.variety, "grade": GRADE,
        "data_start": str(market.index.min().date()), "data_end": str(market.index.max().date()),
        "evaluation_start": str(cutoff.date()), "quote_dates": len(market),
        "weather_evaluated": weather is not None and any(row["scored"] for row in rows),
        "weather_source": "Open-Meteo ERA5 reanalysis" if weather is not None else None,
        "weather_lag_days": WEATHER_DELAY if weather is not None else None,
        "weather_coverage": [str(weather.index.min().date()), str(weather.index.max().date())] if weather is not None else None,
        "arrival_history": [{"date": str(day.date()), "tonnes": round(float(value), 2)} for day, value in recent.items()],
        "horizons": rows,
    }
    if weather is not None:
        recent_weather = weather.loc[:market.index.max()].dropna().tail(7)
        report["weather_history"] = [{"date": str(day.date()), "rain_mm": round(float(row["rain"]), 2),
                                      "max_temp_c": round(float(row["max_temp"]), 2)} for day, row in recent_weather.iterrows()]
    output = ROOT / "saved_models" / f"market_signals_{args.variety.replace(' ', '_')}.json"
    write_json(output, report)
    print(f"{MARKET} / {args.variety} / {GRADE}: {len(market)} quote dates, evaluation from {cutoff.date()}")
    print(pd.DataFrame([{"day": row["day"], "scored": row["scored"],
                         **{name: metric["mae"] for name, metric in row["metrics"].items()}} for row in rows]).to_string(index=False))
    if weather is None:
        print("Weather unavailable. Run with --download-weather or supply an Open-Meteo archive response with --weather-cache.")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
