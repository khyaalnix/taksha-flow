'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { LandingPage } from '@/components/landing/LandingPage';

export default function Home() {
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
