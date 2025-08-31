import redis
import os
import json
from typing import Optional, Any, Tuple

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def cache_set(key: str, value: dict, timeout: int = 60):
    try:
        redis_client.set(key, json.dumps(value), ex=timeout)
    except redis.RedisError as e:
        return {"success": False, "message": f"Redis set error: {e}"}

def cache_get(key: str):
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except redis.RedisError as e:
        return None, {"success": False, "message": f"Redis get error: {e}"}

def cache_delete(key: str): 
    try:
        deleted = redis_client.delete(key)
        if deleted:
            return {"success": True, "message": f"Cache key '{key}' deleted successfully."}
        return {"success": False, "message": f"Cache key '{key}' does not exist."}
    except redis.RedisError as e:
        return {"success": False, "message": f"Redis delete error: {e}"}
