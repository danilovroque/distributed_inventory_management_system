"""In-memory cache with TTL support"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set
import re


class CacheEntry:
    """Cache entry with expiration"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return datetime.utcnow() > self.expires_at


class InMemoryCache:
    """
    In-memory cache with TTL (Time-To-Live) support.
    
    Features:
    - Automatic expiration
    - Pattern-based invalidation
    - LRU eviction when capacity is reached
    """
    
    def __init__(self, default_ttl: int = 30, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum number of entries
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: list = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._access_order.remove(key)
                return None
            
            # Update access order for LRU
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return entry.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        async with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            
            # Evict if at capacity
            if key not in self._cache and len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[key] = CacheEntry(value, ttl)
            
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
    
    async def delete(self, key: str):
        """
        Delete a specific key from cache.
        
        Args:
            key: Cache key to delete
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.remove(key)
    
    async def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Regex pattern to match keys
        """
        async with self._lock:
            regex = re.compile(pattern)
            keys_to_delete = [
                key for key in self._cache.keys() 
                if regex.match(key)
            ]
            
            for key in keys_to_delete:
                del self._cache[key]
                self._access_order.remove(key)
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self._access_order:
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]
    
    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._access_order.remove(key)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            await self.cleanup_expired()
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
            }
