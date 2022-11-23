import math
import time
import redis
from common import base_utils, config_utils, pool_utils, waf_utils, cache_utils

def syn_info_by_keys(user_id, key):
    now_key = key
    base_client = pool_utils.get_redis_cache()
    user_version = base_client.get(pool_utils.user_version_key(user_id, now_key))
    if not user_version:
        return

    value = base_client.get(pool_utils.client_version_key(now_key))
    if value == user_version:
        return
    infos = base_utils.mapgetall(base_client, f"{user_id}:{now_key}")
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            value = client.get(pool_utils.client_version_key(now_key))
            if value == user_version:
                continue 
            pipe = client.pipeline()
            pipe.hset(f"{now_key}_bak", mapping=infos)
            pipe.rename(f"{now_key}_bak", now_key)
            pipe.set(pool_utils.client_version_key(now_key), user_version)
            ok = pipe.execute()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            
def syn_clear_ip_timeout(user_id):
    now_key = "all_ip_changes"
    base_client = pool_utils.get_redis_cache()
    infos = base_utils.mapgetall(base_client, now_key)
    del_keys = []
    for k, v in infos.items():
        temps = v.split("|")
        if len(temps) < 2:
            del_keys.append(k)
        else:
            timeout = base_utils.safe_int(temps[1])
            if timeout < time.time():
                del_keys.append(k)
                
    if len(del_keys) > 0:
        base_client.hdel(now_key, *del_keys)
            

def sync_to_client(user_id):
    syn_info_by_keys(user_id, "all_upstream_infos")
    syn_info_by_keys(user_id, "all_record_ips")
    syn_info_by_keys(user_id, "all_white_urls")
    syn_info_by_keys(user_id, "all_config_infos")
    syn_info_by_keys(user_id, "all_ssl_infos")
    
    syn_clear_ip_timeout(user_id)