#!/usr/bin/env python3
"""
Redis Cache implementation module.

This module provides a Cache class for storing data in Redis
with automatically generated random keys.
"""
import redis
import uuid
from functools import wraps
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count how many times a method is called.
    
    This decorator uses Redis INCR command to count method calls,
    storing the count using the method's qualified name as the key.
    
    Args:
        method: The method to be decorated and counted.
        
    Returns:
        Callable: The wrapped method that increments call count.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments call count and calls original method.
        
        Args:
            self: The instance of the class.
            *args: Positional arguments for the original method.
            **kwargs: Keyword arguments for the original method.
            
        Returns:
            The return value of the original method.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.
    
    This decorator uses Redis RPUSH command to store function call inputs
    and outputs in separate lists, using the method's qualified name with
    ":inputs" and ":outputs" suffixes as keys.
    
    Args:
        method: The method to be decorated and have its history stored.
        
    Returns:
        Callable: The wrapped method that stores call history.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that stores inputs and outputs and calls original method.
        
        Args:
            self: The instance of the class.
            *args: Positional arguments for the original method.
            **kwargs: Keyword arguments for the original method.
            
        Returns:
            The return value of the original method.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        # Store input arguments
        self._redis.rpush(input_key, str(args))
        
        # Execute the wrapped function to get output
        output = method(self, *args, **kwargs)
        
        # Store output
        self._redis.rpush(output_key, output)
        
        return output
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.
    
    This function retrieves the stored inputs and outputs from Redis
    and displays them in a formatted way showing the call history.
    
    Args:
        method: The method whose call history should be displayed.
    """
    # Get the Redis instance from the method's class
    redis_instance = method.__self__._redis
    
    # Get the method's qualified name for keys
    method_name = method.__qualname__
    
    # Get the call count
    count = redis_instance.get(method_name)
    if count is None:
        count = 0
    else:
        count = int(count)
    
    # Get inputs and outputs lists
    inputs = redis_instance.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{method_name}:outputs", 0, -1)
    
    # Display the history
    print(f"{method_name} was called {count} times:")
    
    # Use zip to loop over inputs and outputs together
    for input_args, output in zip(inputs, outputs):
        input_str = input_args.decode('utf-8')
        output_str = output.decode('utf-8')
        print(f"{method_name}(*{input_str}) -> {output_str}")


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
    
    @count_calls
    @call_history
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
