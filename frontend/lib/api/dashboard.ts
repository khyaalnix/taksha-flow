import { apiClient } from './client';
import type { DashboardBrief, CalendarEvent, EmailSummary } from '@/types/dashboard';

export interface DashboardBriefParams {
  include_calendar?: boolean;
  include_email?: boolean;
  include_news?: boolean;
  max_priority_items?: number;
}

export const dashboardApi = {
  async getBrief(params: DashboardBriefParams = {}): Promise<DashboardBrief> {
    const queryParams = new URLSearchParams();

    if (params.include_calendar !== undefined) {
      queryParams.set('include_calendar', String(params.include_calendar));
    }
    if (params.include_email !== undefined) {
      queryParams.set('include_email', String(params.include_email));
    }
    if (params.include_news !== undefined) {
      queryParams.set('include_news', String(params.include_news));
    }
    if (params.max_priority_items !== undefined) {
      queryParams.set('max_priority_items', String(params.max_priority_items));
    }

    const queryString = queryParams.toString();
    const endpoint = `/dashboard/brief${queryString ? `?${queryString}` : ''}`;

    return apiClient.get<DashboardBrief>(endpoint);
  },

  async getTodaysCalendarEvents(maxEvents: number = 10): Promise<{ data: CalendarEvent[]; total: number }> {
    return apiClient.get(`/dashboard/calendar/today?max_events=${maxEvents}`);
  },

  async getEmailSummary(maxEmails: number = 5): Promise<{ data: EmailSummary }> {
    return apiClient.get(`/dashboard/email/summary?max_emails=${maxEmails}`);
  },

  async checkGoogleConnection(): Promise<{ connected: boolean; message: string }> {
    try {
      return await apiClient.get('/dashboard/check/google');
    } catch {
      return { connected: false, message: 'Google services not connected' };
    }
  },

  // Backward compatible aliases
  async checkCalendarConnection(): Promise<{ connected: boolean; message: string }> {
    return this.checkGoogleConnection();
  },

  async checkGmailConnection(): Promise<{ connected: boolean; message: string }> {
    return this.checkGoogleConnection();
  },
};
