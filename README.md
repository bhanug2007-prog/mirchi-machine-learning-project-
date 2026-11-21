# MirchiMandi

**A full-stack machine learning project that helps Andhra Pradesh chilli farmers compare where and when to sell their harvest**

**Live demo:** [MirchiMandi on Render](https://mirchimandi.onrender.com/)

A farmer with 50 quintals of red chilli can take a village broker's offer, pay to transport the crop to a mandi, or pay for cold storage and sell later. The highest quoted price may leave the farmer with less money once those costs are included.

I built MirchiMandi to make that comparison concrete. A Python pipeline imports variety-level price records from a Guntur Mirchi spreadsheet and AGMARKNET reports into PostgreSQL. I compared 12 regression models on a chronological holdout and saved the best-performing model by mean absolute error for each trained variety. FastAPI serves the latest recorded prices and seven-day estimates to an English and Telugu React dashboard, where farmers can compare **broker proceeds with mandi proceeds after transport** and **potential gains from waiting after storage costs**.

**Project status:** The repository contains a React frontend, a FastAPI backend, ingestion and training scripts, Andhra Pradesh price reports, and saved model artifacts. Field adoption has not been verified.

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

The project connects agricultural data ingestion and machine learning to a decision a farmer can make after harvest. The pipeline collects variety-level prices, stores them in PostgreSQL, compares forecasting models, and serves prices and estimates through a dashboard. The calculator translates per-quintal quotes into estimated totals for the farmer's actual quantity.

## Problem Statement

A small farmer might harvest around 50 quintals of mirchi from a two-acre plot. A village broker can buy the crop locally, but the offer may be below the price quoted at a larger market such as Guntur. Selling at the mandi adds a transport cost. A nearby cold store gives the farmer more time, but each day of storage adds a charge and the future selling price is uncertain.

A higher mandi quote can still leave the farmer with less money after transport. Similarly, a forecast price increase may be too small to cover storage. The farmer needs a way to compare those costs against the price difference for the whole harvest.

## Proposed Solution

| Decision | What MirchiMandi calculates |
| --- | --- |
| Sell to the local broker | Broker offer per quintal multiplied by the quantity. |
| Transport to the mandi | Estimated mandi proceeds after transport, compared with the broker offer. |
| Store and wait | Estimated change in sale proceeds over the forecast horizon after the app's daily storage charge. |

The broker-versus-mandi calculator and the storage recommendation are separate tools. Together they let the farmer compare the immediate options and assess whether waiting could cover its own cost.

## Key Features and User Roles

| Role | What you can do |
| --- | --- |
| **Farmer or dashboard visitor** | Select a market and variety, view the latest recorded quote and price history, compare markets, inspect a seven-day forecast, and estimate the effect of transport or storage. Switch between English and Telugu. |
| **Community contributor** | Submit a local variety price and upvote reports. Community prices are a separate source from ingested market records. |
| **Administrator** | Use the passcode-protected dashboard to review, verify, or remove submissions and trigger a price sync. |

The price and model views include varieties such as Teja S17, 334 Sannam, Byadgi, 341, DD Deluxe, and Armoor, depending on available data. The dashboard also shows recorded model comparison metrics for supported varieties.

## Demonstration Flow

1. Open the dashboard and select **Guntur APMC** and a variety with price records, such as **Teja S17**.
2. Read the latest quote and its date, then open the history and seven-day forecast.
3. Enter **50 quintals**, a sample broker quote, the origin and destination, and a vehicle type. Compare the estimated mandi proceeds after transport with the broker proceeds.
4. Check the sell-or-wait recommendation for the same quantity. Read the estimated price gain and storage cost behind the recommendation.
5. Explore the community price form or the model comparison view to see how price reports and forecasting results are presented.

## Architecture

```mermaid
flowchart LR
    Sheet["Guntur Mirchi price spreadsheet"] --> Sync["Python Sheets sync"]
    CSV["AGMARKNET price and arrival CSVs"] --> Import["CSV import"]
    Sync --> DB[("Supabase PostgreSQL")]
    Import --> DB
    DB --> Train["Feature engineering and model comparison"]
    Train --> Models["Saved models, feature lists and metrics"]
    Models --> API["FastAPI"]
    DB <--> API
    API --> Costs["Transport and storage estimates"]
    API <--> UI["React dashboard · English and Telugu"]
```

The backend reads price records and saved model artifacts, builds forecasts, and applies cost rules. The frontend displays the results and sends calculator inputs and community submissions through the API.

## Technology Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | React, Vite, Tailwind CSS | Bilingual dashboard, forecast views, calculators, and admin screens |
| API and persistence | FastAPI, Uvicorn, psycopg2, Supabase PostgreSQL | Price queries, forecasts, recommendations, and moderation |
| Data processing | Python, Requests, pandas, NumPy | Spreadsheet synchronization, CSV ingestion, and feature engineering |
| Machine learning | scikit-learn, XGBoost, LightGBM, PyTorch, joblib | Regression experiments, model selection, and saved inference artifacts |
| Location lookup | OpenStreetMap Nominatim and a distance fallback | Estimates used by the transport calculator |

## Machine Learning: Price Forecasting and Model Selection

### What ML predicts and why it matters

The model predicts **red-chilli prices in rupees per quintal** from historical market data. Today's quote is enough to compare a broker offer with a mandi sale after transport. Deciding whether to **pay for storage and sell later** requires an estimate of future prices. That is where ML helps.

### How I built and evaluated the models

1. **Collect the price history.** Import variety-level prices from a Guntur Mirchi spreadsheet and AGMARKNET price and arrival reports into PostgreSQL.
2. **Build features from past observations.** Use lagged prices, rolling price statistics, recent price changes, calendar features, and lagged market arrivals where available.
3. **Compare 12 regressors on later dates.** Train on the earliest 80% of observations and evaluate on the final 20% without shuffling. Candidates include Linear Regression, Ridge, Lasso, Decision Tree, KNN, SVR, Random Forest, Extra Trees, Gradient Boosting, XGBoost, LightGBM, and a PyTorch multilayer perceptron (MLP).
4. **Select by variety.** Save the model with the lowest mean absolute error (MAE) for each trained variety, along with its feature list and evaluation metadata. The saved results also include RMSE, R², and MAPE.

| Variety | Selected model in the saved run | Holdout MAE |
| --- | --- | --- |
| Teja S17 | Lasso Regression | ₹158.41 per quintal |
| Red | XGBoost | ₹466.71 per quintal |

The selected model varied by chilli variety. The PyTorch MLP was evaluated alongside the classical models. These results describe the historical holdout used for model selection and do not establish seven-day forecast accuracy. [Training code](scripts/02_train_models.py) · [Teja S17 results](saved_models/meta_Teja_S17.json) · [Red results](saved_models/meta_Red.json)

### How the forecast becomes a recommendation

FastAPI loads the model for the selected variety and serves a **seven-day price forecast** to the English and Telugu React dashboard. It can use a moving average when a trained model is unavailable and price history is available. The sell-or-wait calculation subtracts storage costs from the projected change in sale proceeds.

For example, a projected rise of **₹100 per quintal after four days** would fall short of the app's assumed **₹120 per quintal storage cost** for those four days. For **50 quintals**, waiting would leave the farmer an estimated **₹1,000 worse off** than selling at the current price. The forecast supplies the future price estimate, and the cost calculation explains the recommendation.

## Project Structure

```text
backend/                    FastAPI endpoints and Python requirements
frontend/                   React dashboard, Vite config, and npm lockfile
csv_data/                   Andhra Pradesh market price and arrival reports
saved_models/               Model artifacts, feature lists, and evaluation metadata
scripts/                    Sheets sync, CSV import, model training, and daily sync
scratch/check_predictions.py  Local forecast diagnostic
```

## Getting Started

1. Clone the repository and create an isolated Python environment. Install the [backend requirements](backend/requirements.txt). If you plan to rerun ingestion and training, install Requests and PyTorch in that environment as well.
2. Configure a PostgreSQL database you control. The current backend and ingestion and training scripts read a `DB_URL` constant in source. Configure a local working copy with your own connection settings and keep credentials out of Git.
3. From the repository root, run [the CSV importer](scripts/01_upload_to_supabase.py) to initialize and populate the market tables with the included reports. Run [the Sheets sync](scripts/01_sync_google_sheets.py) to add spreadsheet prices if the source is reachable. To retrain, run `python scripts/02_train_models.py` from the root.
4. From `backend/`, start the API with `uvicorn main:app --reload --port 8000`. Open [Swagger UI](http://localhost:8000/docs) to inspect the endpoints. Starting from this directory lets the backend locate `../saved_models`.
5. In a separate terminal, open `frontend/`, run `npm ci`, and start it with `npm run dev`. Set `VITE_API_URL=http://localhost:8000` in `frontend/.env` if you want to configure the endpoint explicitly. Open [the local dashboard](http://localhost:5173).

## Validation and Testing

Reproduce the model comparison with the [training script](scripts/02_train_models.py) and inspect the [saved model metadata](saved_models/). Use the [forecast diagnostic](scratch/check_predictions.py) or the API docs to check price history and inference. For a manual end-to-end check, compare a broker quote with the mandi estimate, then increase the transport cost or change the vehicle to see how the estimated advantage changes. An automated end-to-end suite and a field trial are not documented in this repository.

## Deployment Notes

The intended split is a Vite frontend on Vercel, FastAPI on Render, and PostgreSQL on Supabase. The frontend needs the deployed API URL in `VITE_API_URL`. The backend needs access to its database and saved model artifacts. Move inline database credentials and admin settings to server-side environment variables before publishing a service. The daily sync script requires an external scheduler to run automatically.

## Known Limitations and Roadmap

- Market prices are only as current as the source records and the last successful sync. Check the quote date before using an estimate.
- Transport costs are estimates. The wait recommendation uses a fixed storage assumption of ₹30 per quintal per day. Actual transport quotes, storage fees, and market terms can change the comparison.
- The next steps are to make storage fees configurable, show data freshness more clearly, evaluate forecasts across different dates and markets, and deploy a first pilot for feedback from farmers.
