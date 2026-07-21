"""
STEP 1: Upload your CSV data to Supabase
=========================================
Run: python 01_upload_to_supabase.py

Put all your agmarknet CSV files in: ./csv_data/ folder
This script creates the tables and loads all data.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import glob, os

DB_URL = "postgresql://postgres.akdzzsfhvcuvzpjxmscs:8pohdOKVFAZHJ0VJ@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
def get_conn():
    return psycopg2.connect(DB_URL)

# ─────────────────────────────────────────────────────
# CREATE ALL TABLES
# ─────────────────────────────────────────────────────
def create_tables():
    conn = get_conn()
    cur = conn.cursor()

    # Drop existing tables if schema changed
    cur.execute("DROP TABLE IF EXISTS mirchi_prices CASCADE;")
    cur.execute("DROP TABLE IF EXISTS user_variety_prices CASCADE;")
    cur.execute("DROP TABLE IF EXISTS ml_model_results CASCADE;")

    # Main price table — agmarknet data
    cur.execute("""
        CREATE TABLE mirchi_prices (
            id              SERIAL PRIMARY KEY,
            arrival_date    DATE NOT NULL,
            state           VARCHAR(50)  DEFAULT 'Andhra Pradesh',
            district        VARCHAR(100),
            market          VARCHAR(100) NOT NULL,
            commodity_group VARCHAR(100),
            commodity       VARCHAR(100),
            variety         VARCHAR(100) NOT NULL,
            grade           VARCHAR(50),
            min_price       FLOAT,
            max_price       FLOAT,
            modal_price     FLOAT NOT NULL,
            price_unit      VARCHAR(20)  DEFAULT 'Rs./Quintal',
            arrival_qty     FLOAT,
            arrival_unit    VARCHAR(20),
            created_at      TIMESTAMP DEFAULT NOW(),
            UNIQUE (arrival_date, market, variety, grade)
        )
    """)

    # User-submitted variety prices
    # Farmers/users can add their own variety prices that agmarknet doesn't have
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_variety_prices (
            id              SERIAL PRIMARY KEY,
            submitted_at    TIMESTAMP DEFAULT NOW(),
            arrival_date    DATE NOT NULL,
            market          VARCHAR(100) NOT NULL,
            variety         VARCHAR(100) NOT NULL,    -- user types: "Teja S17", "334", "Byadgi"
            grade           VARCHAR(50)  DEFAULT 'User Reported',
            modal_price     FLOAT NOT NULL,           -- price user reports from their broker/mandi
            min_price       FLOAT,
            max_price       FLOAT,
            arrival_qty     FLOAT,
            reporter_name   VARCHAR(100),             -- optional: "Ramu, Guntur"
            notes           TEXT,                     -- optional: "Broker offered this price"
            is_verified     BOOLEAN DEFAULT FALSE,    -- admin can verify later
            upvotes         INT DEFAULT 0,
            UNIQUE (arrival_date, market, variety, submitted_at)
        )
    """)

    # ML model results — store comparison results
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ml_model_results (
            id          SERIAL PRIMARY KEY,
            trained_at  TIMESTAMP DEFAULT NOW(),
            model_name  VARCHAR(100),
            variety     VARCHAR(100),
            mae         FLOAT,
            rmse        FLOAT,
            r2          FLOAT,
            mape        FLOAT,
            is_best     BOOLEAN DEFAULT FALSE
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ All tables created in Supabase")


# ─────────────────────────────────────────────────────
# CLEAN ONE ROW
# ─────────────────────────────────────────────────────
def clean_price(val):
    try:
        return float(str(val).replace(",", "").strip())
    except:
        return 0.0


# ─────────────────────────────────────────────────────
# LOAD ONE CSV FILE
# ─────────────────────────────────────────────────────
def load_csv(file_path):
    print(f"\n📂 Loading: {os.path.basename(file_path)}")
    
    # agmarknet CSVs have a title row at top — skip it
    df = pd.read_csv(file_path, skiprows=1)
    
    # Rename columns to standard names
    col_map = {
        'State':             'state',
        'District':          'district',
        'Market':            'market',
        'Commodity Group':   'commodity_group',
        'Commodity':         'commodity',
        'Variety':           'variety',
        'Grade':             'grade',
        'Min Price':         'min_price',
        'Max Price':         'max_price',
        'Modal Price':       'modal_price',
        'Price Unit':        'price_unit',
        'Arrival Quantity':  'arrival_qty',
        'Arrival Unit':      'arrival_unit',
        'Arrival Date':      'arrival_date',
    }
    df = df.rename(columns=col_map)
    
    # Verify required columns exist
    required = ['arrival_date', 'market', 'variety', 'modal_price']
    for col in required:
        if col not in df.columns:
            print(f"  ⚠️  Missing column: {col}")
            print(f"  Found: {list(df.columns)}")
            return 0

    # Clean data
    df = df.dropna(subset=['arrival_date', 'market', 'variety'])
    df['arrival_date'] = pd.to_datetime(df['arrival_date'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['arrival_date'])

    for col in ['min_price', 'max_price', 'modal_price', 'arrival_qty']:
        if col in df.columns:
            df[col] = df[col].apply(clean_price)

    df = df[df['modal_price'] > 0]  # remove zero prices

    print(f"  Rows to insert: {len(df)}")
    print(f"  Date range: {df['arrival_date'].min().date()} → {df['arrival_date'].max().date()}")
    print(f"  Markets: {sorted(df['market'].unique())}")
    print(f"  Varieties: {sorted(df['variety'].unique())}")

    # Batch insert into Supabase
    conn = get_conn()
    cur = conn.cursor()

    rows = []
    for _, row in df.iterrows():
        rows.append((
            row['arrival_date'].date(),
            str(row.get('state', 'Andhra Pradesh')),
            str(row.get('district', '')),
            str(row['market']),
            str(row.get('commodity_group', 'Spices')),
            str(row.get('commodity', 'Dry Chillies')),
            str(row['variety']),
            str(row.get('grade', 'FAQ')),
            float(row.get('min_price', 0)),
            float(row.get('max_price', 0)),
            float(row['modal_price']),
            str(row.get('price_unit', 'Rs./Quintal')),
            float(row.get('arrival_qty', 0)),
            str(row.get('arrival_unit', 'Metric Tonnes')),
        ))

    try:
        execute_values(cur, """
            INSERT INTO mirchi_prices
                (arrival_date, state, district, market, commodity_group, commodity,
                 variety, grade, min_price, max_price, modal_price,
                 price_unit, arrival_qty, arrival_unit)
            VALUES %s
            ON CONFLICT (arrival_date, market, variety, grade) DO NOTHING
        """, rows)
        saved = cur.rowcount
        conn.commit()
        print(f"  ✅ Saved {saved} new rows | Skipped {len(rows)-saved} duplicates")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error: {e}")
        saved = 0
    finally:
        cur.close()
        conn.close()

    return saved


# ─────────────────────────────────────────────────────
# VERIFY DATA IN SUPABASE
# ─────────────────────────────────────────────────────
def verify_data():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM mirchi_prices")
    total = cur.fetchone()[0]

    cur.execute("SELECT MIN(arrival_date), MAX(arrival_date) FROM mirchi_prices")
    dates = cur.fetchone()

    cur.execute("""
        SELECT variety, COUNT(*) as days,
               ROUND(AVG(modal_price)::numeric,0) as avg_price,
               ROUND(MIN(modal_price)::numeric,0) as min_p,
               ROUND(MAX(modal_price)::numeric,0) as max_p
        FROM mirchi_prices
        WHERE market = 'Guntur APMC'
        GROUP BY variety ORDER BY days DESC
    """)
    summary = cur.fetchall()

    cur.close()
    conn.close()

    print(f"\n{'='*55}")
    print(f"📊 SUPABASE DATABASE SUMMARY")
    print(f"{'='*55}")
    print(f"Total rows  : {total:,}")
    print(f"Date range  : {dates[0]} → {dates[1]}")
    print(f"\nGuntur APMC — Variety Summary:")
    print(f"{'Variety':<15} {'Days':>5} {'Avg ₹':>9} {'Min ₹':>9} {'Max ₹':>9}")
    print(f"{'-'*50}")
    for row in summary:
        print(f"{row[0]:<15} {row[1]:>5} {row[2]:>9,} {row[3]:>9,} {row[4]:>9,}")
    print(f"{'='*55}")


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌶  MirchiMandi — Step 1: Upload to Supabase")
    print("=" * 55)

    # 1. Create tables
    create_tables()

    # 2. Load all CSVs from ./csv_data/ folder
    csv_folder = "./csv_data"
    os.makedirs(csv_folder, exist_ok=True)

    files = glob.glob(f"{csv_folder}/*.csv") + glob.glob(f"{csv_folder}/*.CSV")

    if not files:
        print(f"\n⚠️  No CSV files found in '{csv_folder}/' folder")
        print("  → Create the folder and put your agmarknet CSVs there")
        print("  → Then run this script again")
    else:
        print(f"\nFound {len(files)} CSV file(s)")
        total = sum(load_csv(f) for f in sorted(files))
        print(f"\n🎉 Total new rows saved to Supabase: {total:,}")

    # 3. Show summary
    verify_data()
