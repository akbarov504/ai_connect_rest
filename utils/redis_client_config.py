import redis, os

def init_redis_client():
    return redis.Redis.from_url(os.getenv('REDIS_URL'))
