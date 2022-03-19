import logging
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

def pretty_print_post(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    logging.warning('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.get_full_path(),
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

NO_CHECK_ARRAY = [
    '/waf/login', '/waf/luojia_admin/'
]

class LoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        
        if not request.path_info.startswith('/admin'):
            pretty_print_post(request)
        
        no_check = False
        for key in NO_CHECK_ARRAY:
            if request.path_info.startswith(key):
                no_check = True
                break
        if not no_check:
            user = request.user
            no_check = user.is_active
        if no_check:
            # 执行视图函数
            response = self.get_response(request)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Headers"] = "*"
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        return JsonResponse({
            'success': '-1',
            'errmsg': '您尚未登陆',
        })
