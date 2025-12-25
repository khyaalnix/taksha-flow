'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { LandingPage } from '@/components/landing/LandingPage';

function HomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const authSuccess = searchParams.get('auth');

    if (authSuccess === 'success') {
      // Redirect to integrations page for new users after OAuth
      router.push('/integrations');
    }
  }, [searchParams, router]);

  return <LandingPage />;
}

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-white dark:bg-[#050505]" />}>
      <HomeContent />
    </Suspense>
  );
}
