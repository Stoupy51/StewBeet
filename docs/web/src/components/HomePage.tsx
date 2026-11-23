import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Hero } from './Hero';
import { Testimonial } from './Testimonial';
import { ControlProof } from './ControlProof';
import { Gains } from './Gains';
import { Spotlights } from './Spotlights';
import { BuiltWith } from './BuiltWith';
import { StandingOnGiants } from './StandingOnGiants';
import { GetStarted } from './GetStarted';
import { Footer } from './Footer';
import { SELECTION_BRAND } from '../theme';

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();

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

  return (
    <div className={`min-h-screen ${SELECTION_BRAND}`}>
      <Navbar />

      <main>
        <Hero />
        <Testimonial />
        <ControlProof />
        <Gains />
        <Spotlights />
        <BuiltWith />
        <StandingOnGiants />
        <GetStarted />
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;
