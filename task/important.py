import redis
import math
import time
import json
import re
from redis import ResponseError
from common import config_utils, pool_utils, base_utils, cache_utils, waf_utils
from task.accessurl import AccessUrl, calc_not_wait_count

def important_request_msg(user_id):
    base_client = pool_utils.get_redis_cache()

    for client in pool_utils.iter_redis_client_cache_data(user_id):
        try:
            all_import_msg = base_utils.mapgetall(client, "all_import_msg")
            if not all_import_msg:
                continue
            client.delete("all_import_msg")
            for (k, v) in all_import_msg.items():
                value = base_utils.safe_json(k)
                action = value.get("action")
                ip = value.get("ip")
                timeout = cache_utils.get_default_forbidden_time(user_id)
                if action == "captcha_ok":
                    base_client.set(waf_utils.get_ip_nocheck(user_id, ip), 1, ex=600)
                    timeout = math.floor(time.time()) + timeout
                    pool_utils.do_client_command(user_id, "hset", "all_ip_changes", ip, f"nocheck|{timeout}")
                    pool_utils.do_client_incr_version("all_ip_changes")
                elif action == "captcha_refresh":
                    from common import captcha_utils
                    captcha_char, captcha_img = captcha_utils.gen_random_image()
                    captcha_key = base_utils.calc_md5(f"{captcha_char}_{time.time()}")
                    pool_utils.do_client_command(user_id, "set", f"result_{captcha_key}", captcha_char, "EX", timeout + 100)
                    pool_utils.do_client_command(user_id, "set", f"image_{captcha_key}", captcha_img, "EX", timeout + 60)
                    timeout = math.floor(time.time()) + timeout
                    pool_utils.do_client_command(user_id, "hset", "all_ip_changes", ip, f"captcha|{timeout}|{captcha_key}")
                    pool_utils.do_client_incr_version("all_ip_changes")
        except ResponseError as e:
            if "WRONGTYPE" in str(e):
                client.delete("all_import_msg")
        except Exception as e:
            import traceback
            traceback.print_exc()


