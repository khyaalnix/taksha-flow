/**
 * Client-side Gemini AI service for summarizing calendar events and emails.
 * Uses Google's Generative AI SDK.
 */
import { GoogleGenerativeAI } from '@google/generative-ai';

const GEMINI_API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY || '';

let genAI: GoogleGenerativeAI | null = null;

if (GEMINI_API_KEY) {
  genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
}

export interface CalendarEventRaw {
  id: string;
  summary: string;
  start_time?: string;
  end_time?: string;
  location?: string;
  attendees: string[];
  is_all_day: boolean;
}

export interface EmailRaw {
  id: string;
  sender?: string;
  subject?: string;
  date?: string;
}

export interface SummarizedCalendarEvent {
  id: string;
  title: string;
  subtitle: string;
  type: 'event';
}

export interface SummarizedEmail {
  id: string;
  title: string;
  subtitle: string;
  type: 'email';
}

/**
 * Format time from ISO string to readable format
 */
function formatTime(isoString?: string): string {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return '';
  }
}

/**
 * Summarize calendar events using Gemini AI
 */
export async function summarizeCalendarEvents(
  events: CalendarEventRaw[]
): Promise<SummarizedCalendarEvent[]> {
  if (!events.length) return [];

  // If no API key, use basic formatting
  if (!genAI) {
    return events.map((event) => ({
      id: event.id,
      title: event.summary || 'Untitled Event',
      subtitle: event.is_all_day
        ? 'All day'
        : `${formatTime(event.start_time)}${event.attendees.length ? ` with ${event.attendees[0].split('@')[0]}` : ''}`,
      type: 'event' as const,
    }));
  }

  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

    const eventsContext = events
      .map(
        (e, i) =>
          `${i + 1}. "${e.summary}" at ${formatTime(e.start_time) || 'TBD'}${e.attendees.length ? ` with ${e.attendees.slice(0, 2).join(', ')}` : ''}${e.location ? ` at ${e.location}` : ''}`
      )
      .join('\n');

    const prompt = `Summarize these calendar events into brief, actionable items. For each event, provide a short subtitle (max 40 chars) that captures when and with whom.

Events:
${eventsContext}

Respond in JSON format only:
{"summaries": [{"id": 0, "subtitle": "..."}]}

Keep subtitles concise like: "10:00 AM with Product Team" or "2 PM - Client call"`;

    const result = await model.generateContent(prompt);
    const response = result.response.text();

    // Parse JSON response
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return events.map((event, index) => ({
        id: event.id,
        title: event.summary || 'Untitled Event',
        subtitle:
          parsed.summaries?.[index]?.subtitle ||
          `${formatTime(event.start_time)}${event.attendees.length ? ` with ${event.attendees[0].split('@')[0]}` : ''}`,
        type: 'event' as const,
      }));
    }
  } catch (error) {
    console.error('Error summarizing calendar events:', error);
  }

  // Fallback to basic formatting
  return events.map((event) => ({
    id: event.id,
    title: event.summary || 'Untitled Event',
    subtitle: event.is_all_day
      ? 'All day'
      : `${formatTime(event.start_time)}${event.attendees.length ? ` with ${event.attendees[0].split('@')[0]}` : ''}`,
    type: 'event' as const,
  }));
}

/**
 * Summarize emails using Gemini AI
 */
export async function summarizeEmails(
  emails: EmailRaw[],
  totalUnread: number
): Promise<SummarizedEmail | null> {
  if (!emails.length) return null;

  // If no API key, use basic formatting
  if (!genAI) {
    const topEmail = emails[0];
    return {
      id: 'email_summary',
      title: `${totalUnread} New Email${totalUnread !== 1 ? 's' : ''}`,
      subtitle: topEmail.subject
        ? `Top: ${topEmail.subject.slice(0, 40)}${topEmail.subject.length > 40 ? '...' : ''}`
        : 'Check your inbox',
      type: 'email' as const,
    };
  }

  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

    const emailsContext = emails
      .slice(0, 5)
      .map((e, i) => `${i + 1}. From: ${e.sender || 'Unknown'} - "${e.subject || 'No subject'}"`)
      .join('\n');

    const prompt = `Summarize these ${totalUnread} unread emails into a brief, actionable subtitle (max 50 chars).

Emails:
${emailsContext}

Focus on what's most important or urgent. Respond in JSON format only:
{"subtitle": "..."}

Example subtitles: "Top: Contract revision from Sarah" or "3 urgent from clients"`;

    const result = await model.generateContent(prompt);
    const response = result.response.text();

    // Parse JSON response
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        id: 'email_summary',
        title: `${totalUnread} New Email${totalUnread !== 1 ? 's' : ''}`,
        subtitle: parsed.subtitle || `Top: ${emails[0].subject?.slice(0, 40) || 'Check inbox'}`,
        type: 'email' as const,
      };
    }
  } catch (error) {
    console.error('Error summarizing emails:', error);
  }

  // Fallback
  const topEmail = emails[0];
  return {
    id: 'email_summary',
    title: `${totalUnread} New Email${totalUnread !== 1 ? 's' : ''}`,
    subtitle: topEmail.subject
      ? `Top: ${topEmail.subject.slice(0, 40)}${topEmail.subject.length > 40 ? '...' : ''}`
      : 'Check your inbox',
    type: 'email' as const,
  };
}
