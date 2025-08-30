import redis
import os
import json

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def cache_set(key: str, value: dict, expire: int = 60):
    redis_client.set(key, json.dumps(value), ex=expire)

def cache_get(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None
def cache_delete(key: str):
    """Delete key from Redis"""
    redis_client.delete(key)
    
