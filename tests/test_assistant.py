"""
Comprehensive Verification Test Suite for MirchiMandi Feature 1:
Agentic AI Market Research Assistant.

Tests run offline with mocked LLM and market services without API keys or network access.
"""

import sys
import os
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from assistant.schemas import (
    AssistantCompareRequest,
    AssistantCompareResponse,
    ConversationContext,
    OptionResult,
    UnavailableOption,
)
from assistant.calculator import compare_sell_options
from assistant.tools import (
    get_market_quote,
    get_price_forecast,
    estimate_transport,
    normalize_variety,
)
from assistant.parser import parse_farmer_message
from assistant.graph import run_assistant_workflow
import main as backend_main


def test_exact_synthetic_test_fixture():
    """
    Verification Requirement 6:
    Exact synthetic data fixture:
    - Quantity: 60 quintals
    - Broker offer: ₹16,000/quintal
    - Observed mandi quote: ₹17,000/quintal
    - Day-seven forecast: ₹17,500/quintal
    - Transport and selling costs: ₹7,000 total for each mandi option
    - Storage: ₹30/quintal/day for seven days

    Expected results:
    - Broker now: ₹960,000
    - Mandi now: ₹1,013,000
    - Waiting: ₹1,030,400, including ₹12,600 in storage costs
    - Waiting has ₹17,400 higher estimated proceeds than selling at the mandi now.
    """
    res = compare_sell_options(
        quantity=60.0,
        variety="Teja S17",
        market="Guntur APMC",
        broker_offer=16000.0,
        observed_quote={
            "modal_price": 17000.0,
            "date": str(date.today()),
            "market": "Guntur APMC",
            "variety": "Teja S17"
        },
        forecast_quote={
            "predicted_price": 17500.0,
            "target_date": str(date.today() + timedelta(days=7)),
            "origin_date": str(date.today()),
            "model_used": "Lasso Regression"
        },
        transport_info={
            "total_cost": 7000.0,
            "transport_fare": 4600.0,
            "labor_cost": 2400.0,
            "distance_km": 88.0,
            "distance_source": "haversine_road_factor",
            "assumptions_en": "Tractor freight + Hamali ₹40/qtl"
        },
        wait_days=7,
        storage_cost_per_qtl_day=30.0,
        reference_date=date.today()
    )

    opts = {o["id"]: o for o in res["options"]}

    # Verify Broker Now
    broker = opts["broker_now"]
    assert broker["gross_proceeds"] == 960000.0
    assert broker["total_costs"] == 0.0
    assert broker["net_proceeds"] == 960000.0
    assert broker["price_type"] == "offered"
    assert broker["is_estimated"] is False

    # Verify Mandi Now
    mandi = opts["mandi_now"]
    assert mandi["gross_proceeds"] == 1020000.0
    assert mandi["total_costs"] == 7000.0
    assert mandi["net_proceeds"] == 1013000.0
    assert mandi["price_type"] == "observed"
    assert mandi["is_estimated"] is True

    # Verify Wait Mandi
    wait = opts["wait_mandi"]
    assert wait["gross_proceeds"] == 1050000.0
    assert wait["storage_cost"] == 12600.0  # 60 * 30 * 7 = 12,600
    assert wait["total_costs"] == 19600.0   # 7000 transport + 12600 storage = 19,600
    assert wait["net_proceeds"] == 1030400.0  # 1050000 - 19600 = 1,030,400
    assert wait["price_type"] == "forecast"
    assert wait["is_estimated"] is True

    # Verify Comparison
    assert res["highest_option_id"] == "wait_mandi"
    assert res["net_advantage"] == 17400.0  # 1030400 - 1013000 = 17,400
    assert res["net_advantage_vs"] == "mandi_now"
    assert res["is_informational"] is False


def test_missing_input_triggers_focused_followup_and_retains_context():
    """
    Test that missing input triggers a focused follow-up, and the next
    message reuses the earlier validated details.
    """
    # Turn 1: No village or pincode supplied
    msg1 = "I have 60 quintals of Teja S17 chilli. A broker is offering ₹16,000 per quintal. Should I sell to him, take it to Guntur mandi, or wait seven days?"
    res1 = run_assistant_workflow(message=msg1, language="en", mock_mode=True)

    assert res1["status"] == "needs_input"
    assert "origin_location" in res1["missing_fields"]
    assert res1["follow_up_question"] is not None
    assert "village" in res1["follow_up_question"].lower() or "pincode" in res1["follow_up_question"].lower()
    assert res1["context"]["quantity_quintals"] == 60.0
    assert res1["context"]["variety"] == "Teja S17"
    assert res1["context"]["broker_offer_price"] == 16000.0
    assert res1["context"]["wait_days"] == 7

    # Turn 2: Farmer supplies missing location
    ctx1 = ConversationContext(**res1["context"])
    msg2 = "I am in Inkollu"
    res2 = run_assistant_workflow(message=msg2, language="en", context=ctx1, mock_mode=True)

    assert res2["status"] in ("complete", "partial")
    assert res2["context"]["origin_location"] == "Inkollu"
    assert res2["context"]["quantity_quintals"] == 60.0
    assert res2["context"]["variety"] == "Teja S17"
    assert res2["context"]["broker_offer_price"] == 16000.0
    assert res2["context"]["wait_days"] == 7
    assert len(res2["options"]) == 3


def test_corrected_quantity_replaces_original_value():
    """
    Test that when a farmer clarifies 'Actually it's 45 quintals',
    the new quantity overrides the prior quantity and all options recalculate.
    """
    initial_ctx = ConversationContext(
        variety="Teja S17",
        quantity_quintals=60.0,
        origin_location="Inkollu",
        destination_market="Guntur APMC",
        broker_offer_price=16000.0,
        wait_days=7,
        storage_cost_per_qtl_day=30.0,
        requested_options=["broker_now", "mandi_now", "wait_mandi"]
    )

    msg = "Actually it's 45 quintals"
    res = run_assistant_workflow(message=msg, language="en", context=initial_ctx, mock_mode=True)

    assert res["context"]["quantity_quintals"] == 45.0
    opts = {o["id"]: o for o in res["options"]}
    # Broker now: 45 * 16,000 = 720,000
    assert opts["broker_now"]["gross_proceeds"] == 720000.0
    assert opts["broker_now"]["net_proceeds"] == 720000.0
    # Wait storage cost: 45 * 30 * 7 = 9,450
    assert opts["wait_mandi"]["storage_cost"] == 9450.0


def test_broker_vs_mandi_skips_forecast_tool():
    """
    Test conditional routing: a question asking only about broker vs mandi
    evaluates broker and mandi options, and does NOT require or call forecast.
    """
    msg = "I have 50 quintals of Teja S17 in Inkollu. Broker is offering ₹16,000. Should I sell to him or take to Guntur mandi?"
    
    with patch("assistant.graph.get_price_forecast") as mock_fc:
        res = run_assistant_workflow(message=msg, language="en", mock_mode=True)
        # Assert forecast was never called
        mock_fc.assert_not_called()

    opt_ids = [o["id"] for o in res["options"]]
    assert "broker_now" in opt_ids
    assert "mandi_now" in opt_ids
    assert "wait_mandi" not in opt_ids


def test_missing_or_expired_forecast_keeps_immediate_options_visible():
    """
    Test that if forecast is unavailable or horizon exceeds 7 days,
    immediate options (broker and mandi) remain visible and evaluated.
    """
    res = compare_sell_options(
        quantity=50.0,
        variety="Teja S17",
        market="Guntur APMC",
        broker_offer=16000.0,
        observed_quote={"modal_price": 20000.0, "date": str(date.today())},
        forecast_quote=None,  # Missing forecast
        transport_info={"total_cost": 6000.0, "transport_fare": 4000.0, "labor_cost": 2000.0},
        wait_days=14,  # Outside 1-7 day horizon
        storage_cost_per_qtl_day=30.0,
    )

    opt_ids = [o["id"] for o in res["options"]]
    assert "broker_now" in opt_ids
    assert "mandi_now" in opt_ids
    assert "wait_mandi" not in opt_ids

    unavail_ids = [u["id"] for u in res["unavailable_options"]]
    assert "wait_mandi" in unavail_ids
    assert "1 and 7 days" in res["unavailable_options"][0]["reason"]


def test_stale_quote_produces_informational_result():
    """
    Test that a quote older than 2 days is marked informational,
    shows the observed quote date, and avoids an active sell-or-wait recommendation.
    """
    stale_date = date.today() - timedelta(days=10)
    res = compare_sell_options(
        quantity=50.0,
        variety="Teja S17",
        market="Guntur APMC",
        broker_offer=16000.0,
        observed_quote={"modal_price": 21000.0, "date": str(stale_date)},
        forecast_quote={"predicted_price": 22000.0, "target_date": str(date.today() + timedelta(days=5))},
        transport_info={"total_cost": 5000.0, "transport_fare": 3000.0, "labor_cost": 2000.0},
        wait_days=5,
        storage_cost_per_qtl_day=30.0,
        reference_date=date.today()
    )

    assert res["is_informational"] is True
    assert "exceeding the 2-day freshness threshold" in res["informational_reason"]
    # No active recommendation given
    assert res["highest_option_id"] is None
    # Options are still available for review
    assert len(res["options"]) == 3


def test_transport_failure_uses_labeled_fallback():
    """
    Test that when geocoding is unavailable, transport calculation uses
    the pincode prefix fallback with transparent assumption labeling.
    """
    with patch("main.get_coordinates", side_effect=[None, (16.3067, 80.4367)]):
        tc = estimate_transport(
            origin="999999",
            destination_market="Guntur APMC",
            vehicle="Tractor",
            quantity=50.0,
        )

    assert tc["success"] is True
    assert tc["total_cost"] > 0.0  # Never zero
    assert tc["is_estimate"] is True
    assert "fallback" in tc["distance_source"].lower() or "fallback" in tc["distance_method"].lower()
    assert "Tractor base" in tc["assumptions_en"]


def test_english_and_telugu_receive_identical_structured_numbers():
    """
    Test that the exact same inputs in English and Telugu produce
    identical numerical calculations and proceeds.
    """
    msg_en = "I have 60 quintals of Teja S17 chilli in Inkollu. A broker is offering ₹16,000 per quintal. Should I sell to him, take it to Guntur mandi, or wait seven days?"
    msg_te = "నా దగ్గర ఇంకొల్లులో 60 క్వింటాళ్ల తేజా S17 మిర్చి ఉంది. బ్రోకర్ క్వింటాలుకు ₹16,000 ఇస్తానంటున్నాడు. ఆయనకు అమ్మేయాలా, గుంటూరు మార్కెట్ కి తీసుకెళ్లాలా, లేక 7 రోజులు ఆగాలా?"

    res_en = run_assistant_workflow(message=msg_en, language="en", mock_mode=True)
    res_te = run_assistant_workflow(message=msg_te, language="te", mock_mode=True)

    assert len(res_en["options"]) == len(res_te["options"])
    en_map = {o["id"]: o for o in res_en["options"]}
    te_map = {o["id"]: o for o in res_te["options"]}

    for opt_id in en_map:
        o_en = en_map[opt_id]
        o_te = te_map[opt_id]
        assert o_en["gross_proceeds"] == o_te["gross_proceeds"]
        assert o_en["total_costs"] == o_te["total_costs"]
        assert o_en["net_proceeds"] == o_te["net_proceeds"]
        assert o_en["price_per_quintal"] == o_te["price_per_quintal"]
        assert o_en["storage_cost"] == o_te["storage_cost"]
        assert o_en["transport_cost"] == o_te["transport_cost"]

    assert res_en.get("net_advantage") == res_te.get("net_advantage")


def test_conversation_isolation():
    """
    Test that state is strictly request-scoped and one conversation's
    inputs never leak into another conversation.
    """
    ctx_farmer_a = ConversationContext(
        variety="Teja S17",
        quantity_quintals=60.0,
        origin_location="Inkollu",
        broker_offer_price=16000.0
    )

    ctx_farmer_b = ConversationContext(
        variety="Byadgi",
        quantity_quintals=25.0,
        origin_location="Chirala",
        broker_offer_price=22000.0
    )

    res_a = run_assistant_workflow("What is my broker revenue?", context=ctx_farmer_a, mock_mode=True)
    res_b = run_assistant_workflow("What is my broker revenue?", context=ctx_farmer_b, mock_mode=True)

    assert res_a["context"]["variety"] == "Teja S17"
    assert res_a["context"]["quantity_quintals"] == 60.0
    assert res_b["context"]["variety"] == "Byadgi"
    assert res_b["context"]["quantity_quintals"] == 25.0


def test_app_starts_without_llm_key_and_returns_unavailable():
    """
    Test that when LLM API keys are absent and mock_mode is False,
    the assistant returns an appropriate 'unavailable' status while the app works.
    """
    with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": "", "OPENAI_API_KEY": "", "MOCK_LLM": ""}):
        res = run_assistant_workflow("Should I sell my chilli?", mock_mode=False)
        assert res["status"] == "unavailable"
        assert "unavailable because no LLM provider key is configured" in res["explanation"]


def test_existing_fastapi_endpoints_work():
    """
    Ensure existing FastAPI backend endpoints remain 100% operational.
    """
    health = backend_main.health()
    assert health["status"] == "ok"
    assert health["total_records"] > 0

    today = backend_main.get_today_price(market="Guntur APMC", variety="Teja S17")
    assert today["variety"] == "Teja S17"
    assert today["modal_price"] > 0

    fc = backend_main.get_forecast(market="Guntur APMC", variety="Teja S17")
    assert fc["market"] == "Guntur APMC"
    assert len(fc["forecast"]) == 7

    tc = backend_main.get_transport_costs(farmer_pincode="Inkollu", market_pincode="522001", vehicle="Tractor", quintals=50)
    assert tc["total_cost"] > 0
    assert tc["distance_km"] > 0

    calc = backend_main.profit_calculator(quintals=50, broker_price=16000, market="Guntur APMC", variety="Teja S17")
    assert calc["loss"] is not None
