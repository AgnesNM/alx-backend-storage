#!/usr/bin/env python3
"""
Redis Cache implementation module.

This module provides a Cache class for storing data in Redis
with automatically generated random keys.
"""
import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class for storing data in Redis with random keys.
    
    This class provides methods to store data in Redis using
    randomly generated UUID keys for data retrieval.
    """
    
    def __init__(self) -> None:
        """
        Initialize Redis client and flush database.
        
        Creates a new Redis client instance and flushes the database
        to ensure a clean state for the cache.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()
    
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.
        
        Takes input data and stores it in Redis using a UUID-based
        random key, then returns the key for future retrieval.
        
        Args:
            data: The data to store in Redis. Can be string, bytes,
                  integer, or float type.
            
        Returns:
            str: The randomly generated key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
