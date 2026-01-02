import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Hero } from './Hero';
import { WhatIsStewBeet } from './WhatIsStewBeet';
import { Features } from './Features';
import { Installation } from './Installation';
import { Templates } from './Templates';
import { Showcase } from './Showcase';
import { Footer } from './Footer';

function HomePage() {
  const location = useLocation();

  // Handle hash navigation
  useEffect(() => {
    if (location.hash) {
      const element = document.querySelector(location.hash);
      if (element) {
        // Small delay to ensure page is rendered
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      }
    }
  }, [location]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-indigo-500/30">
      <Navbar />

      <main>
        <Hero />
        <WhatIsStewBeet />
        <Features />
        <Installation />
        <Templates />
        <Showcase />
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;
