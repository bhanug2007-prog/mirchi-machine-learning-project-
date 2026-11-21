import React from "react";
import { Compass, TrendingUp, CheckCircle, ArrowRight, ShieldCheck, MapPin } from "lucide-react";

export default function HowItWorks({ onLaunchApp, currentLang }) {
  const isTe = currentLang === "te";

  const steps = [
    {
      number: "01",
      icon: Compass,
      title: isTe ? "మార్కెట్ ధరలను కనుగొనండి" : "Explore Market Prices",
      subtitle: isTe ? "దశ 1" : "Step 1",
      description: isTe
        ? "ఆంధ్రప్రదేశ్ మరియు తెలంగాణలోని ప్రముఖ వ్యవసాయ మార్కెట్ల నుండి రోజూ తాజా ధరల సమాచారాన్ని పొందండి."
        : "Discover available chilli market price information across APMC yards with transparent modal and variety breakdowns.",
      bullet: isTe ? "నిజ-సమయ మార్కెట్ రాకలు & ధరలు" : "Official Yard Arrival Data",
    },
    {
      number: "02",
      icon: TrendingUp,
      title: isTe ? "ధోరణులను విశ్లేషించండి" : "Analyze Trends",
      subtitle: isTe ? "దశ 2" : "Step 2",
      description: isTe
        ? "చారిత్రక ధరల హెచ్చుతగ్గులు మరియు మెషిన్ లెర్నింగ్ అంచనాల ద్వారా రాబోయే 7 రోజుల ధోరణిని అర్థం చేసుకోండి."
        : "Understand historical seasonal cycles and review 7-day machine learning forecast trajectories before harvest dispatch.",
      bullet: isTe ? "11 ML మోడల్స్ అంచనాలు" : "Multi-Algorithm Forecasts",
    },
    {
      number: "03",
      icon: CheckCircle,
      title: isTe ? "సరైన నిర్ణయాలు తీసుకోండి" : "Make Informed Decisions",
      subtitle: isTe ? "దశ 3" : "Step 3",
      description: isTe
        ? "స్థానిక బ్రోకర్ ఆఫర్, యార్డు రవాణా ఖర్చులు మరియు కోల్డ్ స్టోరేజ్ అద్దెను పోల్చి సరైన లాభదాయక నిర్ణయం తీసుకోండి."
        : "Compare haulage freight, storage fees, and broker trade-offs before deciding precisely when and where to sell.",
      bullet: isTe ? "రవాణా & నిల్వ లాభ నష్టాల కాలిక్యులేటర్" : "Arbitrage & Haulage Calculator",
    },
  ];

  return (
    <section id="how-it-works" className="relative py-24 lg:py-32 bg-[#0B0D13] overflow-hidden">
      {/* Background glow lines */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-6xl h-64 bg-[#E63946]/05 blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 sm:mb-24 space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-[#10B981]" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              {isTe ? "సులభమైన విధానం" : "Workflow Architecture"}
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight font-cyber">
            {isTe ? "మిర్చీమండి ఎలా పనిచేస్తుంది?" : "How Mirchi Mandi Works"}
          </h2>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            {isTe
              ? "పంట కోత నుండి మార్కెట్ అమ్మకం వరకు కేవలం మూడు సులభమైన దశల్లో పూర్తి సమాచారం."
              : "A transparent three-step intelligence pipeline designed specifically for red chilli growers."}
          </p>
        </div>

        {/* 3 Connected Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Animated Connecting Line on desktop */}
          <div className="hidden md:block absolute top-1/2 left-[16%] right-[16%] h-[2px] bg-gradient-to-r from-[#E63946] via-[#10B981] to-[#F4A261] -translate-y-12 opacity-30 pointer-events-none" />

          {steps.map((step, idx) => {
            const Icon = step.icon;

            return (
              <div
                key={step.number}
                className="relative rounded-3xl p-8 bg-[#121622]/90 border border-white/10 hover:border-white/20 transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-black/60 flex flex-col justify-between backdrop-blur-xl group"
              >
                <div>
                  {/* Step Number & Icon */}
                  <div className="flex items-center justify-between mb-8">
                    <span className="text-4xl font-black text-white/20 font-cyber group-hover:text-[#E63946]/40 transition-colors">
                      {step.number}
                    </span>
                    <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white group-hover:scale-110 group-hover:bg-[#E63946]/15 group-hover:border-[#E63946]/40 transition-all duration-300">
                      <Icon className="w-6 h-6 text-white group-hover:text-[#FF4D5A] transition-colors" />
                    </div>
                  </div>

                  {/* Step Title & Subtitle */}
                  <span className="text-xs uppercase font-bold text-[#E63946] tracking-wider">
                    {step.subtitle}
                  </span>
                  <h3 className="text-xl font-bold text-white mt-1 mb-3 tracking-tight">
                    {step.title}
                  </h3>

                  <p className="text-sm text-slate-300 leading-relaxed font-normal mb-6">
                    {step.description}
                  </p>
                </div>

                {/* Bottom Highlight Bullet */}
                <div className="pt-4 border-t border-white/8 flex items-center gap-2 text-xs font-semibold text-[#10B981]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                  <span>{step.bullet}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Action Button Below Steps */}
        <div className="mt-16 text-center">
          <button
            onClick={onLaunchApp}
            className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl text-sm font-bold text-white bg-gradient-to-r from-[#E63946] to-[#C1121F] shadow-xl shadow-[#E63946]/25 hover:shadow-[#E63946]/45 hover:scale-105 active:scale-95 transition-all duration-200 border border-[#FF6B6B]/30"
          >
            <span>{isTe ? "ఇప్పుడే మార్కెట్ పరిశీలించండి" : "Explore Today's Mandi Data"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>
  );
}
