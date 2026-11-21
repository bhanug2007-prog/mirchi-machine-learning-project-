import React, { useState, useEffect } from "react";
import { Menu, X, ArrowRight, Sparkles, TrendingUp, Compass, HelpCircle, Layers } from "lucide-react";

export default function Navbar({ onLaunchApp, currentLang, onToggleLang }) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("home");

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 30) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }

      // Determine active section by scroll position
      const sections = ["home", "market-intelligence", "farmer-decision", "how-it-works", "about"];
      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 200 && rect.bottom >= 200) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { id: "home", label: currentLang === "te" ? "హోమ్" : "Home", href: "#home" },
    { id: "market-intelligence", label: currentLang === "te" ? "మార్కెట్ ధరలు" : "Market Prices", href: "#market-intelligence" },
    { id: "farmer-decision", label: currentLang === "te" ? "రైతు నిర్ణయం" : "Selling Decisions", href: "#farmer-decision" },
    { id: "how-it-works", label: currentLang === "te" ? "ఇది ఎలా పనిచేస్తుంది" : "How It Works", href: "#how-it-works" },
  ];

  const scrollTo = (href) => {
    setMobileMenuOpen(false);
    const id = href.replace("#", "");
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-[#0B0D0E]/85 backdrop-blur-md border-b border-white/8 py-3.5 shadow-2xl shadow-black/40"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <a
            href="#home"
            onClick={(e) => {
              e.preventDefault();
              scrollTo("#home");
            }}
            className="flex items-center gap-3 group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E63946] to-[#990011] flex items-center justify-center shadow-lg shadow-[#E63946]/20 border border-[#E63946]/30 group-hover:scale-105 transition-transform duration-300">
              <span className="text-xl">🌶️</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold tracking-tight text-white font-cyber flex items-center gap-1.5">
                Mirchi<span className="text-[#FF4D5A]">Mandi</span>
              </span>
              <span className="text-[10px] tracking-wider text-slate-400 font-medium uppercase">
                {currentLang === "te" ? "మిర్చి ధరల వేదిక" : "AgriTech Intelligence"}
              </span>
            </div>
          </a>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-[#131620]/60 border border-white/8 rounded-full px-4 py-1.5 backdrop-blur-md shadow-inner">
            {navLinks.map((link) => {
              const isActive = activeSection === link.id;
              return (
                <a
                  key={link.id}
                  href={link.href}
                  onClick={(e) => {
                    e.preventDefault();
                    scrollTo(link.href);
                  }}
                  className={`px-4 py-2 rounded-full text-xs font-medium tracking-wide transition-all duration-200 relative ${
                    isActive
                      ? "text-white bg-[#E63946]/20 border border-[#E63946]/40 shadow-[0_0_12px_rgba(230,57,70,0.2)]"
                      : "text-slate-300 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {link.label}
                  {isActive && (
                    <span className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-[#E63946]" />
                  )}
                </a>
              );
            })}
          </nav>

          {/* Right Action Buttons */}
          <div className="hidden sm:flex items-center gap-3">
            {/* Language Toggle */}
            <button
              onClick={onToggleLang}
              className="px-3 py-1.5 rounded-full text-xs font-semibold bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors flex items-center gap-1.5"
              title="Switch Language"
            >
              <span className="text-slate-400">🌐</span>
              <span>{currentLang === "te" ? "English" : "తెలుగు"}</span>
            </button>

            {/* Launch App / Dashboard */}
            <button
              onClick={onLaunchApp}
              className="px-5 py-2.5 rounded-full text-xs font-semibold tracking-wide bg-gradient-to-r from-[#E63946] to-[#C1121F] text-white shadow-lg shadow-[#E63946]/25 hover:shadow-[#E63946]/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 flex items-center gap-2 border border-[#FF6B6B]/30"
            >
              <span>{currentLang === "te" ? "యాప్ తెరవండి" : "Launch Platform"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex sm:hidden items-center gap-2">
            <button
              onClick={onToggleLang}
              className="px-2.5 py-1 text-xs rounded-lg bg-white/5 text-slate-300 border border-white/10"
            >
              {currentLang === "te" ? "EN" : "తె"}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl bg-white/5 text-white hover:bg-white/10 transition-colors border border-white/10"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden bg-[#0F121C]/95 border-b border-white/10 backdrop-blur-xl px-4 pt-4 pb-6 mt-3 space-y-3 animate-fadeIn">
          {navLinks.map((link) => (
            <a
              key={link.id}
              href={link.href}
              onClick={(e) => {
                e.preventDefault();
                scrollTo(link.href);
              }}
              className="block px-4 py-2.5 rounded-xl text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 transition-colors"
            >
              {link.label}
            </a>
          ))}
          <div className="pt-3 border-t border-white/10 flex flex-col gap-2.5">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onLaunchApp();
              }}
              className="w-full py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-[#E63946] to-[#C1121F] text-white flex items-center justify-center gap-2 shadow-lg shadow-[#E63946]/25"
            >
              <span>{currentLang === "te" ? "యాప్ ప్రారంభించండి" : "Launch Platform"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
