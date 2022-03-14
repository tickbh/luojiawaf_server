import math

import redis
from common import base_utils, config_utils, pool_utils, waf_utils


def sync_request_msg(user_id):
    base_client = pool_utils.get_redis_cache()

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            all_news = client.hgetall("new_client_maps")
            client.delete("new_client_maps")

            for (k,v) in  all_news.items():
                client_access_times = client.hgetall("client_ip_times:" + k)

                pipe = base_client.pipeline()
                for (k1, v1) in client_access_times.items():
                    pipe.hincrby("client_ip_times:" + k, k1, v1)
                pipe.expire("client_ip_times:" + k, 60 * 60)
                ok = pipe.execute()

                if ok:
                    client.delete("client_ip_times:" + k)

                while True:
                    visit_list = client.execute_command("lpop", "client_ip_list:" + k, 1000)
                    if not visit_list:
                        break

                    base_client.rpush("client_ip_list:" + k, *visit_list)
                    base_client.expire("client_ip_times:" + k, 10 * 60)

            if len(all_news) > 0:
                base_client.hmset("new_client_maps", all_news)
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_upstream_infos(user_id):
    base_client = pool_utils.get_redis_cache()

    upstream_infos = base_client.hgetall(waf_utils.get_upstream_infos(user_id))
    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            key = f"all_upstream_infos"
            pipe = client.pipeline()
            pipe.hset(key + "bak", mapping=upstream_infos)
            pipe.rename(key + "bak", key)
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_records_ip_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    all_record_ips = base_client.hgetall(waf_utils.get_record_ips(user_id))
    if len(all_record_ips) == 0:
        return

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            pipe = client.pipeline()
            pipe.hset("all_record_ips_bak", mapping=all_record_ips)
            pipe.rename("all_record_ips_bak", "all_record_ips")
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

            
def sync_all_whiteurl_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    all_white_urls = base_client.hgetall(waf_utils.get_white_urls(user_id))
    if len(all_white_urls) == 0:
        return

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            pipe = client.pipeline()
            pipe.hset("all_white_urls_bak", mapping=all_white_urls)
            pipe.rename("all_white_urls_bak", "all_white_urls")
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_ssl_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    all_ssl_infos = base_client.hgetall(waf_utils.get_ssl_infos(user_id))
    if len(all_ssl_infos) == 0:
        return

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            pipe = client.pipeline()
            pipe.hset("all_ssl_infos_bak", mapping=all_ssl_infos)
            pipe.rename("all_ssl_infos_bak", "all_ssl_infos")
            ok = pipe.execute()
        except Exception as e:
            import traceback
            traceback.print_exc()

def sync_all_config_infos(user_id):
    base_client = pool_utils.get_redis_cache()
    
    all_config_data = base_client.hgetall(waf_utils.get_config_infos(user_id))
    if len(all_config_data) == 0:
        return

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            pipe = client.pipeline()
            pipe.hset("all_config_infos_bak", mapping=all_config_data)
            pipe.rename("all_config_infos_bak", "all_config_infos")
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
