"""
daily_auto_sync.py
==================
Automated daily synchronization script. Runs lightweight fetches from:
1. Guntur Mirchi Google Sheets API (Variety specific prices: Teja, 334 Sannam, Byadgi...)
2. (Optional) Agmarknet direct API if available.

This script updates the Supabase tables in under 3 seconds without requiring Selenium/Chrome.
Can be triggered from a server cron job or backend admin panel.
"""

import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta, timezone
from math import isfinite
import os
import sys

DB_URL = os.environ.get("DB_URL")
SPREADSHEET_ID = '1dwhlEIQ_H0NcAIT-SSg1sM_ZpsT2KZNUvc2fqWI9lYU'
API_KEY = 'AIzaSyBshQgbcousVir0__rUic0Bj1Ei6XYuKrE'

def get_conn():
    return psycopg2.connect(DB_URL, connect_timeout=8)

def clean_price(val):
    try:
        if not val or str(val).strip() in ['-', '—', '']:
            return None
        price = float(str(val).replace(",", "").strip())
        return price if isfinite(price) and price > 0 else None
    except (TypeError, ValueError):
        return None

def parse_date(date_str):
    for fmt in ('%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return None


def recent_dated_rows(rows, today, limit=15):
    dated = []
    for row in rows:
        day = parse_date(str(row[0]).strip()) if row else None
        if day is not None and day <= today:
            dated.append((day, row))
    return sorted(dated, key=lambda item: item[0])[-limit:]

def sync_variety_prices():
    print("Fetching latest prices from Guntur Mirchi Sheets API...")
    url = f"https://content-sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values:batchGet?ranges=Consolidated%20Prices&ranges=Fatki%20Table&majorDimension=ROWS&key={API_KEY}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://gunturmirchi.in/',
        'Origin': 'https://gunturmirchi.in'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
    except requests.RequestException as error:
        print(f"[ERROR] Price feed request failed ({type(error).__name__}).")
        return False
    if r.status_code != 200:
        print(f"[ERROR] Failed to fetch sheets data: HTTP {r.status_code}")
        return False
        
    data = r.json()
    ranges = {item["range"].split("!", 1)[0].strip("'"): item.get("values", [])
              for item in data.get("valueRanges", [])}
    consolidated_rows = ranges.get("Consolidated Prices", [])
    fatki_rows = ranges.get("Fatki Table", [])
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    
    records = []
    
    # Mappings for consolidated prices
    consolidated_map = {
        1: ("Teja S17", "Medium"),
        2: ("Teja S17", "Med Best"),
        3: ("Teja S17", "Best"),
        4: ("Teja S17", "Deluxe"),
        5: ("334 Sannam", "Medium"),
        6: ("334 Sannam", "Med Best"),
        7: ("334 Sannam", "Best"),
        8: ("334 Sannam", "Deluxe"),
        9: ("Byadgi", "Medium"),
        10: ("Byadgi", "Med Best"),
        11: ("Byadgi", "Best"),
        12: ("Byadgi", "Deluxe"),
        13: ("341", "Medium"),
        14: ("341", "Med Best"),
        15: ("341", "Best"),
        16: ("341", "Deluxe"),
        17: ("DD Deluxe", "Medium"),
        18: ("DD Deluxe", "Med Best"),
        19: ("DD Deluxe", "Best"),
        20: ("DD Deluxe", "Deluxe"),
        21: ("Armoor", "Medium"),
        22: ("Armoor", "Med Best"),
        23: ("Armoor", "Best"),
        24: ("Armoor", "Deluxe"),
    }
    
    # We only take the last 15 rows for the daily update to keep it lightweight,
    # but still cover weekends, holidays, and past week updates.
    for arrival_date, row in recent_dated_rows(consolidated_rows, today):
            
        for col_idx, (variety, grade) in consolidated_map.items():
            if col_idx < len(row):
                price = clean_price(row[col_idx])
                if price is not None and price > 0:
                    records.append((
                        arrival_date, "Andhra Pradesh", "Guntur", "Guntur APMC",
                        "Spices", "Dry Chillies", variety, grade,
                        price, price, price, "Rs./Quintal", None, "Metric Tonnes"
                    ))
                    
    # Mappings for fatki
    fatki_map = {
        1: ("Teja Fatki", "Medium"),
        2: ("Teja Fatki", "Best"),
        3: ("334 Fatki", "Medium"),
        4: ("334 Fatki", "Best"),
        5: ("Seed Variety Fatki", "Medium"),
        6: ("Seed Variety Fatki", "Best")
    }
    
    for arrival_date, row in recent_dated_rows(fatki_rows, today):
            
        for col_idx, (variety, grade) in fatki_map.items():
            if col_idx < len(row):
                price = clean_price(row[col_idx])
                if price is not None and price > 0:
                    records.append((
                        arrival_date, "Andhra Pradesh", "Guntur", "Guntur APMC",
                        "Spices", "Dry Chillies", variety, grade,
                        price, price, price, "Rs./Quintal", None, "Metric Tonnes"
                    ))
                    
    if not records:
        print("[ERROR] The feed returned no usable dated quotes.")
        return False

    # Revisions can repeat a date and grade within a batch.
    records = list({(row[0], row[3], row[6], row[7]): row for row in records}.values())
        
    print(f"Uploading {len(records)} daily sync records to Supabase...")
    conn = get_conn()
    cur = conn.cursor()
    
    query = """
        INSERT INTO mirchi_prices
            (arrival_date, state, district, market, commodity_group, commodity,
             variety, grade, min_price, max_price, modal_price,
             price_unit, arrival_qty, arrival_unit)
        VALUES %s
        ON CONFLICT (arrival_date, market, variety, grade) DO UPDATE
        SET modal_price = EXCLUDED.modal_price,
            min_price = EXCLUDED.min_price,
            max_price = EXCLUDED.max_price
    """
    
    try:
        execute_values(cur, query, records)
        conn.commit()
        latest = max(row[0] for row in records)
        print(f"[OK] Synced {len(records)} variety records. Latest upstream quote date: {latest}.")
        return True
    except psycopg2.Error:
        conn.rollback()
        print("[ERROR] Database rejected the price sync.")
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print(f"Daily sync triggered at {datetime.now().isoformat()}")
    success = sync_variety_prices()
    if success:
        print("Daily sync completed successfully!")
    else:
        print("Daily sync completed with errors.")
        sys.exit(1)
