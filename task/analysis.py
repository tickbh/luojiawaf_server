import redis
import math
import time
import json
import re
from common import config_utils, pool_utils, base_utils, cache_utils, waf_utils
from task.accessurl import AccessUrl, calc_not_wait_count

limitTables = {}
limitCacheTime = 0

# /sys/login_config:_:1635736494.566:0.37800

def check_is_limit(value, rule):
    if rule.get("matchFull"):
        if str.startswith(value, rule["url"]):
            return True
    else:
        if value == rule["url"]:
            return True
    return None


def analysis_request_msg(user_id):
    global limitCacheTime, limitTables
    base_client = pool_utils.get_redis_cache()
    if time.time() - limitCacheTime > 60:
        limitkeys = base_utils.mapgetall(base_client, waf_utils.get_rulelimit_infos(user_id))
        limitTables = {}
        limitCacheTime = time.time()
        for (k, v) in limitkeys.items():
            try:
                data = json.loads(v)
                if data.get("cyclical") == None:
                    continue
                if data.get("limitNum") == None:
                    continue
                if data.get("url") == None:
                    continue
                # if data.get("isMathStart") == None:
                #     continue
                limitTables[k] = data
            except Exception as e:
                import traceback
                traceback.print_exc()
                break

    all_news = base_utils.mapgetall(base_client, "new_client_maps")
    base_client.delete("new_client_maps")

    if len(all_news) == 0:
        return

    for (k, v) in all_news.items():
        is_forbidden = False
        all_visit_table = {}
        last_url = ""
        last_access_time = 0
        while True:
            if is_forbidden:
                break
            visit_list = base_client.execute_command(
                "lpop", "client_ip_list:" + k, 1000)
            if not visit_list:
                break
            for v in visit_list:
                access = AccessUrl(v)
                last_url = access.url
                if all_visit_table.get(access.url) == None:
                    all_visit_table[access.url] = []
                all_visit_table[access.url].append(access)
                last_access_time = max(last_access_time, access.access)
                
                if len(limitTables) > 0:
                    for (name, rule) in limitTables.items():
                        if check_is_limit(access.url, rule):
                            limit_key = "limit_count:" + k + ":" + \
                                str(base_utils.get_cyclical_idx(
                                    rule["cyclical"], access.access))
                            count = base_client.hincrby(limit_key, name, 1)
                            base_client.expire(limit_key, 5 * rule["cyclical"])
                            if count > rule["limitNum"]:
                                is_forbidden = True
                                waf_utils.trigger_forbidden_action(user_id, k, "超过次数限制:" + rule["url"], rule.get("time"))
                                break
                if is_forbidden:
                    break
        base_client.zadd(waf_utils.get_online_client_ips(user_id), {k:last_access_time})
        if is_forbidden:
            continue
        
        not_wait_count, all_count = calc_not_wait_count(all_visit_table)
        min_len = cache_utils.get_cache_wait_forbidden_min_len(user_id)
        if all_count < min_len:
            continue
        ratio = cache_utils.get_cache_wait_forbidden_ratio(user_id)
        if not_wait_count / all_count > ratio:
            waf_utils.trigger_forbidden_action(user_id, k, f"同一条请求未完成又重复请求占比 {not_wait_count / all_count}, 总次数 {all_count}")
            continue

        ip_url_times = base_utils.mapgetall(base_client, "client_ip_times:" + k)
        all_visit_times = 0
        last_visit_counts = ip_url_times.get(last_url or "",  0)
        max_request_times = 0
        second_times = 0

        sort_times_list = []

        for (url, times) in ip_url_times.items():
            times = int(times)
            all_visit_times += times
            sort_times_list.append(times)
        sort_times_list.sort(reverse=True)
        all_max_times = 0
        for i in range(min(len(sort_times_list), cache_utils.get_max_visit_idx_num(user_id))):
            all_max_times += sort_times_list[i]
        ratio = all_max_times / all_visit_times
        if all_visit_times > cache_utils.get_min_all_visit_times(user_id) and ratio > cache_utils.get_max_visit_ratio(user_id):
            
            waf_utils.trigger_forbidden_action(user_id, k, f"前{cache_utils.get_max_visit_idx_num(user_id)}种请求({all_max_times}/{all_visit_times}) 请求占比超过{ratio}")

