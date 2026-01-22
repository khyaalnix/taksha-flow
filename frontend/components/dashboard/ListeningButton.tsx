'use client';

import { useState } from 'react';

interface ListeningButtonProps {
  onTap?: () => void;
  isPlaying?: boolean;
}

export function ListeningButton({ onTap, isPlaying = true }: ListeningButtonProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="relative group">
      {/* Outer glow effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-indigo-500/10 dark:bg-indigo-500/20 rounded-full blur-3xl animate-pulse-slow" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-purple-500/10 dark:bg-purple-500/20 rounded-full blur-2xl animate-pulse delay-75" />

      {/* Main button */}
      <button
        onClick={onTap}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="relative z-10 flex flex-col items-center justify-center w-32 h-32 rounded-full bg-white dark:bg-black border border-zinc-100 dark:border-zinc-800 shadow-2xl hover:scale-105 transition-transform duration-300 focus:outline-none focus:ring-4 focus:ring-indigo-500/30"
      >
        <div className="relative">
          {/* Sound wave bars */}
          <div className="flex items-center justify-center gap-1 h-8">
            {[1, 1.2, 0.8, 1.1, 0.9].map((speed, index) => (
              <div
                key={index}
                className="w-1 bg-zinc-900 dark:bg-white rounded-full"
                style={{
                  animation: isPlaying ? `music ${speed}s ease-in-out infinite` : 'none',
                  height: isPlaying ? undefined : '4px',
                  animationDelay: `${index * 0.1}s`,
                }}
              />
            ))}
          </div>
        </div>
        <span className="mt-2 text-xs font-semibold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
          {isPlaying ? 'Listening' : 'Paused'}
        </span>
      </button>
    </div>
  );
}
