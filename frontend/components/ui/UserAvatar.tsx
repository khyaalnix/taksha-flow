'use client';

import { useState } from 'react';
import type { User } from '@/types/auth';

interface UserAvatarProps {
  user: User;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-12 h-12 text-base',
  lg: 'w-16 h-16 text-xl',
};

export function UserAvatar({ user, size = 'md' }: UserAvatarProps) {
  const [imageError, setImageError] = useState(false);

  const initials = user.name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || user.email[0].toUpperCase();

  if (user.picture && !imageError) {
    return (
      <img
        src={user.picture}
        alt={user.name || user.email}
        className={`${sizeClasses[size]} rounded-full object-cover border border-gray-200`}
        onError={() => setImageError(true)}
        referrerPolicy="no-referrer"
      />
    );
  }

  return (
    <div
      className={`${sizeClasses[size]} rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold`}
    >
      {initials}
    </div>
  );
}
