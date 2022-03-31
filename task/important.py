import redis
import math
import time
import json
import re
from common import config_utils, pool_utils, base_utils, cache_utils, waf_utils
from task.accessurl import AccessUrl, calc_not_wait_count

def important_request_msg(user_id):
    base_client = pool_utils.get_redis_cache()

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            all_import_msg = base_utils.mapgetall(client, "all_import_msg")
            client.delete("all_import_msg")
            for (k, v) in all_import_msg.items():
                value = base_utils.safe_json(k)
                action = value.get("action")
                ip = value.get("ip")
                if action == "captcha_ok":
                    base_client.set(waf_utils.get_ip_allow(user_id, ip), 1, ex=600)
                    
                    pool_utils.do_client_command(user_id, "hset", "all_ip_changes", ip, f"allow|{timeout}")
                elif action == "captcha_refresh":
                    from common import captcha_utils
                    captcha_char, captcha_img = captcha_utils.gen_random_image()
                    timeout = cache_utils.get_default_forbidden_time(user_id)
                    captcha_key = base_utils.calc_md5(f"{captcha_char}_{time.time()}")
                    pool_utils.do_client_command(user_id, "set", f"result_{captcha_key}", captcha_char, "EX", timeout + 100)
                    pool_utils.do_client_command(user_id, "set", f"image_{captcha_key}", captcha_img, "EX", timeout + 60)

        except Exception as e:
            import traceback
            traceback.print_exc()


