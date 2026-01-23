from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any

class LocationResponse(BaseModel):
    ip: str
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    provider: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(populate_by_name=True,extra="allow")