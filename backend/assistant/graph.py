"""
LangGraph workflow for the MirchiMandi Agentic AI Market Research Assistant.
Implements bounded state execution:
START -> parse_message -> merge_context -> decide_actionable -> (conditional)
      -> fetch_data -> calculate_options -> build_response -> END
"""

import os
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, START, END

from .schemas import (
    AssistantCompareResponse,
    ConversationContext,
    OptionResult,
    UnavailableOption,
)
from .calculator import compare_sell_options
from .tools import (
    estimate_transport,
    get_market_quote,
    get_price_forecast,
    normalize_variety,
)
from .llm_provider import (
    extract_fields_with_llm,
    generate_bilingual_explanation,
    is_llm_available,
)


class WorkflowState(TypedDict, total=False):
    # Request inputs
    raw_message: str
    language: str
    existing_context: Dict[str, Any]
    mock_mode: Optional[bool]
    _parsed_fields: Optional[Dict[str, Any]]

    # Merged / Validated fields
    variety: Optional[str]
    quantity_quintals: Optional[float]
    origin_location: Optional[str]
    destination_market: Optional[str]
    vehicle: Optional[str]
    broker_offer_price: Optional[float]
    wait_days: Optional[int]
    storage_cost_per_qtl_day: Optional[float]
    requested_options: List[str]
    field_sources: Dict[str, str]

    # Decision flags
    needs_input: bool
    missing_fields: List[str]
    follow_up_question: Optional[str]
    follow_up_question_te: Optional[str]

    # Tool execution results
    market_quote_result: Optional[Dict[str, Any]]
    forecast_result: Optional[Dict[str, Any]]
    transport_result: Optional[Dict[str, Any]]

    # Calculation results
    comparison_result: Optional[Dict[str, Any]]

    # Final response
    final_response: Dict[str, Any]
    status: str


# ─────────────────────────────────────────────────────────────────────────────
# NODE 1: PARSE MESSAGE
# ─────────────────────────────────────────────────────────────────────────────
def node_parse_message(state: WorkflowState) -> WorkflowState:
    msg = state.get("raw_message", "")
    lang = state.get("language", "en")
    mock_mode = state.get("mock_mode")

    parsed = extract_fields_with_llm(msg, lang, mock_mode)
    return {
        **state,
        "_parsed_fields": parsed
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 2: MERGE CONTEXT
# ─────────────────────────────────────────────────────────────────────────────
def node_merge_context(state: WorkflowState) -> WorkflowState:
    ctx = state.get("existing_context") or {}
    parsed = state.get("_parsed_fields") or {}
    field_sources = dict(ctx.get("field_sources") or {})

    # Start with existing context values
    merged_variety = ctx.get("variety")
    merged_qty = ctx.get("quantity_quintals")
    merged_origin = ctx.get("origin_location")
    merged_dest = ctx.get("destination_market") or "Guntur APMC"
    merged_veh = ctx.get("vehicle")
    merged_broker = ctx.get("broker_offer_price")
    merged_wait = ctx.get("wait_days")
    merged_storage = ctx.get("storage_cost_per_qtl_day")
    merged_options = ctx.get("requested_options") or ["broker_now", "mandi_now", "wait_mandi"]

    # Mark existing fields as conversation_context
    for k in [
        "variety", "quantity_quintals", "origin_location", "destination_market",
        "vehicle", "broker_offer_price", "wait_days", "storage_cost_per_qtl_day"
    ]:
        if ctx.get(k) is not None and k not in field_sources:
            field_sources[k] = "conversation_context"

    # Overlay newly parsed fields from farmer's current message
    if parsed.get("variety"):
        merged_variety = normalize_variety(parsed["variety"])
        field_sources["variety"] = "user_input"

    if parsed.get("quantity_quintals") is not None:
        merged_qty = float(parsed["quantity_quintals"])
        field_sources["quantity_quintals"] = "user_input"

    if parsed.get("origin_location"):
        merged_origin = parsed["origin_location"]
        field_sources["origin_location"] = "user_input"

    if parsed.get("destination_market"):
        merged_dest = parsed["destination_market"]
        field_sources["destination_market"] = "user_input"

    if parsed.get("broker_offer_price") is not None:
        merged_broker = float(parsed["broker_offer_price"])
        field_sources["broker_offer_price"] = "user_input"

    if parsed.get("wait_days") is not None:
        merged_wait = int(parsed["wait_days"])
        field_sources["wait_days"] = "user_input"

    if parsed.get("storage_cost_per_qtl_day") is not None:
        merged_storage = float(parsed["storage_cost_per_qtl_day"])
        field_sources["storage_cost_per_qtl_day"] = "user_input"

    if parsed.get("vehicle"):
        merged_veh = parsed["vehicle"]
        field_sources["vehicle"] = "user_input"

    if parsed.get("requested_options"):
        # If user explicitly asked for specific options, update
        merged_options = parsed["requested_options"]

    # Apply documented app defaults where appropriate
    if not merged_dest:
        merged_dest = "Guntur APMC"
        field_sources["destination_market"] = "app_default"

    # Default storage cost is Rs 30/qtl/day as documented in MirchiMandi
    if "wait_mandi" in merged_options and merged_storage is None:
        merged_storage = 30.0
        field_sources["storage_cost_per_qtl_day"] = "app_default"

    if not merged_veh:
        merged_veh = "Tractor"
        field_sources["vehicle"] = "app_default"

    return {
        **state,
        "variety": merged_variety,
        "quantity_quintals": merged_qty,
        "origin_location": merged_origin,
        "destination_market": merged_dest,
        "vehicle": merged_veh,
        "broker_offer_price": merged_broker,
        "wait_days": merged_wait,
        "storage_cost_per_qtl_day": merged_storage,
        "requested_options": merged_options,
        "field_sources": field_sources,
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 3: DECIDE ACTIONABLE & CHECK MISSING
# ─────────────────────────────────────────────────────────────────────────────
def node_decide_actionable(state: WorkflowState) -> WorkflowState:
    options = state.get("requested_options") or ["broker_now", "mandi_now", "wait_mandi"]
    qty = state.get("quantity_quintals")
    variety = state.get("variety")
    broker = state.get("broker_offer_price")
    origin = state.get("origin_location")
    wait = state.get("wait_days")

    missing: List[str] = []
    follow_up_en = None
    follow_up_te = None

    # Check fundamental required inputs
    if qty is None or qty <= 0:
        missing.append("quantity_quintals")
        follow_up_en = "How many quintals of chilli do you have to sell?"
        follow_up_te = "మీ దగ్గర ఎన్ని క్వింటాళ్ల మిర్చి అమ్మకానికి ఉంది?"
    elif not variety:
        missing.append("variety")
        follow_up_en = "Which chilli variety do you have (e.g. Teja S17, 334 Sannam, Byadgi)?"
        follow_up_te = "మీది ఏ రకం మిర్చి (ఉదా: తేజా S17, 334 సన్నం, బ్యాడిగి)?"
    elif "broker_now" in options and (broker is None or broker <= 0):
        missing.append("broker_offer_price")
        follow_up_en = "What price is the local broker offering per quintal (₹/quintal)?"
        follow_up_te = "స్థానిక బ్రోకర్ క్వింటాలుకు ఎంత ధర ఇస్తానంటున్నారు (రూ/క్వింటాల్)?"
    elif ("mandi_now" in options or "wait_mandi" in options) and not origin:
        missing.append("origin_location")
        follow_up_en = "Please provide your village name or postal pincode so I can calculate transport costs to Guntur APMC."
        follow_up_te = "గుంటూరు యార్డుకు రవాణా ఖర్చులను లెక్కించడానికి దయచేసి మీ గ్రామం పేరు లేదా పిన్‌కోడ్ తెలియజేయండి."
    elif "wait_mandi" in options and (wait is None or wait < 1):
        missing.append("wait_days")
        follow_up_en = "How many days are you considering holding the crop in cold storage (1 to 7 days)?"
        follow_up_te = "మీరు ఎన్ని రోజులు కోల్డ్ స్టోరేజ్‌లో ఉంచాలనుకుంటున్నారు (1 నుండి 7 రోజుల వరకు)?"

    needs_input = len(missing) > 0

    return {
        **state,
        "needs_input": needs_input,
        "missing_fields": missing,
        "follow_up_question": follow_up_en,
        "follow_up_question_te": follow_up_te,
    }


def route_after_decision(state: WorkflowState) -> str:
    """Conditional edge: if missing input blocks comparison, route to response."""
    if state.get("needs_input"):
        return "build_response"
    return "fetch_data"


# ─────────────────────────────────────────────────────────────────────────────
# NODE 4: FETCH DATA (READ-ONLY TOOLS)
# ─────────────────────────────────────────────────────────────────────────────
def node_fetch_data(state: WorkflowState) -> WorkflowState:
    options = state.get("requested_options") or []
    variety = state.get("variety") or "Teja S17"
    market = state.get("destination_market") or "Guntur APMC"
    origin = state.get("origin_location")
    qty = state.get("quantity_quintals") or 50.0
    vehicle = state.get("vehicle") or "Tractor"
    wait_days = state.get("wait_days") or 7

    quote_res = None
    trans_res = None
    fc_res = None

    # Mandi quote needed if mandi_now or wait_mandi requested
    if "mandi_now" in options or "wait_mandi" in options:
        quote_res = get_market_quote(market=market, variety=variety)

    # Transport estimate needed if mandi_now or wait_mandi requested
    if origin and ("mandi_now" in options or "wait_mandi" in options):
        trans_res = estimate_transport(
            origin=origin,
            destination_market=market,
            vehicle=vehicle,
            quantity=qty
        )

    # ML Forecast tool: ONLY called if wait_mandi is requested!
    # If farmer only asked broker vs mandi, forecast lookup is skipped.
    if "wait_mandi" in options:
        fc_res = get_price_forecast(market=market, variety=variety, wait_days=wait_days)

    return {
        **state,
        "market_quote_result": quote_res,
        "transport_result": trans_res,
        "forecast_result": fc_res,
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 5: CALCULATE COMPARISON (DETERMINISTIC PYTHON)
# ─────────────────────────────────────────────────────────────────────────────
def node_calculate_options(state: WorkflowState) -> WorkflowState:
    qty = state.get("quantity_quintals") or 0.0
    variety = state.get("variety") or "Teja S17"
    market = state.get("destination_market") or "Guntur APMC"
    broker = state.get("broker_offer_price")
    wait = state.get("wait_days")
    storage = state.get("storage_cost_per_qtl_day") or 30.0
    options = state.get("requested_options") or ["broker_now", "mandi_now", "wait_mandi"]

    q_res = state.get("market_quote_result")
    t_res = state.get("transport_result")
    f_res = state.get("forecast_result")

    observed_quote = None
    if q_res and q_res.get("success"):
        observed_quote = {
            "modal_price": q_res.get("modal_price"),
            "date": q_res.get("date"),
            "market": q_res.get("market"),
            "variety": q_res.get("variety"),
        }

    forecast_quote = None
    if f_res and f_res.get("success"):
        forecast_quote = {
            "predicted_price": f_res.get("predicted_price"),
            "target_date": f_res.get("target_date"),
            "origin_date": f_res.get("origin_date"),
            "model_used": f_res.get("model_used"),
        }

    transport_info = None
    if t_res and t_res.get("success"):
        transport_info = {
            "total_cost": t_res.get("total_cost"),
            "transport_fare": t_res.get("transport_fare"),
            "labor_cost": t_res.get("labor_cost"),
            "distance_km": t_res.get("distance_km"),
            "distance_source": t_res.get("distance_source"),
            "distance_method": t_res.get("distance_method"),
            "vehicle": t_res.get("vehicle"),
            "assumptions_en": t_res.get("assumptions_en"),
            "assumptions_te": t_res.get("assumptions_te"),
        }

    calc_result = compare_sell_options(
        quantity=qty,
        variety=variety,
        market=market,
        broker_offer=broker,
        observed_quote=observed_quote,
        forecast_quote=forecast_quote,
        transport_info=transport_info,
        wait_days=wait,
        storage_cost_per_qtl_day=storage,
        requested_options=options,
    )

    return {
        **state,
        "comparison_result": calc_result,
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 6: BUILD & VALIDATE RESPONSE
# ─────────────────────────────────────────────────────────────────────────────
def node_build_response(state: WorkflowState) -> WorkflowState:
    lang = state.get("language", "en")
    needs_input = state.get("needs_input", False)
    missing = state.get("missing_fields") or []
    fu_en = state.get("follow_up_question")
    fu_te = state.get("follow_up_question_te")

    # Construct context object to return to frontend
    updated_context = ConversationContext(
        variety=state.get("variety"),
        quantity_quintals=state.get("quantity_quintals"),
        origin_location=state.get("origin_location"),
        destination_market=state.get("destination_market") or "Guntur APMC",
        vehicle=state.get("vehicle"),
        broker_offer_price=state.get("broker_offer_price"),
        wait_days=state.get("wait_days"),
        storage_cost_per_qtl_day=state.get("storage_cost_per_qtl_day"),
        requested_options=state.get("requested_options"),
        language=lang,
        field_sources=state.get("field_sources") or {},
    )

    if needs_input:
        exp_en = f"To provide a complete sell comparison, I need one more detail: {fu_en}"
        exp_te = f"ఖచ్చితమైన విశ్లేషణ కోసం మరింత సమాచారం అవసరం: {fu_te}"
        resp = AssistantCompareResponse(
            status="needs_input",
            language=lang,
            explanation=exp_en,
            explanation_te=exp_te,
            options=[],
            unavailable_options=[],
            missing_fields=missing,
            follow_up_question=fu_en,
            follow_up_question_te=fu_te,
            context=updated_context,
        )
        return {
            **state,
            "final_response": resp.model_dump(),
            "status": "needs_input",
        }

    calc = state.get("comparison_result") or {}
    opts_raw = calc.get("options") or []
    unavail_raw = calc.get("unavailable_options") or []

    opts = [OptionResult(**o) for o in opts_raw]
    unavail = [UnavailableOption(**u) for u in unavail_raw]

    # Generate bilingual explanation based on structured numbers
    exp_en, exp_te = generate_bilingual_explanation(
        comparison=calc,
        quantity=state.get("quantity_quintals") or 0.0,
        variety=state.get("variety") or "Teja S17",
        market=state.get("destination_market") or "Guntur APMC",
        language=lang,
        mock_mode=state.get("mock_mode"),
    )

    # Determine overall status: complete if all requested evaluated, else partial
    req_opts = state.get("requested_options") or []
    status = "complete" if len(opts) == len(req_opts) else "partial"

    resp = AssistantCompareResponse(
        status=status,
        language=lang,
        explanation=exp_en,
        explanation_te=exp_te,
        options=opts,
        unavailable_options=unavail,
        highest_option_id=calc.get("highest_option_id"),
        net_advantage=calc.get("net_advantage"),
        net_advantage_vs=calc.get("net_advantage_vs"),
        is_informational=calc.get("is_informational", False),
        informational_reason=calc.get("informational_reason"),
        informational_reason_te=calc.get("informational_reason_te"),
        source_dates=calc.get("source_dates") or {},
        assumptions=calc.get("assumptions") or [],
        assumptions_te=calc.get("assumptions_te") or [],
        missing_fields=[],
        follow_up_question=None,
        follow_up_question_te=None,
        context=updated_context,
    )

    return {
        **state,
        "final_response": resp.model_dump(),
        "status": status,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH COMPILATION
# ─────────────────────────────────────────────────────────────────────────────
def build_assistant_graph():
    builder = StateGraph(WorkflowState)

    builder.add_node("parse_message", node_parse_message)
    builder.add_node("merge_context", node_merge_context)
    builder.add_node("decide_actionable", node_decide_actionable)
    builder.add_node("fetch_data", node_fetch_data)
    builder.add_node("calculate_options", node_calculate_options)
    builder.add_node("build_response", node_build_response)

    # Linear flow until conditional routing
    builder.add_edge(START, "parse_message")
    builder.add_edge("parse_message", "merge_context")
    builder.add_edge("merge_context", "decide_actionable")

    # Conditional routing: if missing input -> build_response; else -> fetch_data
    builder.add_conditional_edges(
        "decide_actionable",
        route_after_decision,
        {
            "build_response": "build_response",
            "fetch_data": "fetch_data",
        }
    )

    builder.add_edge("fetch_data", "calculate_options")
    builder.add_edge("calculate_options", "build_response")
    builder.add_edge("build_response", END)

    return builder.compile()


# Singleton compiled graph
_compiled_graph = None


def get_assistant_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_assistant_graph()
    return _compiled_graph


def run_assistant_workflow(
    message: str,
    language: str = "en",
    context: Optional[ConversationContext] = None,
    mock_mode: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Main entrypoint for the assistant workflow.
    Checks availability and runs the compiled LangGraph.
    """
    # Check if LLM is configured or mock mode enabled
    if not is_llm_available(mock_mode=mock_mode):
        msg_en = (
            "The AI Market Assistant is currently unavailable because no LLM provider key is configured. "
            "Please configure GEMINI_API_KEY or OPENAI_API_KEY in your backend environment, "
            "or run with MOCK_LLM=1 for local offline demonstration."
        )
        msg_te = (
            "LLM API కీ అందుబాటులో లేనందున AI మార్కెట్ అసిస్టెంట్ తాత్కాలికంగా అందుబాటులో లేదు. "
            "దయచేసి GEMINI_API_KEY లేదా OPENAI_API_KEY కాన్ఫిగర్ చేయండి, లేదా MOCK_LLM=1 తో రన్ చేయండి."
        )
        ctx = context or ConversationContext()
        return AssistantCompareResponse(
            status="unavailable",
            language=language,
            explanation=msg_en,
            explanation_te=msg_te,
            options=[],
            unavailable_options=[],
            context=ctx,
        ).model_dump()

    graph = get_assistant_graph()
    initial_state: WorkflowState = {
        "raw_message": message,
        "language": language,
        "existing_context": context.model_dump() if context else {},
        "mock_mode": mock_mode,
    }

    result = graph.invoke(initial_state)
    return result.get("final_response", {})
