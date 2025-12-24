'use client';

import { LoginButton } from './LoginButton';

export function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-8">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome to Taksha Flow
            </h1>
            <p className="text-gray-600">
              Sign in to connect your calendar, mail, and news feed
            </p>
          </div>

          <div className="flex justify-center">
            <LoginButton />
          </div>

          <div className="text-center text-sm text-gray-500">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </div>
        </div>
      </div>
    </div>
  );
}
