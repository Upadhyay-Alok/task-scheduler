import os
import redis

# Docker me service name "redis" hoga
# Local me "localhost" use hoga
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    db=0,
    decode_responses=True
)