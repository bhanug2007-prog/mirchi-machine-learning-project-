import React, { useState } from "react";
import { Truck, Warehouse, Handshake, Info, ShieldAlert, CheckCircle2, ChevronRight } from "lucide-react";

export default function FarmerDecision({ onLaunchApp, currentLang }) {
  const isTe = currentLang === "te";
  const [selectedDecision, setSelectedDecision] = useState("mandi");

  const decisions = [
    {
      id: "local",
      icon: Handshake,
      title: isTe ? "గ్రామంలోనే అమ్మడం" : "Sell Locally",
      subtitle: isTe ? "స్థానిక బ్రోకర్ ఆఫర్" : "Farmgate Trader & Broker",
      badge: isTe ? "తక్షణ నగదు" : "Immediate Settlement",
      badgeColor: "text-amber-400 bg-amber-400/10 border-amber-400/30",
      description: isTe
        ? "రవాణా లేదా హమాలీ ఖర్చులు ఉండవు, నగదు వెంటనే వస్తుంది. కానీ మార్కెట్ యార్డ్ ధరల కంటే క్వింటాలుకు గణనీయమైన ధర తగ్గుదల ఉండే అవకాశం ఉంది."
        : "Zero haulage expense and immediate cash payment at the village gate, but often at trader discounts compared to prevailing APMC modal prices.",
      pros: isTe
        ? ["రవాణా మరియు ఇంధన ఖర్చులు సున్నా", "తక్షణ చెల్లింపు మరియు సౌలభ్యం"]
        : ["Zero transport and fuel risk", "Immediate same-day payment"],
      cons: isTe
        ? ["మార్కెట్ కంటే తక్కువ ధర లభించే అవకాశం", "నాణ్యత తగ్గింపులు ఎక్కువ"]
        : ["Broker margins reduce farmer profit", "Limited price transparency"],
    },
    {
      id: "mandi",
      icon: Truck,
      title: isTe ? "ప్రధాన యార్డులకు రవాణా" : "Explore Other Markets",
      subtitle: isTe ? "గుంటూరు / ఖమ్మం APMC" : "APMC Mandi Yard",
      badge: isTe ? "అత్యుత్తమ మార్కెట్ ధర" : "Competitive Bidding",
      badgeColor: "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/30",
      description: isTe
        ? "గుంటూరు APMC లేదా సమీప ప్రధాన మార్కెట్‌లలో వేలం ద్వారా ఎక్కువ మంది కొనుగోలుదారుల మధ్య అధిక ధర పొందవచ్చు. రవాణా మరియు హమాలీ ఖర్చులను లెక్కించాలి."
        : "Direct access to hundreds of commission agents, exporters, and open competitive auctions. Requires budgeting for freight and hamali labor.",
      pros: isTe
        ? ["అధిక కొనుగోలుదారుల పోటీ ధర", "ప్రభుత్వ క్రమబద్ధీకరించిన వేలం"]
        : ["Highest competitive buyer bidding", "Direct regulated APMC yard weighment"],
      cons: isTe
        ? ["ట్రాక్టర్ లేదా లారీ రవాణా ఖర్చు", "యార్డులో సమయం వెచ్చించాల్సి ఉంటుంది"]
        : ["Haulage distance & vehicle hire costs", "Market yard unloading queues"],
    },
    {
      id: "storage",
      icon: Warehouse,
      title: isTe ? "కోల్డ్ స్టోరేజ్‌లో నిల్వ" : "Consider Storage",
      subtitle: isTe ? "ధర పెరిగే వరకు ఆగడం" : "Off-Season Cold Chain",
      badge: isTe ? "దీర్ఘకాలిక వ్యూహం" : "Price Appreciation",
      badgeColor: "text-[#06B6D4] bg-[#06B6D4]/10 border-[#06B6D4]/30",
      description: isTe
        ? "కోత సీజన్‌లో మార్కెట్ ధరలు తగ్గినప్పుడు మిర్చిని కోల్డ్ స్టోరేజ్‌లో భద్రపరచి, ఆఫ్‌-సీజన్‌లో డిమాండ్ పెరిగినప్పుడు లాభదాయకంగా అమ్మడం."
        : "Preserve cured dry chilli during peak harvest arrival gluts to capture off-season price spikes, balanced against monthly cold holding fees.",
      pros: isTe
        ? ["ఆఫ్‌-సీజన్ అధిక ధరల ప్రయోజనం", "రసాయన మరియు తేమ రక్షణ"]
        : ["Capture post-monsoon price surges", "Crop preservation without weight loss"],
      cons: isTe
        ? ["నెలవారీ కోల్డ్ స్టోరేజ్ అద్దె", "ధర తగ్గే మార్కెట్ రిస్క్"]
        : ["Monthly storage & insurance rental", "Capital locked in produce"],
    },
  ];

  return (
    <section id="farmer-decision" className="relative py-24 lg:py-32 bg-[#090B10] overflow-hidden">
      {/* Ambient background glows */}
      <div className="absolute top-1/3 left-10 w-96 h-96 bg-[#E63946]/08 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-[#10B981]/08 blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 sm:mb-20 space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-[#E63946]" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              {isTe ? "రైతు వాస్తవ సమస్య" : "The Core Farmer Dilemma"}
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight font-cyber">
            {isTe ? "ప్రతి క్వింటాలుకు ఒక మంచి నిర్ణయం కావాలి." : "Every Quintal Deserves a Better Decision."}
          </h2>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            {isTe
              ? "మిర్చి రైతులు తమ పంటను స్థానిక వ్యాపారులకు అమ్మాలా, గుంటూరు యార్డుకు తీసుకెళ్లాలా లేదా కోల్డ్ స్టోరేజీలో పెట్టాలా అనే సందిగ్ధంలో ఉంటారు. మిర్చీమండి సరైన డేటాతో మీకు అండగా నిలుస్తుంది."
              : "Chilli farmers navigate high-stakes choices at harvest: settle locally with village buyers, transport quintals to regional APMC yards, or store produce for seasonal appreciation."}
          </p>
        </div>

        {/* Split-Screen Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left: 3 Interactive Decision Cards */}
          <div className="lg:col-span-6 space-y-4">
            {decisions.map((item) => {
              const Icon = item.icon;
              const isSelected = selectedDecision === item.id;

              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedDecision(item.id)}
                  className={`cursor-pointer rounded-2xl p-6 transition-all duration-300 border relative overflow-hidden ${
                    isSelected
                      ? "bg-[#141824] border-[#E63946]/60 shadow-xl shadow-[#E63946]/10 -translate-y-0.5"
                      : "bg-[#10131D]/80 border-white/8 hover:bg-[#121622] hover:border-white/15"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-3.5">
                      <div
                        className={`w-11 h-11 rounded-xl flex items-center justify-center transition-colors ${
                          isSelected ? "bg-[#E63946] text-white" : "bg-white/5 text-slate-300"
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
                          {item.title}
                        </h3>
                        <p className="text-xs text-slate-400 font-medium">{item.subtitle}</p>
                      </div>
                    </div>
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${item.badgeColor}`}>
                      {item.badge}
                    </span>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal mb-4">
                    {item.description}
                  </p>

                  {/* Pros & Cons Checklist */}
                  <div className="pt-3 border-t border-white/5 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    <div className="space-y-1">
                      {item.pros.map((pro, pIdx) => (
                        <div key={pIdx} className="flex items-center gap-1.5 text-slate-300">
                          <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981] flex-shrink-0" />
                          <span className="truncate">{pro}</span>
                        </div>
                      ))}
                    </div>
                    <div className="space-y-1">
                      {item.cons.map((con, cIdx) => (
                        <div key={cIdx} className="flex items-center gap-1.5 text-slate-400">
                          <Info className="w-3.5 h-3.5 text-[#F4A261] flex-shrink-0" />
                          <span className="truncate">{con}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right: Agricultural Image Showcase (User Uploaded Real Chillies Photo) */}
          <div className="lg:col-span-6 flex flex-col items-center">
            <div className="relative w-full rounded-3xl overflow-hidden border border-white/15 bg-gradient-to-b from-[#181D2B] to-[#0E111A] p-3 shadow-2xl shadow-black/80 group">
              {/* Photo Container */}
              <div className="relative w-full h-[400px] sm:h-[480px] rounded-2xl overflow-hidden">
                <img
                  src="/harvested_chillies.jpg"
                  alt="Harvested Red Chillies - Andhra Pradesh Yard Quality"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
                />
                {/* Vignette & Gradients */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#0B0D12] via-transparent to-black/30" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#0B0D12]/40 via-transparent to-transparent" />

                {/* Floating Yard Quality Tag */}
                <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/60 backdrop-blur-md border border-white/15 text-white">
                  <span className="w-2 h-2 rounded-full bg-[#10B981]" />
                  <span className="text-xs font-semibold tracking-wide">
                    {isTe ? "ఆంధ్రప్రదేశ్ మిర్చి పంట" : "Authentic Andhra Pradesh Crop"}
                  </span>
                </div>

                {/* Bottom Overlay Info Banner */}
                <div className="absolute bottom-4 left-4 right-4 p-4 rounded-xl bg-[#0F121C]/85 backdrop-blur-md border border-white/10 flex items-center justify-between">
                  <div>
                    <p className="text-[11px] uppercase tracking-wider text-[#FF4D5A] font-bold">
                      {isTe ? "రకం & గ్రేడ్" : "Guntur S17 & Teja"}
                    </p>
                    <p className="text-sm sm:text-base font-bold text-white">
                      {isTe ? "మండీ విశ్లేషణ వేదిక" : "Mandi Grade Dried Red Chilli"}
                    </p>
                  </div>
                  <button
                    onClick={onLaunchApp}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#E63946] text-white hover:bg-[#C1121F] transition-colors flex items-center gap-1.5 shadow-md shadow-[#E63946]/30"
                  >
                    <span>{isTe ? "ధర సరిపోల్చండి" : "Compare"}</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Clear Decision Support Disclaimer Banner */}
        <div className="mt-12 p-4 sm:p-5 rounded-2xl bg-[#121622]/80 border border-white/10 backdrop-blur-md flex items-center gap-4 text-xs sm:text-sm text-slate-300">
          <div className="w-8 h-8 rounded-xl bg-[#F4A261]/15 border border-[#F4A261]/30 flex items-center justify-center flex-shrink-0 text-[#F4A261]">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <p className="leading-relaxed">
            <strong className="text-white font-semibold">
              {isTe ? "నిర్ణయ సహకార వేదిక — " : "Decision Support, Not Guaranteed Profits: "}
            </strong>
            {isTe
              ? "మిర్చీమండి మార్కెట్ పారదర్శకతను మరియు విశ్లేషణాత్మక ధర సమాచారాన్ని అందిస్తుంది. తుది అమ్మకపు నిర్ణయాలు మరియు బేరసారాలు పూర్తిగా రైతులదే."
              : "Mirchi Mandi provides transparent market data, transport cost models, and predictive estimates to assist your negotiations. It is not an assurance of speculative market returns."}
          </p>
        </div>
      </div>
    </section>
  );
}
