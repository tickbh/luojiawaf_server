import logging
import time, datetime
from logging import handlers

def custom_init(filename=None, level=logging.INFO, tag="normal"):
    logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=level)

    if not filename:
        filename = "logs/local.{}_{}.log".format(tag, time.strftime("%Y-%m-%d", time.localtime()))
    
    error_log = "logs/err.local.{}_{}.log".format(tag, time.strftime("%Y-%m-%d", time.localtime()))
    LOG_FORMAT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s'
    # file_run_log = handlers.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0))
    file_run_log = handlers.RotatingFileHandler(filename, mode='a', maxBytes=1024 * 1024 * 10, backupCount=7, encoding="utf-8", delay=0)
    file_run_log.setLevel(level=level)
    file_run_log.setFormatter(logging.Formatter(LOG_FORMAT))

    file_error_log = logging.FileHandler(error_log)
    file_error_log.setLevel(level=logging.ERROR)
    file_error_log.setFormatter(logging.Formatter(LOG_FORMAT))
    
    logging.getLogger().addHandler(file_run_log)
    logging.getLogger().addHandler(file_error_log)
    
    formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
 
