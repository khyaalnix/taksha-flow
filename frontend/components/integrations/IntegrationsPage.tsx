'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '../shared/Navigation';
import { BackgroundGradients } from '../shared/BackgroundGradients';
import { Footer } from '../shared/Footer';
import { IntegrationCard } from './IntegrationCard';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface Integration {
  id: string;
  icon: string;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  status: 'available' | 'connected' | 'coming-soon';
  statusText: string;
  statusColor: string;
  checkEndpoint?: string;
}

const integrationDefinitions: Omit<Integration, 'status'>[] = [
  {
    id: 'gmail',
    icon: 'mail',
    iconBg: 'bg-red-50 dark:bg-red-900/20',
    iconColor: 'text-red-500',
    title: 'Gmail',
    description: 'We scan for newsletters, flight confirmations, and urgent updates to summarize specifically for your morning audio brief.',
    statusText: 'Secure Read-Only Access',
    statusColor: 'bg-green-500',
    checkEndpoint: '/check/gmail',
  },
  {
    id: 'calendar',
    icon: 'calendar_month',
    iconBg: 'bg-blue-50 dark:bg-blue-900/20',
    iconColor: 'text-blue-500',
    title: 'Calendar',
    description: "Sync your meetings to get a rundown of your day. We'll remind you of prep time and identify scheduling conflicts.",
    statusText: 'Events Synced',
    statusColor: 'bg-green-500',
    checkEndpoint: '/check/calendar',
  },
  {
    id: 'location',
    icon: 'near_me',
    iconBg: 'bg-purple-50 dark:bg-purple-900/20',
    iconColor: 'text-purple-500',
    title: 'Location',
    description: 'Provide hyper-local weather updates and traffic estimates for your commute based on your current whereabouts.',
    statusText: 'Approximate Only',
    statusColor: 'bg-yellow-500',
    checkEndpoint: '/check/location',
  },
];

export function IntegrationsPage() {
  const router = useRouter();
  const [integrations, setIntegrations] = useState<Integration[]>(
    integrationDefinitions.map(def => ({ ...def, status: 'available' as const }))
  );
  const [loading, setLoading] = useState(true);

  // Check connection status for all integrations on mount
  useEffect(() => {
    const checkConnectionStatus = async () => {
      const updatedIntegrations = await Promise.all(
        integrationDefinitions.map(async integration => {
          if (!integration.checkEndpoint) {
            return { ...integration, status: 'available' as const };
          }

          try {
            const response = await fetch(`${API_URL}${integration.checkEndpoint}`, {
              credentials: 'include',
            });
            const isConnected = response.status === 200;
            return {
              ...integration,
              status: isConnected ? ('connected' as const) : ('available' as const),
            };
          } catch (error) {
            console.error(`Error checking ${integration.id} status:`, error);
            return { ...integration, status: 'available' as const };
          }
        })
      );

      setIntegrations(updatedIntegrations);
      setLoading(false);
    };

    checkConnectionStatus();
  }, []);

  const handleConnect = async (id: string) => {
    const integration = integrations.find(i => i.id === id);
    if (!integration) return;

    if (integration.status === 'connected') {
      // Handle disconnect
      setIntegrations(prev =>
        prev.map(i =>
          i.id === id ? { ...i, status: 'available' as const } : i
        )
      );
      console.log(`Disconnecting from ${id}...`);
    } else {
      // Handle connect - simulate OAuth flow
      console.log(`Initiating OAuth for ${id}...`);

      // For now, just toggle the status
      // In production, this would redirect to OAuth URL
      setIntegrations(prev =>
        prev.map(i =>
          i.id === id ? { ...i, status: 'connected' as const } : i
        )
      );
    }
  };

  const handleSkip = () => {
    router.push('/');
  };

  if (loading) {
    return (
      <div className="bg-zinc-50 dark:bg-[#050505] min-h-screen flex items-center justify-center">
        <div className="text-zinc-600 dark:text-zinc-400">Loading integrations...</div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-50 dark:bg-[#050505] min-h-screen flex flex-col transition-colors duration-300">
      <BackgroundGradients />
      <Navigation showAuthButton={false} />

      <main className="flex-grow pt-40 pb-20 px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6 text-zinc-900 dark:text-white">
            Power your personal briefing
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            To give you the most relevant daily summary, Flow needs access to your digital life. Your data is encrypted and processed locally whenever possible.
          </p>
        </div>

        {/* Integrations Grid */}
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {integrations.map(integration => (
            <IntegrationCard
              key={integration.id}
              {...integration}
              onConnect={() => handleConnect(integration.id)}
            />
          ))}
        </div>

        {/* Continue and Skip Options */}
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-6">
            <button
              onClick={() => router.push('/interests')}
              className="bg-zinc-900 hover:bg-zinc-800 dark:bg-white dark:hover:bg-zinc-200 text-white dark:text-black px-8 py-3 rounded-full text-base font-semibold transition-all shadow-lg hover:shadow-xl"
            >
              Continue
            </button>
            <button
              onClick={handleSkip}
              className="inline-flex items-center justify-center gap-2 text-zinc-600 dark:text-zinc-400 hover:text-primary dark:hover:text-white font-medium px-8 py-3 transition-colors"
            >
              Skip for now
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          </div>
          <p className="text-xs text-zinc-400 dark:text-zinc-600 max-w-md mx-auto">
            By connecting a service, you agree to our{' '}
            <a className="underline hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors" href="#">
              Privacy Policy
            </a>
            . You can revoke access at any time from your account settings.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
