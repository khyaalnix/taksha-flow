'use client';

import { ListeningButton } from './ListeningButton';

interface CenterSectionProps {
  onListeningTap?: () => void;
  isPlaying?: boolean;
}

export function CenterSection({ onListeningTap, isPlaying = true }: CenterSectionProps) {
  return (
    <section className="flex flex-col items-center justify-center relative">
      {/* Animated lyrics/text display */}
      <div className="w-full max-w-lg h-48 mb-8 lyrics-mask overflow-hidden relative flex flex-col items-center justify-center text-center">
        <div className="space-y-4">
          <p className="text-xl md:text-2xl lg:text-3xl font-medium text-zinc-400 dark:text-zinc-600 blur-[0.5px]">
            Instead of bouncing between apps
          </p>
          <p className="text-2xl md:text-3xl lg:text-4xl font-semibold text-zinc-900 dark:text-white transform scale-105">
            It&apos;s all <span className="italic font-[var(--font-playfair-display)]">you</span>.
          </p>
          <p className="text-xl md:text-2xl lg:text-3xl font-medium text-zinc-400 dark:text-zinc-600 blur-[0.5px]">
            Content that exists because you do
          </p>
        </div>
      </div>

      {/* Listening button */}
      <ListeningButton onTap={onListeningTap} isPlaying={isPlaying} />

      {/* Instruction text */}
      <div className="mt-8 text-center animate-fade-in">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Tap to interrupt or ask &quot;What about my 2pm?&quot;
        </p>
      </div>
    </section>
  );
}
