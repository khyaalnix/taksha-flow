'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '../shared/Navigation';
import { BackgroundGradients } from '../shared/BackgroundGradients';
import { Footer } from '../shared/Footer';
import { InterestCard } from './InterestCard';

interface Interest {
  id: string;
  name: string;
  icon: string;
  description: string;
}

const availableInterests: Interest[] = [
  {
    id: 'news',
    name: 'News & Current Events',
    icon: '📰',
    description: 'Stay updated with global and local news that matters to you',
  },
  {
    id: 'tech',
    name: 'Technology',
    icon: '💻',
    description: 'Latest tech trends, gadgets, and innovations',
  },
  {
    id: 'sports',
    name: 'Sports',
    icon: '⚽',
    description: 'Follow your favorite teams and sporting events',
  },
  {
    id: 'business',
    name: 'Business & Finance',
    icon: '💼',
    description: 'Markets, economy, and business insights',
  },
  {
    id: 'science',
    name: 'Science',
    icon: '🔬',
    description: 'Discoveries, research, and scientific breakthroughs',
  },
  {
    id: 'entertainment',
    name: 'Entertainment',
    icon: '🎬',
    description: 'Movies, TV shows, music, and celebrity news',
  },
  {
    id: 'health',
    name: 'Health & Wellness',
    icon: '💪',
    description: 'Fitness, nutrition, and mental health tips',
  },
  {
    id: 'travel',
    name: 'Travel',
    icon: '✈️',
    description: 'Destinations, travel tips, and adventure ideas',
  },
  {
    id: 'food',
    name: 'Food & Cooking',
    icon: '🍳',
    description: 'Recipes, restaurants, and culinary trends',
  },
];

export function InterestsPage() {
  const router = useRouter();
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Fetch existing interests on mount
  useEffect(() => {
    const fetchInterests = async () => {
      try {
        const response = await fetch('/flow/interests/user');
        if (response.ok) {
          const data = await response.json();
          const existingIds = data.data?.map((item: any) => item.interest_id) || [];
          setSelectedInterests(existingIds);
        }
      } catch (error) {
        console.error('Error fetching interests:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInterests();
  }, []);

  const handleToggle = (id: string) => {
    setSelectedInterests(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleContinue = async () => {
    if (selectedInterests.length === 0) {
      alert('Please select at least one interest');
      return;
    }

    setSaving(true);
    try {
      const response = await fetch('/flow/interests/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interest_ids: selectedInterests,
        }),
      });

      if (response.ok) {
        // Navigate to home or dashboard
        router.push('/');
      } else {
        alert('Failed to save interests. Please try again.');
      }
    } catch (error) {
      console.error('Error saving interests:', error);
      alert('Failed to save interests. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleSkip = () => {
    router.push('/');
  };

  if (loading) {
    return (
      <div className="bg-zinc-50 dark:bg-[#050505] min-h-screen flex items-center justify-center">
        <div className="text-zinc-600 dark:text-zinc-400">Loading interests...</div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-50 dark:bg-[#050505] min-h-screen flex flex-col transition-colors duration-300">
      <BackgroundGradients />
      <Navigation showAuthButton={false} />

      <main className="flex-grow pt-40 pb-20 px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6 text-zinc-900 dark:text-white">
            What interests you?
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            Select topics you'd like to hear about in your daily briefing. We'll curate content based on your interests.
          </p>
        </div>

        {/* Interests Grid */}
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-16">
          {availableInterests.map(interest => (
            <InterestCard
              key={interest.id}
              {...interest}
              selected={selectedInterests.includes(interest.id)}
              onToggle={handleToggle}
            />
          ))}
        </div>

        {/* Selection Counter */}
        <div className="max-w-5xl mx-auto text-center mb-8">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {selectedInterests.length} {selectedInterests.length === 1 ? 'interest' : 'interests'} selected
          </p>
        </div>

        {/* Continue and Skip Options */}
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-6">
            <button
              onClick={handleContinue}
              disabled={saving || selectedInterests.length === 0}
              className="bg-zinc-900 hover:bg-zinc-800 dark:bg-white dark:hover:bg-zinc-200 text-white dark:text-black px-8 py-3 rounded-full text-base font-semibold transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Continue'}
            </button>
            <button
              onClick={handleSkip}
              disabled={saving}
              className="inline-flex items-center justify-center gap-2 text-zinc-600 dark:text-zinc-400 hover:text-primary dark:hover:text-white font-medium px-8 py-3 transition-colors disabled:opacity-50"
            >
              Skip for now
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          </div>
          <p className="text-xs text-zinc-400 dark:text-zinc-600 max-w-md mx-auto">
            You can always update your interests later in settings
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
