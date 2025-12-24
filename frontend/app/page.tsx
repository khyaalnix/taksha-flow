'use client';

import { Suspense } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useAuthRedirect } from '@/hooks/useAuthRedirect';
import { LoginPage } from '@/components/auth/LoginPage';
import { Dashboard } from '@/components/ui/Dashboard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

function HomeContent() {
  useAuthRedirect();
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return isAuthenticated ? <Dashboard /> : <LoginPage />;
}

export default function Home() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HomeContent />
    </Suspense>
  );
}
