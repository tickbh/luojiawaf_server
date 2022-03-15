
import datetime
import hashlib
import json
import random
import re
import time, logging

from django.http import request
from django.http.response import JsonResponse

def get_cyclical_idx(cyclical, now=None):
    #2015-01-01
    if not now:
        now = time.time()
    return int((float(now) - 1420041600) / cyclical)

def get_last_hour_idx(now=None):
    #2015-01-01
    idx = get_cyclical_idx(3600, now)
    return idx

def get_last_day_idx(now=None):
    #2015-01-01
    idx = get_cyclical_idx(86400, now)
    return idx

def calc_times_and_cost_time(value):
    value = float(value)
    times = int(value / 1000)
    cost = (value - times * 1000) * 1000
    return times, cost

def super_transfer(_type, value, default_return=0, is_log=False):
    try:
        result = _type(value)
    except:
        result = default_return
        if is_log:
            logging.error('将{value}转换为{_type}类型时失败'.format(value=value, _type=_type))

    return result

    
def safe_str(value, default_return="", is_log=False) -> str:
    '''
    提供安全的类型转换函数,将value转换为int类型
    :param value:需要被转换的数据
    :param default_return: 转换失败时的返回值
    :param is_log:是否记录日志
    :return:
    '''
    if not value:
        return ""
    if type(value) == str:
        return value
    try:
        if type(value) == bytes:
            return bytes.decode(value, "utf-8")
        if type(value) == dict:
            return json.dumps(value)
        if type(value) == list:
            return json.dumps(value)
        result = str(value)
    except:
        result = default_return
        if is_log:
            logging.error('将{value}转换为{_type}类型时失败'.format(value=value))

    return result

def safe_int(value, default_return=0, is_log=False):
    '''
    提供安全的类型转换函数,将value转换为int类型
    :param value:需要被转换的数据
    :param default_return: 转换失败时的返回值
    :param is_log:是否记录日志
    :return:
    '''
    return super_transfer(int, value, default_return, is_log)


def safe_float(value, default_return=0, is_log=False):
    '''
    提供安全的类型转换函数,将value转换为float类型
    :param value:需要被转换的数据
    :param default_return: 转换失败时的返回值
    :param is_log:是否记录日志
    :return:
    '''
    return super_transfer(float, value, default_return, is_log)

def scankeys(redis, match=None, count=2000, _type=None):
    return [v for v in redis.scan_iter(match, count, _type)]
    
def mapgetall(redis, key, count=2000):
    dict = {}
    for k, v in redis.hscan_iter(key, count= count):
        dict[k] = v
    return dict

rand_array = [
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'a', 'b', 'c', 'd', 'e', 'f',
        'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o',
        'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
        'x', 'y'
    ]
rand_len = len(rand_array)

rannum_array = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

ranhex_array = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

def get_all_headers(request):
    import re
    regex_http_          = re.compile(r'^HTTP_.+$')
    regex_content_type   = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')

    request_headers = {}
    for header in request.META:
        if regex_content_type.match(header) or regex_content_length.match(header):
            request_headers[header] = request.META[header]
        elif regex_http_.match(header):
            request_headers[header[5:]] = request.META[header]
    return request_headers

# def safe_int(num):
#     try:
#         return int(num)
#     except ValueError:
#         result = "0"
#         for c in num:
#             if c not in str.digits:
#                 break
#             result += c
#         return int(result)

def safe_json(source, default={}):
    '''若转化失败, 则返回默认值'''
    try:
        if not isinstance(source, str):
            return source
        value = json.loads(source)
        return value
    except:
        return default

def random_url(num=5):
    result = ''
    for _ in range(0, num):
        result = result + random.choice(rand_array)
    return result

def random_hex(num=32):
    result = ''
    for _ in range(0, num):
        result = result + random.choice(ranhex_array)
    return result


def random_code(num=4):
    result = ''
    for _ in range(0, num):
        result = result + random.choice(rannum_array)
    return result

def random_useraccount(num=8):
    result = ''
    for _ in range(0, num):
        result = result + random.choice(rannum_array)
    return result

def random_password(num=6):
    result = ''
    for _ in range(0, num):
        result = result + random.choice(rannum_array)
    return result

pattern = r'1\d{10}$'
def check_not_telephone(phone):
    if not phone:
        return True
    match = re.match(pattern, phone)
    return match == None

def get_post_data(request, *arg):
    result = []
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            for key in arg:
                result.append(data.get(key) or "")
        else:
            for key in arg:
                result.append("")
    except:
        for key in arg:
            result.append("")
    return result

def get_request_data(request, *arg):
    result = []
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            for key in arg:
                result.append(data.get(key) or "")
            return result
        else:
            for key in arg:
                result.append(request.GET.get(key) or "")
            return result   
    except:
        for key in arg:
            result.append("")
        return result

def get_format_time(now=None):
    now = now or datetime.datetime.now()
    return now.strftime('%Y%m%d%H%M%S')

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]#所以这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')#这里获得代理ip
    return ip

def timestamp_fix_today_start(timestamp):
    timestamp = (safe_int(timestamp) or safe_int(time.time())) + 8 * 3600
    return timestamp -  timestamp % 86400 - 8 * 3600

def ret_err_msg(code, msg, data=None):
    if not data:
        data = {}
    data["success"] = code
    data["err_msg"] = msg
    return JsonResponse(data)

def get_user_id(request):
    if hasattr(request, "user"):
        return request.user.id
    return 0

def calc_md5(data):
    md = hashlib.md5()
    md.update(data.encode(encoding='UTF-8')) 
    return md.hexdigest()