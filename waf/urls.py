from django.urls import path
from . import views
# Create your views here.

urlpatterns = [
    path('', views.index, name='index'),
    path('get_main_detail', views.get_main_detail, name='get_main_detail'),
    path('get_upstream_detail', views.get_upstream_detail),
    path('get_upstream_list', views.get_upstream_list),
    path('add_upstream_client', views.add_upstream_client),
    path('del_upstream_client', views.del_upstream_client),

    path('get_ssl_list', views.get_ssl_list),
    path('add_ssl_client', views.add_ssl_client),
    path('del_ssl_client', views.del_ssl_client),
    
    path('get_client_detail', views.get_client_detail),
    path('get_block_list', views.get_block_list),
    path('add_block_client', views.add_block_client),
    path('del_block_client', views.del_block_client),
    
    path('get_record_ip_list', views.get_record_ip_list),
    path('add_record_ip_client', views.add_record_ip_client),
    path('del_record_ip_client', views.del_record_ip_client),

    path('get_whiteurl_list', views.get_whiteurl_list),
    path('add_whiteurl_client', views.add_whiteurl_client),
    path('del_whiteurl_client', views.del_whiteurl_client),
    
    
    path('get_ccrule_list', views.get_ccrule_list),
    path('add_ccrule_info', views.add_ccrule_info),
    path('del_ccrule_info', views.del_ccrule_info),
    
    path('get_config_list', views.get_config_list),
    path('add_config_info', views.add_config_info),
    path('del_config_info', views.del_config_info),
    
    path('get_error_list', views.get_error_list),
    path('get_server_infos', views.get_server_infos),

    path('get_cc_attck_times', views.get_cc_attck_times),
    path('currentUser', views.currentUser),
    path('outLogin', views.outLogin),
    path('modify_password', views.modify_password),

    path('get_forbidden_ip_list', views.get_forbidden_ip_list),
    path('search_forbidden_ip', views.search_forbidden_ip),
    path('add_forbidden_ip', views.add_forbidden_ip),
    path('del_forbidden_ip', views.del_forbidden_ip),

    path('get_client_ip_visit', views.get_client_ip_visit),
    path('get_client_ip_url_times', views.get_client_ip_url_times),

    path('get_client_random_visits', views.get_client_random_visits),
    path('get_client_attack_visits', views.get_client_attack_visits),

    path('get_request_url_rank', views.get_request_url_rank),
    path('get_request_url_times', views.get_request_url_times),
    path('clear_request_url_rank', views.clear_request_url_rank),
    path('get_request_cost_rank', views.get_request_cost_rank),
    path('get_request_cost_time', views.get_request_cost_time),
    path('clear_request_cost_rank', views.clear_request_cost_rank),
    path('get_request_aver_rank', views.get_request_aver_rank),
    path('get_request_aver_time', views.get_request_aver_time),
    path('clear_request_aver_rank', views.clear_request_aver_rank),
    path('get_online_client_ips', views.get_online_client_ips),
]

def _add_urlpattern(new_patterns):
    for pattern in new_patterns:
        urlpatterns.append(path(pattern[0], pattern[1]))

from . import pa_api
_add_urlpattern(pa_api.urlpatterns)