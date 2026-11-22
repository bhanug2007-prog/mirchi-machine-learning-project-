"""
LLM Provider Abstraction for the Market Research Assistant.
Supports:
1. Google Gemini (via google.generativeai) when GEMINI_API_KEY or GOOGLE_API_KEY is set.
2. OpenAI (via openai client) when OPENAI_API_KEY is set.
3. Deterministic Mock Mode when MOCK_LLM=1, MOCK_SERVICES=1, or mock_mode=True.
4. Clean 'unavailable' state when no key is set and mock mode is off.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from .parser import parse_farmer_message


class LLMUnavailableError(Exception):
    """Raised when LLM provider is requested but no API key is configured."""
    pass


def get_active_provider() -> str:
    """Returns 'gemini', 'openai', 'mock', or 'none'."""
    if os.environ.get("MOCK_LLM") == "1" or os.environ.get("MOCK_SERVICES") == "1":
        return "mock"
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ASSISTANT_RULE_MODE") == "1":
        return "mock"
    return "none"


def is_llm_available(mock_mode: Optional[bool] = None) -> bool:
    if mock_mode is True:
        return True
    return get_active_provider() in ("gemini", "openai", "mock")


def extract_fields_with_llm(
    message: str,
    language: str = "en",
    mock_mode: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Extract structured selling intent and fields from farmer message.
    Uses LLM when available; falls back to robust regex parser.
    """
    if mock_mode or get_active_provider() == "mock":
        return parse_farmer_message(message, language)

    provider = get_active_provider()
    if provider == "none":
        # If no key, rule-based fallback can be used if mock requested or raise error
        return parse_farmer_message(message, language)

    prompt = f"""
You are an agri-market intelligence entity extraction assistant for Indian chilli farmers.
Analyze the farmer's question in English or Telugu.
Extract ONLY the following fields into valid JSON:
{{
  "variety": string or null (commercial chilli variety, e.g. Teja S17, 334 Sannam, Byadgi, 341, DD Deluxe, Red New, Red),
  "quantity_quintals": number or null (volume in quintals, 1 quintal = 100kg),
  "origin_location": string or null (farmer's village or 6-digit AP pincode, e.g. Inkollu, Pavulur, 523167),
  "destination_market": string or null (destination market, default "Guntur APMC"),
  "broker_offer_price": number or null (offered price in Rs per quintal),
  "wait_days": integer or null (number of days to wait in cold storage, 1 to 7),
  "storage_cost_per_qtl_day": number or null (storage cost in Rs per quintal per day),
  "requested_options": list of strings among ["broker_now", "mandi_now", "wait_mandi"],
  "language": "en" or "te"
}}
Return ONLY JSON. Do not add markdown code fences or conversational text.

Farmer Message:
"{message}"
"""

    if provider == "gemini":
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            raw = response.text.strip()
            # Clean possible markdown fences
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'```$', '', raw).strip()
            parsed = json.loads(raw)
            # Combine with regex for safety
            rule_parsed = parse_farmer_message(message, language)
            for k, v in rule_parsed.items():
                if parsed.get(k) is None and v is not None:
                    parsed[k] = v
            return parsed
        except Exception:
            return parse_farmer_message(message, language)

    elif provider == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), timeout=8.0)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You extract agricultural market entities into pure JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = resp.choices[0].message.content.strip()
            parsed = json.loads(content)
            rule_parsed = parse_farmer_message(message, language)
            for k, v in rule_parsed.items():
                if parsed.get(k) is None and v is not None:
                    parsed[k] = v
            return parsed
        except Exception:
            return parse_farmer_message(message, language)

    return parse_farmer_message(message, language)


def generate_bilingual_explanation(
    comparison: Dict[str, Any],
    quantity: float,
    variety: str,
    market: str,
    language: str = "en",
    mock_mode: Optional[bool] = None
) -> Tuple[str, str]:
    """
    Generate bilingual explanation based strictly on deterministic calculation results.
    Never invents numbers. Returns (explanation_en, explanation_te).
    """
    options = comparison.get("options", [])
    highest_id = comparison.get("highest_option_id")
    net_adv = comparison.get("net_advantage")
    vs_id = comparison.get("net_advantage_vs")
    is_info = comparison.get("is_informational", False)
    info_reason = comparison.get("informational_reason")

    opt_map = {o["id"]: o for o in options}
    broker_opt = opt_map.get("broker_now")
    mandi_opt = opt_map.get("mandi_now")
    wait_opt = opt_map.get("wait_mandi")

    # Deterministic templates:
    lines_en: List[str] = []
    lines_te: List[str] = []

    if is_info:
        lines_en.append(f"⚠️ Notice: {info_reason or 'Data is for informational purposes only.'}")
        lines_te.append(f"⚠️ గమనిక: తాజా మార్కెట్ సమాచారం సమాచార ప్రయోజనాల కొరకు మాత్రమే అందించబడింది.")

    # Option descriptions
    if broker_opt:
        lines_en.append(
            f"• Broker Now: Gross ₹{broker_opt['gross_proceeds']:,.0f} (₹{broker_opt['price_per_quintal']:,.0f}/qtl, farmgate cash)."
        )
        lines_te.append(
            f"• స్థానిక బ్రోకర్: మొత్తం ₹{broker_opt['gross_proceeds']:,.0f} (క్వింటాలుకు ₹{broker_opt['price_per_quintal']:,.0f}, తక్షణ నగదు)."
        )

    if mandi_opt:
        lines_en.append(
            f"• Mandi Now ({market}): Gross ₹{mandi_opt['gross_proceeds']:,.0f} @ observed rate ₹{mandi_opt['price_per_quintal']:,.0f}/qtl, "
            f"less ₹{mandi_opt['total_costs']:,.0f} estimated logistics (transport & Hamali labor), yielding net ₹{mandi_opt['net_proceeds']:,.0f}."
        )
        lines_te.append(
            f"• {market} మార్కెట్: స్థానిక ధర ₹{mandi_opt['price_per_quintal']:,.0f} చొప్పున మొత్తం ₹{mandi_opt['gross_proceeds']:,.0f}, "
            f"అంచనా రవాణా మరియు హమాలీ ఖర్చులు ₹{mandi_opt['total_costs']:,.0f} తీసివేయగా నికర ఆదాయం ₹{mandi_opt['net_proceeds']:,.0f}."
        )

    if wait_opt:
        details = wait_opt.get("details", {})
        wait_days = details.get("wait_days", 7)
        lines_en.append(
            f"• Wait {wait_days} Days ({market}): Gross ₹{wait_opt['gross_proceeds']:,.0f} @ forecast rate ₹{wait_opt['price_per_quintal']:,.0f}/qtl ({details.get('model_used', 'ML model')}), "
            f"less ₹{wait_opt['storage_cost']:,.0f} storage cost and ₹{wait_opt['transport_cost'] + wait_opt['labor_cost']:,.0f} logistics, yielding net ₹{wait_opt['net_proceeds']:,.0f}."
        )
        lines_te.append(
            f"• {wait_days} రోజులు వేచి ఉండండి: అంచనా ధర ₹{wait_opt['price_per_quintal']:,.0f} చొప్పున మొత్తం ₹{wait_opt['gross_proceeds']:,.0f}, "
            f"నిల్వ ఖర్చు ₹{wait_opt['storage_cost']:,.0f} మరియు రవాణా/హమాలీ ఖర్చులు తీసివేయగా నికర ఆదాయం ₹{wait_opt['net_proceeds']:,.0f}."
        )

    # Conclusion & recommendation
    if highest_id and net_adv is not None:
        best_name = opt_map[highest_id]["name"]
        vs_name = opt_map[vs_id]["name"] if vs_id and vs_id in opt_map else "the next best option"
        
        if highest_id == "wait_mandi":
            lines_en.append(
                f"Recommendation: Waiting offers the highest estimated return! After accounting for ₹{wait_opt['storage_cost']:,.0f} in storage costs and logistics, "
                f"you gain an estimated ₹{net_adv:,.0f} more than {vs_name}."
            )
            lines_te.append(
                f"సిఫారసు: వేచి ఉండడం వల్ల అత్యధిక లాభం వస్తుందని అంచనా! నిల్వ ఖర్చులు (₹{wait_opt['storage_cost']:,.0f}) మరియు రవాణా ఖర్చులు తీసివేసిన తర్వాత కూడా, "
                f"మీకు ఇతర ఎంపిక కంటే సుమారు ₹{net_adv:,.0f} అదనపు నికర లాభం లభిస్తుంది."
            )
        elif highest_id == "mandi_now":
            lines_en.append(
                f"Recommendation: Transport to {market} now! Even after logistics costs of ₹{mandi_opt['total_costs']:,.0f}, "
                f"selling at the yard gives you ₹{net_adv:,.0f} higher net proceeds than {vs_name}."
            )
            lines_te.append(
                f"సిఫారసు: {market} మార్కెట్‌కు వెళ్లండి! రవాణా ఖర్చులు (₹{mandi_opt['total_costs']:,.0f}) పోను, "
                f"బ్రోకర్‌కు అమ్మడం కంటే మీకు ₹{net_adv:,.0f} అదనపు లాభం లభిస్తుంది."
            )
        elif highest_id == "broker_now":
            lines_en.append(
                f"Recommendation: Sell to the local broker now. Transport costs or projected price drops mean transporting or waiting yields less net profit."
            )
            lines_te.append(
                f"సిఫారసు: స్థానిక బ్రోకర్‌కు ఇప్పుడే అమ్మడం మంచిది. రవాణా ఖర్చులు లేదా ధరల తగ్గుదల వల్ల మార్కెట్‌కు వెళ్లడం కంటే ఇక్కడే అమ్మడం లాభదాయకం."
            )
    elif is_info:
        lines_en.append("This comparison is provided for informational review. No active sell-or-wait recommendation is given for outdated quotes.")
        lines_te.append("పాత మార్కెట్ ధరల ఆధారంగా ఎటువంటి ప్రత్యక్ష సిఫారసు చేయబడలేదు. ఇది కేవలం మీ పరిశీలన కొరకు మాత్రమే.")

    exp_en = "\n".join(lines_en)
    exp_te = "\n".join(lines_te)
    return exp_en, exp_te
