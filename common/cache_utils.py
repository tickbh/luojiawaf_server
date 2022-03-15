import time
from common import pool_utils, base_utils, waf_utils

CACHE_STEP = 60
_cache_time_last_read = 0
cache_table = {}

not_wait_forbidden_ratio = "not_wait_forbidden_ratio"
not_wait_forbidden_min_len = "not_wait_forbidden_min_len"
min_all_visit_times = "min_all_visit_times"
max_visit_idx_num = "max_visit_idx_num"
max_visit_ratio = "max_visit_ratio"
default_forbidden_time = "default_forbidden_time"

def get_cache_by_key(user_id, key, default=None):
    global cache_table, CACHE_STEP, _cache_time_last_read
    cache_user_table = cache_table.get(user_id, {})
    if time.time() - _cache_time_last_read < CACHE_STEP:
        return cache_user_table.get(key, default)

    cache_table[user_id] = {}
    _cache_time_last_read = time.time()
    redis = pool_utils.get_redis_cache()
    datas = base_utils.mapgetall(redis, waf_utils.get_config_infos(user_id))
    for (k, v) in datas.items():
        cache_table[user_id][k] = v
    return cache_table[user_id].get(key, default)

def get_cache_wait_forbidden_ratio(user_id):
    return base_utils.safe_float(get_cache_by_key(user_id, "not_wait_forbidden_ratio", 0.9))

def get_cache_wait_forbidden_min_len(user_id):
    return base_utils.safe_int(get_cache_by_key(user_id, "not_wait_forbidden_min_len", 30)) 

def get_min_all_visit_times(user_id):
    return base_utils.safe_int(get_cache_by_key(user_id, "min_all_visit_times", 20))
    
def get_max_visit_idx_num(user_id):
    return base_utils.safe_int(get_cache_by_key(user_id, "max_visit_idx_num", 2))

def get_max_visit_ratio(user_id):
    return base_utils.safe_float(get_cache_by_key(user_id, "max_visit_ratio", 0.85))

def get_default_forbidden_time(user_id):
    return base_utils.safe_int(get_cache_by_key(user_id, "default_forbidden_time", 600))