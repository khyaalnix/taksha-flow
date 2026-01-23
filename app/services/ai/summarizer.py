"""
AI Summarization service for generating short summaries of content.
Uses Google Gemini 2.5 for news bulletins and email summaries.
"""
import json
from typing import List, Optional
from google import genai
from google.genai import types

from configs.settings import GEMINI_API_KEY
from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()


class AISummarizer:
    """AI-powered summarization service using Google Gemini."""

    def __init__(self):
        self.client = None
        self.model = "gemini-2.0-flash"  # Fast and cost-effective for summarization

        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None

    async def summarize_article(
        self,
        title: str,
        description: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        max_length: int = 80
    ) -> dict:
        """
        Generate a concise one-liner summary and bulletin text for a news article.

        Returns:
            dict with 'summary' and 'bulletin_text' keys
        """
        if not self.client:
            # Fallback: use description or truncated title
            summary = description[:max_length] if description else title[:max_length]
            return {
                "summary": summary,
                "bulletin_text": f"{title}"
            }

        # Build context from available content
        context_parts = [f"Title: {title}"]
        if description:
            context_parts.append(f"Description: {description}")
        if content:
            # Limit content to avoid token limits
            context_parts.append(f"Content: {content[:500]}")

        context = "\n".join(context_parts)

        category_prefix = {
            "technology": "In tech news",
            "business": "In business",
            "sports": "In sports",
            "entertainment": "In entertainment",
            "health": "In health news",
            "science": "In science",
            "general": "In today's news",
        }.get(category, "In news")

        prompt = f"""Summarize this news article in two formats:

1. SUMMARY: A concise one-liner (max {max_length} chars) capturing the key point
2. BULLETIN: A brief sentence starting with "{category_prefix}," suitable for a news bulletin reading

Article:
{context}

Respond in JSON format only:
{{"summary": "...", "bulletin": "..."}}"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=150,
                    response_mime_type="application/json",
                )
            )

            result = json.loads(response.text)

            return {
                "summary": result.get("summary", title[:max_length]),
                "bulletin_text": result.get("bulletin", f"{category_prefix}, {title}")
            }

        except Exception as e:
            logger.error(f"Error summarizing article with Gemini: {e}")
            # Fallback
            return {
                "summary": description[:max_length] if description else title[:max_length],
                "bulletin_text": f"{category_prefix}, {title}"
            }

    async def summarize_batch(
        self,
        articles: List[dict],
        category: str
    ) -> List[dict]:
        """
        Summarize a batch of articles for a category.

        Args:
            articles: List of dicts with 'title', 'description', 'content' keys
            category: News category

        Returns:
            List of dicts with 'summary' and 'bulletin_text' added
        """
        results = []

        for article in articles:
            summary_data = await self.summarize_article(
                title=article.get("title", ""),
                description=article.get("description"),
                content=article.get("content"),
                category=category
            )
            results.append({
                **article,
                "summary": summary_data["summary"],
                "bulletin_text": summary_data["bulletin_text"]
            })

        return results

    async def summarize_emails(
        self,
        emails: List[dict],
        max_length: int = 100
    ) -> str:
        """
        Generate a brief summary of multiple emails.

        Args:
            emails: List of email dicts with 'sender', 'subject', 'snippet' keys

        Returns:
            A concise summary string
        """
        if not self.client:
            # Fallback: simple count
            return f"You have {len(emails)} emails to review."

        if not emails:
            return "No new emails."

        # Build email context
        email_summaries = []
        for i, email in enumerate(emails[:5], 1):  # Limit to 5 emails
            email_summaries.append(
                f"{i}. From: {email.get('sender', 'Unknown')} - {email.get('subject', 'No subject')}"
            )

        context = "\n".join(email_summaries)

        prompt = f"""Summarize these emails in one brief sentence (max {max_length} chars):

{context}

Focus on the most important or actionable items. Return only the summary text, no JSON."""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=100,
                )
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error summarizing emails with Gemini: {e}")
            return f"You have {len(emails)} emails to review."


# Singleton instance
ai_summarizer = AISummarizer()
