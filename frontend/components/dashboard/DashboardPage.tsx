'use client';

import { useState } from 'react';
import { Navigation } from '../shared/Navigation';
import { DailyBriefHeader } from './DailyBriefHeader';
import { PriorityItems } from './PriorityItems';
import { SuggestionCard } from './SuggestionCard';
import { CenterSection } from './CenterSection';
import { DeepcastCard, DeepcastData } from './DeepcastCard';
import { ContentCard, ContentCardData } from './ContentCard';
import { PriorityItemData } from './PriorityItem';
import { WaveFooter } from './WaveFooter';
import { useDashboardData } from '@/hooks/useDashboardData';

// Fallback mock data for when API fails or during loading
const fallbackPriorityItems: PriorityItemData[] = [
  {
    id: '1',
    type: 'event',
    title: 'Loading...',
    subtitle: 'Fetching your schedule',
  },
];

const fallbackDeepcast: DeepcastData = {
  id: '1',
  title: 'Are chickens really dinosaurs?',
  excerpt: '"Exactly. If you compare a T-rex leg bone to a chicken\'s..."',
  imageUrl: 'https://images.unsplash.com/photo-1606567595334-d39972c85dfd?w=400&h=500&fit=crop',
  duration: '0:42',
  progress: 33,
};

const fallbackContentItems: ContentCardData[] = [
  {
    id: '1',
    title: 'Foundry Industrials',
    description: 'Unveils "Air" a new ultralight phone concept.',
    imageUrl: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=100&h=100&fit=crop',
    bookmarked: false,
  },
  {
    id: '2',
    title: 'Weekend Plans',
    description: 'The 12 best sushi spots in the Bay Area right now.',
    imageUrl: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=100&h=100&fit=crop',
    bookmarked: false,
  },
];

export function DashboardPage() {
  const [isPlaying, setIsPlaying] = useState(true);

  const {
    priorityItems,
    urgentCount,
    suggestion,
    deepcast,
    contentItems,
    isLoading,
    isLoadingCalendar,
    isLoadingEmail,
    isSummarizing,
    isFullyLoaded,
  } = useDashboardData();

  const handleListeningTap = () => {
    setIsPlaying(!isPlaying);
  };

  // Transform priority items to component format
  const displayPriorityItems: PriorityItemData[] = priorityItems.map((item) => ({
    id: item.id,
    type: item.type as PriorityItemData['type'],
    title: item.title,
    subtitle: item.subtitle,
  }));

  // Show loading indicator in priority items
  const priorityItemsWithLoading: PriorityItemData[] = [...displayPriorityItems];

  // Add loading indicators if still fetching
  if (isLoadingCalendar && !priorityItems.some((p) => p.type === 'event')) {
    priorityItemsWithLoading.unshift({
      id: 'loading-calendar',
      type: 'event',
      title: isSummarizing ? 'Summarizing...' : 'Loading calendar...',
      subtitle: 'Fetching your events',
    });
  } else if (!isLoadingCalendar && !priorityItems.some((p) => p.type === 'event')) {
    // No calendar events - show "No events" message
    priorityItemsWithLoading.unshift({
      id: 'no-events',
      type: 'event',
      title: 'No Events Today',
      subtitle: 'Your calendar is clear',
    });
  }

  if (isLoadingEmail && !priorityItems.some((p) => p.type === 'email')) {
    priorityItemsWithLoading.push({
      id: 'loading-email',
      type: 'email',
      title: isSummarizing ? 'Summarizing...' : 'Loading emails...',
      subtitle: 'Checking your inbox',
    });
  }

  // Handle priority item clicks
  const handlePriorityItemClick = (item: PriorityItemData) => {
    if (item.type === 'email') {
      window.open('https://mail.google.com', '_blank');
    } else if (item.type === 'event') {
      window.open('https://calendar.google.com', '_blank');
    }
  };

  // Transform deepcast data
  const displayDeepcast: DeepcastData = deepcast
    ? {
        id: deepcast.id,
        title: deepcast.title,
        excerpt: deepcast.excerpt,
        imageUrl: deepcast.image_url || fallbackDeepcast.imageUrl,
        duration: deepcast.duration,
        progress: deepcast.progress,
      }
    : fallbackDeepcast;

  // Transform content items
  const displayContentItems: ContentCardData[] =
    contentItems.length > 0
      ? contentItems.map((item) => ({
          id: item.id,
          title: item.title,
          description: item.description,
          imageUrl: item.image_url,
          bookmarked: item.bookmarked,
        }))
      : fallbackContentItems;

  return (
    <div className="bg-white dark:bg-[#0a0a0a] min-h-screen transition-colors duration-300 relative overflow-hidden">
      {/* Background gradient */}
      <div className="fixed inset-0 pointer-events-none hero-gradient z-0" />

      {/* Navigation */}
      <Navigation />

      {/* Main content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-32 min-h-screen">
        <div className="flex flex-col lg:flex-row gap-8 h-full">
          {/* Left sidebar */}
          <aside className="w-full lg:w-72 flex-shrink-0 flex flex-col gap-6 order-2 lg:order-1">
            <DailyBriefHeader />
            <PriorityItems
              items={priorityItemsWithLoading.slice(0, 5)}
              urgentCount={urgentCount}
              onItemClick={handlePriorityItemClick}
            />
            <div className="mt-auto hidden lg:block">
              <SuggestionCard suggestion={suggestion} />
            </div>
          </aside>

          {/* Center section */}
          <div className="flex-1 flex items-center justify-center order-1 lg:order-2 min-h-[60vh] lg:min-h-0">
            <CenterSection onListeningTap={handleListeningTap} isPlaying={isPlaying} />
          </div>

          {/* Right sidebar */}
          <aside className="w-full lg:w-72 flex-shrink-0 flex flex-col gap-4 order-3">
            <div className="flex items-center justify-between px-1">
              <h3 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400">
                Visual Context
              </h3>
              {isLoading && (
                <span className="text-xs text-zinc-400 animate-pulse">Loading...</span>
              )}
            </div>

            <DeepcastCard data={displayDeepcast} />

            <div className="space-y-3">
              {displayContentItems.map((item) => (
                <ContentCard key={item.id} data={item} />
              ))}
            </div>
          </aside>
        </div>

        {/* Mobile suggestion card */}
        <div className="lg:hidden mt-8">
          <SuggestionCard suggestion={suggestion} />
        </div>
      </main>

      {/* Wave footer */}
      <WaveFooter />
    </div>
  );
}
