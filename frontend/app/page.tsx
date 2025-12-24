'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useAuthRedirect } from '@/hooks/useAuthRedirect';
import { LoginPage } from '@/components/auth/LoginPage';
import { Dashboard } from '@/components/ui/Dashboard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function Home() {
  useAuthRedirect();
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return isAuthenticated ? <Dashboard /> : <LoginPage />;
}
