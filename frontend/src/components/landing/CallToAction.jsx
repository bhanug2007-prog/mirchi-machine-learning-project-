import React from "react";
import { ArrowRight, Sparkles, CheckCircle2 } from "lucide-react";

export default function CallToAction({ onGetStartedClick, currentLang }) {
  const isTe = currentLang === "te";

  return (
    <section className="relative py-24 lg:py-32 overflow-hidden bg-gradient-to-b from-[#090B10] via-[#12080A] to-[#08090D]">
      {/* Cinematic Ambient Glow & Particles Backdrop */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(230,57,70,0.18)_0,transparent_70%)] pointer-events-none" />
      <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#E63946]/10 blur-[130px] pointer-events-none" />

      {/* Decorative Floating Chilli Embers */}
      <div className="absolute top-12 left-12 w-2 h-2 rounded-full bg-[#E63946] animate-ping opacity-60" />
      <div className="absolute bottom-16 right-20 w-3 h-3 rounded-full bg-[#F4A261] animate-pulse opacity-50" />
      <div className="absolute top-1/2 right-12 w-2 h-2 rounded-full bg-[#10B981] animate-bounce opacity-40" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        {/* Animated Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#1F0C0F] border border-[#E63946]/30 mb-8 backdrop-blur-md shadow-lg shadow-[#E63946]/10">
          <Sparkles className="w-4 h-4 text-[#FF4D5A]" />
          <span className="text-xs font-bold text-slate-200 tracking-wide uppercase">
            {isTe ? "భవిష్యత్ వ్యవసాయం ఇక్కడే" : "Next-Gen Agricultural Intelligence"}
          </span>
        </div>

        {/* Main CTA Heading */}
        <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.15] font-cyber mb-6">
          {isTe ? (
            <>
              మెరుగైన మార్కెట్ సమాచారం. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF4D5A] via-[#E63946] to-[#F4A261]">
                తెలివైన వ్యవసాయ నిర్ణయాలు.
              </span>
            </>
          ) : (
            <>
              Better Market Insights. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF4D5A] via-[#E63946] to-[#F4A261]">
                Smarter Farming Decisions.
              </span>
            </>
          )}
        </h2>

        {/* Description */}
        <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed mb-10 font-normal">
          {isTe
            ? "మిర్చీమండితో మిర్చి మార్కెట్‌లను విశ్లేషించే ఆధునిక విధానాన్ని ప్రారంభించండి."
            : "Discover a smarter way to understand chilli markets with Mirchi Mandi."}
        </p>

        {/* Action Button */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={onGetStartedClick}
            className="w-full sm:w-auto px-9 py-4.5 rounded-2xl text-base font-bold tracking-wide text-white bg-gradient-to-r from-[#E63946] via-[#D90429] to-[#C1121F] shadow-2xl shadow-[#E63946]/40 hover:shadow-[#E63946]/60 hover:scale-105 active:scale-95 transition-all duration-300 flex items-center justify-center gap-3 border border-[#FF6B6B]/40 group"
          >
            <span>{isTe ? "ఇప్పుడే ప్రారంభించండి" : "Get Started"}</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        {/* Confidence Checkpoints */}
        <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
            <span>{isTe ? "పూర్తిగా ఉచితం & ఓపెన్" : "100% Free & Open Access"}</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
            <span>{isTe ? "ఆంధ్రప్రదేశ్ & తెలంగాణ కోసం" : "Built for AP & Telangana Farmers"}</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
            <span>{isTe ? "తెలుగు & ఇంగ్లీష్ మద్దతు" : "Bilingual Telugu & English Support"}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
