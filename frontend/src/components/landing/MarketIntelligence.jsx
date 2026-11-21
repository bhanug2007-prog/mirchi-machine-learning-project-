import React, { useState } from "react";
import { Search, TrendingUp, Sparkles, ArrowUpRight, BarChart2, Shield, Eye, Layers } from "lucide-react";

export default function MarketIntelligence({ onExploreClick, currentLang }) {
  const isTe = currentLang === "te";
  const [activeCard, setActiveCard] = useState(null);

  const features = [
    {
      id: "discovery",
      icon: Search,
      tag: isTe ? "ధరల శోధన" : "Price Discovery",
      tagColor: "text-[#E63946] bg-[#E63946]/10 border-[#E63946]/30",
      accentBorder: "group-hover:border-[#E63946]/50",
      glowBg: "from-[#E63946]/15 via-transparent to-transparent",
      title: isTe ? "మార్కెట్ ధరల శోధన" : "Market Price Discovery",
      description: isTe
        ? "వివిధ వ్యవసాయ మార్కెట్ యార్డులలో అందుబాటులో ఉన్న మిర్చి ధరలను సులభంగా అన్వేషించండి."
        : "Explore chilli prices across available agricultural markets with transparent yard breakdowns.",
      interactivePreview: (
        <div className="w-full mt-5 p-3.5 rounded-xl bg-[#0B0D14]/80 border border-white/8 space-y-2.5">
          <div className="flex items-center justify-between text-xs pb-2 border-b border-white/5">
            <span className="text-slate-400 font-medium">{isTe ? "ప్రధాన యార్డులు" : "APMC Market Yard"}</span>
            <span className="text-slate-400 font-medium">{isTe ? "రకం" : "Variety"}</span>
          </div>
          <div className="flex items-center justify-between text-xs py-1">
            <span className="text-white font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" /> Guntur APMC
            </span>
            <span className="px-2 py-0.5 rounded-md bg-white/5 text-slate-300 font-mono text-[11px]">Teja S17</span>
          </div>
          <div className="flex items-center justify-between text-xs py-1">
            <span className="text-white font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" /> Khammam Mandi
            </span>
            <span className="px-2 py-0.5 rounded-md bg-white/5 text-slate-300 font-mono text-[11px]">334 Sannam</span>
          </div>
          <div className="flex items-center justify-between text-xs py-1">
            <span className="text-white font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" /> Warangal Yard
            </span>
            <span className="px-2 py-0.5 rounded-md bg-white/5 text-slate-300 font-mono text-[11px]">Byadgi</span>
          </div>
        </div>
      ),
    },
    {
      id: "trends",
      icon: TrendingUp,
      tag: isTe ? "ధోరణుల విశ్లేషణ" : "Trend Analysis",
      tagColor: "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/30",
      accentBorder: "group-hover:border-[#10B981]/50",
      glowBg: "from-[#10B981]/15 via-transparent to-transparent",
      title: isTe ? "ధరల ధోరణుల విశ్లేషణ" : "Price Trend Analysis",
      description: isTe
        ? "స్పష్టమైన ఇంటరాక్టివ్ చార్ట్‌ల ద్వారా చారిత్రక ధరల కదలికలను, కాలానుగుణ మార్పులను అర్థం చేసుకోండి."
        : "Understand historical price movements and cyclical demand through clear, interactive trend charts.",
      interactivePreview: (
        <div className="w-full mt-5 p-3.5 rounded-xl bg-[#0B0D14]/80 border border-white/8 space-y-2">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-400">{isTe ? "చారిత్రక కదలికలు" : "Historical Price Curve"}</span>
            <span className="text-[#10B981] font-semibold text-[11px] flex items-center gap-1">
              <span>●</span> {isTe ? "యాక్టివ్" : "Interactive"}
            </span>
          </div>
          {/* Stylized Sparkline Visual */}
          <div className="h-16 w-full flex items-end">
            <svg className="w-full h-full overflow-visible" viewBox="0 0 200 60" fill="none">
              <defs>
                <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10B981" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path
                d="M 0,45 Q 35,30 65,38 T 130,22 T 200,10 L 200,60 L 0,60 Z"
                fill="url(#trendGradient)"
              />
              <path
                d="M 0,45 Q 35,30 65,38 T 130,22 T 200,10"
                stroke="#10B981"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              <circle cx="200" cy="10" r="4" fill="#10B981" className="animate-ping" />
              <circle cx="200" cy="10" r="3" fill="#ffffff" />
            </svg>
          </div>
          <div className="flex justify-between text-[10px] text-slate-500 pt-1">
            <span>7 Days</span>
            <span>30 Days</span>
            <span>90 Days</span>
          </div>
        </div>
      ),
    },
    {
      id: "forecasting",
      icon: Sparkles,
      tag: isTe ? "AI అంచనాలు" : "ML Forecasting",
      tagColor: "text-[#F4A261] bg-[#F4A261]/10 border-[#F4A261]/30",
      accentBorder: "group-hover:border-[#F4A261]/50",
      glowBg: "from-[#F4A261]/15 via-transparent to-transparent",
      title: isTe ? "మెషిన్ లెర్నింగ్ ధర అంచనా" : "AI-Powered Forecasting",
      description: isTe
        ? "మెషిన్ లెర్నింగ్ మోడల్స్ రూపొందించిన రాబోయే ధరల అంచనాలను సురక్షితంగా పరిశీలించండి."
        : "Explore estimated future price trajectories generated by robust machine learning algorithms.",
      interactivePreview: (
        <div className="w-full mt-5 p-3.5 rounded-xl bg-[#0B0D14]/80 border border-white/8 space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{isTe ? "7-రోజుల అంచనా సమయం" : "7-Day Projection Horizon"}</span>
            <span className="px-2 py-0.5 rounded-full bg-[#F4A261]/15 text-[#F4A261] text-[10px] font-bold">
              Ensemble ML
            </span>
          </div>
          <div className="grid grid-cols-7 gap-1 pt-1">
            {["D+1", "D+2", "D+3", "D+4", "D+5", "D+6", "D+7"].map((day, idx) => (
              <div
                key={day}
                className={`py-2 px-1 rounded-lg text-center flex flex-col items-center justify-center transition-all ${
                  idx === 6
                    ? "bg-[#10B981]/20 border border-[#10B981]/40 text-white"
                    : "bg-white/5 border border-white/5 text-slate-400"
                }`}
              >
                <span className="text-[9px] font-mono">{day}</span>
                <span className="text-[11px] font-bold mt-0.5">
                  {idx > 2 ? "↑" : "→"}
                </span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-slate-400 text-center">
            {isTe ? "XGBoost, LightGBM & Lasso మోడల్స్ ఆధారంగా" : "Multi-model consensus projections"}
          </p>
        </div>
      ),
    },
  ];

  return (
    <section id="market-intelligence" className="relative py-24 lg:py-32 bg-[#0B0D12] overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-gradient-radial from-[#E63946]/08 via-transparent to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 sm:mb-20 space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
            <Layers className="w-3.5 h-3.5 text-[#E63946]" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              {isTe ? "మార్కెట్ ఇంటెలిజెన్స్" : "Market Intelligence Engine"}
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight font-cyber">
            {isTe ? "అమ్మకానికి ముందే మార్కెట్‌ను తెలుసుకోండి." : "Know the Market Before You Sell."}
          </h2>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            {isTe
              ? "మీ తదుపరి అమ్మకపు నిర్ణయం తీసుకునే ముందు వ్యవసాయ మార్కెట్ సమాచారాన్ని మరియు ధరల కదలికలను క్షుణ్ణంగా అర్థం చేసుకోండి."
              : "Explore agricultural market information and understand price movements before making your next selling decision."}
          </p>
        </div>

        {/* 3 Premium Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feat) => {
            const Icon = feat.icon;
            const isHovered = activeCard === feat.id;

            return (
              <div
                key={feat.id}
                onMouseEnter={() => setActiveCard(feat.id)}
                onMouseLeave={() => setActiveCard(null)}
                className={`group relative rounded-3xl p-8 bg-[#121520]/80 border border-white/10 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-2xl hover:shadow-black/60 flex flex-col justify-between overflow-hidden backdrop-blur-xl ${feat.accentBorder}`}
              >
                {/* Ambient Card Top Glow */}
                <div
                  className={`absolute top-0 left-0 right-0 h-40 bg-gradient-to-b ${feat.glowBg} opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`}
                />

                <div className="relative z-10">
                  {/* Top Icon & Tag */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="w-13 h-13 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center p-3 text-white group-hover:scale-110 group-hover:bg-white/10 transition-all duration-300">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${feat.tagColor}`}>
                      {feat.tag}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-xl font-bold text-white mb-3 tracking-tight group-hover:text-white transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed font-normal">
                    {feat.description}
                  </p>

                  {/* Interactive Micro-Preview Element */}
                  {feat.interactivePreview}
                </div>

                {/* Bottom Action Hint */}
                <div className="relative z-10 pt-6 mt-6 border-t border-white/8 flex items-center justify-between text-xs font-semibold text-slate-400 group-hover:text-white transition-colors">
                  <span>{isTe ? "మరింత చూడండి" : "Explore feature"}</span>
                  <ArrowUpRight className="w-4 h-4 text-[#E63946] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
