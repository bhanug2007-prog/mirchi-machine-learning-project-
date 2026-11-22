"""
Pydantic schemas for the MirchiMandi Agentic AI Market Research Assistant.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConversationContext(BaseModel):
    """
    Request-scoped memory passed between frontend and backend.
    Revalidated on every request.
    """
    variety: Optional[str] = Field(None, description="Commercial chilli variety (e.g. Teja S17, 334 Sannam)")
    quantity_quintals: Optional[float] = Field(None, description="Volume of chilli in quintals (1 quintal = 100 kg)")
    origin_location: Optional[str] = Field(None, description="Village name or 6-digit postal code")
    destination_market: Optional[str] = Field("Guntur APMC", description="Destination APMC market yard")
    vehicle: Optional[str] = Field(None, description="Logistics vehicle (Tractor, Trolley, Truck)")
    broker_offer_price: Optional[float] = Field(None, description="Broker offered price in Rs per quintal")
    wait_days: Optional[int] = Field(None, description="Number of days to hold in cold storage (1-7)")
    storage_cost_per_qtl_day: Optional[float] = Field(None, description="Storage cost in Rs per quintal per day")
    requested_options: Optional[List[str]] = Field(
        default_factory=lambda: ["broker_now", "mandi_now", "wait_mandi"],
        description="Options the farmer wants to evaluate: broker_now, mandi_now, wait_mandi"
    )
    language: Optional[str] = Field("en", description="User's preferred language ('en' or 'te')")
    field_sources: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Tracks origin of each field: 'user_input', 'conversation_context', or 'app_default'"
    )


class AssistantCompareRequest(BaseModel):
    """Request payload for POST /api/assistant/compare"""
    message: str = Field(..., max_length=2000, description="Farmer message in English or Telugu")
    language: str = Field("en", description="Preferred response language: 'en' or 'te'")
    context: Optional[ConversationContext] = Field(default_factory=ConversationContext)
    mock_mode: Optional[bool] = Field(None, description="Force deterministic mock mode for offline testing/demo")


class OptionResult(BaseModel):
    """Detailed evaluation of a single selling option."""
    id: str = Field(..., description="Unique option identifier: 'broker_now', 'mandi_now', or 'wait_mandi'")
    name: str = Field(..., description="Human-readable option title in English")
    name_te: Optional[str] = Field(None, description="Human-readable option title in Telugu")
    price_per_quintal: float = Field(..., description="Base rate in Rs per quintal")
    price_type: str = Field(..., description="'offered', 'observed', or 'forecast'")
    gross_proceeds: float = Field(..., description="Total revenue before deductions (quantity * rate)")
    transport_cost: float = Field(0.0, description="Logistics and haulage cost in Rs")
    storage_cost: float = Field(0.0, description="Holding and cold storage cost in Rs")
    labor_cost: float = Field(0.0, description="Loading/unloading labor (Hamali) in Rs")
    total_costs: float = Field(0.0, description="Sum of all applicable fees and deductions")
    net_proceeds: float = Field(..., description="Net cash in hand for the farmer (gross - total_costs)")
    is_estimated: bool = Field(False, description="True if any costs or prices rely on model estimates")
    is_available: bool = Field(True, description="True if this option could be fully evaluated")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata, vehicle, distance, etc.")


class UnavailableOption(BaseModel):
    """An option that could not be evaluated due to missing data or horizon limits."""
    id: str
    name: str
    name_te: Optional[str] = None
    reason: str
    reason_te: Optional[str] = None


class AssistantCompareResponse(BaseModel):
    """Typed response schema for the Market Assistant."""
    status: str = Field(..., description="'complete', 'partial', 'needs_input', or 'unavailable'")
    language: str = Field("en", description="Language of this response ('en' or 'te')")
    explanation: str = Field(..., description="Bilingual narrative explanation in English")
    explanation_te: Optional[str] = Field(None, description="Narrative explanation in Telugu")
    options: List[OptionResult] = Field(default_factory=list, description="List of evaluated selling options")
    unavailable_options: List[UnavailableOption] = Field(
        default_factory=list,
        description="Options that could not be computed and why"
    )
    highest_option_id: Optional[str] = Field(None, description="ID of the option with highest net proceeds")
    net_advantage: Optional[float] = Field(None, description="Extra profit in Rs of highest option vs second best")
    net_advantage_vs: Optional[str] = Field(None, description="ID of the option being compared against")
    is_informational: bool = Field(False, description="True if quote is stale (>2 days) or forecast expired")
    informational_reason: Optional[str] = Field(None, description="Why this comparison is informational only")
    informational_reason_te: Optional[str] = Field(None, description="Informational reason in Telugu")
    source_dates: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Observed quote date, forecast target date, forecast origin date"
    )
    assumptions: List[str] = Field(default_factory=list, description="Key assumptions in English")
    assumptions_te: List[str] = Field(default_factory=list, description="Key assumptions in Telugu")
    missing_fields: List[str] = Field(default_factory=list, description="Required fields still missing")
    follow_up_question: Optional[str] = Field(None, description="Focused follow-up question in English")
    follow_up_question_te: Optional[str] = Field(None, description="Focused follow-up question in Telugu")
    context: ConversationContext = Field(default_factory=ConversationContext, description="Updated context for frontend")
