import React from "react";
import Navbar from "./Navbar";
import Hero from "./Hero";
import MarketIntelligence from "./MarketIntelligence";
import FarmerDecision from "./FarmerDecision";
import HowItWorks from "./HowItWorks";
import CallToAction from "./CallToAction";
import Footer from "./Footer";

export default function LandingPage({ onLaunchDashboard, currentLang, onToggleLang }) {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-[#080B11] text-[#F3F4F6] selection:bg-[#E63946] selection:text-white relative">
      {/* Top Navbar */}
      <Navbar
        onLaunchApp={onLaunchDashboard}
        currentLang={currentLang}
        onToggleLang={onToggleLang}
      />

      {/* Hero Section with 3D Animated Chillies */}
      <Hero
        onExploreClick={() => scrollTo("market-intelligence")}
        onGetStartedClick={onLaunchDashboard}
        currentLang={currentLang}
      />

      {/* Market Intelligence Feature Section */}
      <MarketIntelligence
        onExploreClick={() => scrollTo("farmer-decision")}
        currentLang={currentLang}
      />

      {/* Farmer Decision Storytelling Section with Harvested Chillies Image */}
      <FarmerDecision
        onLaunchApp={onLaunchDashboard}
        currentLang={currentLang}
      />

      {/* How Mirchi Mandi Works 3-Step Section */}
      <HowItWorks
        onLaunchApp={onLaunchDashboard}
        currentLang={currentLang}
      />

      {/* Premium Call to Action */}
      <CallToAction
        onGetStartedClick={onLaunchDashboard}
        currentLang={currentLang}
      />

      {/* Clean Footer */}
      <Footer
        onLaunchApp={onLaunchDashboard}
        currentLang={currentLang}
      />
    </div>
  );
}
