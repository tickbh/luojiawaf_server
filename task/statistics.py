import redis
import math
import time
import json
import re
from common import config_utils, pool_utils, base_utils, cache_utils, waf_utils
from task.accessurl import AccessUrl, calc_not_wait_count

def statistics_request_msg(user_id):
    base_client = pool_utils.get_redis_cache()

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            upstream_cost = base_utils.mapgetall(client, "upstream_all_cost")
            client.delete("upstream_all_cost")
            pipe = base_client.pipeline()
            key = waf_utils.get_upstream_all_cost(user_id, base_utils.get_last_hour_idx())
            for (k, v) in upstream_cost.items():
                pipe.hincrbyfloat(key, k, v)
            pipe.expire(key, 86400)
            ok = pipe.execute()

            cc_key = "cc_attack_cache_times:" + str(base_utils.get_last_day_idx())
            cc_attck_times = base_utils.safe_int(client.get(cc_key), 0) 
            if cc_attck_times > 0:
                base_client.incrby(f"{user_id}:cc_attack_cache_times", cc_attck_times)
                base_client.incrby(f"{user_id}:{cc_key}", cc_attck_times)
                client.delete(cc_key)
            try:
                normal_cost = base_utils.mapgetall(client, "normal_all_cost")
            except:
                normal_cost = {}
            client.delete("normal_all_cost")

            pipe = base_client.pipeline()
            url_list = []
            for (k, v) in normal_cost.items():
                times, cost_time = base_utils.calc_times_and_cost_time(v)
                pipe.zincrby(waf_utils.get_visit_rank_times_score(user_id), times, k)
                pipe.zincrby(waf_utils.get_visit_rank_cost_score(user_id), cost_time, k)
                url_list.append(k)
            ok = pipe.execute()

            mapping = {}    
            for idx, url in enumerate(url_list):
                aver =  base_utils.safe_float(ok[idx * 2 + 1]) / max(base_utils.safe_int(ok[idx * 2]), 1)
                if aver == 0:
                    continue
                mapping[url] = aver
            if len(mapping) > 0:
                base_client.zadd(waf_utils.get_visit_rank_aver_score(user_id), mapping)
        except Exception as e:
            import traceback
            traceback.print_exc()


