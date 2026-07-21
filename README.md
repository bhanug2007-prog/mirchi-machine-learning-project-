# 🌶 MirchiMandi

Real-time Mirchi Price Intelligence for Andhra Pradesh farmers.

## Project Structure

```
mirchimandi/
├── scripts/
│   ├── 01_upload_to_supabase.py   ← Step 1: Load CSV to Supabase
│   └── 02_train_models.py         ← Step 2: Train 11 ML models
├── backend/
│   ├── main.py                    ← FastAPI backend (all API endpoints)
│   └── requirements.txt
├── frontend/
│   ├── src/App.jsx                ← React frontend (full UI)
│   └── package.json
└── csv_data/                      ← Put your agmarknet CSVs here
```

---

## Step-by-Step Setup

### Step 1 — Add your Supabase DB URL
In all 3 files, replace this line:
```python
DB_URL = "postgresql://postgres.YOUR_PROJECT:YOUR_PASSWORD@..."
```
With your real Supabase connection string from:
Supabase → Settings → Database → Connection String → URI (Transaction pooler)

---

### Step 2 — Upload CSV data to Supabase
```bash
# Put your agmarknet CSVs in ./csv_data/ folder
mkdir csv_data
# Copy your downloaded CSV here

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

### Backend → Render.com (free)
1. Push backend/ to GitHub
2. New Web Service on Render → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `DB_URL = your_supabase_url`

### Frontend → Vercel (free)
1. Push frontend/ to GitHub
2. New project on Vercel → connect repo
3. Add environment variable: `VITE_API_URL = your_render_backend_url`
4. Deploy

---

## Daily Data Update

Every morning from your laptop (Indian IP):
1. Go to agmarknet.gov.in → Daily Price Arrival Report
2. Download today's CSV for Andhra Pradesh, Dry Chillies
3. Put in csv_data/ folder
4. Run: `python scripts/01_upload_to_supabase.py`

Done. New data live on website instantly.

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
