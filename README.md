# 🌶 MirchiMandi

Real-time Mirchi Price Intelligence for Andhra Pradesh farmers.

**Live demo:** [MirchiMandi on Render](https://mirchimandi.onrender.com/)

## Project Structure

```
mirchimandi/
├── scripts/
│   ├── 01_sync_google_sheets.py   ← Step 1: Sync historical data from Google Sheet API
│   ├── 02_train_models.py         ← Step 2: Train 11 ML models
│   ├── daily_auto_sync.py         ← Daily automation script
│   └── 01_upload_to_supabase.py   ← (Optional) Upload manual agmarknet CSVs to Supabase
├── backend/
│   ├── main.py                    ← FastAPI backend (all API endpoints)
│   └── requirements.txt
├── frontend/
│   ├── src/App.jsx                ← React frontend (full UI)
│   └── package.json
└── csv_data/                      ← (Optional) Put fallback agmarknet CSVs here
```

---

## Step-by-Step Setup

### Step 1 — Add your Supabase DB URL
Set `DB_URL` in your shell before running the API, data sync, or training scripts. For example, in PowerShell:
```powershell
$env:DB_URL = "<Supabase connection URI>"
```
With your real Supabase connection string from:
Supabase → Settings → Database → Connection String → URI (Transaction pooler)

---

### Step 2 — Ingest prices to Supabase

The primary data source is Guntur Mirchi's price tracking spreadsheet. We use an automated Google Sheets API scraper to fetch both historical and daily prices for real AP varieties (Teja S17, 334 Sannam, Byadgi, 341, DD Deluxe, and Armoor).

Run the Google Sheets synchronization script to fetch and populate your Supabase database:
```bash
pip install requests psycopg2-binary
python scripts/01_sync_google_sheets.py
```

*(Optional Fallback)*: If you want to load manual CSV reports downloaded from agmarknet.gov.in:
```bash
mkdir csv_data
# Copy your downloaded CSV files into ./csv_data/
pip install pandas psycopg2-binary
python scripts/01_upload_to_supabase.py
```

---

### Step 3 — Train all ML models
```bash
pip install scikit-learn xgboost lightgbm joblib numpy
python scripts/02_train_models.py
```

This trains 11 models and shows a comparison table:
- Linear Regression (baseline)
- Ridge Regression
- Lasso Regression
- Decision Tree
- KNN
- SVR
- Random Forest
- Extra Trees
- Gradient Boosting
- **XGBoost** (usually best)
- **LightGBM** (usually best)

Best model is saved automatically.

### Offline forecasting benchmark

Run from the project root with pandas and scikit-learn installed. The benchmark reads local AGMARKNET CSVs and requires no database connection.

```bash
python scripts/backtest.py
python scripts/backtest.py --variety Red
```

The script evaluates Guntur APMC dry chilli modal prices (FAQ grade by default). It uses the final 30% of eligible observation dates as forecast origins. At each origin it refits a separate Ridge model for each of the next seven calendar days using only prices available by that date. Each horizon reports mean absolute error in rupees per quintal for Ridge and a last-observed-price baseline on the same dates.

The sell-or-wait simulation uses ₹30 per quintal per calendar day for storage and recommends waiting if the expected gain exceeds ₹200 per quintal. Both inputs can be changed with `--storage-cost` and `--minimum-gain`. The report compares scored decisions with selling immediately and counts wait signals without an observed sale price separately. The benchmark evaluates a separate Ridge candidate. The live API serves the existing forecasting system.

On the bundled reports, each variety has 141 observations from November 2025 through July 2026. The last-price baseline had lower MAE at all seven horizons for both varieties. Selected results are below (₹/quintal).

| Variety | Horizon | Scored dates | Last price MAE | Ridge MAE |
|---|---:|---:|---:|---:|
| Red New | 1 day | 31 | 38.71 | 92.62 |
| Red New | 7 days | 30 | 213.33 | 271.82 |
| Red | 1 day | 31 | 64.52 | 105.19 |
| Red | 7 days | 30 | 250.00 | 345.86 |

The simulation issued one wait signal for Red New, whose target date lacked a reported price, and no wait signals for Red. These runs provide zero scored wait outcomes.

---

### Step 4 — Run the backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Test: http://localhost:8000/api/price/today?market=Guntur%20APMC&variety=Red%20New

---

### Step 5 — Run the frontend
```bash
cd frontend
npm install
# Create .env file:
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

Open: http://localhost:5173

---

## API Endpoints

| Endpoint | Description |
|---|---|
| GET /api/price/today | Today's price by market + variety |
| GET /api/price/history | Historical price chart data |
| GET /api/forecast | 7-day ML price forecast |
| GET /api/recommendation | Sell now or wait? + total gain |
| GET /api/calculator | Broker vs mandi profit calculator |
| GET /api/varieties/today | All varieties' prices today |
| GET /api/markets/compare | Compare all AP markets |
| GET /api/models/comparison | ML model accuracy table |
| POST /api/user/submit-price | User submits Teja/334 price |
| GET /api/user/varieties | Get user-submitted variety prices |

---

## Deployment

### Render

The repository-root `render.yaml` defines one Docker web service. FastAPI serves both the built React frontend and `/api`, so the production build uses relative API URLs.

1. Rotate the previously committed Supabase password and obtain the new pooler connection URI. Populate Supabase with the existing sync script if needed.
2. Push the project files and connect the repository in **Render → New → Blueprint**.
3. Enter the new URI for `DB_URL` in Render. The Blueprint generates `ADMIN_PASSCODE`, which you can retrieve from the service's Environment page to use in the admin UI.
4. After the deploy finishes, open the generated URL and check `/api/health` for the latest database date. Open the market dashboard and verify a price lookup and a forecast before sharing the URL.

---

## Daily Data Update

Instead of manually downloading CSV files every day, the project uses a highly efficient scraper that queries the Guntur Mirchi Google Sheets API directly:

1. **Run the Automated Sync Script:**
   ```bash
   python scripts/daily_auto_sync.py
   ```
2. **Details:**
   - Updates all variety-specific tables in under 3 seconds.
   - Requires no browser, Selenium, or proxy setup.
   - Can easily be set up on a server cron job or triggered from a backend administrative interface.

---

## User-Submitted Varieties Feature

Farmers/users can submit prices for varieties not in agmarknet
(Teja S17, 334 Sannam, Byadgi, etc.) via the "Submit Price" tab.

These appear in the app with an "User Reported" badge.
As more users submit, the data becomes richer over time.

---

## Varieties in agmarknet

| agmarknet Name | What it means |
|---|---|
| Red New | Fresh season premium (Teja/334 grade) |
| Red | Standard red mirchi |
| Red Top | Top grade red |
| Guntur | Local Guntur variety |
| White | Dried white chilli |
| Local | Mixed local variety |

---

Built with ❤️ for AP farmers · Data: agmarknet.gov.in
