# MirchiMandi

MirchiMandi helps Andhra Pradesh chilli farmers compare where and when to sell their harvest. It combines mandi price data, machine learning forecasts, and an English and Telugu dashboard that calculates the proceeds farmers could take home.

**[Live demo on Render](https://mirchimandi.onrender.com/)** · **[Latest application source](https://github.com/bhanug2007-prog/mirchi-machine-learning-project-/tree/render-deploy)**

Growing up in an agricultural family in Andhra Pradesh, I watched my father and neighboring farmers confront a stressful decision after every harvest. A farmer with 50 quintals of red chilli can take a village broker's offer, pay to transport the crop to a mandi, or pay for cold storage and wait. Seeing their hard work undercut by unclear prices, transport risks, and unexpected storage fees inspired me to build MirchiMandi.

## What the app does

| Feature | What you can do |
| --- | --- |
| Market prices | Find the latest reported price for a variety, check its date, and explore historical trends. |
| Sell-or-wait comparison | Compare a broker's offer with mandi proceeds after estimated freight and Hamali fees, then account for storage if you wait. |
| Market Assistant | Ask a question in English or Telugu. A LangGraph workflow extracts the details, asks for missing inputs, and uses the same price, forecast, and transport tools as the dashboard. |
| Forecast uncertainty | Inspect seven-calendar-day estimates and calibrated prediction intervals where a matching evaluation is available. |
| My Inventory | Save private harvest lots, calculate accumulated storage costs, and receive in-app alerts when a recent observed quote reaches your target. |
| Agricultural Guidance | Find cited English or Telugu guidance on eNAM registration, payments, and dried chilli handling. |
| Weather and arrivals | Compare price-only models with models that use lagged arrivals or archive weather under the same historical evaluation. |
| Community reporting | Submit local prices. Unusual quotes are flagged for moderator review before they can enter verified aggregates. |

### Try this in the Market Assistant

> I have 60 quintals of Teja S17 chilli in Inkollu. A broker is offering ₹16,000 per quintal. Should I sell to him, take it to Guntur mandi, or wait seven days?

The broker offer totals ₹9,60,000 before any farmer-supplied costs. The assistant uses dated quotes and forecasts to estimate the other options and itemizes transport and storage. If evidence is missing or stale, it labels the affected comparison accordingly. The free Render configuration can use rule-based parsing with the app's market tools.

## Architecture

- **Data:** Guntur Mirchi Google Sheets for variety-level updates, AGMARKNET reports for historical mandi data, and Open-Meteo ERA5 for the weather experiment.
- **Backend:** FastAPI, Pydantic, LangGraph, and Python functions for financial calculations. Production connects to PostgreSQL through Supabase. Local price lookups can use a populated DuckDB snapshot, with SQLite for local portfolio accounts and inventory.
- **ML:** scikit-learn, XGBoost, LightGBM, PyTorch, pandas, and NumPy.
- **Frontend:** React, Vite, and Tailwind CSS, with English and Telugu support.
- **Deployment:** Docker and Render. The deployment configuration also supports a separate static frontend so the landing page can load independently of a cold API.

## Forecasting and evaluation

The saved benchmark contains **120 model–variety evaluations** across 12 regression architectures and 10 chilli varieties. Saved one-step holdout MAE includes Teja S17 Lasso at ₹158.41/quintal, Red XGBoost at ₹466.71/quintal, and Red New Lasso at ₹661.32/quintal. These are from a separate evaluation from the rolling, multi-horizon results below.

### Seven-day forecast for Guntur APMC Red New, FAQ grade

The chronological experiment used 70 quote dates for model selection, 35 for interval calibration, and 36 for holdout evaluation. Each horizon was scored only when an actual quote existed on its target date.

| Calendar-day horizon | Scored dates | Last-price MAE (₹/quintal) | Recursive Lasso MAE (₹/quintal) | Observed interval coverage |
| --- | ---: | ---: | ---: | ---: |
| 1 | 28 | 42.86 | 232.12 | 89.3% |
| 2 | 20 | 60.00 | 373.48 | 100% |
| 3 | 16 | 125.00 | 469.80 | 100% |
| 4 | 14 | 221.43 | 734.81 | 100% |
| 5 | 16 | 212.50 | 814.65 | 100% |
| 6 | 22 | 222.73 | 856.93 | 100% |
| 7 | 24 | 245.83 | 1,044.00 | 100% |

Last price had the lowest MAE at all seven horizons for this series. The API uses this baseline when the market, variety, and grade match the calibration. The interval target is 80%. Coverage above is historical and sample sizes are small. The day-one margin was zero in this calibration, so it shows how concentrated those residuals were. Future prices can still move.

### Historical selling decisions

The timing simulation compared three rules on 22 common scorable dates, using ₹30 per quintal per day in storage costs and a ₹200 per quintal minimum projected gain for the selective rule.

| Strategy | Average realized gain vs. immediate sale (₹/quintal) | Combined simulated gain across dates (50 quintals per date) |
| --- | ---: | ---: |
| Sell immediately | 0.00 | ₹0 |
| Always wait seven days | −228.18 | −₹2,51,000 |
| Selective recursive Lasso rule | +32.27 | +₹35,500 |

These are historical simulations. The selective rule used a refitted recursive Lasso candidate, while the calibrated Red New forecast uses the last-price baseline. The weather and arrivals experiment also found that last price had the lowest MAE across all seven horizons for both Red New and Red. The added signals remain experimental.

## Run locally

Use Python 3.11 and Node.js 22 to match the deployment. The latest app and its setup files are on `render-deploy`.

```bash
git clone --branch render-deploy https://github.com/bhanug2007-prog/mirchi-machine-learning-project-.git
cd mirchi-machine-learning-project-
python -m venv .venv
# Activate .venv, then install the backend dependencies.
python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r backend/requirements.txt
```

Set `DB_URL` for a populated PostgreSQL database, or provide a populated `backend/mirchimandi.duckdb` snapshot. The local DuckDB file is ignored by Git. The deployment branch README documents the data setup and synchronization scripts.

Start the backend with `python -m uvicorn backend.main:app --reload --port 8000`. Set `ASSISTANT_RULE_MODE=1` in the backend environment for keyless parsing. In a separate terminal, run the frontend from the project root.

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

**[Local dashboard](http://localhost:5173/)** · **[Local API docs](http://localhost:8000/docs)**

## Reproduce the analysis

From the project root, install `pytest` and `httpx` in the development environment before running the test suite.

```bash
python scripts/backtest.py --variety "Red New"
python scripts/backtest.py --verify-no-leakage
python scripts/market_signals.py
python scripts/market_signals.py --variety Red
python -m pytest tests -q
npm --prefix frontend run build
```

The leakage check mutates future price and arrival records and checks that the tested cutoff's outputs stay unchanged. Forecast and calibration artifacts live in `saved_models/`. The backend modules are under `backend/`, the dashboard is under `frontend/`, and the evaluation and ingestion entry points are under `scripts/`.

## Limitations

- **Market freshness.** Today’s label requires a quote dated today in India. Markets can close or publish late. Varieties outside the Guntur Sheets feed depend on a recent AGMARKNET import.
- **Costs.** Transport uses distance and vehicle-rate estimates rather than carrier quotes. The base sell-or-wait rule uses ₹30/quintal/day for storage, while portfolio lots accept a custom rate.
- **Guidance scope.** The library covers general eNAM and dried chilli guidance. Local yard requirements and cultivar-specific storage settings need separate verification.
- **Free hosting.** The API can sleep when idle, so market data may take longer on the first visit.
