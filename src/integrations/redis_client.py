"""Redis client for caching and session management."""
import json
import logging
from typing import Optional, Any
from redis import Redis
from src.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper with error handling."""
    
    def __init__(self):
        self._client: Optional[Redis] = None
        self._enabled = settings.use_redis
        
        if self._enabled:
            try:
                self._client = Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self._client.ping()
                logger.info(f"✓ Redis connected: {settings.redis_host}:{settings.redis_port}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using file-based storage.")
                self._enabled = False
                self._client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._enabled and self._client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        if not self.is_available:
            return None
        
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.debug(f"Redis GET error for {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration (seconds)."""
        if not self.is_available:
            return False
        
        try:
            serialized = json.dumps(value)
            if expire:
                self._client.setex(key, expire, serialized)
            else:
                self._client.set(key, serialized)
            return True
        except Exception as e:
            logger.debug(f"Redis SET error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self.is_available:
            return False
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.debug(f"Redis DELETE error for {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.is_available:
            return False
        
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.debug(f"Redis EXISTS error for {key}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """Clear all Redis data."""
        if not self.is_available:
            return False
        
        try:
            self._client.flushdb()
            logger.info("Redis cache cleared")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSH error: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()
