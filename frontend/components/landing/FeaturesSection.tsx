import { FeatureCard } from './FeatureCard';

const features = [
  {
    emoji: '🎙️',
    title: 'Your morning, personalized',
    description: 'Instead of bouncing between apps trying to catch up on everything, you get a personalized daily briefing that knows your schedule.',
    ctaText: 'Get daily brief',
  },
  {
    emoji: '💬',
    title: 'Companion that listens',
    description: 'Interrupt and say "wait, explain that differently" or "give me more detail". Your AI companion adapts to how you think.',
    ctaText: 'Try it',
  },
  {
    emoji: '🎧',
    title: 'Always available, always fresh',
    description: 'Your personalized companion is ready 24/7 with updates from your email, calendar, news, and more. Get briefed whenever.',
    ctaText: 'Start listening',
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 bg-white dark:bg-[#050505]/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </div>
    </section>
  );
}
