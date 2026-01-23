import uuid
from typing import Union, Optional, Any
import json
from redis.asyncio import RedisError

from app.connectors.connectors import get_redis_client
from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()

class RedisCache:
    def __init__(self):
        self._redis = None

    @property
    def redis(self):
        if self._redis is None:
            self._redis = get_redis_client()
        return self._redis
    
    async def set(self, key: str, payload: Union[dict[str, Any],str], expiry: Optional[int]=None) -> bool:
        try:
            serialized_payload = json.dumps(payload) if isinstance(payload,dict) else payload
            if expiry:
                return await self.redis.set(key,serialized_payload,ex=expiry)
            else:
                return await self.redis.set(key, serialized_payload)
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Error setting Redis key {key}: {e}")
            return False

    async def get(self, key: str):
        try:
            serialized_payload = await self.redis.get(key)
            if serialized_payload:
                try:
                    return json.loads(serialized_payload)
                except json.JSONDecodeError:
                    return serialized_payload
            else:
                return None
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Error getting Redis key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        try:
            return await self.redis.delete(key)
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Error deleting Redis key {key}: {e}")
            return False

    async def exists(self, key):
        try:
            return await self.redis.exists(key) > 0
        except RedisError as e:
            logger.error(f"Error checking Redis key {key} existence: {e}")
            return False
    


class LockManager:
    def __init__(self, prefix: str, ttl: int = 300):
        self.prefix = f"flow:{prefix}"
        self.ttl = ttl
        self._redis = None

    @property
    def redis(self):
        if self._redis is None:
            self._redis = get_redis_client()
        return self._redis
    
    async def acquire(self) -> Optional[str]:
        if not self.redis:
            raise ValueError("Redis client is not initialized")

        token = str(uuid.uuid4())
        try:
            ok = await self.redis.set(
                f"{self.prefix}",
                token,
                ex=self.ttl,
                nx=True
            )
            return token if ok else None
        except Exception:
            logger.error(f"Lock Acquisition issue in LockManager for key: {self.prefix}")
            return None

    async def release(self, token: str) -> bool:
        if not self.redis:
            raise ValueError("Redis client is not initialized")

        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            await self.redis.eval(lua, 1, f"{self.prefix}", token)
            return True
        except Exception:
            logger.error(f"Lock Release issue in LockManager for key: {self.prefix}")
            return False

