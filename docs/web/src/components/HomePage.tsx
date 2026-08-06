import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Hero } from './Hero';
import { WhyStewBeet } from './WhyStewBeet';
import { ManualShowcase } from './ManualShowcase';
import { Features } from './Features';
import { BuiltWith } from './BuiltWith';
import { Installation } from './Installation';
import { FinalCTA } from './FinalCTA';
import { Footer } from './Footer';
import { SELECTION_BRAND } from '../theme';

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();

  // Handle hash navigation
  useEffect(() => {
    if (!location.hash) return;

    // The plugins table now lives on /documentation: keep the old anchor working
    if (location.hash === '#plugins') {
      navigate('/documentation#plugins', { replace: true });
      return;
    }

    const element = document.querySelector(location.hash);
    if (element) {
      // Small delay to ensure page is rendered
      setTimeout(() => {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [location, navigate]);

  return (
    <div className={`min-h-screen bg-slate-950 text-slate-100 ${SELECTION_BRAND}`}>
      <Navbar />

      {/* Hero -> trust -> why -> features -> social proof -> supporting -> final CTA: a visitor
          meets the evidence that the project is alive before being asked to read about it. */}
      <main>
        <Hero />
        <WhyStewBeet />
        <ManualShowcase />
        <Features />
        <BuiltWith />
        <Installation />
        <FinalCTA />
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;
