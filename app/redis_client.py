from typing import Dict
import redis

class RedisClient:
    def __init__(self):
        self.redis_conn = None

    def get_redis_connection(self) -> redis.Redis:
        try:
            self.redis_conn = redis.Redis(host='localhost', port=6380, db=0)
            return self.redis_conn
        except Exception as e:
            print(f"Error connecting to Redis: {str(e)}")
            return None

    def close_redis_connection(self):
        if self.redis_conn is not None:
            self.redis_conn.close()