import { Navigation } from '../shared/Navigation';
import { BackgroundGradients } from '../shared/BackgroundGradients';
import { HeroSection } from './HeroSection';
import { FeaturesSection } from './FeaturesSection';
import { CTASection } from './CTASection';
import { Footer } from '../shared/Footer';

export function LandingPage() {
  return (
    <div className="bg-white dark:bg-[#050505] text-zinc-900 dark:text-white min-h-screen">
      <BackgroundGradients />
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <CTASection />
      <Footer />
    </div>
  );
}
