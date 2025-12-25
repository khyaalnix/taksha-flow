'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ProfileMenu } from './ProfileMenu';

export function Dashboard() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-[#050505] transition-colors duration-300">
      {/* Animated Background Gradients */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[20%] -right-[10%] w-[50%] h-[50%] bg-primary/5 dark:bg-primary/3 rounded-full blur-[120px] animate-float"></div>
        <div className="absolute -bottom-[20%] -left-[10%] w-[50%] h-[50%] bg-purple-500/5 dark:bg-purple-500/3 rounded-full blur-[120px] animate-float" style={{animationDelay: '-5s'}}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 bg-white/80 dark:bg-zinc-900/50 backdrop-blur-xl border-b border-zinc-200 dark:border-zinc-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-black flex items-center justify-center">
                <span className="material-symbols-outlined text-xl">auto_awesome</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight text-zinc-900 dark:text-white">Flow</h1>
            </div>
            <ProfileMenu />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-10">
          <h2 className="text-3xl md:text-4xl font-bold text-zinc-900 dark:text-white mb-3 tracking-tight">
            Good morning, {user.name?.split(' ')[0] || 'there'}
          </h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-lg">
            Your personalized daily briefing is ready
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <StatCard
            title="Connected Services"
            value="2"
            icon="link"
            iconBg="bg-blue-100 dark:bg-blue-900/30"
            iconColor="text-blue-600 dark:text-blue-400"
            description="Gmail & Calendar"
          />
          <StatCard
            title="Today's Events"
            value="0"
            icon="calendar_today"
            iconBg="bg-green-100 dark:bg-green-900/30"
            iconColor="text-green-600 dark:text-green-400"
            description="No events scheduled"
          />
          <StatCard
            title="Unread Emails"
            value="0"
            icon="mail"
            iconBg="bg-purple-100 dark:bg-purple-900/30"
            iconColor="text-purple-600 dark:text-purple-400"
            description="All caught up!"
          />
        </div>

        {/* Features Section */}
        <div>
          <h3 className="text-xl font-bold text-zinc-900 dark:text-white mb-6">
            Your Integrations
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <FeatureCard
              title="Email"
              icon="mail"
              description="View and manage your emails with AI-powered insights"
              status="Coming Soon"
            />
            <FeatureCard
              title="Calendar"
              icon="calendar_month"
              description="Stay organized with your schedule and events"
              status="Coming Soon"
            />
            <FeatureCard
              title="News Feed"
              icon="newspaper"
              description="Personalized news and updates from your interests"
              status="Coming Soon"
            />
            <FeatureCard
              title="Settings"
              icon="settings"
              description="Manage your preferences and integrations"
              status="Coming Soon"
            />
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

function StatCard({
  title,
  value,
  icon,
  iconBg,
  iconColor,
  description
}: {
  title: string;
  value: string;
  icon: string;
  iconBg: string;
  iconColor: string;
  description: string;
}) {
  return (
    <div className="bg-white dark:bg-zinc-900/50 backdrop-blur-xl rounded-2xl border border-zinc-200 dark:border-zinc-800 p-6 hover:shadow-lg dark:hover:shadow-[0_0_40px_-10px_rgba(234,88,12,0.2)] transition-all">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">{title}</p>
        <div className={`w-10 h-10 ${iconBg} rounded-xl flex items-center justify-center`}>
          <span className={`material-symbols-outlined text-xl ${iconColor}`}>{icon}</span>
        </div>
      </div>
      <p className="text-3xl font-bold text-zinc-900 dark:text-white mb-1">{value}</p>
      <p className="text-sm text-zinc-500 dark:text-zinc-400">{description}</p>
    </div>
  );
}

function FeatureCard({
  title,
  icon,
  description,
  status
}: {
  title: string;
  icon: string;
  description: string;
  status: string;
}) {
  return (
    <div className="group bg-white dark:bg-zinc-900/50 backdrop-blur-xl rounded-2xl border border-zinc-200 dark:border-zinc-800 p-6 hover:border-primary dark:hover:border-primary transition-all hover:shadow-lg dark:hover:shadow-[0_0_40px_-10px_rgba(234,88,12,0.2)] cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-zinc-100 dark:bg-zinc-800 rounded-xl flex items-center justify-center group-hover:bg-primary/10 transition-colors">
            <span className="material-symbols-outlined text-2xl text-zinc-700 dark:text-zinc-300 group-hover:text-primary transition-colors">
              {icon}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">{title}</h3>
        </div>
        <span className="px-3 py-1 text-xs font-medium text-primary bg-primary/10 rounded-full">
          {status}
        </span>
      </div>
      <p className="text-zinc-600 dark:text-zinc-400 text-sm">{description}</p>
    </div>
  );
}
