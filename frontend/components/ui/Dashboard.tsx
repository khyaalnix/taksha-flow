'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ProfileMenu } from './ProfileMenu';

export function Dashboard() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">Taksha Flow</h1>
            <ProfileMenu />
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user.name?.split(' ')[0] || 'User'}!
          </h2>
          <p className="text-gray-600">
            Your personalized dashboard for calendar, mail, and news feed
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Connected Services"
            value="2"
            icon="🔗"
            description="Gmail & Calendar"
          />
          <StatCard
            title="Today's Events"
            value="0"
            icon="📅"
            description="No events scheduled"
          />
          <StatCard
            title="Unread Emails"
            value="0"
            icon="📧"
            description="All caught up!"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FeatureCard
            title="📧 Email"
            description="Email integration coming soon..."
            status="Coming Soon"
          />
          <FeatureCard
            title="📅 Calendar"
            description="Calendar integration coming soon..."
            status="Coming Soon"
          />
          <FeatureCard
            title="📰 News Feed"
            description="News feed integration coming soon..."
            status="Coming Soon"
          />
          <FeatureCard
            title="⚙️ Settings"
            description="Manage your preferences and integrations"
            status="Coming Soon"
          />
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, icon, description }: {
  title: string;
  value: string;
  icon: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-sm text-gray-500">{description}</p>
    </div>
  );
}

function FeatureCard({ title, description, status }: {
  title: string;
  description: string;
  status: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-full">
          {status}
        </span>
      </div>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
