export type PriorityItemType = 'event' | 'email' | 'news' | 'task';

export interface PriorityItem {
  id: string;
  type: PriorityItemType;
  title: string;
  subtitle: string;
  timestamp?: string;
  metadata?: Record<string, unknown>;
}

export interface DeepcastItem {
  id: string;
  title: string;
  excerpt: string;
  image_url?: string;
  audio_url?: string;
  duration: string;
  progress: number;
  source?: string;
}

export interface ContentItem {
  id: string;
  title: string;
  description: string;
  image_url?: string;
  source_url?: string;
  source_name?: string;
  bookmarked: boolean;
  category?: string;
}

export interface DashboardBrief {
  greeting: string;
  date: string;
  priority_items: PriorityItem[];
  urgent_count: number;
  suggestion?: string;
  deepcast?: DeepcastItem;
  content_items: ContentItem[];
}

export interface CalendarEvent {
  id: string;
  summary: string;
  start_time?: string;
  end_time?: string;
  location?: string;
  attendees: string[];
  is_all_day: boolean;
}

export interface EmailSummary {
  total_unread: number;
  top_sender?: string;
  top_subject?: string;
  priority_emails: Array<{
    id: string;
    sender?: string;
    subject?: string;
    date?: string;
  }>;
}
