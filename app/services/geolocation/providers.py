import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Literal
import httpx
import asyncio
from app.schemas.geolocation import LocationResponse

def _to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _split_loc(loc: Any) -> Tuple[Optional[float], Optional[float]]:
    if not isinstance(loc, str) or "," not in loc:
        return None, None
    a, b = loc.split(",", 1)
    return _to_float(a), _to_float(b)


class GeolocationProvider(ABC):
    name: str

    @abstractmethod
    async def lookup(self, ip: str) -> LocationResponse: ...


class HttpJSONProvider(GeolocationProvider):
    timeout_s: float = 5.0

    async def _get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, dict) else {"raw": data}


class IPAPI(HttpJSONProvider):
    name = "ipapi"

    async def lookup(self, ip: str) -> LocationResponse:
        data = await self._get_json(f"https://ipapi.co/{ip}/json/")
        print(data)
        return LocationResponse(
            ip=str(data.get("ip", ip)),
            provider=self.name,
            city=data.get("city"),
            region=data.get("region"),
            country=data.get("country_name"),
            country_code=data.get("country_code"),
            latitude=_to_float(data.get("latitude")),
            longitude=_to_float(data.get("longitude")),
            timezone=data.get("timezone"),
            utc_offset=data.get("utc_offset"),
            currency=data.get("currency")
        )


class IPInfo(HttpJSONProvider):
    name = "ipinfo"

    async def lookup(self, ip: str) -> LocationResponse:
        token = os.getenv("IPINFO_ACCESS_KEY")
        headers = {"Authorization": f"Bearer {token}"} if token else None
        data = await self._get_json(f"https://ipinfo.io/{ip}/json", headers=headers)
        lat, lng = _split_loc(data.get("loc"))
        return LocationResponse(
            ip=str(data.get("ip", ip)),
            provider=self.name,
            city=data.get("city"),
            region=data.get("region"),
            country=data.get("country"),
            country_code=data.get("country"),
            latitude=lat,
            longitude=lng,
            timezone=data.get("timezone")
        )


class IPStack(HttpJSONProvider):
    name = "ipstack"

    async def lookup(self, ip: str) -> LocationResponse:
        key = os.getenv("IPSTACK_ACCESS_KEY")
        if not key:
            raise ValueError("Missing IPSTACK_ACCESS_KEY")
        data = await self._get_json(f"http://api.ipstack.com/{ip}?access_key={key}")
        return LocationResponse(
            ip=ip,
            provider=self.name,
            city=data.get("city"),
            region=data.get("region_name"),
            country=data.get("country_name"),
            country_code=data.get("country_code"),
            latitude=_to_float(data.get("latitude")),
            longitude=_to_float(data.get("longitude")),
            timezone=(data.get("time_zone") or {}).get("id")
        )


class IPGeolocation(HttpJSONProvider):
    name = "ipgeolocation"

    async def lookup(self, ip: str) -> LocationResponse:
        key = os.getenv("IPGEOLOCATION_API_KEY")
        if not key:
            raise ValueError("Missing IPGEOLOCATION_API_KEY")
        data = await self._get_json(f"https://api.ipgeolocation.io/ipgeo?apiKey={key}&ip={ip}")
        return LocationResponse(
            ip=str(data.get("ip", ip)),
            provider=self.name,
            city=data.get("city"),
            region=data.get("state_prov"),
            country=data.get("country_name"),
            country_code=data.get("country_code2"),
            latitude=_to_float(data.get("latitude")),
            longitude=_to_float(data.get("longitude")),
            timezone=(data.get("time_zone") or {}).get("name")
        )


_PROVIDERS: Dict[str, GeolocationProvider] = {
    "ipapi": IPAPI(),
    "ipinfo": IPInfo(),
    "ipstack": IPStack(),
    "ipgeolocation": IPGeolocation(),
}


def get_provider(name: str) -> GeolocationProvider:
    key = (name or "").lower()
    if key not in _PROVIDERS:
        raise ValueError(f"Unknown provider '{name}'. Supported: {', '.join(sorted(_PROVIDERS))}")
    return _PROVIDERS[key]


async def get_location(ip: str, provider: Literal["ipapi", "ipinfo", "ipstack", "ipgeolocation", "all"] = "all") -> LocationResponse:
    if provider == "all":
        return await asyncio.gather(*[get_provider(p).lookup(ip) for p in _PROVIDERS])
    
    return await get_provider(provider).lookup(ip)
