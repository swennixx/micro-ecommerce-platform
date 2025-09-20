import redis.asyncio as redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def get_product_from_cache(product_id: int):
    key = f"product:{product_id}"
    data = await redis_client.get(key)
    return data

async def set_product_to_cache(product_id: int, data: str, expire: int = 300):
    key = f"product:{product_id}"
    await redis_client.set(key, data, ex=expire)
