import React from "react";
import { ArrowRight, Compass, Sparkles, TrendingUp, ShieldCheck, MapPin } from "lucide-react";
import ChilliScene3D from "./ChilliScene3D";

export default function Hero({ onExploreClick, onGetStartedClick, currentLang }) {
  const isTe = currentLang === "te";

  return (
    <section id="home" className="relative min-h-screen pt-28 pb-16 lg:pt-36 lg:pb-24 flex items-center overflow-hidden">
      {/* Background ambient radial gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-gradient-radial from-[#E63946]/12 via-[#E63946]/02 to-transparent blur-[120px] pointer-events-none" />
      <div className="absolute top-10 right-10 w-96 h-96 bg-[#10B981]/08 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-80 h-80 bg-[#F4A261]/06 blur-[90px] pointer-events-none" />

      {/* Subtle Grid Texture */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_40%,#000_70%,transparent_100%)] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Headlines & CTA */}
          <div className="lg:col-span-6 flex flex-col items-start text-left space-y-6 sm:space-y-8">
            {/* Animated Pill Badge */}
            <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-[#161A26]/80 border border-[#E63946]/30 shadow-lg shadow-[#E63946]/10 backdrop-blur-md">
              <span className="w-2.5 h-2.5 rounded-full bg-[#E63946] animate-pulse shadow-[0_0_8px_#E63946]" />
              <span className="text-xs font-semibold tracking-wide text-slate-200">
                {isTe ? "స్మార్ట్ వ్యవసాయం • మెరుగైన నిర్ణయాలు" : "Smart Agriculture. Better Decisions."}
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.12] font-cyber">
              {isTe ? (
                <>
                  మీ పంట. మీ మార్కెట్. <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF4D5A] via-[#E63946] to-[#F4A261]">
                    మీ నిర్ణయం.
                  </span>
                </>
              ) : (
                <>
                  Your Harvest. <br />
                  Your Market. <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF4D5A] via-[#E63946] to-[#F4A261]">
                    Your Decision.
                  </span>
                </>
              )}
            </h1>

            {/* Supporting Description */}
            <p className="text-base sm:text-lg text-slate-300 max-w-xl font-normal leading-relaxed">
              {isTe
                ? "మిర్చీమండి ద్వారా మార్కెట్ ధరలను కనుగొనండి, ధరల ధోరణులను పరిశీలించండి మరియు సరైన సమయంలో మంచి అమ్మకపు నిర్ణయాలు తీసుకోండి."
                : "Discover chilli market prices, explore price trends, and make informed selling decisions with Mirchi Mandi."}
            </p>

            {/* Two Prominent Action Buttons */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto">
              {/* Primary: Explore Markets */}
              <button
                onClick={onExploreClick}
                className="px-7 py-4 rounded-2xl text-sm font-bold tracking-wide text-white bg-gradient-to-r from-[#E63946] to-[#C1121F] shadow-xl shadow-[#E63946]/30 hover:shadow-[#E63946]/50 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 flex items-center justify-center gap-3 border border-[#FF6B6B]/40 group"
              >
                <span>{isTe ? "మార్కెట్లను అన్వేషించండి" : "Explore Markets"}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>

              {/* Secondary: Get Started */}
              <button
                onClick={onGetStartedClick}
                className="px-7 py-4 rounded-2xl text-sm font-bold tracking-wide text-slate-200 bg-[#141824]/80 hover:bg-[#1A2030] hover:text-white border border-white/10 shadow-lg shadow-black/20 hover:border-[#10B981]/40 transition-all duration-200 flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4 text-[#10B981]" />
                <span>{isTe ? "ప్రారంభించండి" : "Get Started"}</span>
              </button>
            </div>

            {/* Feature Trust Badges */}
            <div className="pt-4 border-t border-white/8 grid grid-cols-3 gap-4 sm:gap-6 w-full max-w-lg">
              <div className="flex flex-col">
                <span className="text-xs text-slate-400 font-medium">{isTe ? "యార్డ్ డేటా" : "Market Coverage"}</span>
                <span className="text-sm sm:text-base font-bold text-white flex items-center gap-1.5 mt-0.5">
                  <span className="text-[#E63946]">●</span> APMC AP & TS
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-slate-400 font-medium">{isTe ? "ML మోడల్స్" : "ML Forecasting"}</span>
                <span className="text-sm sm:text-base font-bold text-white flex items-center gap-1.5 mt-0.5">
                  <span className="text-[#10B981]">●</span> 11 Models
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-slate-400 font-medium">{isTe ? "అప్‌డేట్స్" : "Intelligence"}</span>
                <span className="text-sm sm:text-base font-bold text-white flex items-center gap-1.5 mt-0.5">
                  <span className="text-[#F4A261]">●</span> Real-time Sync
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: 3D Chilli Composition */}
          <div className="lg:col-span-6 relative w-full flex items-center justify-center">
            <ChilliScene3D onExploreClick={onExploreClick} />
          </div>
        </div>
      </div>
    </section>
  );
}
