"""
Deterministic calculation engine for selling options comparison.
Pure Python business logic: calculates net proceeds, evaluates freshness,
deduplicates fees, and ranks viable alternatives.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple


FRESHNESS_THRESHOLD_DAYS = 2  # As documented in MirchiMandi Outdated Data Guard


def parse_date_safe(d_val: Any) -> Optional[date]:
    if not d_val:
        return None
    if isinstance(d_val, date) and not isinstance(d_val, datetime):
        return d_val
    if isinstance(d_val, datetime):
        return d_val.date()
    try:
        return datetime.strptime(str(d_val)[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def compare_sell_options(
    quantity: float,
    variety: str,
    market: str,
    broker_offer: Optional[float] = None,
    observed_quote: Optional[Dict[str, Any]] = None,
    forecast_quote: Optional[Dict[str, Any]] = None,
    transport_info: Optional[Dict[str, Any]] = None,
    wait_days: Optional[int] = None,
    storage_cost_per_qtl_day: float = 30.0,
    requested_options: Optional[List[str]] = None,
    reference_date: Optional[date] = None,
    farmer_broker_costs: float = 0.0,
) -> Dict[str, Any]:
    """
    Deterministic calculation of net proceeds across:
    1. broker_now
    2. mandi_now
    3. wait_mandi

    Returns dictionary with evaluated options, unavailable options,
    highest_option_id, net_advantage, freshness/informational flags,
    source dates, and key assumptions.
    """
    if requested_options is None:
        requested_options = ["broker_now", "mandi_now", "wait_mandi"]

    if reference_date is None:
        reference_date = date.today()

    options: List[Dict[str, Any]] = []
    unavailable: List[Dict[str, Any]] = []
    source_dates: Dict[str, Optional[str]] = {
        "quote_date": None,
        "forecast_origin_date": None,
        "forecast_target_date": None,
        "forecast_model": None,
    }
    assumptions: List[str] = []
    assumptions_te: List[str] = []

    is_informational = False
    informational_reasons: List[str] = []
    informational_reasons_te: List[str] = []

    # ─────────────────────────────────────────────────────────────
    # 1. OPTION: SELL TO BROKER NOW
    # ─────────────────────────────────────────────────────────────
    if "broker_now" in requested_options:
        if broker_offer is not None and broker_offer > 0:
            gross = round(quantity * broker_offer, 2)
            total_costs = round(farmer_broker_costs, 2)
            net = round(gross - total_costs, 2)
            options.append({
                "id": "broker_now",
                "name": "Sell to Local Broker Now",
                "name_te": "స్థానిక బ్రోకర్‌కు ఇప్పుడే అమ్మండి",
                "price_per_quintal": round(broker_offer, 2),
                "price_type": "offered",
                "gross_proceeds": gross,
                "transport_cost": 0.0,
                "storage_cost": 0.0,
                "labor_cost": 0.0,
                "total_costs": total_costs,
                "net_proceeds": net,
                "is_estimated": False,
                "is_available": True,
                "details": {
                    "includes": "Immediate cash sale at farmgate, no transport or storage deductions",
                    "includes_te": "గ్రామంలోనే తక్షణ నగదు అమ్మకం, రవాణా లేదా నిల్వ ఖర్చులు లేవు"
                }
            })
        else:
            unavailable.append({
                "id": "broker_now",
                "name": "Sell to Local Broker Now",
                "name_te": "స్థానిక బ్రోకర్‌కు ఇప్పుడే అమ్మండి",
                "reason": "Broker offer price per quintal was not provided.",
                "reason_te": "బ్రోకర్ ప్రతిపాదించిన ధర వివరాలు అందలేదు."
            })

    # ─────────────────────────────────────────────────────────────
    # 2. OPTION: SELL AT MANDI NOW
    # ─────────────────────────────────────────────────────────────
    transport_cost = 0.0
    labor_cost = 0.0
    has_transport = False

    if transport_info and transport_info.get("total_cost") is not None:
        has_transport = True
        transport_cost = float(transport_info.get("transport_fare", 0.0))
        labor_cost = float(transport_info.get("labor_cost", 0.0))
        # Total cost is transport_fare + labor_cost (Hamali)
        total_mandi_logistics = float(transport_info.get("total_cost", transport_cost + labor_cost))
        
        # Include transport assumptions
        if transport_info.get("assumptions_en"):
            assumptions.append(f"Logistics: {transport_info['assumptions_en']}")
        if transport_info.get("assumptions_te"):
            assumptions_te.append(f"రవాణా: {transport_info['assumptions_te']}")
    else:
        total_mandi_logistics = None

    if "mandi_now" in requested_options:
        quote_price = observed_quote.get("modal_price") if observed_quote else None
        q_date_str = observed_quote.get("date") if observed_quote else None
        source_dates["quote_date"] = q_date_str

        # Check quote freshness
        q_date = parse_date_safe(q_date_str)
        if q_date:
            age = (reference_date - q_date).days
            if age > FRESHNESS_THRESHOLD_DAYS:
                is_informational = True
                msg_en = f"Market quote is {age} days old (from {q_date_str}), exceeding the {FRESHNESS_THRESHOLD_DAYS}-day freshness threshold. Comparison is informational only."
                msg_te = f"మార్కెట్ ధర {age} రోజుల పాతది ({q_date_str} నాటిది). ఇది సమాచార ప్రయోజనం కొరకు మాత్రమే."
                informational_reasons.append(msg_en)
                informational_reasons_te.append(msg_te)

        if quote_price is not None and total_mandi_logistics is not None:
            gross = round(quantity * quote_price, 2)
            net = round(gross - total_mandi_logistics, 2)
            options.append({
                "id": "mandi_now",
                "name": f"Sell at {market} Now",
                "name_te": f"{market}లో ఇప్పుడే అమ్మండి",
                "price_per_quintal": round(quote_price, 2),
                "price_type": "observed",
                "gross_proceeds": gross,
                "transport_cost": round(transport_cost, 2),
                "storage_cost": 0.0,
                "labor_cost": round(labor_cost, 2),
                "total_costs": round(total_mandi_logistics, 2),
                "net_proceeds": net,
                "is_estimated": True,  # Transport is an estimate
                "is_available": True,
                "details": {
                    "quote_date": q_date_str,
                    "market": market,
                    "includes": f"Mandi sale based on observed price from {q_date_str}, minus estimated freight and labor",
                    "includes_te": f"{q_date_str} నాటి మార్కెట్ ధర ఆధారంగా అమ్మకం, అంచనా రవాణా మరియు హమాలీ ఖర్చులు మినహాయించబడ్డాయి"
                }
            })
        else:
            missing_parts = []
            if quote_price is None:
                missing_parts.append(f"market quote for {variety} at {market}")
            if total_mandi_logistics is None:
                missing_parts.append("transport cost estimate (origin village/pincode needed)")
            
            reason = f"Cannot evaluate mandi option: missing {', '.join(missing_parts)}."
            unavailable.append({
                "id": "mandi_now",
                "name": f"Sell at {market} Now",
                "name_te": f"{market}లో ఇప్పుడే అమ్మండి",
                "reason": reason,
                "reason_te": "రవాణా లేదా మార్కెట్ ధర వివరాలు లేనందున లెక్కించలేకపోయాము."
            })

    # ─────────────────────────────────────────────────────────────
    # 3. OPTION: WAIT AND SELL AT MANDI
    # ─────────────────────────────────────────────────────────────
    if "wait_mandi" in requested_options:
        fc_price = forecast_quote.get("predicted_price") if forecast_quote else None
        target_date_str = forecast_quote.get("target_date") if forecast_quote else None
        origin_date_str = forecast_quote.get("origin_date") if forecast_quote else None
        fc_model = forecast_quote.get("model_used") if forecast_quote else None

        source_dates["forecast_target_date"] = target_date_str
        source_dates["forecast_origin_date"] = origin_date_str
        source_dates["forecast_model"] = fc_model

        # Check if target date has passed
        t_date = parse_date_safe(target_date_str)
        if t_date and t_date < reference_date:
            is_informational = True
            msg_en = f"Forecast target date ({target_date_str}) has already passed. Comparison is informational."
            msg_te = f"అంచనా వేసిన తేదీ ({target_date_str}) గడిచిపోయింది. ఇది సమాచార ప్రయోజనం కొరకు మాత్రమే."
            informational_reasons.append(msg_en)
            informational_reasons_te.append(msg_te)

        if wait_days is None or wait_days < 1 or wait_days > 7:
            unavailable.append({
                "id": "wait_mandi",
                "name": f"Wait and Sell at {market}",
                "name_te": f"వేచి ఉండి {market}లో అమ్మండి",
                "reason": f"Waiting horizon must be between 1 and 7 days (received: {wait_days}).",
                "reason_te": "వేచి ఉండే సమయం 1 నుండి 7 రోజుల మధ్య ఉండాలి."
            })
        elif fc_price is None:
            unavailable.append({
                "id": "wait_mandi",
                "name": f"Wait and Sell at {market}",
                "name_te": f"వేచి ఉండి {market}లో అమ్మండి",
                "reason": f"No forecast model output available for {variety} for horizon {wait_days} days.",
                "reason_te": f"{variety} రకానికి {wait_days} రోజుల భవిష్యత్ ధర అంచనా అందుబాటులో లేదు."
            })
        elif total_mandi_logistics is None:
            unavailable.append({
                "id": "wait_mandi",
                "name": f"Wait and Sell at {market}",
                "name_te": f"వేచి ఉండి {market}లో అమ్మండి",
                "reason": "Transport cost estimate unavailable (origin village/pincode needed).",
                "reason_te": "రవాణా ఖర్చు అంచనా వేయడానికి గ్రామం లేదా పిన్‌కోడ్ అవసరం."
            })
        else:
            storage_total = round(quantity * storage_cost_per_qtl_day * wait_days, 2)
            total_costs = round(total_mandi_logistics + storage_total, 2)
            gross = round(quantity * fc_price, 2)
            net = round(gross - total_costs, 2)

            assumptions.append(
                f"Storage: ₹{storage_cost_per_qtl_day:.0f}/qtl/day for {wait_days} days (total ₹{storage_total:,.0f})."
            )
            assumptions_te.append(
                f"నిల్వ ఖర్చు: క్వింటాలుకు రోజుకు ₹{storage_cost_per_qtl_day:.0f} చొప్పున {wait_days} రోజులకు మొత్తం ₹{storage_total:,.0f}."
            )

            options.append({
                "id": "wait_mandi",
                "name": f"Wait {wait_days} Days & Sell at {market}",
                "name_te": f"{wait_days} రోజులు వేచి ఉండి {market}లో అమ్మండి",
                "price_per_quintal": round(fc_price, 2),
                "price_type": "forecast",
                "gross_proceeds": gross,
                "transport_cost": round(transport_cost, 2),
                "storage_cost": storage_total,
                "labor_cost": round(labor_cost, 2),
                "total_costs": total_costs,
                "net_proceeds": net,
                "is_estimated": True,  # Both forecast price and transport are estimates
                "is_available": True,
                "details": {
                    "wait_days": wait_days,
                    "target_date": target_date_str,
                    "model_used": fc_model,
                    "storage_cost_per_qtl_day": storage_cost_per_qtl_day,
                    "includes": f"Forecast price for {target_date_str} using {fc_model or 'ML model'}, minus storage and transport",
                    "includes_te": f"{target_date_str} నాటి అంచనా ధర ({fc_model or 'ML మోడల్'}), నిల్వ మరియు రవాణా ఖర్చులు మినహాయించబడ్డాయి"
                }
            })

    # ─────────────────────────────────────────────────────────────
    # 4. RANKING & NET ADVANTAGE COMPARISON
    # ─────────────────────────────────────────────────────────────
    highest_option_id = None
    net_advantage = None
    net_advantage_vs = None

    if options:
        # Sort options descending by net proceeds
        sorted_opts = sorted(options, key=lambda o: o["net_proceeds"], reverse=True)
        top = sorted_opts[0]

        # Only declare an active recommendation if not informational and multiple options evaluated
        if not is_informational:
            highest_option_id = top["id"]
            if len(sorted_opts) > 1:
                runner_up = sorted_opts[1]
                net_advantage = round(top["net_proceeds"] - runner_up["net_proceeds"], 2)
                net_advantage_vs = runner_up["id"]
        else:
            # Informational only: do not provide an active recommendation
            highest_option_id = None
            if len(sorted_opts) > 1:
                runner_up = sorted_opts[1]
                net_advantage = round(top["net_proceeds"] - runner_up["net_proceeds"], 2)
                net_advantage_vs = runner_up["id"]

    return {
        "options": options,
        "unavailable_options": unavailable,
        "highest_option_id": highest_option_id,
        "net_advantage": net_advantage,
        "net_advantage_vs": net_advantage_vs,
        "is_informational": is_informational,
        "informational_reason": " ".join(informational_reasons) if informational_reasons else None,
        "informational_reason_te": " ".join(informational_reasons_te) if informational_reasons_te else None,
        "source_dates": source_dates,
        "assumptions": assumptions,
        "assumptions_te": assumptions_te,
    }
