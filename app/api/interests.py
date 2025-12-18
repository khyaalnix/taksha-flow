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
import json
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from pydantic import Json

from app.schemas.entity import MetaData, ListResponse, PaginationInfo
from app import getAppState, AppState
from app.schemas.interests import (
    MasterInterestCreate,
    UpdateScore,
    OnBoardingInterestCreate,
    OnBoardingInterestInDB,
    UserInterestResponse,
    InterestModulationRequest
)
from app.core.security import get_current_user
from configs.settings import Collection, FLOW_DATABASE, RATE_LIMITER_CONFIG
from app.utils.utility import get_collection

from app.utils.logger import LoggerFactory
logger = LoggerFactory().get_logger()

with open(RATE_LIMITER_CONFIG, "r") as f:
    rate_limiter_config = json.load(f)

router = APIRouter(
    prefix="/interests",
    tags=["interests"],
    dependencies=[Depends(RateLimiter(**rate)) for rate in rate_limiter_config["app"]]
)

@router.post("/onboarding",status_code=status.HTTP_201_CREATED)
async def create_onboarding_flow(
    onboarding_interest: OnBoardingInterestCreate,
    app_state: AppState = Depends(getAppState),
    current_user: dict = Depends(get_current_user),
):
    errors = []
    try:
        collection = await get_collection(app_state.resources['mongo'], FLOW_DATABASE, Collection.INTERESTS)
        metadata = MetaData(
            createdBy=current_user["name"],
            updatedBy=current_user["name"],
        )
        for int_ in onboarding_interest.interest_ids:
            onboarding_interest_db = OnBoardingInterestInDB(
                name=current_user["email"],
                interest_id=int_,
            )
            onboarding_interest_db.metadata = metadata
            result = await collection.insert_one(onboarding_interest_db.model_dump(exclude={'id'}))
            if not result.inserted_id:
                errors.append(int_)
                # TODO:
                # add a retry logic here or scrape the collection to check if the document is inserted
                # if not, then insert it
        return JSONResponse(content={"message": "Onboarding flow created successfully", "errors": errors})
    except Exception as e:
        logger.error(f"Error creating onboarding flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/user", status_code=status.HTTP_200_OK)
async def list_user_interests(
    app_state: AppState = Depends(getAppState),
    current_user: dict = Depends(get_current_user),
):
    """
    List all interests for the currently authenticated user.
    Returns up to 5 interests (current max limit).
    """
    try:
        collection = await get_collection(app_state.resources['mongo'], FLOW_DATABASE, Collection.INTERESTS)

        # Query for user's interests
        cursor = collection.find({"name": current_user["email"]})
        interests = await cursor.to_list(length=None)

        # Transform to response model
        data = []
        for interest in interests:
            data.append(UserInterestResponse(
                id=str(interest["_id"]),
                interest_id=interest["interest_id"],
                score=interest.get("score", 1.0),
                name=interest["name"],
                createdAt=interest.get("createdAt", ""),
                updatedAt=interest.get("updatedAt")
            ))

        return JSONResponse(content={
            "message": "User interests retrieved successfully",
            "data": [item.model_dump() for item in data],
            "total": len(data)
        })
    except Exception as e:
        logger.error(f"Error retrieving user interests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/score", status_code=status.HTTP_200_OK)
async def modulate_interest_score(
    modulation: InterestModulationRequest,
    app_state: AppState = Depends(getAppState),
    current_user: dict = Depends(get_current_user),
):
    """
    Modulate user's interest score based on their interactions within the app.

    Heuristic scoring based on interaction types:
    - article_tap: +0.15 boost
    - event_interaction: +0.15 boost
    - search: +0.10 boost
    - time_spent: +0.20 boost (for high engagement)
    - dismiss: -0.10 degrade
    - reset: sets score back to 1.0

    This endpoint is designed to be easily replaceable with ML-based inference in the future.
    """
    try:
        collection = await get_collection(app_state.resources['mongo'], FLOW_DATABASE, Collection.INTERESTS)

        # Find the user's interest document
        interest_doc = await collection.find_one({
            "name": current_user["email"],
            "interest_id": modulation.interest_id
        })

        if not interest_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interest with id {modulation.interest_id} not found for user"
            )

        current_score = interest_doc.get("score", 1.0)

        # Heuristic scoring logic
        if modulation.action == "reset":
            new_score = 1.0
        elif modulation.action == "boost":
            # Determine magnitude based on interaction type
            magnitude = 0.1  # default
            if modulation.interaction_type == "article_tap":
                magnitude = 0.15
            elif modulation.interaction_type == "event_interaction":
                magnitude = 0.15
            elif modulation.interaction_type == "search":
                magnitude = 0.10
            elif modulation.interaction_type == "time_spent":
                # Can be enhanced to factor in duration from context
                magnitude = 0.20

            new_score = min(current_score + magnitude, 1.0)
        elif modulation.action == "degrade":
            magnitude = 0.1  # default
            if modulation.interaction_type == "dismiss":
                magnitude = 0.10

            new_score = max(current_score - magnitude, 0.0)
        else:
            new_score = current_score

        # Update the score and metadata
        from datetime import datetime, timezone
        update_result = await collection.update_one(
            {
                "name": current_user["email"],
                "interest_id": modulation.interest_id
            },
            {
                "$set": {
                    "score": new_score,
                    "updatedAt": str(datetime.now(timezone.utc)),
                    "updatedBy": current_user["name"]
                }
            }
        )

        if update_result.modified_count == 0:
            logger.warning(f"Score update failed for interest {modulation.interest_id} for user {current_user['email']}")

        return JSONResponse(content={
            "message": "Interest score updated successfully",
            "data": {
                "interest_id": modulation.interest_id,
                "previous_score": current_score,
                "new_score": new_score,
                "action": modulation.action,
                "interaction_type": modulation.interaction_type
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error modulating interest score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
