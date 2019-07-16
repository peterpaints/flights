import datetime
import json
from redis import StrictRedis


class JsonEncoderWithDatetime(json.JSONEncoder):
    """Convert datetime.date objects to string."""

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super(JsonEncoderWithDatetime, self).default(obj)


def reset_redis_database_cache():
    """deletes cached results in redis"""
    redis = StrictRedis(host='redis', port=6379)
    redis.flushdb()
