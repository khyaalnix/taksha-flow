'use client';

import { LoginButton } from './LoginButton';
import { useState } from 'react';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle email/password login
    console.log('Email login:', email);
  };

  return (
    <div className="min-h-screen flex flex-col relative bg-white dark:bg-[#050505] transition-colors duration-300">
      {/* Animated Background Gradients */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-primary/10 dark:bg-primary/5 rounded-full blur-[120px] animate-float"></div>
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] bg-purple-500/10 dark:bg-purple-500/5 rounded-full blur-[120px] animate-float" style={{animationDelay: '-5s'}}></div>
      </div>

      {/* Navigation */}
      <nav className="w-full px-6 py-6 flex justify-between items-center relative z-10 max-w-7xl mx-auto">
        <a href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-black flex items-center justify-center transition-transform group-hover:scale-105">
            <span className="material-symbols-outlined text-xl">auto_awesome</span>
          </div>
          <span className="font-bold text-xl tracking-tight text-zinc-900 dark:text-white">Flow</span>
        </a>
        <div className="flex items-center gap-4">
          <span className="text-sm text-zinc-500 dark:text-zinc-400 hidden sm:block">New to Flow?</span>
          <a href="#" className="text-sm font-semibold text-zinc-900 dark:text-white hover:text-primary dark:hover:text-primary transition-colors">
            Sign up
          </a>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow flex items-center justify-center px-4 py-12 relative z-10">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-4xl font-bold mb-3 tracking-tight text-zinc-900 dark:text-white">
              Welcome back
            </h1>
            <p className="text-zinc-500 dark:text-zinc-400">
              Your personalized daily briefing is waiting.
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-white dark:bg-zinc-900/50 backdrop-blur-xl border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 sm:p-8 shadow-xl dark:shadow-[0_0_80px_-20px_rgba(234,88,12,0.3)] transition-all duration-300">
            {/* Social Login Buttons */}
            <div className="flex flex-col gap-3 mb-6">
              <LoginButton />

              <button className="flex items-center justify-center gap-3 w-full py-2.5 px-4 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors group">
                <svg className="w-5 h-5 dark:invert" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879V14.89h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.989C18.343 21.129 22 16.99 22 12c0-5.523-4.477-10-10-10z"/>
                </svg>
                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-200">Continue with Apple</span>
              </button>
            </div>

            {/* Divider */}
            <div className="relative flex items-center gap-4 py-4 mb-4">
              <div className="flex-grow h-px bg-zinc-200 dark:bg-zinc-800"></div>
              <span className="text-xs font-medium text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
                Or with email
              </span>
              <div className="flex-grow h-px bg-zinc-200 dark:bg-zinc-800"></div>
            </div>

            {/* Email/Password Form */}
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
                  Email address
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 text-lg">
                    mail
                  </span>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-zinc-50 dark:bg-zinc-950/50 border border-zinc-200 dark:border-zinc-700 rounded-xl text-zinc-900 dark:text-white placeholder-zinc-400 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="password" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    Password
                  </label>
                  <a href="#" className="text-xs font-medium text-primary hover:text-primary/80 transition-colors">
                    Forgot password?
                  </a>
                </div>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 text-lg">
                    lock
                  </span>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-zinc-50 dark:bg-zinc-950/50 border border-zinc-200 dark:border-zinc-700 rounded-xl text-zinc-900 dark:text-white placeholder-zinc-400 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-3 px-4 bg-zinc-900 dark:bg-white hover:bg-zinc-800 dark:hover:bg-zinc-200 text-white dark:text-black font-semibold rounded-full transition-all transform hover:scale-[1.01] active:scale-[0.98] shadow-lg shadow-zinc-900/10 dark:shadow-white/5 flex items-center justify-center gap-2"
                >
                  <span>Log in</span>
                  <span className="material-symbols-outlined text-lg">arrow_forward</span>
                </button>
              </div>
            </form>
          </div>

          {/* Footer Text */}
          <div className="mt-8 text-center space-y-4">
            <p className="text-xs text-zinc-400 dark:text-zinc-500 max-w-xs mx-auto">
              By clicking continue, you agree to our{' '}
              <a href="#" className="underline hover:text-zinc-700 dark:hover:text-zinc-300">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="#" className="underline hover:text-zinc-700 dark:hover:text-zinc-300">
                Privacy Policy
              </a>.
            </p>
          </div>
        </div>
      </main>

      {/* Dark Mode Toggle */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => document.documentElement.classList.toggle('dark')}
          className="p-3 rounded-full bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white shadow-lg border border-zinc-200 dark:border-zinc-700 hover:scale-110 transition-transform"
        >
          <span className="material-symbols-outlined block dark:hidden">dark_mode</span>
          <span className="material-symbols-outlined hidden dark:block">light_mode</span>
        </button>
      </div>
    </div>
  );
}
