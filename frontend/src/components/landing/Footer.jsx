import React from "react";
import { Heart, Globe, Mail, Phone, MapPin } from "lucide-react";

export default function Footer({ onLaunchApp, currentLang }) {
  const isTe = currentLang === "te";

  return (
    <footer className="relative bg-[#07080C] border-t border-white/8 text-slate-400 text-xs sm:text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 lg:gap-12">
          {/* Brand Column */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E63946] to-[#990011] flex items-center justify-center shadow-lg shadow-[#E63946]/20 border border-[#E63946]/30">
                <span className="text-xl">🌶️</span>
              </div>
              <span className="text-xl font-bold tracking-tight text-white font-cyber">
                Mirchi<span className="text-[#FF4D5A]">Mandi</span>
              </span>
            </div>

            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed max-w-sm font-normal">
              {isTe
                ? "మిర్చీమండి అనేది ఆంధ్రప్రదేశ్ మరియు తెలంగాణ మిర్చి రైతులకు పారదర్శక ధర సమాచారం మరియు మెషిన్ లెర్నింగ్ ధర అంచనాలను అందించే ఆధునిక వేదిక."
                : "Real-time chilli price intelligence, forecasting, and transport arbitrage support designed for Andhra Pradesh and Telangana red chilli farmers."}
            </p>

            <div className="pt-2 flex items-center gap-2 text-xs text-slate-500">
              <MapPin className="w-4 h-4 text-[#E63946]" />
              <span>Guntur APMC Yard & Andhra Pradesh Mandis</span>
            </div>
          </div>

          {/* Quick Links Column */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">
              {isTe ? "ముఖ్యమైన లింకులు" : "Platform Navigation"}
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="#home" className="hover:text-white transition-colors">
                  {isTe ? "హోమ్ పేజీ" : "Home"}
                </a>
              </li>
              <li>
                <a href="#market-intelligence" className="hover:text-white transition-colors">
                  {isTe ? "మార్కెట్ ధరలు" : "Market Prices"}
                </a>
              </li>
              <li>
                <a href="#farmer-decision" className="hover:text-white transition-colors">
                  {isTe ? "అమ్మకపు నిర్ణయాలు" : "Selling Decisions"}
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-white transition-colors">
                  {isTe ? "ఇది ఎలా పనిచేస్తుంది" : "How It Works"}
                </a>
              </li>
              <li>
                <button
                  onClick={onLaunchApp}
                  className="text-[#FF4D5A] hover:underline font-semibold"
                >
                  {isTe ? "రైతు డాష్‌బోర్డ్ తెరవండి →" : "Farmer Dashboard →"}
                </button>
              </li>
            </ul>
          </div>

          {/* Data Transparency & Contact */}
          <div className="md:col-span-4 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">
              {isTe ? "సమాచార వనరులు & మద్దతు" : "Data Integrity & Contact"}
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              {isTe
                ? "అధికారిక అగ్‌మార్క్‌నెట్ (Agmarknet) మరియు గుంటూరు మిర్చి యార్డు రోజువారీ నివేదికల ఆధారంగా రూపొందించబడింది."
                : "Aggregated from official Agmarknet arrivals and Guntur APMC price tracking registries with multi-model predictive validation."}
            </p>
            <div className="pt-2 space-y-1.5 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-[#10B981]" />
                <span>support@mirchimandi.in</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-3.5 h-3.5 text-[#06B6D4]" />
                <span>Open-Source Agricultural Initiative</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© 2026 MirchiMandi. Built for Indian chilli farmers.</p>
          <div className="flex items-center gap-1 text-slate-400">
            <span>Crafted with</span>
            <span className="text-[#E63946]">❤️</span>
            <span>for Andhra Pradesh & Telangana Farmers</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
