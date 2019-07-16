import json
import redis

REDIS_CONN = redis.StrictRedis(host='redis', port=6379)

cache_params = {
    'use_cache': {
        'description': 'Bool — whether to use cache',
        'in': 'header',
        'type': 'boolean',
        'default': False,
        'required': False
    }
}


def parse_use_cache(headers):
    cache_header = headers.get('use_cache', 'false')
    return json.loads(cache_header.lower())


def cache_data_in_redis(data):
    """Cache data in redis.

    Parameters
    ----------
    data : dict of {key : value}
    """
    # TODO: Refactor using REDIS_CONN.pipeline() to allow setting expire times
    # https://redis-py.readthedocs.io/en/latest/index.html#redis.Redis.pipeline
    json_data = {k: json.dumps(v) for k, v in data.items()}
    return REDIS_CONN.mset(json_data)


def get_data_from_redis(keys):
    """Fetch cached data from redis.

    Parameters
    ----------
    keys : list of str

    Returns
    -------
    data: dict of {key : value}
    """
    json_data = REDIS_CONN.mget(keys)
    results = [None if data is None else json.loads(data) for data in json_data]

    data = {
        key: value
        for (key, value) in zip(keys, results)
        if value is not None
    }
    return data
