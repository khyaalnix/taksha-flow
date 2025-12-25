'use client';

import Link from 'next/link';

interface NavigationProps {
  showAuthButton?: boolean;
}

export function Navigation({ showAuthButton = true }: NavigationProps) {
  return (
    <nav className="fixed top-0 w-full z-50 bg-white/80 dark:bg-[#050505]/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex-shrink-0 flex items-center gap-2 cursor-pointer">
            <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-black flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">auto_awesome</span>
            </div>
            <span className="font-bold text-xl tracking-tight">Flow</span>
          </Link>

          <div className="hidden md:flex items-center space-x-8">
            <a
              className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white transition-colors"
              href="#features"
            >
              Features
            </a>
            <a
              className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white transition-colors"
              href="#how-it-works"
            >
              How it works
            </a>
            <a
              className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white transition-colors"
              href="#discord"
            >
              Discord
            </a>
            <a
              className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white transition-colors"
              href="#blog"
            >
              Blog
            </a>
          </div>

          <div className="flex items-center gap-4">
            <button
              className="p-2 rounded-full hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors"
              onClick={() => document.documentElement.classList.toggle('dark')}
              aria-label="Toggle dark mode"
            >
              <span className="material-symbols-outlined text-zinc-600 dark:text-zinc-300 text-sm block dark:hidden">
                dark_mode
              </span>
              <span className="material-symbols-outlined text-zinc-600 dark:text-zinc-300 text-sm hidden dark:block">
                light_mode
              </span>
            </button>
            {showAuthButton && (
              <Link
                href="/login"
                className="bg-zinc-900 hover:bg-zinc-800 dark:bg-white dark:hover:bg-zinc-200 text-white dark:text-black px-5 py-2 rounded-full text-sm font-medium transition-all shadow-lg hover:shadow-xl"
              >
                Get Started
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
