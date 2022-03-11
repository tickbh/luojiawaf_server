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
