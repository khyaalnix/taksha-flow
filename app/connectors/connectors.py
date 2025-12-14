from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient

from configs.settings import REDIS_URL, MONGO_URL

def get_redis_client():
    return Redis.from_url(REDIS_URL)

def get_mongo_client():
    return AsyncIOMotorClient(MONGO_URL)


