import time
from common import pool_utils, cache_utils, base_utils

def do_forbidden_ip(user_id, ip, reason, timeout=None):
    if not timeout:
        timeout = cache_utils.get_default_forbidden_time(user_id)
    pool_utils.do_client_command(user_id, "hset", "all_ip_changes", ip, f"add|{timeout}")
    base_client = pool_utils.get_redis_cache()
    base_client.zadd(get_forbidden_key(user_id), {ip:time.time()})
    base_client.set(get_forbidden_reason_key(user_id, ip), reason, ex=86400)

def do_captcha_ip(user_id, ip, captcha_char, captcha_img, reason, timeout=None):
    if not timeout:
        timeout = cache_utils.get_default_forbidden_time(user_id)

    captcha_key = base_utils.calc_md5(f"{captcha_char}_{time.time()}")

    pool_utils.do_client_command(user_id, "set", f"result_{captcha_key}", captcha_char, "EX", timeout + 100)
    pool_utils.do_client_command(user_id, "set", f"image_{captcha_key}", captcha_img, "EX", timeout + 60)
    
    pool_utils.do_client_command(user_id, "hset", "all_ip_changes", ip, f"captcha|{timeout}|{captcha_key}")

    base_client = pool_utils.get_redis_cache()
    base_client.zadd(get_forbidden_key(user_id), {ip:time.time()})
    base_client.set(get_forbidden_reason_key(user_id, ip), reason, ex=86400)

def trigger_forbidden_action(user_id, ip, reason, timeout=None):
    base_client = pool_utils.get_redis_cache()
    #刚刚被加白, 暂时不拉黑
    if base_client.get(get_ip_allow(user_id, ip)) == 1:
        return

    if cache_utils.get_trigger_forbidden_action(user_id) == "captcha":
        from common import captcha_utils
        captcha_char, captcha_img = captcha_utils.gen_random_image()
        do_captcha_ip(user_id, ip, captcha_char, captcha_img, reason, timeout)
    else:
        do_forbidden_ip(user_id, ip, reason, timeout)
    
def do_del_fobidden_ip(user_id, ip_list):
    new_ip_list = []
    for ip in ip_list:
        new_ip_list.append(ip)
        new_ip_list.append("del")

    pool_utils.do_client_command(user_id, "hmset", "all_ip_changes", *new_ip_list)

def get_forbidden_key(user_id):
    return f"{user_id}:now_forbidden_range"

def get_forbidden_reason_key(user_id, ip):
    return f"{user_id}:reason_forbidden:{ip}"

def get_config_infos(user_id):
    return f"{user_id}:all_config_infos"

def get_client_infos(user_id):
    return f"{user_id}:all_client_infos"

def get_ssl_infos(user_id):
    return f"{user_id}:all_ssl_infos"

def get_upstream_infos(user_id):
    return f"{user_id}:all_upstream_infos"

def get_record_ips(user_id):
    return f"{user_id}:all_record_ips"

def get_white_urls(user_id):
    return f"{user_id}:all_white_urls"
    
def get_limit_infos(user_id):
    return f"{user_id}:all_limit_infos"

def get_rulelimit_infos(user_id):
    return f"{user_id}:all_rulelimit_infos"

def get_upstream_all_cost(user_id, hour_idx):
    return f"{user_id}:upstream_all_cost:{hour_idx}"

def get_cc_attack_cache_times(user_id, day_idx = None):
    if not day_idx:
        return f"{user_id}:cc_attack_cache_times"
    return f"{user_id}:cc_attack_cache_times:{day_idx}"

def get_visit_rank_times_score(user_id):
    return f"{user_id}:visit_rank_times_score"

def get_visit_rank_cost_score(user_id):
    return f"{user_id}:visit_rank_cost_score"

def get_visit_rank_aver_score(user_id):
    return f"{user_id}:visit_rank_aver_score"

def get_online_client_ips(user_id):
    return f"{user_id}:online_client_ips"
    
def get_project_name(user_id):
    return f"{user_id}:project_name"

def get_ip_allow(user_id, ip):
    return f"{user_id}:{ip}:allow"