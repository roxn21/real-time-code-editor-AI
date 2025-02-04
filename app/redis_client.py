import redis
from fastapi import HTTPException

# Connect to Redis
def get_redis_client():
    try:
        return redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Redis connection error")

redis_client = get_redis_client()
