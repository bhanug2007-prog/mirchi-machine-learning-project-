"""
01_sync_google_sheets.py
========================
Fetches the complete historical price data from the Guntur Mirchi Google Sheet API
and loads it into the Supabase 'mirchi_prices' table. This provides robust data
for actual AP varieties: Teja S17, 334 Sannam, Byadgi, 341, DD Deluxe, and Armoor.
"""

import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import sys

DB_URL = "postgresql://postgres.akdzzsfhvcuvzpjxmscs:8pohdOKVFAZHJ0VJ@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
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

def fetch_sheet_data():
    url = f"https://content-sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values:batchGet?ranges=Consolidated%20Prices&ranges=Fatki%20Table&majorDimension=ROWS&key={API_KEY}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://gunturmirchi.in/',
        'Origin': 'https://gunturmirchi.in'
    }
    
    print("Fetching data from Guntur Mirchi Google Sheets API...")
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f"Error: HTTP {r.status_code} - {r.text}")
        sys.exit(1)
        
    data = r.json()
    valueRanges = data.get('valueRanges', [])
    return valueRanges[0].get('values', []), valueRanges[1].get('values', [])

def parse_date(date_str):
    for fmt in ('%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unknown date format: {date_str}")

def process_consolidated(rows):
    mappings = {
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
    
    records = []
    print(f"Parsing {len(rows)-1} consolidated price rows...")
    
    for row in rows[1:]:
        if not row or not row[0]:
            continue
        try:
            arrival_date = parse_date(row[0])
        except Exception:
            continue
            
        for col_idx, (variety, grade) in mappings.items():
            if col_idx < len(row):
                price = clean_price(row[col_idx])
                if price is not None and price > 0:
                    records.append((
                        arrival_date,
                        "Andhra Pradesh",
                        "Guntur",
                        "Guntur APMC",
                        "Spices",
                        "Dry Chillies",
                        variety,
                        grade,
                        price, # min_price
                        price, # max_price
                        price, # modal_price
                        "Rs./Quintal",
                        None,
                        "Metric Tonnes"
                    ))
    return records

def process_fatki(rows):
    mappings = {
        1: ("Teja Fatki", "Medium"),
        2: ("Teja Fatki", "Best"),
        3: ("334 Fatki", "Medium"),
        4: ("334 Fatki", "Best"),
        5: ("Seed Variety Fatki", "Medium"),
        6: ("Seed Variety Fatki", "Best")
    }
    
    records = []
    print(f"Parsing {len(rows)-1} Fatki price rows...")
    for row in rows[1:]:
        if not row or not row[0]:
            continue
        try:
            arrival_date = parse_date(row[0])
        except Exception:
            continue
            
        for col_idx, (variety, grade) in mappings.items():
            if col_idx < len(row):
                price = clean_price(row[col_idx])
                if price is not None and price > 0:
                    records.append((
                        arrival_date,
                        "Andhra Pradesh",
                        "Guntur",
                        "Guntur APMC",
                        "Spices",
                        "Dry Chillies",
                        variety,
                        grade,
                        price,
                        price,
                        price,
                        "Rs./Quintal",
                        None,
                        "Metric Tonnes"
                    ))
    return records

def upload_to_supabase(records):
    if not records:
        print("No records to upload.")
        return
        
    print(f"Uploading {len(records)} records to Supabase...")
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
        print(f"[OK] Successfully saved/updated {cur.rowcount} rows in Supabase.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Starting Guntur Mirchi Google Sheets Historical Ingest...")
    
    consolidated_raw, fatki_raw = fetch_sheet_data()
    
    records = []
    records += process_consolidated(consolidated_raw)
    records += process_fatki(fatki_raw)
    
    print(f"Total structured price records parsed: {len(records)}")
    upload_to_supabase(records)
    print("Ingest complete!")
