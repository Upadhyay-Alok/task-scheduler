import os
import redis

#  Render + Local compatible
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(
    redis_url,
    decode_responses=True
)