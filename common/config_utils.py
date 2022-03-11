
import yaml, traceback, os
import logging
yaml.warnings({'YAMLLoadWarning':False}) 

curpath = os.path.dirname(__file__)

_config_data = None
def init_config():
    global _config_data
    try:
        print("config_path==" + curpath + '/../config_local.yaml')
        f=open(curpath + '/../config_local.yaml','r',encoding='utf-8')      #打开yaml文件
        cfg=f.read()
        _config_data=yaml.full_load(cfg)     #将数据转换成python字典行驶输出，存在多个文件时，用load_all，单个的时候load就可以
        f.close()
        logging.info("-----loaded local config------")
        return
    except Exception as e:
        logging.warning("-----not found local config------")
        pass

    f=open(curpath + '/config.yaml','r',encoding='utf-8')      #打开yaml文件
    cfg=f.read()
    _config_data=yaml.full_load(cfg)     #将数据转换成python字典行驶输出，存在多个文件时，用load_all，单个的时候load就可以
    f.close()

def _ensure_config_exist():
    global _config_data
    if not _config_data:
        init_config()
    
def get_redis_db():
    _ensure_config_exist()
    global _config_data
    return _config_data["redis_db"]

def get_task_redis_db():
    _ensure_config_exist()
    global _config_data
    return _config_data["task_redis"]
