from django.shortcuts import render
from django.http import response

from django.contrib.auth.models import User
from django.http.response import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
import time, json, re
import redis, requests

from common import pool_utils, base_utils, waf_utils, cache_utils

def login(request):
    user, password = base_utils.get_request_data(request, "user", "password")
    errData = {
        "status": "failed",
        "type": "none",
        "currentAuthority": ""
    }
    if not user or not password:
        return base_utils.ret_err_msg(-1, "请输入用户名和密码", errData)
    ip = base_utils.get_ip(request)
    key = str.format("auth_key_{}_{}", base_utils.get_cyclical_idx(60), ip)
    client = pool_utils.get_redis_cache()
    count = client.incr(key)
    client.expire(key, 120)
    if count > 30:
        return base_utils.ret_err_msg(-1, "慢一点,你输入的太快了", errData)

    count = User.objects.filter().count()

    user_obj = User.objects.filter(username=user).first()
    if not user_obj:
        if count == 0:
            user_obj = User(username=user)
            user_obj.set_password(password)
            user_obj.save()

    if not user_obj:
        return base_utils.ret_err_msg(-1, "用户或密码不正确", errData)
        
    is_correct = user_obj.check_password(password)
    if not is_correct:
        return base_utils.ret_err_msg(-1, "用户或密码不正确", errData)
    auth.login(request, user_obj)

    return JsonResponse({
        "token": request.session.session_key,
        "user": user,
        "success": 0,
        "status": "ok",
        "type": "admin",
        "currentAuthority": user
    })

urlpatterns = [
    ("login", login),
]