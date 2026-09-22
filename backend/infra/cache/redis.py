import redis.asyncio as redis
import os

REDIS_URL = os.getenv("HOST_REDIS")

redis_client = redis.from_url(
    REDIS_URL or "redis://localhost:6379/0",
    decode_responses= True
)

async def get_redis():
    return redis_client







