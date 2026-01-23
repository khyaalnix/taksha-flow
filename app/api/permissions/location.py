import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_limiter.depends import RateLimiter
from configs.settings import RATE_LIMITER_CONFIG

from app.services.geolocation import get_location as lookup_location


with open(RATE_LIMITER_CONFIG, "r") as f:
    rate_limiter_config = json.load(f)

router = APIRouter(prefix="/permissions", tags=["Permissions"], dependencies=[Depends(RateLimiter(**rate)) for rate in rate_limiter_config["app"]])


@router.get("/location")
async def get_location(request: Request):
    ip = request.client.host
    location = await lookup_location(ip, provider="ipapi")
    return location



    
