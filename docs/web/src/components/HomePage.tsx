import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Hero } from './Hero';
import { Gains } from './Gains';
import { Spotlights } from './Spotlights';
import { BuiltWith } from './BuiltWith';
import { StandingOnGiants } from './StandingOnGiants';
import { Installation } from './Installation';
import { StackSection } from './StackSection';
import { FinalCTA } from './FinalCTA';
import { Footer } from './Footer';
import { useReveal } from '../hooks/useReveal';
import { SELECTION_BRAND } from '../theme';

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();
  useReveal();

  useEffect(() => {
    if (!location.hash) return;

    // The plugins table lives on /documentation: keep the old anchor working
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

  // Proof before pitch: the hero holds the build and the adoption numbers, then what StewBeet
  // does beyond files, the gain in detail, the packs built with it, what it stands on, how to start,
  // and last, for a visitor who has never heard of beet, who makes which of the tools involved.
  return (
    <div className={`min-h-screen bg-ink-950 text-ink-200 ${SELECTION_BRAND}`}>
      <Navbar />

      <main>
        <Hero />
        <Spotlights />
        <Gains />
        <BuiltWith />
        <StandingOnGiants />
        <Installation />
        <StackSection />
        <FinalCTA />
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;
