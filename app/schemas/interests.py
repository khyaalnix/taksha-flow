from pydantic import BaseModel, Field, RootModel, field_validator
from typing import Optional, Literal, Union

from app.schemas.entity import NamedEntity, ListResponse

class MasterInterest(NamedEntity):
    slug: str 
    search_terms: list[str]
    tags: list[str]
    default_weight: float = Field(0.5, ge=0.0, le=1.0) 
    is_custom: bool = False
    icon_url: Optional[str] = None

class MasterInterestCreate(RootModel[list[MasterInterest]]):
    pass

class UpdateScore(BaseModel):
    action: Literal["boost", "degrade", "mute"]
    context: Optional[str] = None


class InterestModulationRequest(BaseModel):
    interest_id: str
    action: Literal["boost", "degrade", "reset"]
    interaction_type: Optional[Literal["article_tap", "event_interaction", "search", "time_spent", "dismiss"]] = None
    context: Optional[dict] = None  # Can include article_id, event_id, category, duration, etc.

    @field_validator("interest_id", mode='before')
    def validate_interest_id(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("interest_id must be a non-empty string")
        return v
    

class OnBoardingInterestCreate(BaseModel):
    interest_ids: list[str] 

    @field_validator("interest_ids",mode='before')
    def validate_interest_ids(cls, v):
        if len(v) > 5:
            raise ValueError("Cannot add more than 5 interests")
        return v
    

class OnBoardingInterestInDB(NamedEntity):
    interest_id: str
    score: float = Field(1.0, ge=0.0, le=1.0)
    custom: Optional[dict] = None


class UserInterestResponse(BaseModel):
    id: str
    interest_id: str
    score: float
    name: str
    createdAt: str
    updatedAt: Optional[str] = None

