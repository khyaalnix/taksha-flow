import os 
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
MONGO_URL = os.getenv("MONGO_URL")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

RATE_LIMITER_CONFIG = "configs/ratelimiter.json"

# News API
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# AI Summarization (for news bulletins) - Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

FLOW_DATABASE = "flow"
class Collection:
    INTERESTS = "interests"
    NEWS_CACHE = "news_cache"
    
    


