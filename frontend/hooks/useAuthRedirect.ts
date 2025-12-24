'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export function useAuthRedirect() {
  const { checkAuth } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const authSuccess = searchParams.get('auth');

    if (authSuccess === 'success') {
      checkAuth().then(() => {
        router.replace('/');
      });
    }
  }, [searchParams, checkAuth, router]);
}
