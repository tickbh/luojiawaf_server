from array import array
from http import client
from django.shortcuts import render
from django.http import response
from django.http.response import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
import time, json, re
import redis, requests

from common import pool_utils, base_utils, waf_utils, cache_utils, captcha_utils

def index(request):
    return HttpResponse('welcome !!!!!')

def get_main_detail(request):
    user_id = base_utils.get_user_id(request)
    ret_data = {}
    client_infos = {}
    for (host, pool) in pool_utils.get_redis_client_cache_data(user_id).items():
        try:
            data = pool_utils.get_redis_data_cache(user_id, host)
            client = redis.Redis(connection_pool=pool)
            keys = [str.format("now_record_cost:{}", base_utils.get_last_hour_idx()), str.format("now_record_cost:{}", base_utils.get_last_hour_idx() -1)]
            times = client.mget(keys)
            client_times, client_cost_time = 0, 0
            
            for _, time in enumerate(times):
                if not time:
                    continue

                now_times, cost_time = base_utils.calc_times_and_cost_time(time)
                client_times += now_times
                client_cost_time += cost_time
                
            client_infos[data.get("name", "")] = {
                "times": client_times,
                "cost": client_cost_time
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()

    return JsonResponse({
        "success": 0,
        "client_infos": client_infos,
    })
    
def get_client_detail(request):
    user_id = base_utils.get_user_id(request)
    ret_data = {}
    client_infos = {}
    for (host, pool) in pool_utils.get_redis_client_cache_data(user_id).items():
        try:
            data = pool_utils.get_redis_data_cache(user_id, host)
            client = redis.Redis(connection_pool=pool)
            keys = [str.format("now_record_cost:{}", base_utils.get_last_hour_idx()), str.format("now_record_cost:{}", base_utils.get_last_hour_idx() -1)]
            times = client.mget(keys)
            client_times, client_cost_time = 0, 0
            
            for _, time in enumerate(times):
                if not time:
                    continue

                now_times, cost_time = base_utils.calc_times_and_cost_time(time)
                client_times += now_times
                client_cost_time += cost_time
                
            client_infos[data.get("name")] = {
                "times": client_times,
                "cost": client_cost_time
            }
        except Exception as e:
            import traceback
            traceback.print_exc()

    return JsonResponse({
        "success": 0,
        "client_infos": client_infos,
    })

# 服务器列表
def get_block_list(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()
    infos = base_utils.mapgetall(client, waf_utils.get_client_infos(user_id))
    return JsonResponse({
        "success": True,
        "lists": [v for _, v in infos.items()],
    })

def add_block_client(request):
    user_id = base_utils.get_user_id(request)
    name, server_id, oriname = base_utils.get_request_data(request, "name", "server_id", "oriname")
    client = pool_utils.get_redis_cache()
    if not server_id or not name:
        return base_utils.ret_err_msg(-1, "参数不正确")
    info = json.dumps({"server_id": server_id, "name": name})
    
    client.hset(waf_utils.get_client_infos(user_id), name, info)
    if oriname and oriname != name:
        client.hdel(waf_utils.get_client_infos(user_id), oriname)

    return JsonResponse({
        "success": True,
        "info": info,
    })

# 删除服务器列表
def del_block_client(request):
    user_id = base_utils.get_user_id(request)
    name, _ = base_utils.get_request_data(request, "name", "_")
    if not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()
    ok = client.hdel(waf_utils.get_client_infos(user_id), name)
    return JsonResponse({
        "success": True,
        "name": name,
        "ok": ok,
    })
    
# IP访问记录
def get_record_ip_list(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()
    infos = base_utils.mapgetall(client,waf_utils.get_record_ips(user_id))
    return JsonResponse({
        "success": True,
        "lists": [{ip:v} for ip, v in infos.items()],
    })

def add_record_ip_client(request):
    user_id = base_utils.get_user_id(request)
    ip, action, oriip = base_utils.get_request_data(request, "ip", "action", "oriip")
    client = pool_utils.get_redis_cache()
    if not ip or not action:
        return base_utils.ret_err_msg(-1, "参数不正确")
    
    client.hset(waf_utils.get_record_ips(user_id), ip, action)
    if oriip and oriip != ip:
        client.hdel(waf_utils.get_record_ips(user_id), oriip)

    return JsonResponse({
        "success": True,
        "ip": ip,
    })

def del_record_ip_client(request):
    user_id = base_utils.get_user_id(request)
    ip, _ = base_utils.get_request_data(request, "ip", "_")
    if not ip:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()

    ori_value = client.hget(waf_utils.get_record_ips(user_id), ip)
    ok = client.hdel(waf_utils.get_record_ips(user_id), ip)
    
    if "deny" in ori_value:
        waf_utils.do_del_fobidden_ip(user_id, [ip])
    return JsonResponse({
        "success": True,
        "ok": ok,
    })

# 白名单URL
def get_whiteurl_list(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()
    infos = base_utils.mapgetall(client, waf_utils.get_white_urls(user_id))
    return JsonResponse({
        "success": True,
        "lists": [{ip:v} for ip, v in infos.items()],
    })

def add_whiteurl_client(request):
    user_id = base_utils.get_user_id(request)
    url, action, oriurl = base_utils.get_request_data(request, "url", "action", "oriurl")
    client = pool_utils.get_redis_cache()
    if not url or not action:
        return base_utils.ret_err_msg(-1, "参数不正确")
    
    client.hset(waf_utils.get_white_urls(user_id), url, action)
    if oriurl and oriurl != url:
        client.hdel(waf_utils.get_white_urls(user_id), oriurl)

    return JsonResponse({
        "success": True,
        "url": url,
    })

def del_whiteurl_client(request):
    user_id = base_utils.get_user_id(request)
    url, _ = base_utils.get_request_data(request, "url", "_")
    if not url:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()

    ok = client.hdel(waf_utils.get_white_urls(user_id), url)
    return JsonResponse({
        "success": True,
        "ok": ok,
    })

# CC规则访问记录
def get_ccrule_list(request):
    client = pool_utils.get_redis_cache()
    infos = base_utils.mapgetall(client, waf_utils.get_rulelimit_infos(base_utils.get_user_id(request)))
    return JsonResponse({
        "success": True,
        "lists": [v for _, v in infos.items()],
    })

def add_ccrule_info(request):
    name, url, cyclical, limitNum, isMathStart, time, oriname = base_utils.get_request_data(request, "name", "url", "cyclical", "limitNum", "isMathStart", "time", "oriname")
    if not isMathStart:
        isMathStart = True
    if not time:
        time = cache_utils.get_default_forbidden_time(base_utils.get_user_id(request))
    if not name or not url or not cyclical or not limitNum:
        return base_utils.ret_err_msg(-1, "参数不正确")
    cyclical, limitNum, time = base_utils.safe_int(cyclical), base_utils.safe_int(limitNum), base_utils.safe_int(time)
    if cyclical <= 0 or limitNum <=0 or time <=0 :
        return base_utils.ret_err_msg(-1, "参数cyclical或limitNum或time不正确")

    client = pool_utils.get_redis_cache()
    key = waf_utils.get_rulelimit_infos(base_utils.get_user_id(request))
    client.hset(key, name, json.dumps({
        "name": name, "url": url, "cyclical": cyclical, "limitNum": limitNum, "isMathStart": isMathStart, "time": time
    }) )

    if oriname and oriname != name:
        client.hdel(key, name)
    return JsonResponse({
        "success": True,
        "name": name,
    })

def del_ccrule_info(request):
    name, _ = base_utils.get_request_data(request, "name", "_")
    if not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()
    key = waf_utils.get_rulelimit_infos(base_utils.get_user_id(request))
    ok = client.hdel(key, name)
    return JsonResponse({
        "success": True,
        "name": name,
        "ok": ok,
    })
    
#配置文件
def get_config_list(request):
    client = pool_utils.get_redis_cache()
    infos = base_utils.mapgetall(client, waf_utils.get_config_infos(base_utils.get_user_id(request)))
    return JsonResponse({
        "success": True,
        "lists": [{k: v} for k, v in infos.items()],
    })

def add_config_info(request):
    key, value = base_utils.get_request_data(request, "key1", "value")
    if not key or not value:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()
    config_key = waf_utils.get_config_infos(base_utils.get_user_id(request))

    if key == "limit_all_ip":
        matchObj = re.match( r'(.*)/(.*)', value, re.M|re.I)
        if not matchObj:
            return base_utils.ret_err_msg(-1, "limit_all_ip参数必须为333/444且为数字")
            
        g1 = base_utils.safe_int(matchObj.group(1))
        g2 = base_utils.safe_int(matchObj.group(2))
        if g1 <= 0 or g2 <= 0:
            return base_utils.ret_err_msg(-1, "limit_all_ip参数必须为333/444且为数字")
            
        # client.set(key, value)

    client.hset(config_key, key, value)
    return JsonResponse({
        "success": True,
        "name": key,
    })

def del_config_info(request):
    key, _ = base_utils.get_request_data(request, "key1", "_")
    if not key:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()
    # if key == "limit_all_ip":
    #     client.delete("limit_all_ip")

    config_key = waf_utils.get_config_infos(base_utils.get_user_id(request))
    ok = client.hdel(config_key, key)
    return JsonResponse({
        "success": True,
        "name": key,
        "ok": ok,
    })

def get_error_list(request):
    
    name, status, page, pagecount, yesterday = base_utils.get_request_data(request, "name", "status", "page", "pagecount", "yesterday")
    if not name or not status:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_client_cache(base_utils.get_user_id(request), name)
    if not client:
        return base_utils.ret_err_msg(-1, "该高防不存在")

    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)

    idx = base_utils.get_last_day_idx()
    if yesterday == "1":
        idx -= 1
    key = str.format("server_request_{}_{}", status, idx)
    
    datas = client.zrange(key, (page - 1) * pagecount, page * pagecount - 1, desc=True, withscores=True)
    count = client.zcount(key, "-inf", "+inf")

    return JsonResponse({
        "success": True,
        "datas": datas,
    })
    
def get_server_infos(request):
    name, is_hour = base_utils.get_request_data(request, "name", "is_hour")
    if not name:
        return base_utils.ret_err_msg(-1, "参数不正确")
    
    cache = pool_utils.get_redis_data_cache(base_utils.get_user_id(request), name)
    server_id = base_utils.safe_json(cache).get("server_id", 0)
    client = pool_utils.get_redis_cache()
    if not client:
        return base_utils.ret_err_msg(-1, "该高防不存在")

    cpu_infos = client.lrange(waf_utils.get_unique_key(server_id, "all_cpu_info") , -180, -1)
    network_infos = client.lrange(waf_utils.get_unique_key(server_id, "all_network_info"), -180, -1)
    mem_infos = client.lrange(waf_utils.get_unique_key(server_id, "all_mem_info"), -180, -1)

    return JsonResponse({
        "success": True,
        "cpu_infos": cpu_infos,
        "network_infos": network_infos,
        "mem_infos": mem_infos,
    })

# cc攻击数
def get_cc_attck_times(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()
    key_all = f"{user_id}:cc_attack_cache_times"
    key = f"{user_id}:cc_attack_cache_times:" + str(base_utils.get_last_day_idx() - 1) 
    key1 = f"{user_id}:cc_attack_cache_times:" + str(base_utils.get_last_day_idx())
    
    value_all, value, value1 = client.mget(key_all, key, key1)
    cc_attck_times = base_utils.safe_int(value) + base_utils.safe_int(value1)

    
    return JsonResponse({
        "success": True,
        "all_times": value_all,
        "times": cc_attck_times,
    })
    
# 负载均衡状态
def get_upstream_detail(request):
    client = pool_utils.get_redis_cache()
    user_id = base_utils.get_user_id(request)
    keys = [waf_utils.get_upstream_all_cost(user_id, base_utils.get_last_hour_idx()), waf_utils.get_upstream_all_cost(user_id, base_utils.get_last_hour_idx() - 1)]
    
    values = [base_utils.mapgetall(client, key) for key in keys]
    upstream_infos = {}
    
    for _, value_map in enumerate(values):
        if len(value_map) == 0:
            continue
        
        for name, time in value_map.items():
            if not upstream_infos.get(name):
                upstream_infos[name] = {"times": 0, "cost":0}
            
            now_times, cost_time = base_utils.calc_times_and_cost_time(time)
            upstream_infos[name]["times"] += now_times
            upstream_infos[name]["cost"] += cost_time
        
    return JsonResponse({
        "success": 0,
        "upstream_infos": upstream_infos,
    })
    
def get_upstream_list(request):
    host, show_all = base_utils.get_request_data(request, "host", "show_all")
    client = pool_utils.get_redis_cache()
    user_id = base_utils.get_user_id(request)
    
    infos = base_utils.mapgetall(client, waf_utils.get_upstream_infos(user_id))
    values = [{name: v} for name, v in infos.items()]

    return JsonResponse({
        "success": True,
        "values": values
    })

def add_upstream_client(request):
    user_id = base_utils.get_user_id(request)
    host, ip, port, fail, fail_timeout, weight, name, oriname =  \
        base_utils.get_request_data(request, "host", "ip", "port", "fail", "fail_timeout", "weight", "name", "oriname")
    client = pool_utils.get_redis_cache()
    if not port:
        port = "80"
    if not host:
        host = "*"
    if not ip or not port or not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    subhost = f"{ip}:{port}"
    try:
        url = f'http://{subhost}'
        r = requests.get(url, timeout=5)
        if r.status_code != requests.codes.ok:
            raise
    except Exception as e:
        return base_utils.ret_err_msg(-1, "该地址无法访问:" + subhost)

    info = json.dumps({"ip": ip, "port": port, "host": host, "name":name, "fail": fail or 3, "fail_timeout": fail_timeout or 180, "weight": weight or 100})
    client.hset(waf_utils.get_upstream_infos(user_id), name, info)

    if oriname and oriname != name:
        client.hdel(waf_utils.get_upstream_infos(user_id), oriname)

    return JsonResponse({
        "success": True,
        "info": info,
    })

def del_upstream_client(request):
    name, _ = base_utils.get_request_data(request, "name", "_")
    if not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()
    user_id = base_utils.get_user_id(request)
    ok = client.hdel(waf_utils.get_upstream_infos(user_id), name)
    return JsonResponse({
        "success": True,
        "ok": ok,
    })
    
def get_ssl_list(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()

    infos = base_utils.mapgetall(client, waf_utils.get_ssl_infos(user_id))
    values = [{name: v} for name, v in infos.items()]

    return JsonResponse({
        "success": True,
        "values": values
    })

def add_ssl_client(request):
    user_id = base_utils.get_user_id(request)
    host, pem, pem_key, name, oriname =  \
        base_utils.get_request_data(request, "host", "pem", "pem_key", "name", "oriname")
    client = pool_utils.get_redis_cache()
    if not host:
        host = "*"
    if not pem or not pem_key or not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    info = json.dumps({"host": host, "pem": pem,  "pem_key":pem_key, "name": name})
    client.hset(waf_utils.get_ssl_infos(user_id), name, info)
    if oriname and oriname != name:
        client.hdel(waf_utils.get_ssl_infos(user_id), oriname)
    return JsonResponse({
        "success": True,
        "info": info,
    })

def del_ssl_client(request):
    user_id = base_utils.get_user_id(request)
    host, _ = base_utils.get_request_data(request, "host", "_")
    if not host:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()
    ok = client.hdel(waf_utils.get_ssl_infos(user_id), host)
    return JsonResponse({
        "success": True,
    })

def get_forbidden_ip_list(request):
    user_id = base_utils.get_user_id(request)
    page, pagecount = base_utils.get_request_data(request, "page", "pagecount")
    client = pool_utils.get_redis_cache()
    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)
    startTime = time.time() - 86400
    count = client.zcount(waf_utils.get_forbidden_key(user_id), startTime, "+inf")
    
    datas = []
    if count != 0:
        startIdx = min((page - 1) * pagecount, count) 
        endIdx = min(page * pagecount, count)

        datas = client.zrange(waf_utils.get_forbidden_key(user_id), startIdx, endIdx - 1, desc=True, withscores=True)

    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })

def search_forbidden_ip(request):
    user_id = base_utils.get_user_id(request)
    client_ip, _ = base_utils.get_request_data(request, "client_ip", "_")
    client = pool_utils.get_redis_cache()
    if not client_ip:
        return base_utils.ret_err_msg(-1, "客户端ip不存在")

    forbidden_time = client.zscore(waf_utils.get_forbidden_key(user_id), client_ip)
    forbidden_reason = client.get(waf_utils.get_forbidden_reason_key(user_id, client_ip))
    exist = True
    if not forbidden_time:
        exist = False
        forbidden_time = 0
        
    return JsonResponse({
        "success": True,
        "datas":[
            [client_ip, forbidden_time, forbidden_reason]
        ],
        "exist": exist
    })
    
def add_forbidden_ip(request):
    client_ip_list, _ = base_utils.get_request_data(request, "client_ip_list", "_")
    client = pool_utils.get_redis_cache()
    if not client_ip_list:
        return base_utils.ret_err_msg(-1, "客户端ip不存在")

    
    # list = base_utils.safe_json(client_ip_list)
    list = str.split(client_ip_list, ";")
    if len(list) == 0:
        return base_utils.ret_err_msg(-1, "客户端ip不存在")

    for ip in list:
        ip = ip.strip()
        waf_utils.trigger_forbidden_action(base_utils.get_user_id(request), ip, "forbidden by admin")

    return JsonResponse({
        "success": True,
        "client_ip_list": client_ip_list,
    })

def del_forbidden_ip(request):
    client_ip_list, is_all = base_utils.get_request_data(request, "client_ip_list", "is_all")
    client = pool_utils.get_redis_cache()
    if not client_ip_list and not is_all:
        return base_utils.ret_err_msg(-1, "客户端ip不存在")

    user_id = base_utils.get_user_id(request)
    forbidden_key = waf_utils.get_forbidden_key(base_utils.get_user_id(request))
    if not is_all:
        list = str.split(client_ip_list, ";")
        if len(list) == 0:
            return base_utils.ret_err_msg(-1, "客户端ip不存在")
        ok = client.zrem(forbidden_key, *list)
        waf_utils.do_del_fobidden_ip(user_id, list)
    else:
        all_list = client.zrange(forbidden_key, 0, -1)
        waf_utils.do_del_fobidden_ip(user_id, all_list)
        client.delete(forbidden_key)
    return JsonResponse({
        "success": True,
        "client_ip_list": client_ip_list,
        "is_all": is_all,
        "ok": ok,
    })
    
    
def get_client_ip_visit(request):
    name, ip, page, pagecount = base_utils.get_request_data(request, "name", "ip", "page", "pagecount")
    if not name or not ip:
        return base_utils.ret_err_msg(-1, "参数不正确")

    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_client_cache(user_id, name)
    if not client:
        return base_utils.ret_err_msg(-1, "该高防不存在")

    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)

    key = "client_url_lists:" + ip
    datas = client.lrange(key, (page - 1) * pagecount, page * pagecount)
    count = client.llen(key)
    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })

def get_client_ip_url_times(request):
    ip, _ = base_utils.get_request_data(request, "ip", "_")
    if not ip:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_cache()

    key = "client_ip_times:" + ip
    datas = base_utils.mapgetall(client, key)
    array = []
    for url, times in datas.items():
        array.append({"u": url, "t": base_utils.safe_int(times) or 0})

    array.sort(key = lambda v: -v["t"])

    return JsonResponse({
        "success": True,
        "datas": array[:20],
    })

def get_client_random_visits(request):
    user_id = base_utils.get_user_id(request)
    name, page, pagecount = base_utils.get_request_data(request, "name", "page", "pagecount")
    if not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_client_cache(user_id, name)
    if not client:
        return base_utils.ret_err_msg(-1, "该高防不存在")

    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)

    key = "client_random_url:" + str(base_utils.get_last_day_idx())
    datas = client.lrange(key, (page - 1) * pagecount, page * pagecount - 1)
    count = client.llen(key)
    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })

def get_client_attack_visits(request):
    user_id = base_utils.get_user_id(request)
    name, page, pagecount = base_utils.get_request_data(request, "name", "page", "pagecount")
    if not name:
        return base_utils.ret_err_msg(-1, "参数不正确")

    client = pool_utils.get_redis_client_cache(user_id, name)
    if not client:
        return base_utils.ret_err_msg(-1, "该高防不存在")

    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)

    key = "client_attack_url_all"
    datas = client.lrange(key, (page - 1) * pagecount, page * pagecount - 1)
    count = client.llen(key)
    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })


def get_request_url_rank(request):
    page, pagecount = base_utils.get_request_data(request, "page", "pagecount")
    client = pool_utils.get_redis_cache()
    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)
    user_id = base_utils.get_user_id(request)
    datas = client.zrange(waf_utils.get_visit_rank_times_score(user_id), (page - 1) * pagecount, page * pagecount - 1, desc=True, withscores=True)
    count = client.zcount(waf_utils.get_visit_rank_times_score(user_id), "-inf", "+inf")
    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })

def get_request_url_times(request):
    urls_str, _ = base_utils.get_request_data(request, "urls", "_")
    client = pool_utils.get_redis_cache()
    urls = base_utils.safe_json(urls_str)

    user_id = base_utils.get_user_id(request)
    pipe = client.pipeline()
    for (idx, key) in enumerate(urls):
        pipe.zscore(waf_utils.get_visit_rank_times_score(user_id), key)
    datas = pipe.execute()

    return JsonResponse({
        "success": True,
        "urls": urls,
        "datas": datas,
    })

def clear_request_url_rank(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()
    ok = client.delete(waf_utils.get_visit_rank_times_score(user_id))
    return JsonResponse({
        "success": True,
        "datas": [],
        "count": 0
    })

def get_request_cost_rank(request):
    page, pagecount = base_utils.get_request_data(request, "page", "pagecount")
    client = pool_utils.get_redis_cache()
    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)

    user_id = base_utils.get_user_id(request)
    datas = client.zrange(waf_utils.get_visit_rank_cost_score(user_id), (page - 1) * pagecount, page * pagecount - 1, desc=True, withscores=True)
    count = client.zcount(waf_utils.get_visit_rank_cost_score(user_id), "-inf", "+inf")
    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })

def get_request_cost_time(request):
    urls_str, _ = base_utils.get_request_data(request, "urls", "_")
    client = pool_utils.get_redis_cache()
    urls = base_utils.safe_json(urls_str)
    user_id = base_utils.get_user_id(request)
    pipe = client.pipeline()
    for (idx, key) in enumerate(urls):
        pipe.zscore(waf_utils.get_visit_rank_cost_score(user_id), key)
    datas = pipe.execute()

    return JsonResponse({
        "success": True,
        "urls": urls,
        "datas": datas,
    })
    
def clear_request_cost_rank(request):
    user_id = base_utils.get_user_id(request)
    client = pool_utils.get_redis_cache()
    ok = client.delete(waf_utils.get_visit_rank_cost_score(user_id))
    return JsonResponse({
        "success": True,
        "datas": [],
        "count": 0
    })

def get_request_aver_rank(request):
    page, pagecount = base_utils.get_request_data(request, "page", "pagecount")
    client = pool_utils.get_redis_cache()
    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)

    user_id = base_utils.get_user_id(request)
    datas = client.zrange(waf_utils.get_visit_rank_aver_score(user_id), (page - 1) * pagecount, page * pagecount - 1, desc=True, withscores=True)
    count = client.zcount(waf_utils.get_visit_rank_aver_score(user_id), "-inf", "+inf")
    return JsonResponse({
        "success": True,
        "datas": datas,
        "count": count
    })

def get_request_aver_time(request):
    urls_str, _ = base_utils.get_request_data(request, "urls", "_")
    client = pool_utils.get_redis_cache()
    urls = base_utils.safe_json(urls_str)

    user_id = base_utils.get_user_id(request)
    pipe = client.pipeline()
    for (idx, key) in enumerate(urls):
        pipe.zscore(waf_utils.get_visit_rank_aver_score(user_id), key)
    datas = pipe.execute()

    return JsonResponse({
        "success": True,
        "urls": urls,
        "datas": datas,
    })

def clear_request_aver_rank(request):
    client = pool_utils.get_redis_cache()
    user_id = base_utils.get_user_id(request)
    ok = client.delete(waf_utils.get_visit_rank_aver_score(user_id))
    return JsonResponse({
        "success": True,
        "datas": [],
        "count": 0
    })
    
def get_online_client_ips(request):
    page, pagecount = base_utils.get_request_data(request, "page", "pagecount")
    client = pool_utils.get_redis_cache()
    page = max(base_utils.safe_int(page, 1), 1) 
    pagecount = base_utils.safe_int(pagecount, 20)
    user_id = base_utils.get_user_id(request)
    startTime = int(time.time()) - 5 * 60
    five_count = client.zcount(waf_utils.get_online_client_ips(user_id), startTime, "+inf")
    startTime = int(time.time()) - 2.5 * 60
    count = client.zcount(waf_utils.get_online_client_ips(user_id), startTime, "+inf")
    datas = []
    if count != 0:
        startIdx = min((page - 1) * pagecount, count) 
        endIdx = min(page * pagecount, count)
        datas = client.zrange(waf_utils.get_online_client_ips(user_id), startIdx, endIdx - 1, desc=True, withscores=True)

    return JsonResponse({
        "success": True,
        "datas": datas,
        "five_count": five_count,
        "count": count
    })

def currentUser(request):
    user = request.user
    client = pool_utils.get_redis_cache()
    project_name = client.get(waf_utils.get_project_name(base_utils.get_user_id(request))) or ""
    return JsonResponse({
        "success": True,
        "data": {
            "name": user.username,
            "access": "admin",
            "project_name": project_name,
        }
    })

def outLogin(request):
    auth.logout(request)
    return JsonResponse({
        "data": {},
        "success": True,
    })

def modify_password(request):
    old_password, password = base_utils.get_request_data(request, "old_password", "password")
    if not request.user.check_password(old_password):
        return JsonResponse({
            "errorMessage": "密码不正确",
            "success": False,
        })
        return base_utils.ret_err_msg(400, "密码不正确")
    request.user.set_password(password)
    request.user.save()
    return JsonResponse({
        "token": request.session.session_key,
        "data": {},
        "success": True,
    })


def modify_project_name(request):
    project_name, _ = base_utils.get_request_data(request, "project_name", "_")
    client = pool_utils.get_redis_cache()
    client.set(waf_utils.get_project_name(base_utils.get_user_id(request)), project_name)
    return JsonResponse({
        "data": {},
        "project_name": project_name,
        "success": True,
    })
    