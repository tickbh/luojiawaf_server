

import redis, time, json
from . import config_utils, waf_utils, base_utils

_redis_cache_pool = None;
def get_redis_cache():
    global _redis_cache_pool;
    if _redis_cache_pool == None:
        _redis_cache_pool = redis.ConnectionPool.from_url(config_utils.get_redis_db(), decode_responses=True, health_check_interval=10, socket_timeout=5)
    return redis.Redis(connection_pool=_redis_cache_pool)

_redis_online_config_cache = {}
_redis_config_cache_names = {}
_redis_last_read_time = {}

def get_redis_client_cache_data(user_id):
    global _redis_online_config_cache, _redis_last_read_time
    base_client = get_redis_cache()
    if time.time() - _redis_last_read_time.get(user_id, 0) > 60:
        _redis_last_read_time[user_id] = time.time()
        _redis_online_config_cache[user_id] = {}
        _redis_config_cache_names[user_id] = {}
        all_caches = base_utils.mapgetall(base_client, waf_utils.get_client_infos(user_id))
        for (k, v) in all_caches.items():
            try:
                data = json.loads(v)
                if data.get("name"):
                    _redis_config_cache_names[user_id][data.get("name")] = data
                    pool = redis.ConnectionPool.from_url(data.get("host"), decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
                    red = redis.Redis(connection_pool=pool)
                    if red.ping():
                        _redis_online_config_cache[user_id][data.get("name")] = pool
            except Exception as e:
                continue
    
    return _redis_online_config_cache.get(user_id, {})


def iter_redis_client_cache_data(user_id):
    datas = get_redis_client_cache_data(user_id)
    for _, pool in datas.items():
        yield redis.Redis(connection_pool=pool)


def get_redis_client_cache(user_id, name):
    global _redis_online_config_cache
    
    user_cache = _redis_online_config_cache.get(user_id, {})

    if user_cache.get(name) == None:
        pool = get_redis_client_cache_data(user_id).get(name)
        if not pool:
            return None
        return redis.Redis(connection_pool=pool)
    return redis.Redis(connection_pool=user_cache.get(name))


def get_redis_data_cache(user_id, name):
    global _redis_config_cache_names
    
    user_cache = _redis_config_cache_names.get(user_id, {})
    return user_cache.get(name, {})

def do_client_command(user_id, *args, **options):
    for client in iter_redis_client_cache_data(user_id):
        client.execute_command(*args, **options)