import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// ─── TRANSLATIONS ──────────────────────────────────────
const T = {
  en: {
    appName:       "MirchiMandi",
    tagline:       "Real-time Chilli Price Intelligence",
    selectLang:    "Select Language",
    today:         "Today's Price",
    arrivals:      "Today's Arrivals",
    forecast:      "7-Day Forecast",
    recommendation:"Recommendation",
    calculator:    "Profit Calculator",
    allVarieties:  "All Varieties Today",
    compareMarkets:"Market Comparison",
    userSubmit:    "Submit Your Price",
    modelCompare:  "ML Model Comparison",
    variety:       "Variety",
    market:        "Market",
    quintal:       "Quintal",
    selling:       "Selling Price",
    broker:        "Broker Price",
    yourLoss:      "You are losing",
    yourGain:      "You will gain",
    calculate:     "Calculate",
    submit:        "Submit Price",
    loading:       "Loading...",
    sellToday:     "SELL TODAY",
    waitDays:      (d) => `WAIT ${d} DAYS`,
    priceRising:   "RISING ↑",
    priceFalling:  "FALLING ↓",
    perQtl:        "per Quintal",
    yourQtls:      "Your Quintals",
    brokerOffer:   "Broker's Offer (₹/qtl)",
    submit_variety:"Your Variety Name (e.g. Teja S17, 334)",
    submit_price:  "Price You Got (₹/qtl)",
    submit_date:   "Date",
    submit_name:   "Your Name (optional)",
    submit_note:   "Note (optional)",
    submitted_ok:  "✅ Price submitted! Thank you.",
    nav_home:      "Dashboard",
    nav_submit:    "Submit Price",
    nav_models:    "ML Models",
    nav_admin:     "Admin Dashboard",
    outdated_warning: (d) => `⚠️ Outdated Data: Showing price from ${d}`,
    latest_price:  "Latest Available Price",
  },
  te: {
    appName:       "మిర్చీమండి",
    tagline:       "నిజమైన ధర తెలుసుకోండి. నష్టపోకండి.",
    selectLang:    "భాష ఎంచుకోండి",
    today:         "నేటి ధర",
    arrivals:      "నేటి రాకలు",
    forecast:      "7 రోజుల అంచనా",
    recommendation:"సిఫారసు",
    calculator:    "లాభం లెక్కలు",
    allVarieties:  "అన్ని రకాల ధరలు",
    compareMarkets:"మార్కెట్ పోలిక",
    userSubmit:    "మీ ధర నమోదు చేయండి",
    modelCompare:  "ML మోడల్ పోలిక",
    variety:       "రకం",
    market:        "మార్కెట్",
    quintal:       "క్వింటాల్",
    selling:       "అమ్మకపు ధర",
    broker:        "బ్రోకర్ ధర",
    yourLoss:      "మీరు పోగొట్టుకుంటున్నారు",
    yourGain:      "మీరు లాభపడతారు",
    calculate:     "లెక్కించు",
    submit:        "ధర నమోదు చేయండి",
    loading:       "లోడ్ అవుతోంది...",
    sellToday:     "ఈరోజే అమ్మండి",
    waitDays:      (d) => `${d} రోజులు ఆగండి`,
    priceRising:   "పెరుగుతోంది ↑",
    priceFalling:  "తగ్గుతోంది ↓",
    perQtl:        "క్వింటాలుకు",
    yourQtls:      "మీ క్వింటాళ్ళు",
    brokerOffer:   "బ్రోకర్ ధర (₹/క్విం)",
    submit_variety:"మీ మిర్చి రకం (ఉదా: Teja S17, 334)",
    submit_price:  "మీకు వచ్చిన ధర (₹/క్విం)",
    submit_date:   "తేదీ",
    submit_name:   "మీ పేరు (ఐచ్ఛికం)",
    submit_note:   "గమనిక (ఐచ్ఛికం)",
    submitted_ok:  "✅ ధర నమోదైంది! ధన్యవాదాలు.",
    nav_home:      "డాష్‌బోర్డ్",
    nav_submit:    "ధర నమోదు",
    nav_models:    "ML మోడల్స్",
    nav_admin:     "అడ్మిన్ డాష్‌బోర్డ్",
    outdated_warning: (d) => `⚠️ పాత సమాచారం: ${d} నాటి ధర`,
    latest_price:  "చివరిగా అందుబాటులో ఉన్న ధర",
  }
};

// ─── HOOKS ─────────────────────────────────────────────
function useFetch(path, deps = []) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  useEffect(() => {
    if (!path) return;
    setLoading(true);
    fetch(`${API}${path}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, deps);
  return { data, loading, error };
}

// ─── SMALL COMPONENTS ──────────────────────────────────
function Card({ children, className = "", highlight = false, borderType = "default" }) {
  let borderClass = "border-[#1E293B]";
  
  if (highlight) {
    borderClass = "border-[#10B981]/40 shadow-[0_0_20px_rgba(16,185,129,0.06)]";
  } else if (borderType === "amber") {
    borderClass = "border-[#F59E0B]/40 shadow-[0_0_20px_rgba(245,158,11,0.06)]";
  } else if (borderType === "cyan") {
    borderClass = "border-[#06B6D4]/40 shadow-[0_0_20px_rgba(6,182,212,0.06)]";
  } else if (borderType === "red") {
    borderClass = "border-[#EF4444]/40 shadow-[0_0_20px_rgba(239,68,68,0.06)]";
  }

  return (
    <div className={`bg-[#0F1322] border ${borderClass} rounded-2xl p-5 card-glow-hover ${className}`}>
      {children}
    </div>
  );
}

function Badge({ text, type = "neutral" }) {
  const colors = {
    up:      "bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/30",
    down:    "bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/30",
    neutral: "bg-slate-800 text-slate-400 border border-slate-700",
    info:    "bg-[#06B6D4]/15 text-[#06B6D4] border border-[#06B6D4]/30",
  };
  return (
    <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium tracking-wider ${colors[type]}`}>
      {text}
    </span>
  );
}

function PriceChange({ change, t }) {
  if (change == null) return null;
  const up = change >= 0;
  return (
    <span className={`text-sm font-semibold flex items-center gap-1 ${up ? "text-[#10B981] glow-text-green" : "text-[#EF4444] glow-text-red"}`}>
      {up ? (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
      ) : (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" /></svg>
      )}
      ₹{Math.abs(change).toLocaleString("en-IN")} {up ? "from yesterday" : "from yesterday"}
    </span>
  );
}

// ─── LANGUAGE SELECT SCREEN ────────────────────────────
function LangSelect({ onSelect }) {
  return (
    <div className="fixed inset-0 bg-[#070A13] flex flex-col items-center justify-center z-50 p-6">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.07)_0,transparent_60%)] pointer-events-none" />
      
      <div className="w-full max-w-md bg-[#0F1322] border border-[#1E293B]/70 rounded-3xl p-8 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#10B981] to-[#06B6D4]" />
        
        <div className="flex flex-col items-center text-center mt-4">
          <div className="w-16 h-16 bg-[#10B981]/10 rounded-2xl flex items-center justify-center mb-5 border border-[#10B981]/25 relative">
            <span className="text-3xl animate-bounce">🌶</span>
            <div className="absolute -inset-0.5 rounded-2xl bg-[#10B981] blur-md opacity-25" />
          </div>
          
          <h1 className="text-4xl font-black text-white mb-2 tracking-wide font-cyber">MirchiMandi</h1>
          <p className="text-gray-400 text-sm mb-1 font-medium font-body">Know the real price. Stop losing money.</p>
          <p className="text-slate-500 text-sm mb-8 noto-telugu">నిజమైన ధర తెలుసుకోండి. డబ్బు పోగొట్టుకోవద్దు.</p>
          
          <div className="w-full space-y-4">
            <button 
              onClick={() => onSelect("en")}
              className="w-full py-4 bg-[#10B981] hover:bg-emerald-400 text-black font-bold rounded-2xl text-lg transition duration-300 shadow-lg shadow-emerald-950/20 active:scale-95"
            >
              English
            </button>
            <button 
              onClick={() => onSelect("te")}
              className="w-full py-4 border-2 border-[#10B981]/60 text-[#10B981] hover:bg-[#10B981]/10 font-bold rounded-2xl text-lg transition duration-300 active:scale-95 noto-telugu"
            >
              తెలుగు
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── TODAY'S PRICE CARD ────────────────────────────────
function TodayPriceCard({ variety, market, t, lang }) {
  const { data, loading } = useFetch(
    `/api/price/today?market=${encodeURIComponent(market)}&variety=${encodeURIComponent(variety)}`,
    [variety, market]
  );

  if (loading) {
    return (
      <Card className="min-h-[250px] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 text-sm animate-pulse">{t.loading}</p>
        </div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="min-h-[250px] flex items-center justify-center text-center">
        <p className="text-slate-500">No market data reported for this variety in {market} today.</p>
      </Card>
    );
  }

  // Detect if the price is outdated (older than 2 days)
  const priceDate = new Date(data.date);
  const todayDate = new Date();
  priceDate.setHours(0,0,0,0);
  todayDate.setHours(0,0,0,0);
  const diffTime = Math.abs(todayDate - priceDate);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  const isOutdated = diffDays > 2;

  const cardTitle = isOutdated ? (t.latest_price || "Latest Available Price") : t.today;
  const subtitle = isOutdated 
    ? (t.outdated_warning ? t.outdated_warning(data.date) : `⚠️ Showing price from ${data.date}`)
    : (lang === "te" ? `నేటి ${market} ధర` : `Today's ${market} Price`);

  return (
    <Card 
      highlight={!isOutdated} 
      borderType={isOutdated ? "amber" : "default"}
      className="relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.06)_0,transparent_70%)] pointer-events-none" />
      
      {/* Header */}
      <div className="flex justify-between items-start mb-3 flex-wrap gap-2">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-semibold">{cardTitle}</p>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-lg font-bold text-white tracking-tight">{data.variety}</h3>
            {data.is_user_reported && <Badge text="User Reported" type="info" />}
          </div>
        </div>
        {isOutdated && (
          <span className="text-xs bg-amber-950/30 text-[#F59E0B] px-3 py-1 rounded-full border border-[#F59E0B]/30 font-medium">
            {diffDays} days old
          </span>
        )}
      </div>

      <p className={`text-xs mb-3 font-medium ${isOutdated ? "text-[#F59E0B]" : "text-[#10B981]"}`}>{subtitle}</p>

      {/* Main Large Price */}
      <div className="mb-1">
        <span className={`text-5xl font-black tracking-tight font-cyber ${isOutdated ? "text-[#F59E0B] glow-text-amber" : "text-[#10B981] glow-text-green"}`}>
          ₹{data.modal_price?.toLocaleString("en-IN")}
        </span>
        <span className="text-slate-500 text-sm ml-2 font-medium">/ {t.quintal} (100 kg)</span>
      </div>

      <div className="mt-2 mb-6">
        {!isOutdated ? (
          <PriceChange change={data.change} t={t} />
        ) : (
          <span className="text-xs text-slate-500 font-medium">Note: Market reports for this variety are not updated daily.</span>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-[#1E293B]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-950/20 border border-red-500/20 flex items-center justify-center text-red-400">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 13l-7 7-7-7m14-6l-7 7-7-7" /></svg>
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber">Min Price</p>
            <p className="text-sm font-bold text-slate-200 font-cyber">₹{data.min_price?.toLocaleString("en-IN")}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-950/20 border border-emerald-500/20 flex items-center justify-center text-[#10B981]">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 11l7-7 7 7M5 19l7-7 7 7" /></svg>
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber">Max Price</p>
            <p className="text-sm font-bold text-slate-200 font-cyber">₹{data.max_price?.toLocaleString("en-IN")}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-950/20 border border-cyan-500/20 flex items-center justify-center text-[#06B6D4]">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber">Arrivals</p>
            <p className="text-sm font-bold text-slate-200 font-cyber">{data.arrival_qty} MT</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-slate-800/40 border border-slate-700/50 flex items-center justify-center text-slate-400">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber font-semibold">Report Date</p>
            <p className="text-sm font-bold text-slate-200 font-cyber">{data.date}</p>
          </div>
        </div>
      </div>
    </Card>
  );
}

// ─── RECOMMENDATION CARD ───────────────────────────────
function RecommendationCard({ variety, market, quintals, t }) {
  const { data, loading } = useFetch(
    `/api/recommendation?market=${encodeURIComponent(market)}&variety=${encodeURIComponent(variety)}&quintals=${quintals}`,
    [variety, market, quintals]
  );

  if (loading) {
    return (
      <Card className="min-h-[180px] flex items-center justify-center">
        <div className="w-6 h-6 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </Card>
    );
  }

  if (!data) return null;
  const isWait = data.action === "WAIT";

  return (
    <Card 
      highlight={!isWait}
      borderType={isWait ? "amber" : "default"}
      className={`relative overflow-hidden ${
        isWait 
          ? "bg-gradient-to-br from-[#0F1322] via-[#0F1322] to-[#F59E0B]/5" 
          : "bg-gradient-to-br from-[#0F1322] via-[#0F1322] to-[#10B981]/5"
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Recommendation Icon */}
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 border ${
          isWait 
            ? "bg-[#F59E0B]/10 border-[#F59E0B]/30 text-[#F59E0B]" 
            : "bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]"
        }`}>
          {isWait ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          )}
        </div>

        {/* Content */}
        <div className="flex-1">
          <p className={`text-xs uppercase tracking-widest font-cyber font-bold ${isWait ? "text-[#F59E0B]" : "text-[#10B981]"}`}>
            💡 {t.recommendation}
          </p>
          <h2 className="text-2xl font-black text-white mt-1 mb-1 font-cyber tracking-tight">
            {isWait ? t.waitDays(data.wait_days) : t.sellToday}
          </h2>
          <p className="text-slate-300 text-sm font-medium noto-telugu mb-3">
            {isWait ? data.recommendation_te : "ఈరోజే అమ్మండి — ధర పెరగడం లేదు"}
          </p>

          {isWait && (
            <div className="bg-slate-900/50 rounded-xl p-3 border border-[#1E293B] max-w-md">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs text-slate-500">Expected Profit Gain:</span>
                <span className="text-sm font-bold text-[#10B981] font-cyber">+₹{data.gain_per_quintal?.toLocaleString("en-IN")} / qtl</span>
              </div>
              <div className="flex justify-between items-center pt-1 border-t border-slate-800">
                <span className="text-xs text-slate-400 font-semibold">Total Extra Revenue ({quintals} qtls):</span>
                <span className="text-base font-black text-[#10B981] font-cyber glow-text-green">+₹{data.total_gain?.toLocaleString("en-IN")}</span>
              </div>
            </div>
          )}

          {!isWait && (
            <p className="text-slate-400 text-xs font-semibold leading-relaxed border-l-2 border-[#10B981] pl-3 mt-1 py-0.5">
              Reason: {data.reason}
            </p>
          )}

          <div className="mt-4 flex gap-4 text-xs text-slate-500 font-cyber font-medium">
            <span>Forecast Expected: ₹{data.expected_price?.toLocaleString("en-IN")}</span>
            <span>·</span>
            <span>Today Mandi: ₹{data.today_price?.toLocaleString("en-IN")}</span>
          </div>
        </div>
      </div>
    </Card>
  );
}

// ─── FORECAST CARD ─────────────────────────────────────
function ForecastCard({ variety, market, t }) {
  const { data, loading } = useFetch(
    `/api/forecast?market=${encodeURIComponent(market)}&variety=${encodeURIComponent(variety)}`,
    [variety, market]
  );

  if (loading) {
    return (
      <Card className="min-h-[220px] flex items-center justify-center">
        <div className="w-6 h-6 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </Card>
    );
  }

  if (!data || !data.forecast) return null;
  const trend = data.trend === "RISING";

  return (
    <Card className="relative overflow-hidden">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-semibold">{t.forecast}</p>
          <span className="text-slate-400 text-xs font-medium">Next 7 Days Price Trend</span>
        </div>
        <Badge text={trend ? t.priceRising : t.priceFalling} type={trend ? "up" : "down"} />
      </div>

      {/* Custom Bar Chart Visualizer */}
      <div className="h-28 flex items-end gap-2.5 mt-6 px-1 relative">
        {/* Horizontal grid guide lines */}
        <div className="absolute inset-x-0 bottom-0 h-px bg-slate-800" />
        <div className="absolute inset-x-0 bottom-1/3 h-px border-t border-dashed border-slate-800/70" />
        <div className="absolute inset-x-0 bottom-2/3 h-px border-t border-dashed border-slate-800/70" />
        
        {data.forecast.map((p, i) => {
          const maxP = Math.max(...data.forecast);
          const minP = Math.min(...data.forecast);
          const range = maxP - minP || 1;
          const height = 15 + ((p - minP) / range) * 75;
          const isMax = p === maxP;
          
          return (
            <div key={i} className="flex flex-col items-center flex-1 h-full justify-end relative group">
              <div className="absolute bottom-full mb-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 border border-slate-700 text-white rounded px-1.5 py-0.5 text-[10px] font-cyber z-10 font-bold whitespace-nowrap shadow-xl">
                ₹{Math.round(p).toLocaleString("en-IN")}
              </div>
              <div
                className={`w-full rounded-t-lg transition-all duration-500 relative ${
                  isMax 
                    ? "bg-gradient-to-t from-emerald-500/30 to-[#10B981] shadow-[0_0_10px_rgba(16,185,129,0.3)] border border-[#10B981]/50" 
                    : "bg-gradient-to-t from-emerald-950/20 to-emerald-600/40 hover:to-emerald-500/70 border border-emerald-500/10"
                }`}
                style={{ height: `${height}%` }}
              />
              <p className="text-[10px] text-slate-500 font-cyber font-medium mt-2">{i === 0 ? "Tmr" : `D+${i+1}`}</p>
              <p className="text-[10px] text-slate-400 font-cyber font-bold">₹{Math.round(p/1000)}k</p>
            </div>
          );
        })}
      </div>

      {/* Model Stats Strip */}
      <div className="bg-slate-900/60 border border-[#1E293B] rounded-xl p-3 mt-6 flex justify-between items-center text-[10px] text-slate-500 font-cyber">
        <div>
          <span>Model: </span>
          <span className="text-[#06B6D4] font-bold">{data.model_used}</span>
        </div>
        <div>
          <span>MAE: </span>
          <span className="text-slate-300 font-bold">₹{data.accuracy_mae?.toLocaleString("en-IN")}</span>
        </div>
        <div>
          <span>R²: </span>
          <span className={`font-bold ${data.accuracy_r2 >= 0.7 ? "text-[#10B981]" : "text-amber-400"}`}>{data.accuracy_r2?.toFixed(3)}</span>
        </div>
      </div>
    </Card>
  );
}

// ─── TRANSPORT & ARBITRAGE CALCULATOR ──────────────────
function CalculatorCard({ variety, market, t }) {
  const [qtl, setQtl] = useState(50);
  const [brokerPrice, setBrokerPrice] = useState(19000);
  const [farmerPincode, setFarmerPincode] = useState("Pavulur"); // Default Pavulur village
  const [vehicle, setVehicle] = useState("Tractor");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const calculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = `${API}/api/arbitrage?farmer_pincode=${encodeURIComponent(farmerPincode)}&market_pincode=${encodeURIComponent(market)}&vehicle=${vehicle}&quintals=${qtl}&broker_price=${brokerPrice}&variety=${encodeURIComponent(variety)}&market=${encodeURIComponent(market)}`;
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error("Could not calculate transport costs. Check village location.");
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const inputClass = "w-full bg-slate-900 border border-[#1E293B] focus:border-[#10B981]/50 focus:ring-1 focus:ring-[#10B981]/30 rounded-xl px-3.5 py-2.5 text-white text-sm outline-none transition font-medium";
  const labelClass = "text-xs font-bold text-slate-500 block mb-1.5 uppercase tracking-wider font-cyber";

  return (
    <Card className="relative overflow-hidden">
      <div className="flex justify-between items-start mb-1">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-semibold">🚚 Profit Maximizer</p>
          <h3 className="text-lg font-bold text-white tracking-tight">Transport & Arbitrage ({variety})</h3>
        </div>
      </div>
      <p className="text-slate-400 text-xs noto-telugu mb-5">బ్రోకర్ కి అమ్మాలా? లేక సొంతంగా మార్కెట్ కి తీసుకెళ్ళాలా? లెక్కించండి</p>

      <div className="space-y-4">
        {/* Row 1: Village & Market */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Village Name or Pin (విలేజ్ పేరు లేదా పిన్)</label>
            <input
              type="text"
              value={farmerPincode}
              onChange={e => setFarmerPincode(e.target.value)}
              className={inputClass}
              placeholder="e.g. Pavulur or 523187"
            />
          </div>
          <div>
            <label className={labelClass}>Market Yard (మార్కెట్ యార్డ్)</label>
            <input
              type="text"
              value={market}
              disabled
              className="w-full bg-slate-950 border border-[#1E293B] rounded-xl px-3.5 py-2.5 text-slate-400 text-sm outline-none cursor-not-allowed font-semibold"
            />
          </div>
        </div>

        {/* Row 2: Quintals and Vehicle */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <label className={labelClass}>Qty ({t.quintal})</label>
            <input
              type="number"
              value={qtl}
              onChange={e => setQtl(+e.target.value)}
              className={`${inputClass} font-cyber`}
            />
          </div>
          <div className="md:col-span-2">
            <label className={labelClass}>Logistics Vehicle (రవాణా వాహనం)</label>
            <select
              value={vehicle}
              onChange={e => setVehicle(e.target.value)}
              className={`${inputClass} text-slate-300 font-semibold`}
            >
              <option value="Tractor">Tractor (ట్రాక్టర్) - AP standard</option>
              <option value="Trolley">Trolley / Tata Ace (ట్రోలీ)</option>
              <option value="Truck">Truck (లారీ)</option>
            </select>
          </div>
        </div>

        {/* Row 3: Broker offer */}
        <div>
          <label className={labelClass}>{t.brokerOffer}</label>
          <input
            type="number"
            value={brokerPrice}
            onChange={e => setBrokerPrice(+e.target.value)}
            className={`${inputClass} font-cyber`}
          />
        </div>

        <button
          onClick={calculate}
          disabled={loading || !farmerPincode}
          className="w-full bg-[#10B981] hover:bg-emerald-400 text-black font-bold py-3.5 rounded-xl text-sm transition duration-300 disabled:opacity-40 active:scale-95 mt-2"
        >
          {loading ? t.loading : "Compare Broker vs Mandi"}
        </button>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-950/20 border border-red-500/20 rounded-xl text-[#EF4444] text-xs font-semibold flex items-center gap-2">
          <span>⚠️</span> {error}
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-5 border-t border-[#1E293B] pt-5">
          {/* Recommendation Banner */}
          <div className={`p-4 rounded-2xl border flex items-start gap-3 ${
            result.is_profitable 
              ? "bg-[#10B981]/5 border-[#10B981]/30 text-[#10B981]" 
              : "bg-[#F59E0B]/5 border-[#F59E0B]/30 text-[#F59E0B]"
          }`}>
            <span className="text-xl">{result.is_profitable ? "💡" : "⚠️"}</span>
            <div>
              <p className="font-bold text-sm mb-0.5 uppercase tracking-wide font-cyber">
                {result.is_profitable ? "Recommendation: Go to Mandi!" : "Recommendation: Sell to Local Broker"}
              </p>
              <p className="text-xs text-slate-300 font-semibold noto-telugu leading-relaxed">
                {t.selectLang === "Select Language" ? result.recommendation.message_en : result.recommendation.message_te}
              </p>
            </div>
          </div>

          {/* Simple Visual Route map */}
          <div className="bg-slate-900/60 rounded-2xl p-4 border border-[#1E293B] relative">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber font-bold mb-4">📋 Logistics Route Map</p>
            
            <div className="flex items-center justify-between text-xs font-cyber text-slate-400 mb-2">
              <span className="font-bold text-slate-300">Your Village ({farmerPincode})</span>
              <span className="bg-[#06B6D4]/10 text-[#06B6D4] px-2 py-0.5 rounded border border-[#06B6D4]/30">{result.distance_km} km</span>
              <span className="font-bold text-slate-300">Mandi Market ({market})</span>
            </div>
            
            {/* Visual connecting line */}
            <div className="h-1.5 w-full bg-slate-800 rounded-full flex items-center relative overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-500 to-[#06B6D4] animate-pulse" style={{ width: "100%" }} />
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t border-slate-800 text-xs text-slate-400">
              <div>Rent Cost: <span className="text-slate-200 font-bold font-cyber">₹{result.transport_details.transport_fare.toLocaleString("en-IN")}</span></div>
              <div>Labor Cost: <span className="text-slate-200 font-bold font-cyber">₹{result.transport_details.labor_cost.toLocaleString("en-IN")}</span></div>
            </div>
            <div className="flex justify-between items-center mt-3 pt-2 border-t border-slate-800 text-xs">
              <span className="text-slate-500 font-bold font-cyber">TOTAL ROAD LOGISTICS FARE:</span>
              <span className="text-slate-200 font-black font-cyber">₹{result.transport_cost.toLocaleString("en-IN")}</span>
            </div>
          </div>

          {/* Revenue Breakdown */}
          <div className="bg-slate-900/60 rounded-2xl p-4 border border-[#1E293B] space-y-3">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber font-bold">💰 Net Earnings Breakdown</p>
            
            <div className="space-y-2 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Gross Mandi Price ({variety}):</span>
                <span className="text-slate-200 font-cyber">₹{result.mandi_price.toLocaleString("en-IN")}/qtl</span>
              </div>
              <div className="flex justify-between">
                <span>Gross Mandi Value ({qtl} qtls of {variety}):</span>
                <span className="text-slate-200 font-cyber">₹{result.mandi_revenue.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between text-[#EF4444] font-medium">
                <span>Deduct Total Logistics Costs:</span>
                <span className="font-cyber">- ₹{result.transport_cost.toLocaleString("en-IN")}</span>
              </div>
              
              <div className="h-px bg-slate-800 my-2" />
              
              <div className="flex justify-between text-[#10B981] font-bold text-sm">
                <span>Net Mandi Earning:</span>
                <span className="font-cyber">₹{result.net_mandi_revenue.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Broker Earnings ({qtl} qtls @ ₹{brokerPrice}/qtl):</span>
                <span className="font-cyber text-slate-300">₹{result.broker_revenue.toLocaleString("en-IN")}</span>
              </div>
            </div>

            <div className={`flex justify-between items-center border-t border-slate-800 pt-3 mt-2 p-3 rounded-xl ${
              result.is_profitable ? "bg-[#10B981]/5" : "bg-[#EF4444]/5"
            }`}>
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider font-cyber">
                {result.is_profitable ? "Extra Net Profit" : "Net Arbitrage Loss"} (లాభం):
              </span>
              <span className={`text-xl font-black font-cyber ${result.is_profitable ? "text-[#10B981] glow-text-green" : "text-[#EF4444] glow-text-red"}`}>
                {result.is_profitable ? "+" : ""} ₹{result.arbitrage_gain.toLocaleString("en-IN")}
              </span>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}

// ─── ALL VARIETIES TABLE ──────────────────────────────
function AllVarietiesCard({ market, t }) {
  const { data, loading } = useFetch(
    `/api/varieties/today?market=${encodeURIComponent(market)}`,
    [market]
  );

  if (loading) {
    return (
      <Card className="min-h-[200px] flex items-center justify-center">
        <div className="w-6 h-6 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </Card>
    );
  }

  if (!data || !data.varieties?.length) {
    return (
      <Card className="min-h-[200px] flex items-center justify-center">
        <p className="text-slate-500">No alternate variety data found today for {market}.</p>
      </Card>
    );
  }

  return (
    <Card>
      <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold mb-1">📋 {t.allVarieties}</p>
      <h3 className="text-base font-bold text-white tracking-tight mb-4">{market} Reports</h3>
      
      <div className="overflow-x-auto rounded-xl border border-[#1E293B]">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-900/80 text-[10px] font-cyber uppercase tracking-wider text-slate-400 border-b border-[#1E293B]">
              <th className="text-left py-3.5 px-4 font-semibold">{t.variety}</th>
              <th className="text-right py-3.5 px-4 font-semibold">Modal Price</th>
              <th className="text-right py-3.5 px-4 font-semibold">Min Price</th>
              <th className="text-right py-3.5 px-4 font-semibold">Max Price</th>
              <th className="text-right py-3.5 px-4 font-semibold">Arrival Quantity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {data.varieties.map((v, i) => (
              <tr key={i} className="hover:bg-slate-900/50 transition-colors">
                <td className="py-3.5 px-4 text-slate-200 font-semibold font-cyber flex items-center gap-2">
                  <span className="text-emerald-500">🌶</span>
                  <span>{v.variety}</span>
                  {v.grade && <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700">{v.grade}</span>}
                </td>
                <td className="text-right py-3.5 px-4 text-[#10B981] font-bold font-cyber">
                  ₹{v.modal_price?.toLocaleString("en-IN")}
                </td>
                <td className="text-right py-3.5 px-4 text-slate-400 font-cyber">₹{v.min_price?.toLocaleString("en-IN")}</td>
                <td className="text-right py-3.5 px-4 text-slate-400 font-cyber">₹{v.max_price?.toLocaleString("en-IN")}</td>
                <td className="text-right py-3.5 px-4 text-slate-400 font-cyber font-medium">{v.arrival_qty} MT</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

// ─── USER SUBMIT PRICE ────────────────────────────────
function UserSubmitCard({ market, t }) {
  const [form, setForm] = useState({
    arrival_date: new Date().toISOString().split("T")[0],
    market, variety: "", modal_price: "", reporter_name: "", notes: ""
  });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!form.variety || !form.modal_price) return;
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/user/submit-price`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, modal_price: +form.modal_price })
      });
      const d = await r.json();
      setStatus(d.success ? "ok" : "error");
    } catch { setStatus("error"); }
    setLoading(false);
  };

  const inp = "w-full bg-slate-900 border border-[#1E293B] focus:border-[#10B981]/50 focus:ring-1 focus:ring-[#10B981]/30 rounded-xl px-4 py-3 text-white text-sm outline-none transition";
  const lbl = "text-xs font-bold text-slate-500 block mb-1.5 uppercase tracking-wider font-cyber";

  return (
    <Card className="max-w-xl mx-auto">
      <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold mb-1">✍️ {t.userSubmit}</p>
      <h3 className="text-lg font-bold text-white tracking-tight mb-2">Crowdsource Price Feed</h3>
      <p className="text-slate-400 text-xs noto-telugu mb-6">agmarknet లో లేని రకాల ధరలు నమోదు చేయండి (Teja, 334, Byadgi...)</p>
      
      <div className="space-y-4">
        <div>
          <label className={lbl}>{t.submit_date}</label>
          <input type="date" value={form.arrival_date}
            onChange={e => setForm({ ...form, arrival_date: e.target.value })} className={inp} />
        </div>
        <div>
          <label className={lbl}>{t.submit_variety}</label>
          <input type="text" placeholder="e.g. Teja S17, 334 Sannam, Byadgi"
            value={form.variety} onChange={e => setForm({ ...form, variety: e.target.value })} className={inp} />
        </div>
        <div>
          <label className={lbl}>{t.submit_price} (₹/quintal)</label>
          <input type="number" placeholder="e.g. 22400"
            value={form.modal_price} onChange={e => setForm({ ...form, modal_price: e.target.value })} className={`${inp} font-cyber`} />
        </div>
        <div>
          <label className={lbl}>{t.submit_name}</label>
          <input type="text" placeholder="Ramu, Guntur (optional)"
            value={form.reporter_name} onChange={e => setForm({ ...form, reporter_name: e.target.value })} className={inp} />
        </div>
        <div>
          <label className={lbl}>{t.submit_note}</label>
          <input type="text" placeholder="e.g. Sold via local commission agent (optional)"
            value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} className={inp} />
        </div>
        <button onClick={submit} disabled={loading || !form.variety || !form.modal_price}
          className="w-full bg-[#10B981] hover:bg-emerald-400 text-black font-bold py-3.5 rounded-xl text-sm transition duration-300 disabled:opacity-40 mt-2">
          {loading ? t.loading : t.submit}
        </button>
        {status === "ok" && (
          <div className="p-3 bg-emerald-950/20 border border-emerald-500/20 text-[#10B981] text-xs font-semibold rounded-xl mt-3">
            {t.submitted_ok}
          </div>
        )}
        {status === "error" && (
          <div className="p-3 bg-red-950/20 border border-red-500/20 text-[#EF4444] text-xs font-semibold rounded-xl mt-3">
            ❌ Something went wrong. Try again.
          </div>
        )}
      </div>

      {/* Show recent user submissions */}
      <UserSubmissions market={market} t={t} />
    </Card>
  );
}

function UserSubmissions({ market, t }) {
  const { data } = useFetch(`/api/user/varieties?market=${encodeURIComponent(market)}`, [market]);
  if (!data?.data?.length) return null;
  return (
    <div className="mt-6 pt-6 border-t border-[#1E293B]">
      <p className="text-xs font-bold text-slate-500 uppercase tracking-widest font-cyber mb-3">Recent crowdsourced submissions:</p>
      <div className="space-y-2">
        {data.data.slice(0, 5).map((v, i) => (
          <div key={i} className="flex justify-between items-center text-sm py-2 px-3 bg-slate-900/40 border border-[#1E293B]/50 rounded-xl">
            <span className="text-slate-200 font-semibold font-cyber">{v.variety}</span>
            <span className="text-slate-400 text-xs font-cyber">{v.submissions} reports · avg <span className="text-[#10B981] font-bold">₹{v.avg_price?.toLocaleString("en-IN")}</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── ML MODEL COMPARISON ──────────────────────────────
function MLModelsCard({ variety, t }) {
  const { data, loading, error } = useFetch(
    `/api/models/comparison?variety=${encodeURIComponent(variety)}`,
    [variety]
  );

  if (loading) {
    return (
      <Card className="min-h-[200px] flex items-center justify-center">
        <div className="w-6 h-6 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="max-w-xl mx-auto flex items-center justify-center text-center p-8 border-red-500/30">
        <div>
          <p className="text-red-400 text-sm mb-2 font-bold font-cyber">⚠️ CONNECTION ERROR</p>
          <p className="text-slate-300 text-xs mb-4">Could not connect to the backend server at <code className="bg-slate-900 px-1 py-0.5 rounded text-[#06B6D4]">{API}</code>.</p>
          <p className="text-slate-400 text-xs">Please check that the FastAPI backend server is running and accessible.</p>
        </div>
      </Card>
    );
  }

  if (!data?.models?.length) {
    return (
      <Card className="max-w-xl mx-auto flex items-center justify-center text-center p-8">
        <div>
          <p className="text-slate-400 text-sm mb-2">No trained machine learning models found for variety: {variety}.</p>
          <code className="text-xs bg-slate-900 text-[#06B6D4] px-2 py-1 rounded">run 02_train_models.py</code>
        </div>
      </Card>
    );
  }


  return (
    <Card className="max-w-3xl mx-auto">
      <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold mb-1">🤖 {t.modelCompare}</p>
      <h3 className="text-lg font-bold text-white tracking-tight mb-6">Variety Target: {variety}</h3>
      
      {/* Visual Model Comparison Bar Chart */}
      <div className="bg-slate-900/40 border border-[#1E293B] rounded-2xl p-5 mb-6">
        <p className="text-[10px] text-slate-500 uppercase tracking-widest font-cyber font-bold mb-4">📊 Performance Chart (MAE - Lower is Better)</p>
        <div className="space-y-4">
          {data.models.map((m, idx) => {
            const maes = data.models.map(x => x.mae || 0);
            const maxMae = Math.max(...maes) || 1;
            const minMae = Math.min(...maes) || 0;
            const range = maxMae - minMae || 1;
            // Calculate a score: 100% for min_mae (best), down to 15% for max_mae (worst)
            const score = 15 + ((maxMae - (m.mae || 0)) / range) * 85;
            
            // Choose color based on model error class
            let barColor = "from-emerald-500 to-[#10B981]";
            if (m.is_best) {
              barColor = "from-emerald-400 to-teal-400 shadow-[0_0_8px_rgba(16,185,129,0.25)]";
            } else if (idx < 3) {
              barColor = "from-emerald-600/70 to-emerald-500/90";
            } else if (idx < 8) {
              barColor = "from-amber-600/60 to-amber-500/80";
            } else {
              barColor = "from-red-600/50 to-red-500/70";
            }
            
            return (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-cyber font-semibold text-slate-300 flex items-center gap-1.5">
                    {m.is_best && <span className="animate-pulse">⭐</span>}
                    {m.model_name}
                  </span>
                  <span className="font-cyber text-slate-400">
                    MAE: <span className="font-bold text-white">₹{Math.round(m.mae).toLocaleString("en-IN")}</span>
                  </span>
                </div>
                <div className="h-2.5 w-full bg-slate-950 rounded-full overflow-hidden flex items-center relative border border-slate-800/50">
                  <div 
                    className={`h-full bg-gradient-to-r ${barColor} rounded-full transition-all duration-1000`} 
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      <div className="overflow-x-auto rounded-xl border border-[#1E293B]">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-900 text-[10px] font-cyber uppercase tracking-wider text-slate-400 border-b border-[#1E293B]">
              <th className="text-left py-3.5 px-4 font-semibold">Model Architecture</th>
              <th className="text-right py-3.5 px-4 font-semibold">MAE (Price ₹)</th>
              <th className="text-right py-3.5 px-4 font-semibold">RMSE</th>
              <th className="text-right py-3.5 px-4 font-semibold">R² (R-Squared)</th>
              <th className="text-right py-3.5 px-4 font-semibold">MAPE %</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {data.models.map((m, i) => (
              <tr key={i} className={`transition-colors ${m.is_best ? "bg-emerald-950/10 hover:bg-emerald-950/20" : "hover:bg-slate-900/50"}`}>
                <td className="py-3.5 px-4 text-slate-200 font-semibold flex items-center gap-2">
                  {m.is_best ? (
                    <span className="text-[#10B981] flex items-center gap-1 font-bold"><span className="animate-pulse">⭐</span> Best</span>
                  ) : (
                    <span className="text-slate-500 font-cyber"># {i+1}</span>
                  )}
                  <span className="font-cyber">{m.model_name}</span>
                </td>
                <td className="text-right py-3.5 px-4 font-bold text-slate-200 font-cyber">₹{m.mae?.toLocaleString("en-IN")}</td>
                <td className="text-right py-3.5 px-4 text-slate-400 font-cyber">{m.rmse?.toLocaleString("en-IN")}</td>
                <td className={`text-right py-3.5 px-4 font-bold font-cyber ${m.r2 >= 0.7 ? "text-[#10B981]" : "text-amber-500"}`}>{m.r2?.toFixed(3)}</td>
                <td className="text-right py-3.5 px-4 text-slate-400 font-cyber">{m.mape?.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

// ─── ADMIN DASHBOARD ──────────────────────────────────
function AdminDashboard({ passcode, setPasscode, t }) {
  const [unverified, setUnverified] = useState([]);
  const [authError, setAuthError] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchUnverified = async () => {
    if (!passcode) return;
    try {
      const r = await fetch(`${API}/api/admin/unverified?passcode=${passcode}`);
      if (r.status === 401) {
        setAuthError("Invalid passcode");
        setUnverified([]);
        return;
      }
      const d = await r.json();
      setUnverified(d);
      setAuthError(null);
    } catch (e) {
      setAuthError("Failed to fetch unverified prices");
    }
  };

  useEffect(() => {
    if (passcode === "1234") {
      fetchUnverified();
    }
  }, [passcode]);

  const verifyPrice = async (id) => {
    try {
      const r = await fetch(`${API}/api/admin/verify/${id}?passcode=${passcode}`, { method: "POST" });
      if (r.ok) {
        setUnverified(unverified.filter(u => u.id !== id));
      }
    } catch {}
  };

  const deletePrice = async (id) => {
    try {
      const r = await fetch(`${API}/api/admin/delete/${id}?passcode=${passcode}`, { method: "DELETE" });
      if (r.ok) {
        setUnverified(unverified.filter(u => u.id !== id));
      }
    } catch {}
  };

  const triggerSync = async () => {
    setLoading(true);
    setSyncStatus("Triggering database sync...");
    try {
      const r = await fetch(`${API}/api/admin/trigger-scraper?passcode=${passcode}`, { method: "POST" });
      const d = await r.json();
      if (d.success) {
        setSyncStatus("Sync started in background! Check back in a few seconds.");
      } else {
        setSyncStatus("Sync failed to start.");
      }
    } catch (e) {
      setSyncStatus("Error: could not connect to server.");
    }
    setLoading(false);
  };

  if (passcode !== "1234") {
    return (
      <Card className="max-w-md mx-auto">
        <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold mb-1">🔒 Access Control</p>
        <h3 className="text-lg font-bold text-white tracking-tight mb-2">Admin Panel Gate</h3>
        <p className="text-slate-400 text-xs mb-6">Enter passcode to manage crowdsourced listings & sync database.</p>
        
        <div className="space-y-4">
          <input
            type="password"
            placeholder="Enter passcode"
            className="w-full bg-slate-900 border border-[#1E293B] focus:border-[#10B981]/50 focus:ring-1 focus:ring-[#10B981]/30 rounded-xl px-4 py-3 text-white text-sm outline-none transition font-cyber"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                setPasscode(e.target.value);
              }
            }}
          />
          <button
            onClick={(e) => setPasscode(e.currentTarget.previousSibling.value)}
            className="w-full bg-[#10B981] hover:bg-emerald-400 text-black font-bold py-3.5 rounded-xl text-sm transition duration-300"
          >
            Authenticate Access
          </button>
        </div>
        {authError && <p className="text-[#EF4444] text-xs font-semibold mt-3">❌ {authError}</p>}
      </Card>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Card borderType="cyan" className="bg-gradient-to-br from-[#0F1322] via-[#0F1322] to-[#06B6D4]/5">
        <div className="flex justify-between items-start flex-wrap gap-4">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold mb-1">🛠 System Administrator Actions</p>
            <h3 className="text-lg font-bold text-white tracking-tight">Active Terminal Control</h3>
          </div>
          <button
            onClick={() => setPasscode("")}
            className="border border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444]/10 font-bold px-4 py-2 rounded-xl text-xs transition duration-300"
          >
            Sign Out
          </button>
        </div>
        
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={triggerSync}
            disabled={loading}
            className="bg-[#10B981] hover:bg-emerald-400 text-black font-bold px-5 py-3 rounded-xl text-sm transition duration-300 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
            ) : "🔄"}
            Run Agmarknet Scraping Script
          </button>
        </div>
        {syncStatus && (
          <div className="p-3 bg-slate-900 border border-[#1E293B] rounded-xl text-amber-400 text-xs font-semibold font-cyber mt-4">
            {syncStatus}
          </div>
        )}
      </Card>

      <Card>
        <div className="mb-4">
          <p className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold mb-1">✍️ Unverified User Reports</p>
          <h3 className="text-base font-bold text-white tracking-tight">Pending Validation Queue ({unverified.length})</h3>
        </div>

        {unverified.length === 0 ? (
          <div className="py-8 text-center bg-slate-900/40 border border-dashed border-[#1E293B] rounded-2xl">
            <p className="text-slate-500 text-sm">All submissions verified! No items in queue.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {unverified.map((u) => (
              <div key={u.id} className="bg-slate-900 border border-[#1E293B] rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-slate-700 transition">
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-white font-cyber">{u.variety}</span>
                    <span className="text-[10px] text-slate-500 font-cyber font-semibold">{u.arrival_date}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-semibold">{u.market}</span>
                    <span className="text-[#10B981] font-bold font-cyber text-sm">₹{u.modal_price.toLocaleString("en-IN")}</span>
                  </div>
                  {u.reporter_name && <p className="text-xs text-slate-500">Reporter: <span className="text-slate-300 font-semibold">{u.reporter_name}</span></p>}
                  {u.notes && <p className="text-xs italic text-slate-500 bg-slate-950 p-2 rounded-lg border border-slate-800">Notes: {u.notes}</p>}
                </div>
                <div className="flex gap-2.5 pt-3 border-t border-slate-800/80">
                  <button
                    onClick={() => verifyPrice(u.id)}
                    className="flex-1 bg-[#10B981]/15 hover:bg-[#10B981]/30 text-[#10B981] border border-[#10B981]/30 font-bold py-2 rounded-xl text-xs transition duration-300"
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => deletePrice(u.id)}
                    className="flex-1 bg-[#EF4444]/15 hover:bg-[#EF4444]/30 text-[#EF4444] border border-[#EF4444]/30 font-bold py-2 rounded-xl text-xs transition duration-300"
                  >
                    ✗ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

// ─── MAIN APP ──────────────────────────────────────────
export default function App() {
  const [lang,    setLang]    = useState(localStorage.getItem("mm_lang") || null);
  const [variety, setVariety] = useState("Teja S17"); // Default variety
  const [market,  setMarket]  = useState("Guntur APMC");
  const [quintals,setQuintals]= useState(50);
  const [tab,     setTab]     = useState("home");
  const [passcode,setPasscode]= useState("");
  const [userVarieties, setUserVarieties] = useState([]);

  const selectLang = (l) => {
    localStorage.setItem("mm_lang", l);
    setLang(l);
  };

  useEffect(() => {
    fetch(`${API}/api/user/varieties?market=${encodeURIComponent(market)}`)
      .then(r => r.json())
      .then(d => {
        if (d && d.data) {
          const names = d.data.map(item => item.variety);
          setUserVarieties(names);
        }
      })
      .catch(() => {});
  }, [market, tab]);

  if (!lang) return <LangSelect onSelect={selectLang} />;

  const t = T[lang];

  const VARIETIES = Array.from(new Set([
    "Teja S17", "334 Sannam", "Byadgi", "341", "DD Deluxe", "Armoor",
    "Teja Fatki", "334 Fatki", "Seed Variety Fatki",
    "Red New", "Red", "Guntur", "Red Top", "White", "Local", "Dry Chillies",
    ...userVarieties
  ]));
  const MARKETS   = ["Guntur APMC"];

  // Inline SVGs for Navigation
  const Icons = {
    home: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" /></svg>
    ),
    submit: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
    ),
    models: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
    ),
    admin: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
    )
  };

  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-[#080B11] text-slate-100 antialiased font-sans">
      
      {/* ─── DESKTOP SIDEBAR (LAPTOP) ─── */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-[#0F1322] border-r border-[#1E293B] sticky top-0 h-screen p-6 justify-between flex-shrink-0 z-40">
        <div className="space-y-8">
          {/* Logo Branding */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#10B981]/15 border border-[#10B981]/30 rounded-xl flex items-center justify-center text-xl shadow-[0_0_15px_rgba(16,185,129,0.1)]">
              🌶
            </div>
            <div>
              <span className="font-cyber font-black text-xl text-white tracking-wider uppercase block">MirchiMandi</span>
              <span className="text-[10px] text-slate-500 uppercase tracking-widest block font-bold mt-0.5">AP Price Intel</span>
            </div>
          </div>

          {/* Desktop Nav Items */}
          <nav className="space-y-2">
            {[
              { key: "home",   icon: Icons.home, label: t.nav_home },
              { key: "submit", icon: Icons.submit, label: t.nav_submit },
              { key: "models", icon: Icons.models, label: t.nav_models },
              { key: "admin",  icon: Icons.admin, label: t.nav_admin },
            ].map(n => (
              <button 
                key={n.key} 
                onClick={() => setTab(n.key)}
                className={`w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold tracking-wide transition duration-300 relative group
                  ${tab === n.key 
                    ? "bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20" 
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
                  }`}
              >
                {/* Active left indicator tag */}
                {tab === n.key && (
                  <div className="absolute left-0 w-1 h-6 bg-[#10B981] rounded-r-md" />
                )}
                <span className="transition-transform group-hover:scale-110">{n.icon}</span>
                <span className="noto-telugu">{n.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Desktop Footer Actions */}
        <div className="space-y-4 pt-6 border-t border-[#1E293B]/70">
          <div className="flex justify-between items-center text-xs text-slate-500 font-semibold font-cyber">
            <span>Market Clock</span>
            <span>{new Date().toLocaleDateString("en-IN")}</span>
          </div>
          
          <button 
            onClick={() => selectLang(lang === "en" ? "te" : "en")}
            className="w-full flex items-center justify-center gap-2 border border-[#1E293B] hover:border-slate-600 rounded-xl py-3 px-4 text-xs font-cyber font-bold text-slate-300 hover:text-white transition duration-300"
          >
            🌐 Language Selection: <span className="text-[#10B981] uppercase">{lang === "en" ? "తెలుగు" : "English"}</span>
          </button>
        </div>
      </aside>

      {/* ─── MOBILE TOP HEADER (PHONE) ─── */}
      <header className="lg:hidden flex items-center justify-between px-5 py-4 bg-[#0F1322] border-b border-[#1E293B] sticky top-0 z-50">
        <div className="flex items-center gap-2.5">
          <span className="text-2xl">🌶</span>
          <span className="font-cyber font-black text-lg text-white tracking-wider uppercase">{t.appName}</span>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={() => selectLang(lang === "en" ? "te" : "en")}
            className="text-xs font-cyber font-bold border border-[#1E293B] rounded-full px-3 py-1.5 text-slate-300 hover:text-white bg-slate-900 transition"
          >
            {lang === "en" ? "తెలుగు" : "ENGLISH"}
          </button>
        </div>
      </header>

      {/* ─── MAIN CONTENT REGION ─── */}
      <main className="flex-1 flex flex-col min-h-screen overflow-x-hidden pb-24 lg:pb-8">
        
        {/* ─── TOP STATUS STRIP (Patna Metro Style Ticker) ─── */}
        <div className="bg-[#0A0D18] border-b border-[#1E293B] px-5 py-2.5 flex items-center gap-6 overflow-x-auto no-scrollbar whitespace-nowrap z-30">
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10B981] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#10B981] glow-dot-green"></span>
            </span>
            <span className="text-[10px] font-cyber font-extrabold text-[#10B981] uppercase tracking-widest">LIVE Mandi Feeds</span>
          </div>

          <div className="h-4 w-px bg-slate-800 flex-shrink-0" />
          
          <div className="flex items-center gap-2 flex-shrink-0 text-xs font-cyber">
            <span className="text-slate-500 font-semibold uppercase">ACTIVE MANDIS:</span>
            <span className="text-slate-200 font-extrabold">4 APMC</span>
          </div>

          <div className="h-4 w-px bg-slate-800 flex-shrink-0" />

          <div className="flex items-center gap-2 flex-shrink-0 text-xs font-cyber">
            <span className="text-slate-500 font-semibold uppercase">MAIN TARGET:</span>
            <span className="text-[#06B6D4] font-extrabold">{variety}</span>
          </div>

          <div className="h-4 w-px bg-slate-800 flex-shrink-0" />

          <div className="flex items-center gap-2 flex-shrink-0 text-xs font-cyber">
            <span className="text-slate-500 font-semibold uppercase">MARKET ZONE:</span>
            <span className="text-slate-200 font-extrabold">{market}</span>
          </div>

          <div className="h-4 w-px bg-slate-800 flex-shrink-0" />

          <div className="flex items-center gap-2 flex-shrink-0 text-xs font-cyber">
            <span className="text-slate-500 font-semibold uppercase">AI ENGINE:</span>
            <span className="text-[#10B981] font-bold">XGBoost & LightGBM Active</span>
          </div>
        </div>

        {/* ─── BODY CONTAINER ─── */}
        <div className="px-4 lg:px-8 py-6 space-y-6 max-w-7xl mx-auto w-full">
          
          {/* ─── SHARED FILTERS BOX (Adjusts for Mobile/Desktop) ─── */}
          <div className="bg-[#0F1322] border border-[#1E293B] rounded-2xl p-5 shadow-sm">
            <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-4">
              
              {/* Static Market Info */}
              <div className="flex-1 min-w-0">
                <label className="text-[10px] font-cyber font-bold uppercase tracking-wider text-slate-500 block mb-1.5">APMC Market Yard (మార్కెట్)</label>
                <div className="flex items-center gap-3 bg-slate-900/60 border border-[#1E293B] rounded-xl px-3.5 py-3 text-sm text-slate-200 font-semibold h-[50px]">
                  <span className="text-emerald-500 text-lg">📍</span>
                  <div>
                    <span className="text-white font-bold block leading-none mb-1">Guntur APMC</span>
                    <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold leading-none block">Asia's Largest Chilli Yard</span>
                  </div>
                </div>
              </div>

              {/* Select Variety */}
              <div className="flex-1 min-w-0">
                <label className="text-[10px] font-cyber font-bold uppercase tracking-wider text-slate-500 block mb-1.5">Chilli Variety (మిర్చి రకం)</label>
                <div className="relative">
                  <select 
                    value={variety} 
                    onChange={e => setVariety(e.target.value)}
                    className="w-full bg-slate-900 border border-[#1E293B] focus:border-[#10B981]/50 focus:ring-1 focus:ring-[#10B981]/30 rounded-xl px-3.5 py-3 text-sm text-slate-200 font-semibold outline-none transition appearance-none"
                  >
                    {VARIETIES.map(v => <option key={v} className="bg-slate-950 text-slate-200">{v}</option>)}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3.5 text-slate-400">
                    <svg className="fill-current h-4 w-4" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                  </div>
                </div>
              </div>

              {/* Input Quintals */}
              <div className="w-full lg:w-44">
                <label className="text-[10px] font-cyber font-bold uppercase tracking-wider text-slate-500 block mb-1.5">{t.yourQtls} (క్వింటాళ్ళు)</label>
                <div className="relative">
                  <input 
                    type="number" 
                    value={quintals} 
                    onChange={e => setQuintals(+e.target.value)}
                    className="w-full bg-slate-900 border border-[#1E293B] focus:border-[#10B981]/50 focus:ring-1 focus:ring-[#10B981]/30 rounded-xl px-4 py-3 text-white font-cyber font-extrabold text-sm outline-none transition" 
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                    <span className="text-xs text-slate-500 uppercase tracking-widest font-cyber font-bold">QTL</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* ─── DYNAMIC TABS ROUTER ─── */}
          {tab === "home" && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column - Main Pricing Info */}
              <div className="lg:col-span-7 space-y-6">
                <TodayPriceCard variety={variety} market={market} t={t} lang={lang} />
                <RecommendationCard variety={variety} market={market} quintals={quintals} t={t} />
              </div>

              {/* Right Column - Forecasting and Arbitrage */}
              <div className="lg:col-span-5 space-y-6">
                <ForecastCard variety={variety} market={market} t={t} />
                <CalculatorCard variety={variety} market={market} t={t} />
              </div>

              {/* Full Width Bottom Table */}
              <div className="lg:col-span-12">
                <AllVarietiesCard market={market} t={t} />
              </div>
            </div>
          )}

          {tab === "submit" && (
            <UserSubmitCard market={market} t={t} />
          )}

          {tab === "models" && (
            <MLModelsCard variety={variety} t={t} />
          )}

          {tab === "admin" && (
            <AdminDashboard passcode={passcode} setPasscode={setPasscode} t={t} />
          )}

        </div>
      </main>

      {/* ─── MOBILE BOTTOM NAVIGATION BAR (PHONE) ─── */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-[#0F1322]/95 backdrop-blur-md border-t border-[#1E293B] flex z-40 px-2 py-1 shadow-2xl">
        {[
          { key: "home",   icon: Icons.home, label: t.nav_home },
          { key: "submit", icon: Icons.submit, label: t.nav_submit },
          { key: "models", icon: Icons.models, label: t.nav_models },
          { key: "admin",  icon: Icons.admin, label: t.nav_admin },
        ].map(n => (
          <button 
            key={n.key} 
            onClick={() => setTab(n.key)}
            className={`flex-1 py-2.5 flex flex-col items-center gap-1.5 text-[10px] font-bold transition duration-300 relative
              ${tab === n.key ? "text-[#10B981]" : "text-slate-500 hover:text-slate-400"}`}
          >
            {/* Active indicator dot */}
            {tab === n.key && (
              <div className="absolute -top-1 w-1.5 h-1.5 bg-[#10B981] rounded-full shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
            )}
            <span className="text-xl">{n.icon}</span>
            <span className="noto-telugu truncate max-w-[80px]">{n.label}</span>
          </button>
        ))}
      </nav>
      
    </div>
  );
}
