'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { LandingPage } from '@/components/landing/LandingPage';
import { DashboardPage } from '@/components/dashboard';
import { useAuth } from '@/contexts/AuthContext';

function HomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    const authSuccess = searchParams.get('auth');

    if (authSuccess === 'success') {
      // Redirect to interests page for new users after OAuth
      // (permissions were already shown on /setup before login)
      router.push('/interests');
    }
  }, [searchParams, router]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-[#050505] flex items-center justify-center">
        <div className="text-zinc-600 dark:text-zinc-400">Loading...</div>
      </div>
    );
  }

  // Show dashboard for authenticated users, landing page for others
  return isAuthenticated ? <DashboardPage /> : <LandingPage />;
}

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-white dark:bg-[#050505]" />}>
      <HomeContent />
    </Suspense>
  );
}
