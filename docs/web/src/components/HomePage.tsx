import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Hero } from './Hero';
import { TrustStrip } from './TrustStrip';
import { Gains } from './Gains';
import { Spotlights } from './Spotlights';
import { BuiltWith } from './BuiltWith';
import { StandingOnGiants } from './StandingOnGiants';
import { Installation } from './Installation';
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

  // Proof before pitch: the build, the numbers and the packs that use it come first, then what
  // it does beyond files, the gain in detail, what it stands on, and how to start.
  return (
    <div className={`min-h-screen bg-ink-950 text-ink-200 ${SELECTION_BRAND}`}>
      <Navbar />

      <main>
        <Hero />
        <TrustStrip />
        <BuiltWith />
        <Spotlights />
        <Gains />
        <StandingOnGiants />
        <Installation />
        <FinalCTA />
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;
