import redis.asyncio as redis
import os

REDIS_URL = os.getenv("HOST_REDIS")

redis_client = redis.from_url(
    REDIS_URL,
    decode_reponses= True
)

async def get_redis():
    return redis_client







