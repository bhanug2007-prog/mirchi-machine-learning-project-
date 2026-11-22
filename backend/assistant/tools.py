"""
Read-only tools for the MirchiMandi Market Research Assistant.
Wraps existing backend logic directly without internal HTTP requests.
"""

from datetime import date, datetime, timedelta
from importlib import import_module
from typing import Any, Dict, List, Optional
from fastapi import HTTPException


def get_backend():
    package = __package__.rpartition(".")[0]
    return import_module(f"{package}.main" if package else "main")

# Variety aliases to match farmer queries to database cultivars
VARIETY_ALIASES: Dict[str, str] = {
    "teja": "Teja S17",
    "teja s17": "Teja S17",
    "tejas17": "Teja S17",
    "s17": "Teja S17",
    "తేజా": "Teja S17",
    "తేజ": "Teja S17",
    "334": "334 Sannam",
    "334 sannam": "334 Sannam",
    "sannam": "334 Sannam",
    "సన్నం": "334 Sannam",
    "byadgi": "Byadgi",
    "byadagi": "Byadgi",
    "బ్యాడిగి": "Byadgi",
    "341": "341",
    "dd deluxe": "DD Deluxe",
    "deluxe": "DD Deluxe",
    "armoor": "Armoor",
    "red new": "Red New",
    "red": "Red",
    "guntur": "Guntur",
    "white": "White",
    "local": "Local",
    "dry chillies": "Dry Chillies",
}

SUPPORTED_VARIETIES = [
    "Teja S17", "334 Sannam", "Byadgi", "341", "DD Deluxe",
    "Armoor", "Red New", "Red", "Guntur", "White", "Local"
]


def normalize_variety(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    cleaned = str(name).strip().lower()
    if cleaned in VARIETY_ALIASES:
        return VARIETY_ALIASES[cleaned]
    # Check if any alias is a substring
    for alias, standard in VARIETY_ALIASES.items():
        if alias in cleaned:
            return standard
    # Check case-insensitive match against supported varieties
    for std in SUPPORTED_VARIETIES:
        if std.lower() == cleaned:
            return std
    return name.strip()


def get_market_quote(market: str = "Guntur APMC", variety: str = "Teja S17") -> Dict[str, Any]:
    """
    Find the latest available quote for the requested market and variety.
    Returns the price, unit, observed date, and source. Does not silently substitute.
    """
    backend_main = get_backend()

    norm_var = normalize_variety(variety) or variety
    try:
        data = backend_main.get_today_price(market=market, variety=norm_var)
        return {
            "success": True,
            "market": data.get("market", market),
            "variety": data.get("variety", norm_var),
            "modal_price": data.get("modal_price"),
            "min_price": data.get("min_price"),
            "max_price": data.get("max_price"),
            "date": str(data.get("date")),
            "unit": data.get("unit", "Rs. per Quintal (100 kg)"),
            "is_user_reported": data.get("is_user_reported", False),
            "grade": data.get("grade", "All Grades (Avg)"),
        }
    except HTTPException as e:
        return {
            "success": False,
            "error": f"No quote found for {norm_var} at {market}: {e.detail}",
            "market": market,
            "variety": norm_var,
            "modal_price": None,
            "supported_varieties": SUPPORTED_VARIETIES,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve market quote: {str(e)}",
            "market": market,
            "variety": norm_var,
            "modal_price": None,
        }


def get_price_forecast(market: str = "Guntur APMC", variety: str = "Teja S17", wait_days: int = 7) -> Dict[str, Any]:
    """
    Return the relevant forecast with its origin date, target date, method, and predicted price.
    Returns unavailable if requested wait is outside supported horizon (1-7 days).
    """
    backend_main = get_backend()

    if wait_days < 1 or wait_days > 7:
        return {
            "success": False,
            "error": f"Requested wait period of {wait_days} days is outside supported 1-7 day ML horizon.",
            "market": market,
            "variety": variety,
            "predicted_price": None,
        }

    norm_var = normalize_variety(variety) or variety
    try:
        fc = backend_main.get_forecast(market=market, variety=norm_var)
        preds = fc.get("forecast", [])
        if not preds or len(preds) < wait_days:
            return {
                "success": False,
                "error": f"Forecast predictions insufficient for horizon {wait_days} days.",
                "market": market,
                "variety": norm_var,
                "predicted_price": None,
            }

        predicted_price = float(preds[wait_days - 1])
        model_used = fc.get("model_used", "ML Model")

        # Determine origin and target dates
        today_quote = get_market_quote(market, norm_var)
        origin_date_str = today_quote.get("date") if today_quote.get("success") else str(date.today())
        
        origin_d = date.today()
        if origin_date_str:
            try:
                origin_d = datetime.strptime(origin_date_str[:10], "%Y-%m-%d").date()
            except Exception:
                pass
        target_d = origin_d + timedelta(days=wait_days)

        return {
            "success": True,
            "market": market,
            "variety": norm_var,
            "wait_days": wait_days,
            "origin_date": origin_d.strftime("%Y-%m-%d"),
            "target_date": target_d.strftime("%Y-%m-%d"),
            "predicted_price": predicted_price,
            "model_used": model_used,
            "all_forecasts": preds,
            "trend": fc.get("trend", "STABLE"),
            "accuracy_mae": fc.get("accuracy_mae"),
            "accuracy_r2": fc.get("accuracy_r2"),
        }
    except HTTPException as e:
        return {
            "success": False,
            "error": f"No forecast available for {norm_var}: {e.detail}",
            "market": market,
            "variety": norm_var,
            "predicted_price": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Forecast service failed: {str(e)}",
            "market": market,
            "variety": norm_var,
            "predicted_price": None,
        }


def estimate_transport(
    origin: str,
    destination_market: str = "Guntur APMC",
    vehicle: Optional[str] = "Tractor",
    quantity: float = 50.0
) -> Dict[str, Any]:
    """
    Reuse the existing transport logic. Return total estimate and its basis,
    including distance source, vehicle, and applicable fees. Uses fallback when needed.
    """
    backend_main = get_backend()

    market_pincode = "522001"  # Guntur APMC Pincode
    veh = vehicle or "Tractor"

    try:
        tc = backend_main.get_transport_costs(
            farmer_pincode=origin,
            market_pincode=market_pincode,
            vehicle=veh,
            quintals=quantity
        )
        return {
            "success": True,
            "origin": origin,
            "destination_market": destination_market,
            "destination_pincode": market_pincode,
            "distance_km": tc.get("distance_km"),
            "distance_source": tc.get("distance_source"),
            "distance_method": tc.get("distance_method"),
            "vehicle": tc.get("vehicle", veh),
            "transport_fare": tc.get("transport_fare"),
            "labor_cost": tc.get("labor_cost"),
            "total_cost": tc.get("total_cost"),
            "is_estimate": tc.get("is_estimate", True),
            "assumptions_en": tc.get("assumptions_en"),
            "assumptions_te": tc.get("assumptions_te"),
        }
    except Exception as e:
        # Documented fallback if transport lookup crashes
        fallback_km = backend_main.fallback_distance(origin, market_pincode)
        base_fare = 1500
        per_km = 35
        transport_fare = base_fare + (fallback_km * per_km)
        labor_cost = quantity * 40.0
        total_cost = transport_fare + labor_cost
        return {
            "success": True,
            "origin": origin,
            "destination_market": destination_market,
            "destination_pincode": market_pincode,
            "distance_km": fallback_km,
            "distance_source": "pincode_prefix_fallback",
            "distance_method": "Pincode prefix heuristic fallback (recovery)",
            "vehicle": "Tractor",
            "transport_fare": round(transport_fare, 0),
            "labor_cost": round(labor_cost, 0),
            "total_cost": round(total_cost, 0),
            "is_estimate": True,
            "assumptions_en": f"Estimated one-way freight: Tractor base ₹{base_fare} + ₹{per_km}/km for {fallback_km} km (fallback), plus Hamali ₹40/qtl. Return trip excluded.",
            "assumptions_te": f"అంచనా రవాణా ఖర్చు: ట్రాక్టర్ బేస్ ₹{base_fare} + {fallback_km} కి.మీ లకు ₹{per_km}/కి.మీ (ఫాల్‌బ్యాక్), మరియు హమాలీ ₹40/క్విం. తిరుగు ప్రయాణం చేర్చబడలేదు.",
        }
