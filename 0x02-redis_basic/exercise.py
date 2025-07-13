#!/usr/bin/env python3
"""
Redis Cache implementation module.

This module provides a Cache class for storing data in Redis
with automatically generated random keys.
"""
import redis
import uuid
from typing import Union, Callable, Optional


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

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using a callable.
        
        Gets data from Redis using the provided key and applies the optional
        conversion function to transform the data back to its original type.
        
        Args:
            key: The key to retrieve data from Redis.
            fn: Optional callable function to convert the retrieved data.
            
        Returns:
            The retrieved data, optionally converted by fn, or None if key doesn't exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """
        Retrieve data from Redis and convert it to a string.
        
        Gets data from Redis using the provided key and automatically
        converts it to a UTF-8 decoded string.
        
        Args:
            key: The key to retrieve data from Redis.
            
        Returns:
            The retrieved data as a string, or None if key doesn't exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """
        Retrieve data from Redis and convert it to an integer.
        
        Gets data from Redis using the provided key and automatically
        converts it to an integer.
        
        Args:
            key: The key to retrieve data from Redis.
            
        Returns:
            The retrieved data as an integer, or None if key doesn't exist.
        """
        return self.get(key, fn=int)
