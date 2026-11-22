# MirchiMandi

MirchiMandi helps Andhra Pradesh chilli farmers decide where and when to sell. The English and Telugu web app combines reported market prices, seven-day forecasts, and cost estimates to compare what farmers could take home from a broker sale, a sale at the Guntur market, or waiting to sell.

**[Live Demo](https://mirchimandi.onrender.com/)** · **[Application Source](https://github.com/bhanug2007-prog/mirchi-machine-learning-project-/tree/render-deploy)**

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Proposed Solution](#proposed-solution)
- [Key Features and User Roles](#key-features-and-user-roles)
- [Demonstration Flow](#demonstration-flow)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Machine Learning: Price Forecasting and Model Selection](#machine-learning-price-forecasting-and-model-selection)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Validation and Testing](#validation-and-testing)
- [Deployment Notes](#deployment-notes)
- [Known Limitations and Roadmap](#known-limitations-and-roadmap)

## Project Overview

I grew up in an agricultural family in Andhra Pradesh and watched my father and neighboring farmers weigh the same choices after each harvest. I built MirchiMandi to make those choices easier to compare using dated quotes and a farmer's actual harvest quantity.

## Problem Statement

A farmer with 50 quintals of chilli can accept a local broker's offer, pay to transport the crop to the Guntur market, or pay for cold storage and wait. A higher market quote can yield lower proceeds once freight and handling fees are deducted. Waiting adds storage costs and leaves the farmer exposed to price changes. Farmers need a way to compare the three options on the same basis before deciding.

## Proposed Solution

MirchiMandi converts prices per quintal into estimated proceeds for the farmer's harvest quantity. It shows the reported price date, lists the costs applied, and distinguishes observed market quotes from forecasts.

| Selling option | Calculation |
| --- | --- |
| Sell to a broker | Broker offer × harvest quantity, less any costs entered for that sale |
| Sell at the Guntur market | Latest reported market price × quantity, less estimated freight and handling fees |
| Wait and sell at the market | Forecast price × quantity, less estimated storage, freight, and handling fees |

## Key Features and User Roles

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

Visitors can view prices, forecasts, and guidance. Signed-in farmers can save harvest lots and receive target-price alerts. Contributors can submit quotes, and administrators review flagged submissions.

## Demonstration Flow

Open the dashboard, select a variety, and check the reported date on the latest quote. Use the calculator or ask the Market Assistant a question:

> I have 60 quintals of Teja S17 chilli in Inkollu. A broker is offering ₹16,000 per quintal. Should I sell to him, take it to Guntur mandi, or wait seven days?

The broker offer totals ₹9,60,000 before any farmer-supplied costs. The assistant uses dated quotes and forecasts to estimate the other options and itemizes transport and storage. If evidence is missing or stale, it labels the affected comparison accordingly. The free Render configuration can use rule-based parsing with the app's market tools.

## Architecture

1. **Ingest market data.** Python scripts load the Guntur Mirchi Sheets feed and AGMARKNET reports into PostgreSQL. A populated DuckDB snapshot supports local historical reads.
2. **Serve prices and estimates.** FastAPI exposes market quotes, forecasts, transport estimates, and evaluation results. Shared Python calculations power the dashboard and the LangGraph Market Assistant.
3. **Present the decision.** The React dashboard displays dated prices, estimated net proceeds, and available forecast intervals in English and Telugu. Farmer inventory uses PostgreSQL in production or SQLite in local mode.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic, LangGraph |
| Storage | PostgreSQL on Supabase, DuckDB, SQLite |
| Machine learning and data | scikit-learn, XGBoost, LightGBM, PyTorch, pandas, NumPy |
| Deployment and testing | Docker, Render, pytest |

## Machine Learning: Price Forecasting and Model Selection

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

Last price had the lowest MAE at all seven horizons for this series. The application uses this baseline for the matching market, variety, and grade. The interval target is 80%. Coverage above is historical and sample sizes are small. The day-one interval had zero width because the calibration residuals were concentrated at zero. Future prices can still move.

### Historical selling decisions

The timing simulation compared three rules on 22 common scorable dates, using ₹30 per quintal per day in storage costs and a ₹200 per quintal minimum projected gain for the selective rule.

| Strategy | Average realized gain vs. immediate sale (₹/quintal) | Combined simulated gain across dates (50 quintals per date) |
| --- | ---: | ---: |
| Sell immediately | 0.00 | ₹0 |
| Always wait seven days | −228.18 | −₹2,51,000 |
| Selective recursive Lasso rule | +32.27 | +₹35,500 |

These are historical simulations. The selective rule used a refitted recursive Lasso candidate, while the calibrated Red New forecast uses the last-price baseline. The weather and arrivals experiment also found that last price had the lowest MAE across all seven horizons for both Red New and Red. The added signals remain experimental.

## Project Structure

| Path | Contents |
| --- | --- |
| `backend/` | FastAPI routes, Market Assistant, farmer portfolio, and agricultural guidance |
| `frontend/` | React dashboard and project views |
| `scripts/` | Ingestion, training, data audit, and backtests |
| `csv_data/` | Historical market reports and the weather archive snapshot |
| `saved_models/` | Model artifacts, calibration data, and evaluation results |
| `tests/` | Regression and integration checks |

## Getting Started

Use Python 3.11 and Node.js 22 to match the deployment. The latest app and its setup files are on `render-deploy`.

```bash
git clone --branch render-deploy https://github.com/bhanug2007-prog/mirchi-machine-learning-project-.git
cd mirchi-machine-learning-project-
python -m venv .venv
# Activate .venv, then install the backend dependencies.
python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r backend/requirements.txt
```

Set `DB_URL` for a populated PostgreSQL database, or provide a populated `backend/mirchimandi.duckdb` snapshot. The local DuckDB file is ignored by Git. See the [data setup and synchronization instructions](https://github.com/bhanug2007-prog/mirchi-machine-learning-project-/blob/render-deploy/README.md#step-by-step-setup).

Start the backend with `python -m uvicorn backend.main:app --reload --port 8000`. Set `ASSISTANT_RULE_MODE=1` in the backend environment for keyless parsing. In a separate terminal, run the frontend from the project root.

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

**[Local dashboard](http://localhost:5173/)** · **[Local API docs](http://localhost:8000/docs)**

## Validation and Testing

From the project root, install `pytest` and `httpx` in the development environment before running the test suite.

```bash
python scripts/backtest.py --variety "Red New"
python scripts/backtest.py --verify-no-leakage
python scripts/market_signals.py
python scripts/market_signals.py --variety Red
python -m pytest tests -q
npm --prefix frontend run build
```

The leakage check mutates future price and arrival records and checks that the tested cutoff's outputs stay unchanged.

## Deployment Notes

The [`render-deploy` branch](https://github.com/bhanug2007-prog/mirchi-machine-learning-project-/tree/render-deploy) contains the application and Render configuration. FastAPI runs in Docker and reads production prices from Supabase PostgreSQL through the server-side `DB_URL`. The Blueprint also supports hosting the React frontend as a separate static site. The free Market Assistant can use rule-based parsing with the same market and calculation tools.

## Known Limitations and Roadmap

- **Market freshness.** Today’s label requires a quote dated today in India. Markets can close or publish late. Varieties outside the Guntur Sheets feed depend on a recent AGMARKNET import.
- **Costs.** Transport uses distance and vehicle-rate estimates rather than carrier quotes. The base sell-or-wait rule uses ₹30/quintal/day for storage, while portfolio lots accept a custom rate.
- **Guidance scope.** The library covers general eNAM and dried chilli guidance. Local yard requirements and cultivar-specific storage settings need separate verification.
- **Free hosting.** The API can sleep when idle, so market data may take longer on the first visit.

Potential next steps are broader market coverage and voice input in Telugu.
