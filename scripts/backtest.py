"""Evaluate a seven-calendar-day forecasting benchmark on local AGMARKNET reports."""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def load_prices(directory, market, variety, grade):
    reports = sorted(directory.glob("*.csv"))
    if not reports:
        raise ValueError(f"No CSVs found in {directory}")
    rows = pd.concat([pd.read_csv(report, skiprows=1) for report in reports])
    matching = rows.loc[
        (rows["Market"] == market) & (rows["Variety"] == variety)
        & (rows["Grade"] == grade) & (rows["Commodity"] == "Dry Chillies")
        & (rows["Price Unit"] == "Rs./Quintal"), ["Arrival Date", "Modal Price"]
    ].copy()
    matching["date"] = pd.to_datetime(matching["Arrival Date"], format="%d-%m-%Y", errors="coerce")
    matching["price"] = pd.to_numeric(
        matching["Modal Price"].astype(str).str.replace(",", "", regex=False), errors="coerce"
    )
    matching = matching.loc[matching["price"] > 0].dropna(subset=["date"])
    # Overlapping exports can contain the same quote or disagree about a date.
    return matching.drop_duplicates(["date", "price"]).groupby("date")["price"].median()


def evaluate(prices, storage_cost, minimum_gain):
    features = pd.DataFrame({
        "price": prices,
        "previous_price": prices.shift(1),
        "mean_5": prices.rolling(5).mean(),
    }).dropna()
    if len(features) < 60:
        raise ValueError("At least 60 usable observations are required")

    horizons = range(1, 8)
    targets = {}
    for day in horizons:
        dates = features.index + pd.Timedelta(days=day)
        targets[day] = pd.Series(prices.reindex(dates).to_numpy(), index=features.index)

    test_start = features.index[int(len(features) * 0.7)]
    forecasts = []
    decisions = []
    for origin in features.loc[test_start:].index:
        today = prices.at[origin]
        predictions = {}
        for day in horizons:
            delay = pd.Timedelta(days=day)
            known = targets[day].loc[:origin - delay].dropna()
            if len(known) < 20:
                continue
            model = make_pipeline(StandardScaler(), Ridge())
            model.fit(features.loc[known.index], known - features.loc[known.index, "price"])
            predicted = today + model.predict(features.loc[[origin]])[0]
            predictions[day] = predicted
            actual = targets[day].at[origin]
            if pd.notna(actual):
                forecasts.append((day, abs(actual - today), abs(actual - predicted)))

        if len(predictions) != len(horizons) or origin + pd.Timedelta(days=7) > prices.index[-1]:
            continue
        best_day = max(predictions, key=lambda day: predictions[day] - storage_cost * day)
        if predictions[best_day] - today - storage_cost * best_day <= minimum_gain:
            decisions.append((False, 0.0))
        else:
            actual = targets[best_day].at[origin]
            decisions.append((True, actual - today - storage_cost * best_day))

    return (
        pd.DataFrame(forecasts, columns=["day", "baseline_error", "ridge_error"]),
        pd.DataFrame(decisions, columns=["wait", "net_gain"]),
        test_start,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, default=Path(__file__).resolve().parents[1] / "csv_data")
    parser.add_argument("--market", default="Guntur APMC")
    parser.add_argument("--variety", default="Red New")
    parser.add_argument("--grade", default="FAQ")
    parser.add_argument("--storage-cost", type=float, default=30)
    parser.add_argument("--minimum-gain", type=float, default=200)
    args = parser.parse_args()
    try:
        prices = load_prices(args.csv_dir, args.market, args.variety, args.grade)
        forecasts, decisions, test_start = evaluate(prices, args.storage_cost, args.minimum_gain)
    except ValueError as error:
        parser.error(str(error))

    print(f"{args.market} / {args.variety} / {args.grade}")
    print(f"{len(prices)} observations from {prices.index[0].date()} to {prices.index[-1].date()}")
    print(f"First evaluation date: {test_start.date()}")
    print("\nForecast MAE (INR/quintal), paired with the last observed price baseline")
    print(forecasts.groupby("day").agg(
        scored=("baseline_error", "size"),
        baseline_mae=("baseline_error", "mean"),
        ridge_mae=("ridge_error", "mean"),
    ).round(2).reindex(range(1, 8)).to_string())

    waits = decisions.loc[decisions["wait"].astype(bool), "net_gain"]
    scored = decisions["net_gain"].dropna()
    print(f"\nDecision origins: {len(decisions)}. Wait signals: {len(waits)}.")
    print(f"Wait signals with observed sale price: {waits.count()}. Profitable waits: {(waits > 0).sum()}.")
    if waits.count() == 0:
        print("No wait outcomes could be evaluated.")
    if not scored.empty:
        print(f"Mean realized gain vs. selling immediately: {scored.mean():.2f} INR/quintal over {len(scored)} scored decisions.")


if __name__ == "__main__":
    main()
