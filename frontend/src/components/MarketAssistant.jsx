import { useState } from "react";

const DEMO_QUESTIONS = {
  en: "I have 60 quintals of Teja S17 chilli in Inkollu. A broker is offering ₹16,000 per quintal. Should I sell to him, take it to Guntur mandi, or wait seven days?",
  te: "నా దగ్గర ఇంకొల్లులో 60 క్వింటాళ్ల తేజా S17 మిర్చి ఉంది. బ్రోకర్ క్వింటాలుకు ₹16,000 ఇస్తానంటున్నాడు. ఆయనకు అమ్మేయాలా, గుంటూరు మార్కెట్ కి తీసుకెళ్లాలా, లేక 7 రోజులు ఆగాలా?"
};

export default function MarketAssistant({ api, lang = "en" }) {
  const [message, setMessage] = useState("");
  const [context, setContext] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [latestResponse, setLatestResponse] = useState(null);

  const isTe = lang === "te";

  const handleSend = async (textToSend) => {
    const query = (textToSend || message).trim();
    if (!query || loading) return;

    setLoading(true);
    setError(null);

    const newHistoryItem = {
      role: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
    setHistory(prev => [...prev, newHistoryItem]);

    try {
      const payload = {
        message: query,
        language: lang,
        context: context || {}
      };

      const res = await fetch(`${api}/api/assistant/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (${res.status})`);
      }

      const data = await res.json();
      setLatestResponse(data);
      if (data.context) {
        setContext(data.context);
      }

      setHistory(prev => [
        ...prev,
        {
          role: "assistant",
          data: data,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);

      setMessage("");
    } catch (err) {
      setError(err.message || "Failed to reach market assistant service.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setContext(null);
    setHistory([]);
    setLatestResponse(null);
    setMessage("");
    setError(null);
  };

  const handleApplyDemo = () => {
    const demo = DEMO_QUESTIONS[lang] || DEMO_QUESTIONS.en;
    setMessage(demo);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto w-full">
      {/* ── Header Title Banner ── */}
      <div className="bg-[#0F1322] border border-[#1E293B] rounded-2xl p-6 relative overflow-hidden shadow-sm">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.08)_0,transparent_70%)] pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="text-xs px-2.5 py-0.5 rounded-full font-medium tracking-wider bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/30">
                Agentic Decision Support
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-medium tracking-wider bg-[#06B6D4]/15 text-[#06B6D4] border border-[#06B6D4]/30 font-cyber">
                LangGraph Bounded Engine
              </span>
            </div>
            <h2 className="text-2xl font-black text-white tracking-wide font-cyber flex items-center gap-2">
              <span>🌶️</span>
              <span>{isTe ? "AI మార్కెట్ రీసెర్చ్ అసిస్టెంట్" : "AI Market Research Assistant"}</span>
            </h2>
            <p className="text-slate-400 text-xs md:text-sm mt-1 noto-telugu">
              {isTe
                ? "మిర్చి రైతుల కోసం బ్రోకర్ ధర, గుంటూరు యార్డు రవాణా ఖర్చులు మరియు 7 రోజుల నిల్వ లాభాల సమగ్ర పోలిక."
                : "Real-time decision intelligence: Compare Farmgate Broker vs Guntur APMC Yard vs Cold Storage Holding."}
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <button
              onClick={handleApplyDemo}
              className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 hover:text-emerald-300 text-xs font-semibold rounded-xl border border-emerald-500/30 transition flex items-center gap-1.5 active:scale-95 shadow-sm"
              title="Fill example question"
            >
              <span>💡</span>
              <span>{isTe ? "నమూనా ప్రశ్న" : "Try Demo Question"}</span>
            </button>
            {history.length > 0 && (
              <button
                onClick={handleReset}
                className="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold rounded-xl border border-[#1E293B] transition active:scale-95"
              >
                {isTe ? "కొత్త ప్రశ్న" : "Reset Context"}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Active Conversation History ── */}
      {history.length > 0 && (
        <div className="space-y-4">
          {history.map((item, idx) => (
            <div key={idx} className="space-y-3">
              {item.role === "user" ? (
                <div className="flex justify-end">
                  <div className="max-w-2xl bg-emerald-950/20 border border-emerald-500/30 rounded-2xl p-4 text-emerald-100 text-sm shadow-md">
                    <div className="flex items-center justify-between gap-4 mb-1 text-[10px] text-emerald-400 font-cyber font-bold">
                      <span>FARMER QUERY</span>
                      <span>{item.timestamp}</span>
                    </div>
                    <p className="leading-relaxed noto-telugu">{item.text}</p>
                  </div>
                </div>
              ) : (
                <div className="flex justify-start">
                  <div className="w-full space-y-4">
                    {/* Render response card */}
                    <AssistantResponseView
                      response={item.data}
                      lang={lang}
                      onFollowUpClick={(fuText) => {
                        setMessage(fuText);
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── Follow-Up Suggestion Banner (If status is needs_input) ── */}
      {latestResponse && latestResponse.status === "needs_input" && (
        <div className="bg-amber-950/20 border border-amber-500/30 rounded-2xl p-4 text-amber-200 flex items-start gap-3 shadow-md animate-pulse">
          <span className="text-xl">⚠️</span>
          <div className="flex-1">
            <p className="text-xs font-bold font-cyber uppercase tracking-wider text-amber-400 mb-0.5">
              {isTe ? "అదనపు సమాచారం అవసరం" : "Additional Detail Needed"}
            </p>
            <p className="text-sm font-semibold text-white noto-telugu">
              {isTe
                ? latestResponse.follow_up_question_te || latestResponse.follow_up_question
                : latestResponse.follow_up_question}
            </p>
          </div>
        </div>
      )}

      {/* ── Error Banner ── */}
      {error && (
        <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-2xl text-red-300 text-xs font-semibold flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* ── Main Input Box ── */}
      <div className="bg-[#0F1322] border border-[#1E293B] rounded-2xl p-4 shadow-sm relative">
        <label className="text-[10px] font-cyber font-bold uppercase tracking-wider text-slate-500 block mb-2">
          {isTe ? "మీ ప్రశ్నను ఇక్కడ అడగండి (ఇంగ్లీష్ లేదా తెలుగు)" : "Ask your market question (English or Telugu)"}
        </label>
        
        <div className="flex flex-col md:flex-row gap-3">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={
              isTe
                ? "ఉదా: నా దగ్గర ఇంకొల్లులో 60 క్వింటాళ్ల తేజా S17 మిర్చి ఉంది. బ్రోకర్ ₹16,000 ఇస్తానంటున్నాడు. ఆయనకు అమ్మాలా, గుంటూరు వెళ్లాలా, లేక 7 రోజులు ఆగాలా?"
                : "e.g. I have 60 quintals of Teja S17 chilli in Inkollu. A broker is offering ₹16,000 per quintal. Should I sell to him, take it to Guntur mandi, or wait seven days?"
            }
            rows={3}
            maxLength={2000}
            className="flex-1 bg-slate-900 border border-[#1E293B] focus:border-[#10B981]/50 focus:ring-1 focus:ring-[#10B981]/30 rounded-xl p-3.5 text-white text-sm outline-none transition resize-none font-medium noto-telugu placeholder:text-slate-600"
          />

          <div className="flex md:flex-col justify-between items-end gap-2">
            <span className="text-[10px] text-slate-500 font-cyber">
              {message.length} / 2000
            </span>
            <button
              onClick={() => handleSend()}
              disabled={loading || !message.trim()}
              className="w-full md:w-32 py-3 px-4 bg-[#10B981] hover:bg-emerald-400 text-black font-extrabold rounded-xl text-sm transition duration-300 disabled:opacity-40 active:scale-95 shadow-md shadow-emerald-950/20 flex items-center justify-center gap-2 font-cyber"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                  <span>...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>{isTe ? "విశ్లేషించు" : "Analyze"}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Active Context Indicators */}
        {context && Object.keys(context).some(k => context[k] !== null && k !== "field_sources" && k !== "language" && k !== "requested_options") && (
          <div className="mt-3 pt-3 border-t border-[#1E293B]/70 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
            <span className="text-slate-500 font-cyber uppercase tracking-wider font-bold">Active Context:</span>
            {context.variety && (
              <span className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-lg text-slate-200">
                Variety: <strong className="text-emerald-400">{context.variety}</strong>
              </span>
            )}
            {context.quantity_quintals && (
              <span className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-lg text-slate-200">
                Qty: <strong className="text-cyan-400">{context.quantity_quintals} qtl</strong>
              </span>
            )}
            {context.origin_location && (
              <span className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-lg text-slate-200">
                Origin: <strong className="text-slate-200">{context.origin_location}</strong>
              </span>
            )}
            {context.broker_offer_price && (
              <span className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-lg text-slate-200">
                Broker: <strong className="text-amber-400">₹{context.broker_offer_price.toLocaleString("en-IN")}/qtl</strong>
              </span>
            )}
            {context.wait_days && (
              <span className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-lg text-slate-200">
                Wait: <strong className="text-purple-400">{context.wait_days} Days</strong>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sub-component to render structured assistant response ──
function AssistantResponseView({ response, lang }) {
  if (!response) return null;
  const isTe = lang === "te";

  // Check if status is unavailable
  if (response.status === "unavailable") {
    return (
      <div className="bg-[#0F1322] border border-amber-500/30 rounded-2xl p-6 space-y-3">
        <div className="flex items-center gap-2 text-amber-400">
          <span className="text-xl">⚠️</span>
          <h4 className="font-bold text-sm uppercase tracking-wider font-cyber">Assistant Service Unavailable</h4>
        </div>
        <p className="text-slate-300 text-sm leading-relaxed noto-telugu">
          {isTe ? response.explanation_te || response.explanation : response.explanation}
        </p>
        <div className="bg-slate-900/80 rounded-xl p-3 text-xs text-slate-400 border border-slate-800">
          <p className="font-semibold text-slate-300 mb-1">How to enable locally:</p>
          <code className="text-emerald-400">export MOCK_LLM=1</code> (for offline deterministic testing) or configure <code className="text-cyan-400">GEMINI_API_KEY</code>.
        </div>
      </div>
    );
  }

  const {
    options = [],
    unavailable_options = [],
    highest_option_id,
    net_advantage,
    net_advantage_vs,
    is_informational,
    informational_reason,
    informational_reason_te,
    explanation,
    explanation_te,
    source_dates = {},
    assumptions = [],
    assumptions_te = []
  } = response;

  const expl = isTe ? (explanation_te || explanation) : explanation;
  const infoText = isTe ? (informational_reason_te || informational_reason) : informational_reason;

  return (
    <div className="bg-[#0F1322] border border-[#1E293B] rounded-2xl p-6 space-y-6 shadow-xl">
      {/* ── Status Banner & Freshness Notice ── */}
      {is_informational && (
        <div className="p-4 bg-amber-950/20 border border-amber-500/30 rounded-xl text-amber-300 text-xs flex items-start gap-3">
          <span className="text-lg">ℹ️</span>
          <div>
            <p className="font-bold font-cyber uppercase tracking-wider text-amber-400 mb-0.5">
              {isTe ? "సమాచార పరిశీలన మాత్రమే" : "Informational Notice"}
            </p>
            <p className="noto-telugu leading-relaxed">{infoText}</p>
          </div>
        </div>
      )}

      {/* ── Recommendation Callout (If actionable) ── */}
      {!is_informational && highest_option_id && net_advantage && (
        <div className="p-4 bg-[#10B981]/10 border border-[#10B981]/40 rounded-2xl flex items-center justify-between flex-wrap gap-3 shadow-[0_0_20px_rgba(16,185,129,0.08)]">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏆</span>
            <div>
              <p className="text-xs text-emerald-400 font-cyber font-extrabold uppercase tracking-widest">
                {isTe ? "సిఫారసు చేయబడిన సరైన ఎంపిక" : "Recommended Optimal Choice"}
              </p>
              <h4 className="text-base font-bold text-white tracking-tight">
                {options.find(o => o.id === highest_option_id)?.name || highest_option_id}
              </h4>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 uppercase font-cyber block">Net Extra Gain</span>
            <span className="text-xl font-black text-[#10B981] font-cyber">
              +₹{net_advantage.toLocaleString("en-IN")}
            </span>
          </div>
        </div>
      )}

      {/* ── Compact Selling Options Grid ── */}
      {options.length > 0 && (
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <h4 className="text-xs font-cyber font-bold uppercase tracking-wider text-slate-400">
              {isTe ? "అమ్మకపు ఎంపికల విశ్లేషణ" : "Evaluated Selling Options"}
            </h4>
            <span className="text-[10px] text-slate-500 font-cyber">
              {options.length} options evaluated
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {options.map((opt) => {
              const isHighest = opt.id === highest_option_id && !is_informational;
              return (
                <div
                  key={opt.id}
                  className={`rounded-2xl p-5 border relative overflow-hidden transition-all duration-300 flex flex-col justify-between ${
                    isHighest
                      ? "bg-[#10B981]/5 border-[#10B981]/50 shadow-[0_0_25px_rgba(16,185,129,0.12)] ring-1 ring-[#10B981]/30"
                      : "bg-slate-900/60 border-[#1E293B]"
                  }`}
                >
                  {isHighest && (
                    <div className="absolute top-0 right-0 bg-[#10B981] text-black text-[9px] font-black font-cyber px-2.5 py-0.5 rounded-bl-lg tracking-widest uppercase">
                      Best Net Return
                    </div>
                  )}

                  <div>
                    {/* Header: Title and Price Basis Badge */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h5 className="font-bold text-sm text-white tracking-tight leading-snug">
                        {isTe && opt.name_te ? opt.name_te : opt.name}
                      </h5>
                    </div>

                    <div className="flex items-center gap-2 mb-3">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-cyber uppercase tracking-wider font-semibold border ${
                        opt.price_type === "offered"
                          ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                          : opt.price_type === "forecast"
                          ? "bg-purple-500/10 text-purple-400 border-purple-500/20"
                          : "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
                      }`}>
                        {opt.price_type === "offered"
                          ? "Offered Price"
                          : opt.price_type === "forecast"
                          ? "7D Forecast"
                          : "Observed Quote"}
                      </span>
                      {opt.is_estimated && (
                        <span className="text-[10px] text-slate-500 font-cyber">
                          (Estimated costs)
                        </span>
                      )}
                    </div>

                    {/* Net Proceeds Display */}
                    <div className="mb-4">
                      <span className="text-[10px] text-slate-400 uppercase tracking-widest font-cyber block mb-0.5">
                        {isTe ? "నికర లాభం (Net Proceeds)" : "Total Net Proceeds"}
                      </span>
                      <span className={`text-2xl font-black font-cyber ${
                        isHighest ? "text-[#10B981] glow-text-green" : "text-white"
                      }`}>
                        ₹{opt.net_proceeds.toLocaleString("en-IN")}
                      </span>
                    </div>

                    {/* Cost Breakdown Table */}
                    <div className="space-y-1.5 text-xs border-t border-[#1E293B] pt-3 text-slate-400">
                      <div className="flex justify-between">
                        <span>Rate:</span>
                        <span className="font-cyber font-semibold text-slate-200">
                          ₹{opt.price_per_quintal.toLocaleString("en-IN")}/qtl
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Gross Revenue:</span>
                        <span className="font-cyber text-slate-300">
                          ₹{opt.gross_proceeds.toLocaleString("en-IN")}
                        </span>
                      </div>
                      {opt.transport_cost > 0 && (
                        <div className="flex justify-between text-amber-400/90">
                          <span>Freight & Haulage:</span>
                          <span className="font-cyber">-₹{opt.transport_cost.toLocaleString("en-IN")}</span>
                        </div>
                      )}
                      {opt.labor_cost > 0 && (
                        <div className="flex justify-between text-amber-400/90">
                          <span>Hamali (Labor):</span>
                          <span className="font-cyber">-₹{opt.labor_cost.toLocaleString("en-IN")}</span>
                        </div>
                      )}
                      {opt.storage_cost > 0 && (
                        <div className="flex justify-between text-purple-400/90">
                          <span>Cold Storage:</span>
                          <span className="font-cyber">-₹{opt.storage_cost.toLocaleString("en-IN")}</span>
                        </div>
                      )}
                      <div className="flex justify-between pt-1 border-t border-slate-800 font-bold text-slate-200">
                        <span>Total Deductions:</span>
                        <span className="font-cyber">
                          {opt.total_costs > 0 ? `-₹${opt.total_costs.toLocaleString("en-IN")}` : "₹0"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Unavailable Options ── */}
      {unavailable_options.length > 0 && (
        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800 text-xs space-y-1.5">
          <p className="text-[10px] font-cyber font-bold uppercase text-slate-500">
            {isTe ? "లెక్కించలేని ఎంపికలు" : "Unavailable Options for Current Query"}
          </p>
          {unavailable_options.map((u, i) => (
            <div key={i} className="text-slate-400 flex items-center gap-2">
              <span className="text-slate-600">•</span>
              <strong className="text-slate-300">{u.name}:</strong>
              <span>{isTe && u.reason_te ? u.reason_te : u.reason}</span>
            </div>
          ))}
        </div>
      )}

      {/* ── Narrative Explanation Text ── */}
      {expl && (
        <div className="bg-slate-900/50 rounded-xl p-4 border border-[#1E293B]">
          <p className="text-[10px] font-cyber font-bold uppercase text-slate-500 mb-2">
            {isTe ? "విశ్లేషణ సారాంశం" : "Market Intelligence Summary"}
          </p>
          <div className="text-xs text-slate-300 leading-relaxed noto-telugu whitespace-pre-line space-y-1">
            {expl}
          </div>
        </div>
      )}

      {/* ── Source Dates & Assumptions Footnote ── */}
      <div className="pt-3 border-t border-[#1E293B]/70 grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px] text-slate-500">
        <div>
          <span className="font-cyber font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Verified Source Data:
          </span>
          <p>• Latest Quote Date: <span className="text-slate-300">{source_dates.quote_date || "N/A"}</span></p>
          {source_dates.forecast_target_date && (
            <p>
              • Forecast Horizon: <span className="text-slate-300">{source_dates.forecast_target_date}</span> ({source_dates.forecast_model || "ML Model"})
            </p>
          )}
        </div>

        <div>
          <span className="font-cyber font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Cost & Freight Basis:
          </span>
          {(isTe ? assumptions_te : assumptions).map((a, i) => (
            <p key={i}>• {a}</p>
          ))}
        </div>
      </div>
    </div>
  );
}
