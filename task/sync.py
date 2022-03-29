import math

import redis
from common import base_utils, config_utils, pool_utils, waf_utils, cache_utils


def sync_request_msg(user_id):
    base_client = pool_utils.get_redis_cache()

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            all_news = base_utils.mapgetall(client, "new_client_maps")
            client.delete("new_client_maps")

            for (k,v) in  all_news.items():
                client_access_times = base_utils.mapgetall(client, "client_ip_times:" + k)

                pipe = base_client.pipeline()
                for (k1, v1) in client_access_times.items():
                    pipe.hincrby("client_ip_times:" + k, k1, v1)
                pipe.expire("client_ip_times:" + k, cache_utils.get_client_ip_times_timeout(user_id))
                ok = pipe.execute()

                if ok:
                    client.delete("client_ip_times:" + k)

                while True:
                    visit_list = client.execute_command("lpop", "client_ip_list:" + k, 1000)
                    if not visit_list:
                        break

                    base_client.rpush("client_ip_list:" + k, *visit_list)
                    base_client.expire("client_ip_times:" + k, cache_utils.get_client_ip_times_timeout(user_id))

            if len(all_news) > 0:
                base_client.hmset("new_client_maps", all_news)
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_upstream_infos(user_id):
    base_client = pool_utils.get_redis_cache()

    upstream_infos = base_utils.mapgetall(base_client, waf_utils.get_upstream_infos(user_id))
    if not upstream_infos:
        return;
    cache_md5 = base_utils.calc_md5(base_utils.safe_str(upstream_infos))
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            cache_key = "cache:all_upstream_infos"
            value = client.get(cache_key)
            if value == cache_md5:
                continue 
            key = f"all_upstream_infos"
            pipe = client.pipeline()
            pipe.hset(key + "bak", mapping=upstream_infos)
            pipe.rename(key + "bak", key)
            pipe.set(cache_key, cache_md5)
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_records_ip_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    all_record_ips = base_utils.mapgetall(base_client, waf_utils.get_record_ips(user_id))
    if len(all_record_ips) == 0:
        return

    cache_md5 = base_utils.calc_md5(base_utils.safe_str(all_record_ips))
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            cache_key = "cache:all_record_ips"
            value = client.get(cache_key)
            if value == cache_md5:
                continue 
            pipe = client.pipeline()
            pipe.hset("all_record_ips_bak", mapping=all_record_ips)
            pipe.rename("all_record_ips_bak", "all_record_ips")
            pipe.set(cache_key, cache_md5)
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

            
def sync_all_whiteurl_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    all_white_urls = base_utils.mapgetall(base_client, waf_utils.get_white_urls(user_id))
    if len(all_white_urls) == 0:
        return

    cache_md5 = base_utils.calc_md5(base_utils.safe_str(all_white_urls))
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            cache_key = "cache:all_white_urls"
            value = client.get(cache_key)
            if value == cache_md5:
                continue 
            pipe = client.pipeline()
            pipe.hset("all_white_urls_bak", mapping=all_white_urls)
            pipe.rename("all_white_urls_bak", "all_white_urls")
            pipe.set(cache_key, cache_md5)
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_ssl_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    all_ssl_infos = base_utils.mapgetall(base_client, waf_utils.get_ssl_infos(user_id))
    if len(all_ssl_infos) == 0:
        return

    cache_md5 = base_utils.calc_md5(base_utils.safe_str(all_ssl_infos))
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            cache_key = "cache:all_ssl_infos"
            value = client.get(cache_key)
            if value == cache_md5:
                continue 
            pipe = client.pipeline()
            pipe.hset("all_ssl_infos_bak", mapping=all_ssl_infos)
            pipe.rename("all_ssl_infos_bak", "all_ssl_infos")
            pipe.set(cache_key, cache_md5)
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_config_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    
    all_config_data = base_utils.mapgetall(base_client, waf_utils.get_config_infos(user_id))
    if len(all_config_data) == 0:
        return

    cache_md5 = base_utils.calc_md5(base_utils.safe_str(all_config_data))
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            cache_key = "cache:all_config_infos"
            value = client.get(cache_key)
            if value == cache_md5:
                continue 
            pipe = client.pipeline()
            pipe.hset("all_config_infos_bak", mapping=all_config_data)
            pipe.rename("all_config_infos_bak", "all_config_infos")
            pipe.set(cache_key, cache_md5)
            ok = pipe.execute()
            
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_to_client(user_id):
    sync_all_upstream_infos(user_id)
    sync_all_records_ip_infos(user_id)
    sync_all_whiteurl_infos(user_id)
    sync_all_config_infos(user_id)
    sync_all_ssl_infos(user_id)
