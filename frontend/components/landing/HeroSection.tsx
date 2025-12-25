import Link from 'next/link';
import { PhoneMockup } from './PhoneMockup';

export function HeroSection() {
  return (
    <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-28 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
          It&apos;s all <span className="italic font-serif font-light text-zinc-600 dark:text-zinc-400">you</span>
        </h1>
        <p className="text-lg md:text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto mb-10">
          Content that exists because you do. Your personalized audio briefing that learns, adapts, and grows with you every morning.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
          <Link
            href="/login"
            className="bg-zinc-900 hover:bg-zinc-800 dark:bg-white dark:hover:bg-zinc-200 text-white dark:text-black px-8 py-3.5 rounded-full text-base font-semibold flex items-center justify-center gap-2 transition-all transform hover:scale-105 shadow-xl"
          >
            <span className="material-symbols-outlined text-lg">mic</span>
            Start listening
          </Link>
          <button className="bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-900 dark:text-white px-8 py-3.5 rounded-full text-base font-medium flex items-center justify-center gap-2 transition-all">
            <span className="material-symbols-outlined text-lg">play_circle</span>
            Watch demo
          </button>
        </div>

        <PhoneMockup />
      </div>
    </section>
  );
}
