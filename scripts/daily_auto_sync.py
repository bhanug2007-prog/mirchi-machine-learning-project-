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
from datetime import datetime, date
import os
import sys

DB_URL = os.environ.get("DB_URL")
SPREADSHEET_ID = '1dwhlEIQ_H0NcAIT-SSg1sM_ZpsT2KZNUvc2fqWI9lYU'
API_KEY = 'AIzaSyBshQgbcousVir0__rUic0Bj1Ei6XYuKrE'

def get_conn():
    return psycopg2.connect(DB_URL)

def clean_price(val):
    try:
        if not val or str(val).strip() in ['-', '—', '']:
            return None
        return float(str(val).replace(",", "").strip())
    except Exception:
        return None

def parse_date(date_str):
    for fmt in ('%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return None

def sync_variety_prices():
    print("Fetching latest prices from Guntur Mirchi Sheets API...")
    url = f"https://content-sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values:batchGet?ranges=Consolidated%20Prices&ranges=Fatki%20Table&majorDimension=ROWS&key={API_KEY}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://gunturmirchi.in/',
        'Origin': 'https://gunturmirchi.in'
    }
    
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f"[ERROR] Failed to fetch sheets data: HTTP {r.status_code}")
        return False
        
    data = r.json()
    valueRanges = data.get('valueRanges', [])
    consolidated_rows = valueRanges[0].get('values', [])
    fatki_rows = valueRanges[1].get('values', [])
    
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
    recent_rows = [consolidated_rows[0]] + consolidated_rows[-15:]
    
    for row in recent_rows[1:]:
        if not row or not row[0]:
            continue
        arrival_date = parse_date(row[0])
        if not arrival_date:
            continue
            
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
    
    recent_fatki = [fatki_rows[0]] + fatki_rows[-15:]
    for row in recent_fatki[1:]:
        if not row or not row[0]:
            continue
        arrival_date = parse_date(row[0])
        if not arrival_date:
            continue
            
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
        print("No new prices to save today.")
        return True
        
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
        print(f"[OK] Successfully synched {len(records)} variety records in Supabase.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database sync failed: {e}")
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
