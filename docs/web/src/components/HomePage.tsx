import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Hero } from './Hero';
import { Testimonial } from './Testimonial';
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

  // The hero and the quote are the redesigned top of the page; the sections below keep a flat
  // page colour over the grid until their turn comes.
  return (
    <div className={`min-h-screen ${SELECTION_BRAND}`}>
      <Navbar />

      <main>
        <Hero />
        <Testimonial />
        <div className="bg-surface text-ink-200">
          <Spotlights />
          <Gains />
          <BuiltWith />
          <StandingOnGiants />
          <Installation />
          <StackSection />
          <FinalCTA />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;
