import redis
from typing import Optional

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):  # Ensure default Redis port (6379)
        self.redis_conn: Optional[redis.Redis] = None
        self.host = host
        self.port = port
        self.db = db

    def get_redis_connection(self) -> redis.Redis:
        """Establish a Redis connection, if not already connected."""
        if not self.redis_conn:
            try:
                self.redis_conn = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True  # Ensures string responses instead of byte strings
                )
            except Exception as e:
                print(f" Error connecting to Redis: {str(e)}")
        return self.redis_conn

    def close_redis_connection(self):
        """Close the Redis connection."""
        if self.redis_conn:
            try:
                self.redis_conn.close()
            except Exception as e:
                print(f" Error closing Redis connection: {str(e)}")
