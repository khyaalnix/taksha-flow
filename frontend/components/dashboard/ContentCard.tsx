'use client';

import Image from 'next/image';

export interface ContentCardData {
  id: string;
  title: string;
  description: string;
  imageUrl?: string;
  bookmarked?: boolean;
}

interface ContentCardProps {
  data: ContentCardData;
  onClick?: () => void;
  onBookmark?: () => void;
}

export function ContentCard({ data, onClick, onBookmark }: ContentCardProps) {
  return (
    <div
      onClick={onClick}
      className="glass-panel p-4 rounded-xl flex gap-3 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer group"
    >
      {/* Thumbnail */}
      {data.imageUrl && (
        <div className="h-12 w-12 rounded-lg bg-zinc-200 dark:bg-zinc-700 flex-shrink-0 overflow-hidden relative">
          <Image
            src={data.imageUrl}
            alt={data.title}
            fill
            className="object-cover group-hover:scale-110 transition-transform"
            unoptimized
          />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <h5 className="text-sm font-medium text-zinc-900 dark:text-white truncate">
          {data.title}
        </h5>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2">
          {data.description}
        </p>
      </div>

      {/* Bookmark button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onBookmark?.();
        }}
        className="text-zinc-400 hover:text-indigo-500 transition-colors"
      >
        <span className="material-symbols-outlined text-sm">
          {data.bookmarked ? 'bookmark' : 'bookmark_border'}
        </span>
      </button>
    </div>
  );
}
