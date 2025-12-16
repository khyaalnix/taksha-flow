from pydantic import BaseModel, Field, RootModel  
from typing import Optional, Literal, Union

from app.schemas.entity import NamedEntity

class MasterInterest(NamedEntity):
    slug: str 
    search_terms: list[str]
    tags: list[str]
    default_weight: float = Field(0.5, ge=0.0, le=1.0) 
    is_custom: bool = False
    icon_url: Optional[str] = None

class MasterInterestCreate(RootModel[list[MasterInterest]]):
    pass

class UpdatScore(BaseModel):
    action: Literal["boost", "degrade", "mute"]
    context: Optional[str] = None
    