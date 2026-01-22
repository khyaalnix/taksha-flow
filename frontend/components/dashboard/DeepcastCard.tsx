'use client';

import { useState } from 'react';
import Image from 'next/image';

export interface DeepcastData {
  id: string;
  title: string;
  excerpt: string;
  imageUrl: string;
  duration: string;
  progress: number; // 0-100
}

interface DeepcastCardProps {
  data: DeepcastData;
  onPlay?: () => void;
}

export function DeepcastCard({ data, onPlay }: DeepcastCardProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handlePlayClick = () => {
    setIsPlaying(!isPlaying);
    onPlay?.();
  };

  return (
    <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-zinc-800 to-zinc-900 aspect-[4/5] shadow-lg">
      {/* Background image */}
      {!imageError && (
        <Image
          src={data.imageUrl}
          alt={data.title}
          fill
          className="object-cover opacity-80 group-hover:scale-110 transition-transform duration-700"
          unoptimized
          onError={() => setImageError(true)}
        />
      )}

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />

      {/* Content */}
      <div className="absolute bottom-0 left-0 right-0 p-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="bg-white/20 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-medium text-white uppercase tracking-wide">
            Deepcast
          </span>
          <span className="material-symbols-outlined text-white text-xs">graphic_eq</span>
        </div>

        <h4 className="text-white font-medium leading-snug mb-1">{data.title}</h4>
        <p className="text-gray-300 text-xs line-clamp-2">{data.excerpt}</p>

        {/* Player controls */}
        <div className="mt-4 flex items-center justify-between bg-white/10 backdrop-blur-md rounded-lg p-2">
          <button
            onClick={handlePlayClick}
            className="text-white hover:text-indigo-400 transition-colors"
          >
            <span className="material-symbols-outlined text-lg">
              {isPlaying ? 'pause' : 'play_arrow'}
            </span>
          </button>
          <div className="h-1 flex-1 mx-3 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${data.progress}%` }}
            />
          </div>
          <span className="text-[10px] text-gray-300 font-mono">{data.duration}</span>
        </div>
      </div>
    </div>
  );
}
