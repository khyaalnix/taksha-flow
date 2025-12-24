'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { UserAvatar } from './UserAvatar';

export function ProfileMenu() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      setIsLoggingOut(false);
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 hover:bg-gray-100 rounded-full p-1 transition-colors"
        aria-label="Open profile menu"
      >
        <UserAvatar user={user} size="sm" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 py-3 z-50">
          <div className="px-4 py-3 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <UserAvatar user={user} size="lg" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
              </div>
            </div>
          </div>

          <div className="py-2">
            <button
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoggingOut ? 'Signing out...' : 'Sign out'}
            </button>
          </div>

          <div className="px-4 py-2 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Taksha Flow • {new Date().getFullYear()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
