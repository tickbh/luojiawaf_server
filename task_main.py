import time, logging, os, sys

import threadpool, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LuojiaWaf.settings')
django.setup()

from django.contrib.auth.models import User
from distask import create_scheduler, register_job
from distask import util, Job
from distask.events import EVENT_SCHEDULER_START, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from task import sync, analysis, statistics
import threadpool

from common import log_utils, config_utils

def sync_request_msg_task(times, *args, **kwargs):
    logging.warning("sync_request_msg_task")
    for user in User.objects.filter():
        sync.sync_request_msg(user.id)
        sync.sync_to_client(user.id)

def analysis_task(times, *args, **kwargs):
    logging.warning("analysis_request_msg")
    for user in User.objects.filter():
        analysis.analysis_request_msg(user.id)

def statistics_task(times, *args, **kwargs):
    logging.warning("statistics_request_msg")
    for user in User.objects.filter():
        statistics.statistics_request_msg(user.id)
    
def do_start_task(idx=None):

    client_data = {
        't': 'redis',
        "client_args":{
            "host":'redis_back_db', 
            'port':6479,
            'db':15, 
        }
    }

    connection_details=[
        {'host': 'redis_back_db', 'port': 6479, 'db': 15},
    ]
    lock_data = {
        "t": "rllock",
        "reentrant":True, 
        "connection_details":connection_details, 
        "ttl":10_000
    }

    scheduler = create_scheduler(client_data, lock_data, serialize="pickle", backgroud=False, limit=1, maxwait=5)
    scheduler.add_job(Job(sync_request_msg_task, "interval", (), group="11", subgroup="", seconds=3))
    scheduler.add_job(Job(analysis_task, "interval", (), group="11", subgroup="", seconds=3))
    scheduler.add_job(Job(statistics_task, "interval", (), group="11", subgroup="", seconds=6))

    def job_execute(event):
        if event.code == EVENT_SCHEDULER_START:
            logging.info("start success task event")
        if event.code == EVENT_JOB_ERROR:
            import traceback
            traceback.print_tb(event.traceback)
        if event.code == EVENT_JOB_EXECUTED:
            logging.info("event {} success".format(event.job_id))

    def scheduler_start(event):
        if event.code == EVENT_SCHEDULER_START:
            logging.info("start success")
    scheduler.add_listener(scheduler_start, EVENT_SCHEDULER_START)

    scheduler.add_listener(job_execute, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    scheduler.start()

    import signal
    def fun(sig, stack_frame):
        scheduler.shutdown(False)
        sys.exit(0)

    signal.signal(signal.SIGINT, fun)

if __name__ == '__main__':
    log_utils.custom_init(level=logging.DEBUG, tag="task")
    logging.warning("main")
    pool = threadpool.ThreadPool(20) 
    requests = threadpool.makeRequests(do_start_task, range(1, 21)) 
    [pool.putRequest(req) for req in requests] 
    while True:
        try:
            import time
            time.sleep(1)
        except KeyboardInterrupt:
            break

        try:
            pool.poll(False)
        except threadpool.NoResultsPending:
            break
        
    logging.warning("finish")
    