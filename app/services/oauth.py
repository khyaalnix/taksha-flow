from abc import ABC, abstractmethod
import asyncio

from app.utils.redis import RedisCache, LockManager
from app.utils.logger import LoggerFactory
logger = LoggerFactory().get_logger()



class AuthBuilder(ABC):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    @abstractmethod
    def build_creds_from_token(self,token: str, scopes: list[str]):
        raise NotImplementedError

    @abstractmethod
    def build_creds_from_access_token(self,access_token: str,expires_in: str,scopes: list[str]):
        raise NotImplementedError
    
    @abstractmethod
    def refresh_or_create(self,existing_token = None, scopes: list[str] = None):
        raise NotImplementedError

    @abstractmethod
    def is_valid(self,creds, refresh_buffer_seconds: int = 300):
        raise NotImplementedError

    @abstractmethod
    def ttl(self,creds, refresh_buffer_seconds: int = 300) -> int:
        raise NotImplementedError

    @abstractmethod
    def to_json(self, creds):
        raise NotImplementedError



class OAuthService:

    def __init__(
        self,
        auth_builder: AuthBuilder,
        key_prefix: str,
        refresh_buffer_seconds: int = 300,
        scopes: list[str] = None
    ):
        self.auth_builder = auth_builder
        self.key_prefix = key_prefix
        self.refresh_buffer_seconds = refresh_buffer_seconds
        self.store = RedisCache()
        self.scopes = scopes or []

    def _token_key(self, user_id: str):
        """Generate user-specific token key."""
        return f"flow:{self.key_prefix}:user:{user_id}:token"

    def _lock_manager(self, user_id: str):
        """Get user-specific lock manager."""
        return LockManager(prefix=f"{self.key_prefix}:user:{user_id}")

    async def _try_get_cached_token(self, user_id: str):
        try:
            token_json = await self.store.get(self._token_key(user_id))
            if not token_json:
                return None

            creds = self.auth_builder.build_creds_from_token(token_json, self.scopes)
            if not self.auth_builder.is_valid(creds):
                return None

            return creds
        except Exception as e:
            logger.error(f"Error getting cached token for user {user_id}: {e}")
            return None

    async def cache_user_token(self, user_id: str, access_token: str, expires_in: str):
        try:
            creds = self.auth_builder.build_creds_from_access_token(access_token, expires_in, self.scopes)
            if not self.auth_builder.is_valid(creds):
                raise ValueError("Invalid credentials")

            token_json = self.auth_builder.to_json(creds)
            ttl = self.auth_builder.ttl(creds, self.refresh_buffer_seconds)
            await self.store.set(self._token_key(user_id), token_json, ttl)
            logger.info(f"Token cached for user {user_id} with TTL: {ttl} seconds")
            return True, None
        except Exception as e:
            logger.error(f"Error caching token for user {user_id}: {e}")
            return False, str(e)

    async def get_credentials(self, user_id: str):
        try:
            creds = await self._try_get_cached_token(user_id)
            if not creds:
                creds = await self._refresh_token(user_id)
                return creds

            return creds
        except Exception as e:
            logger.error(f"Error getting credentials for user {user_id}: {e}")
            raise
    
    
    async def _refresh_token(self, user_id: str, timeout: int = 10):
        """
        Makes 3 attempts to refresh the token for a specific user.
        """
        token_key = self._token_key(user_id)
        lock_manager = self._lock_manager(user_id)
        lock_token = await lock_manager.acquire()

        if lock_token:
            try:
                # Check if token is already cached from some other request
                token_json = await self.store.get(token_key)
                if token_json:
                    try:
                        creds = self.auth_builder.build_creds_from_token(token_json, self.scopes)
                        if self.auth_builder.is_valid(creds):
                            return creds
                    except Exception as e:
                        logger.error(f"Error fetching existing token for user {user_id}: {e}")
                        pass

                # No active token found, let's refresh and cache it
                existing_creds = None
                if token_json:
                    try:
                        existing_creds = self.auth_builder.build_creds_from_token(token_json, self.scopes)
                    except Exception as e:
                        logger.error(f"Error fetching existing token for user {user_id}: {e}")
                        pass

                new_creds = self.auth_builder.refresh_or_create(existing_creds, self.scopes)

                # saving to cache
                token_json = self.auth_builder.to_json(new_creds)
                ttl = self.auth_builder.ttl(new_creds, self.refresh_buffer_seconds)
                await self.store.set(token_key, token_json, ttl)
                logger.info(f"Refreshed token cached for user {user_id} with TTL: {ttl} seconds")
                return new_creds
            finally:
                await lock_manager.release(lock_token)

        # If lock cannot be acquired, then another process is already refreshing it
        # wait for it to complete and check once again for validity

        logger.info(f"Waiting for lock to be released for user {user_id} until timeout")
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            token_json = await self.store.get(token_key)
            if token_json:
                try:
                    creds = self.auth_builder.build_creds_from_token(token_json, self.scopes)
                    if self.auth_builder.is_valid(creds):
                        return creds
                except Exception as e:
                    print(f"Error fetching existing token for user {user_id}: {e}") # replace with logger
                    pass
            await asyncio.sleep(1)

        logger.info(f"Timeout reached for user {user_id}, no valid token found. Making final attempt to refresh token.")
        # this step can be removed and can be replaced by client asking to login again to the user

        # final attempt:::
        lock_token = await lock_manager.acquire()
        if lock_token:
            try:
                token_json = await self.store.get(token_key)
                existing_creds = None
                if token_json:
                    try:
                        existing_creds = self.auth_builder.build_creds_from_token(token_json, self.scopes)
                    except Exception as e:
                        pass

                new_creds = self.auth_builder.refresh_or_create(existing_creds, self.scopes)

                # saving to cache
                token_json = self.auth_builder.to_json(new_creds)
                ttl = self.auth_builder.ttl(new_creds, self.refresh_buffer_seconds)
                await self.store.set(token_key, token_json, ttl)
                logger.info(f"Refreshed token cached for user {user_id} with TTL: {ttl} seconds")
                return new_creds
            finally:
                await lock_manager.release(lock_token)

        raise RuntimeError(f"Failed to refresh token for user {user_id} after multiple attempts.")
        
    async def check_if_valid_token(self, user_id: str):
        """Will be used by client to check if token is valid for a specific user."""
        token_json = await self.store.get(self._token_key(user_id))
        if token_json:
            try:
                creds = self.auth_builder.build_creds_from_token(token_json, self.scopes)
                if self.auth_builder.is_valid(creds):
                    return True
            except Exception as e:
                logger.error(f"Error checking token validity for user {user_id}: {e}")
                pass
        return False

    async def invalidate_cache(self, user_id: str):
        """Invalidate cached token for a specific user."""
        try:
            result = await self.store.delete(self._token_key(user_id))
            if result:
                logger.info(f"Cache invalidated successfully for user {user_id}.")
            else:
                logger.info(f"Cache key not found for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error invalidating cache for user {user_id}: {e}")
            return False
    
