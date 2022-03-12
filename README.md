## 洛甲WAF,中控后端服务器
中控服务器, 管理各个前端服务器

### 安装docker
```
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```
安装docker-compose
```
python3 -m pip install --upgrade pip
pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
pip config set install.trusted-host mirrors.aliyun.com
pip3 install docker-compose
```

#### 构建docker
进入到compose/full, 运行docker-compose build
然后运行docker-compose up -d启动程序

#### 本地调试
安装相应的python环境,
```
pip install -r requirements.txt
```
运行django和task_main.py


#### 参数配置说明
```
limit_ip:all 值 为 aaa/bbbb 均为数字, aaa表示桶数, bbbb超出桶延时请求的最大数
limit_uri:all 值 为 aaa/bbbb 均为数字, aaa表示桶数, bbbb超出桶延时请求的最大数
limit_ip:ip 对单IP进行限制 为 aaa/bbbb 均为数字, aaa表示桶数, bbbb超出桶延时请求的最大数
limit_uri:ip 对单IP进行限制 为 aaa/bbbb 均为数字, aaa表示桶数, bbbb超出桶延时请求的最大数

not_wait_forbidden_ratio 默认为0.9, 规则判断错序的比例
not_wait_forbidden_min_len 默认为20, 规则判断错序最小值

min_all_visit_times 默认为20, 规则判定总访问次数的起点值
max_visit_idx_num 默认为2, 排序最高的前两台占比
max_visit_ratio 默认为0.85, 即前2条访问量占总比值的比例

default_forbidden_time 默认为600即10分钟, 禁用ip的默认时长

white_ip_check 白名单检查 on 为开启
forbidden_ip_check IP禁止检查 on 为开启
limit_ip_check IP限制检查 on 为开启
limit_uri_check uri限制检查 on 为开启
white_url_check 白url检查 on 为开启

post_attack_check post参数攻击请求on 为开启
url_args_attack urls参数攻击请求on 为开启

random_record_value 随机记录的值, 100%则填10000
```


## 💬 社区交流

##### QQ交流群

加QQ群号 684772704, 验证信息: luojiawaf
