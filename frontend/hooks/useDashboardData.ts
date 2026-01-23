'use client';

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { dashboardApi } from '@/lib/api/dashboard';
import {
  summarizeCalendarEvents,
  summarizeEmails,
  type CalendarEventRaw,
  type SummarizedCalendarEvent,
  type SummarizedEmail,
} from '@/lib/ai/gemini';
import type { DashboardBrief, PriorityItem } from '@/types/dashboard';

interface DashboardBaseState {
  // From backend (pre-fetched news)
  greeting: string;
  date: string;
  suggestion: string;
  newsItem: PriorityItem | null;
  deepcast: DashboardBrief['deepcast'] | null;
  contentItems: DashboardBrief['content_items'];

  // From client-side summarization
  calendarItems: SummarizedCalendarEvent[];
  emailItem: SummarizedEmail | null;

  // Loading states
  isLoading: boolean;
  isLoadingCalendar: boolean;
  isLoadingEmail: boolean;
  isSummarizing: boolean;

  // Error states
  error: string | null;
}

const initialState: DashboardBaseState = {
  greeting: 'Good Morning',
  date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
  suggestion: '"Hey Flow, what\'s on my agenda today?"',
  newsItem: null,
  deepcast: null,
  contentItems: [],
  calendarItems: [],
  emailItem: null,
  isLoading: true,
  isLoadingCalendar: true,
  isLoadingEmail: true,
  isSummarizing: false,
  error: null,
};

export function useDashboardData() {
  const [state, setState] = useState<DashboardBaseState>(initialState);
  const hasFetched = useRef(false);

  // Derive priority items from state using useMemo (not useEffect + setState)
  const priorityItems = useMemo<PriorityItem[]>(() => {
    const items: PriorityItem[] = [];

    // Add calendar events first (most urgent)
    state.calendarItems.forEach((event) => {
      items.push({
        id: event.id,
        type: 'event',
        title: event.title,
        subtitle: event.subtitle,
      });
    });

    // Add email summary
    if (state.emailItem) {
      items.push({
        id: state.emailItem.id,
        type: 'email',
        title: state.emailItem.title,
        subtitle: state.emailItem.subtitle,
      });
    }

    // Add news item
    if (state.newsItem) {
      items.push(state.newsItem);
    }

    return items.slice(0, 5);
  }, [state.calendarItems, state.emailItem, state.newsItem]);

  // Derive urgent count from calendar items
  const urgentCount = useMemo(() => state.calendarItems.length, [state.calendarItems]);

  // Fetch base dashboard data (news, deepcast, content - pre-cached on backend)
  const fetchBaseDashboard = useCallback(async () => {
    try {
      // Fetch dashboard brief without calendar/email (handled separately)
      const data = await dashboardApi.getBrief({
        include_calendar: false,
        include_email: false,
        include_news: true,
        max_priority_items: 5,
      });

      setState((prev) => ({
        ...prev,
        greeting: data.greeting,
        date: data.date,
        suggestion: data.suggestion || prev.suggestion,
        newsItem: data.priority_items?.find((item) => item.type === 'news') || null,
        deepcast: data.deepcast || null,
        contentItems: data.content_items || [],
        isLoading: false,
      }));
    } catch (error) {
      console.error('Error fetching dashboard brief:', error);
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: 'Failed to load dashboard data',
      }));
    }
  }, []);

  // Fetch and summarize calendar events (client-side)
  const fetchAndSummarizeCalendar = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoadingCalendar: true }));

    try {
      const response = await dashboardApi.getTodaysCalendarEvents(5);
      const events = response.data as CalendarEventRaw[];

      if (events.length > 0) {
        setState((prev) => ({ ...prev, isSummarizing: true }));
        const summarized = await summarizeCalendarEvents(events);
        setState((prev) => ({
          ...prev,
          calendarItems: summarized,
          isLoadingCalendar: false,
          isSummarizing: false,
        }));
      } else {
        setState((prev) => ({
          ...prev,
          calendarItems: [],
          isLoadingCalendar: false,
        }));
      }
    } catch (error) {
      console.error('Error fetching calendar events:', error);
      setState((prev) => ({
        ...prev,
        calendarItems: [],
        isLoadingCalendar: false,
        isSummarizing: false,
      }));
    }
  }, []);

  // Fetch and summarize emails (client-side)
  const fetchAndSummarizeEmail = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoadingEmail: true }));

    try {
      const response = await dashboardApi.getEmailSummary(5);
      const emailData = response.data;

      if (emailData && emailData.total_unread > 0) {
        setState((prev) => ({ ...prev, isSummarizing: true }));
        const summarized = await summarizeEmails(
          emailData.priority_emails || [],
          emailData.total_unread
        );
        setState((prev) => ({
          ...prev,
          emailItem: summarized,
          isLoadingEmail: false,
          isSummarizing: false,
        }));
      } else {
        setState((prev) => ({
          ...prev,
          emailItem: null,
          isLoadingEmail: false,
        }));
      }
    } catch (error) {
      console.error('Error fetching email summary:', error);
      setState((prev) => ({
        ...prev,
        emailItem: null,
        isLoadingEmail: false,
        isSummarizing: false,
      }));
    }
  }, []);

  // Initial fetch - use ref to prevent double fetching
  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    // Fetch all data in parallel
    void fetchBaseDashboard();
    void fetchAndSummarizeCalendar();
    void fetchAndSummarizeEmail();
  }, [fetchBaseDashboard, fetchAndSummarizeCalendar, fetchAndSummarizeEmail]);

  // Refresh function
  const refresh = useCallback(() => {
    setState((prev) => ({
      ...prev,
      isLoading: true,
      isLoadingCalendar: true,
      isLoadingEmail: true,
      error: null,
    }));

    void fetchBaseDashboard();
    void fetchAndSummarizeCalendar();
    void fetchAndSummarizeEmail();
  }, [fetchBaseDashboard, fetchAndSummarizeCalendar, fetchAndSummarizeEmail]);

  return {
    ...state,
    priorityItems,
    urgentCount,
    refresh,
    isFullyLoaded: !state.isLoading && !state.isLoadingCalendar && !state.isLoadingEmail,
  };
}
