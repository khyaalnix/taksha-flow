'use client';

import { useState, useEffect } from 'react';
import { Navigation } from '../shared/Navigation';
import { DailyBriefHeader } from './DailyBriefHeader';
import { PriorityItems } from './PriorityItems';
import { SuggestionCard } from './SuggestionCard';
import { CenterSection } from './CenterSection';
import { DeepcastCard, DeepcastData } from './DeepcastCard';
import { ContentCard, ContentCardData } from './ContentCard';
import { PriorityItemData } from './PriorityItem';
import { WaveFooter } from './WaveFooter';
import { dashboardApi } from '@/lib/api/dashboard';
import type { DashboardBrief } from '@/types/dashboard';

// Fallback mock data for when API fails or during loading
const fallbackPriorityItems: PriorityItemData[] = [
  {
    id: '1',
    type: 'event',
    title: 'Design Review',
    subtitle: '10:00 AM with Product Team',
  },
  {
    id: '2',
    type: 'email',
    title: '8 New Emails',
    subtitle: 'Top: Contract revision from Sarah',
  },
  {
    id: '3',
    type: 'news',
    title: 'Tech Daily',
    subtitle: 'Apple announces new spatial devices.',
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
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardBrief | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await dashboardApi.getBrief({
          include_calendar: true,
          include_email: true,
          include_news: true,
          max_priority_items: 5,
        });
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Keep using fallback data on error
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleListeningTap = () => {
    setIsPlaying(!isPlaying);
  };

  // Transform API data to component format
  const priorityItems: PriorityItemData[] = dashboardData?.priority_items?.map((item) => ({
    id: item.id,
    type: item.type as PriorityItemData['type'],
    title: item.title,
    subtitle: item.subtitle,
  })) || fallbackPriorityItems;

  const urgentCount = dashboardData?.urgent_count ?? 3;

  const suggestion = dashboardData?.suggestion || '"Hey Flow, draft a reply to Sarah about the contract."';

  const deepcast: DeepcastData = dashboardData?.deepcast
    ? {
        id: dashboardData.deepcast.id,
        title: dashboardData.deepcast.title,
        excerpt: dashboardData.deepcast.excerpt,
        imageUrl: dashboardData.deepcast.image_url || fallbackDeepcast.imageUrl,
        duration: dashboardData.deepcast.duration,
        progress: dashboardData.deepcast.progress,
      }
    : fallbackDeepcast;

  const contentItems: ContentCardData[] = dashboardData?.content_items?.map((item) => ({
    id: item.id,
    title: item.title,
    description: item.description,
    imageUrl: item.image_url,
    bookmarked: item.bookmarked,
  })) || fallbackContentItems;

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
            <PriorityItems items={priorityItems} urgentCount={urgentCount} />
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
            </div>

            <DeepcastCard data={deepcast} />

            <div className="space-y-3">
              {contentItems.map((item) => (
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
