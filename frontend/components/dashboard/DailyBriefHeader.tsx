'use client';

import { useAuth } from '@/contexts/AuthContext';

export function DailyBriefHeader() {
  const { user } = useAuth();

  const now = new Date();
  const formattedDate = now.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const getGreeting = () => {
    const hour = now.getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const firstName = user?.name?.split(' ')[0] || 'there';

  return (
    <div className="glass-panel p-6 rounded-2xl shadow-sm">
      <p className="text-sm text-zinc-500 dark:text-zinc-400 font-medium uppercase tracking-wider mb-1">
        Daily Brief &bull; {formattedDate}
      </p>
      <h1 className="text-3xl font-semibold text-zinc-900 dark:text-white leading-tight">
        {getGreeting()},<br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-purple-600">
          {firstName}
        </span>
      </h1>
    </div>
  );
}
