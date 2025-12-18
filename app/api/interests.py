"""
1. CRUD for admin to manage global interest 
    - name
    - slug 
    - search terms 
    - scope 
    - sources 

2. User Onboarding based on interest selection
    - User selects their interests
    - System recommends articles based on selected interests
    - Tracks User's behaviour on type of content they listen and personalizes recommendations
    - To start with, either boost or degrade score based on the user clicks and interactions (controlled by the client side)
    - Over time, adjust the scoring algorithm to fine-tune recommendations

3. News Feed API 
    - Voice Transcription for the daily/hourly news feed 
    - Show news articles based on the user's selected interests
    - User can filter the news feed based on the selected interests
    - User can listen to the news feed in a voice format

4. Daily Mailers & Event Feeds 
5. Reminder System based on the selected interests for news event, personal events or captured from mail 


"""
from fastapi import APIRouter, Depends

from app import getAppState, AppState
from app.schemas.interests import MasterInterestCreate, UpdatScore

from app.utils.logger import LoggerFactory
logger = LoggerFactory().get_logger()

router = APIRouter(
    prefix="/interests",
    tags=["interests"],
)


