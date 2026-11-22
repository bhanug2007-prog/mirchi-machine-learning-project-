"""
Bilingual Natural Language Entity & Intent Parser for MirchiMandi.
Extracts farmer inputs (variety, quantity, origin, broker offer, wait days, storage cost)
from English and Telugu queries, and handles corrections and follow-ups.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from .tools import normalize_variety, SUPPORTED_VARIETIES


KNOWN_LOCATIONS = [
    ("inkollu", "Inkollu"),
    ("ఇంకొల్లు", "Inkollu"),
    ("pavulur", "Pavulur"),
    ("పావులూరు", "Pavulur"),
    ("chirala", "Chirala"),
    ("చీరాల", "Chirala"),
    ("bapatla", "Bapatla"),
    ("బాపట్ల", "Bapatla"),
    ("chilakaluripet", "Chilakaluripet"),
    ("చిలకలూరిపేట", "Chilakaluripet"),
    ("narasaraopet", "Narasaraopet"),
    ("నరసరావుపేట", "Narasaraopet"),
    ("tenali", "Tenali"),
    ("తెనాలి", "Tenali"),
    ("vijayawada", "Vijayawada"),
    ("విజయవాడ", "Vijayawada"),
    ("ongole", "Ongole"),
    ("ఒంగోలు", "Ongole"),
    ("guntur", "Guntur"),
    ("గుంటూరు", "Guntur"),
]

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "ఒక": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "ఐదు": 5, "ఆరు": 6, "ఏడు": 7,
}


def detect_language(text: str) -> str:
    """Detect if text is primarily Telugu or English."""
    telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
    return "te" if telugu_chars > 3 else "en"


def parse_farmer_message(message: str, current_lang: str = "en") -> Dict[str, Any]:
    """
    Extract structured values from farmer's prompt in English or Telugu.
    Returns dictionary with extracted fields (None for fields not present).
    """
    text = message.strip()
    lower_text = text.lower()
    extracted: Dict[str, Any] = {}

    # Detect language if not specified
    lang = detect_language(text) or current_lang
    extracted["language"] = lang

    # ─────────────────────────────────────────────────────────────
    # 1. QUANTITY (QUINTALS) & CORRECTIONS
    # ─────────────────────────────────────────────────────────────
    # Look for "actually 45", "actually it's 45", "కాదు 45", "45 quintals"
    qty_match = None
    
    # Priority 1: Correction phrasing
    corr_match = re.search(
        r'(?:actually\s+(?:it\'?s\s+)?|కాదు\s*(?:ఇది\s*)?|సవరణ\s*)(\d+(?:\.\d+)?)\s*(?:quintals?|qtls?|qtl|క్వింటాళ్లు|క్వింటాళ్ల|క్వింటాళ్ళ|క్వింటాలు|క్వింటాల్)?',
        lower_text
    )
    if corr_match:
        extracted["quantity_quintals"] = float(corr_match.group(1))
        extracted["is_correction"] = True
    else:
        # Standard quantity match: "60 quintals", "60 qtl", "60 క్వింటాళ్లు"
        std_match = re.search(
            r'(\d+(?:\.\d+)?)\s*(?:quintals?|qtls?|qtl|క్వింటాళ్లు|క్వింటాళ్ల|క్వింటాళ్ళ|క్వింటాలు|క్వింటాల్)',
            lower_text
        )
        if std_match:
            extracted["quantity_quintals"] = float(std_match.group(1))

    # ─────────────────────────────────────────────────────────────
    # 2. VARIETY
    # ─────────────────────────────────────────────────────────────
    # Check for known varieties in text
    variety_found = None
    for var in SUPPORTED_VARIETIES:
        if var.lower() in lower_text:
            variety_found = var
            break

    if not variety_found:
        # Check aliases
        if "teja" in lower_text or "తేజా" in lower_text or "తేజ" in lower_text:
            variety_found = "Teja S17"
        elif "334" in lower_text or "sannam" in lower_text or "సన్నం" in lower_text:
            variety_found = "334 Sannam"
        elif "byadgi" in lower_text or "byadagi" in lower_text or "బ్యాడిగి" in lower_text:
            variety_found = "Byadgi"
        elif "341" in lower_text:
            variety_found = "341"
        elif "deluxe" in lower_text:
            variety_found = "DD Deluxe"
        elif "armoor" in lower_text:
            variety_found = "Armoor"
        elif "red new" in lower_text:
            variety_found = "Red New"
        elif "red" in lower_text and "red new" not in lower_text:
            variety_found = "Red"

    if variety_found:
        extracted["variety"] = normalize_variety(variety_found)

    # ─────────────────────────────────────────────────────────────
    # 3. LOCATION OR PINCODE
    # ─────────────────────────────────────────────────────────────
    # Check for 6-digit AP pincode
    pin_match = re.search(r'\b(5\d{5})\b', text)
    if pin_match:
        extracted["origin_location"] = pin_match.group(1)
    else:
        # Check explicit origin patterns: "in Inkollu", "from Pavulur", "ఇంకొల్లులో"
        prep_match = re.search(r'(?:in|from|at|near|గ్రామం|వద్ద|నుండి)\s+([A-Za-z]+)', text, re.IGNORECASE)
        if prep_match:
            candidate = prep_match.group(1).lower()
            if candidate not in ["guntur", "mandi", "the", "a", "cold"]:
                for needle, canon in KNOWN_LOCATIONS:
                    if candidate == needle or candidate in needle:
                        extracted["origin_location"] = canon
                        break
                if "origin_location" not in extracted:
                    extracted["origin_location"] = prep_match.group(1).capitalize()

        if "origin_location" not in extracted:
            # Check known locations, excluding "guntur" when used as destination market
            for needle, canon in KNOWN_LOCATIONS:
                if needle in ["guntur", "గుంటూరు"]:
                    # Only treat Guntur as origin if explicitly "in Guntur" or "from Guntur"
                    if re.search(r'(?:in|from|at|నుండి|లో)\s+guntur', lower_text):
                        extracted["origin_location"] = canon
                        break
                    continue
                if re.search(rf'\b{re.escape(needle)}', lower_text):
                    extracted["origin_location"] = canon
                    break

    # ─────────────────────────────────────────────────────────────
    # 4. BROKER OFFER (₹/QUINTAL)
    # ─────────────────────────────────────────────────────────────
    # Patterns: "offering ₹16,000", "₹16,000 per quintal", "broker is offering 16000", "16,000 per quintal"
    broker_patterns = [
        r'(?:offering|offer|offered|broker|ఆయన|బ్రోకర్)[^\d₹rs]*[₹rs\.\s]*([1-9]\d{1,2}(?:,\d{3})+|\d{4,6})',
        r'[₹rs\.\s]*([1-9]\d{1,2}(?:,\d{3})+|\d{4,6})\s*(?:per\s+quintal|/qtl|per\s+qtl|క్వింటాలుకు|క్వింటాకు)',
        r'[₹]\s*([1-9]\d{1,2}(?:,\d{3})+|\d{4,6})',
    ]
    for pat in broker_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val_str = m.group(1).replace(',', '')
            val = float(val_str)
            # Sanity check: chilli price per quintal is typically 5000 to 50000
            if 3000 <= val <= 100000:
                extracted["broker_offer_price"] = val
                break

    # ─────────────────────────────────────────────────────────────
    # 5. WAIT DURATION (DAYS)
    # ─────────────────────────────────────────────────────────────
    # "wait seven days", "wait 7 days", "7 days", "7 రోజులు", "ఏడు రోజులు"
    wait_match = re.search(
        r'(?:wait|hold|ఆగాలా|వేచి)\s*(?:for\s+)?(\d+|one|two|three|four|five|six|seven|ఒక|రెండు|మూడు|నాలుగు|ఐదు|ఆరు|ఏడు)\s*(?:days?|రోజులు)?',
        lower_text
    )
    if not wait_match:
        wait_match = re.search(
            r'(\d+|one|two|three|four|five|six|seven|ఒక|రెండు|మూడు|నాలుగు|ఐదు|ఆరు|ఏడు)\s*(?:days?|రోజులు)',
            lower_text
        )

    if wait_match:
        val_raw = wait_match.group(1)
        if val_raw.isdigit():
            extracted["wait_days"] = int(val_raw)
        elif val_raw in WORD_NUMBERS:
            extracted["wait_days"] = WORD_NUMBERS[val_raw]

    # ─────────────────────────────────────────────────────────────
    # 6. STORAGE COST (₹/QUINTAL/DAY)
    # ─────────────────────────────────────────────────────────────
    # "Storage is ₹30 per quintal per day", "storage is 30", "నిల్వ ఖర్చు 30"
    storage_match = re.search(
        r'(?:storage|cold\s+storage|నిల్వ|కోల్డ్\s*స్టోరేజ్)[^\d₹rs]*[₹rs\.\s]*(\d+(?:\.\d+)?)',
        lower_text
    )
    if storage_match:
        extracted["storage_cost_per_qtl_day"] = float(storage_match.group(1))

    # ─────────────────────────────────────────────────────────────
    # 7. DESTINATION MARKET
    # ─────────────────────────────────────────────────────────────
    if "guntur" in lower_text or "గుంటూరు" in lower_text:
        extracted["destination_market"] = "Guntur APMC"

    # ─────────────────────────────────────────────────────────────
    # 8. REQUESTED OPTIONS INTENT
    # ─────────────────────────────────────────────────────────────
    has_broker = any(k in lower_text for k in ["broker", "sell to him", "ఆయనకు", "బ్రోకర్", "ఇస్తానంటున్నాడు", "వ్యాపారి"])
    has_mandi = any(k in lower_text for k in ["mandi", "market", "guntur", "గుంటూరు", "మార్కెట్", "యార్డ్", "తీసుకెళ్లాలా"])
    has_wait = any(k in lower_text for k in ["wait", "days", "hold", "storage", "ఆగాలా", "వేచి", "రోజులు", "నిల్వ"])

    req_opts = []
    if has_broker:
        req_opts.append("broker_now")
    if has_mandi:
        req_opts.append("mandi_now")
    if has_wait:
        req_opts.append("wait_mandi")

    # If general inquiry, default to all three
    if not req_opts:
        req_opts = ["broker_now", "mandi_now", "wait_mandi"]
    elif len(req_opts) == 1 and "broker_now" in req_opts and "wait_days" in extracted:
        req_opts.append("wait_mandi")

    extracted["requested_options"] = req_opts

    return extracted
