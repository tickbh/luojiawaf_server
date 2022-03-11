##############################################
# 基于centos7构建python3运行环境
# 构建命令: 在Dockerfile文件目录下执行 docker build -t python-debian:3.8 . --progress plain
# 容器启动命令: docker run -itd --name python --restart always --privileged=true -v /root/dockers/python:/root/python -v /root/dockers/python/cron:/var/spool/cron python-centos:3.8 /usr/sbin/init
#$ dockerd --registry-mirror=https://registry.docker-cn.com
#docker run -itd --name python_sss python-centos:3.8 
# 进入容器：docker exec -it python /bin/bash
##############################################
FROM debian:11.2
COPY compose/django/sources.list /etc/apt/sources.list
RUN cat /etc/apt/sources.list
# RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update
RUN apt-get install wget -y
RUN apt-get install wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev -y


COPY compose/django/Python-3.8.10.tgz Python-3.8.10.tgz
RUN set -ex \
    # 预安装所需组件
    # && wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz \
    && tar -zxvf Python-3.8.10.tgz \
    && cd Python-3.8.10 \
    && ./configure prefix=/usr/local/python3 \
    && make -j 8 \
    && make install \
    && make clean \
    && rm -rf /Python-3.8.10*
# 设置默认为python3
RUN set -ex \
    # 配置默认为python3
    && ln -s /usr/local/python3/bin/python3.8 /usr/bin/python \
    && ln -s /usr/local/python3/bin/pip3 /usr/bin/pip

# 基础环境配置
RUN set -ex \
    # 修改系统时区为东八区
    && rm -rf /etc/localtime \
    && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# 支持中文
# RUN yum install kde-l10n-Chinese -y
# RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
# 更新pip版本

RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN /usr/local/python3/bin/python3.8 -m pip install --upgrade pip

RUN pip install uwsgi
# ENV LC_ALL zh_CN.UTF-8

RUN apt-get install -y gcc
WORKDIR /app

COPY compose/django/sqlite-autoconf-3360000.tar.gz /app/sqlite.tar.gz
RUN mkdir -p sqlite \
    && tar -zxvf sqlite.tar.gz -C sqlite --strip-components=1 \
    && rm -f sqlite.tar.gz \
    && ( \
    cd sqlite \
    && ./configure --prefix=/usr/local/ && make && make install  \
    ) \
    && rm -rf sqlite \
    && rm -f /usr/bin/sqlite3 \
    && ln -s /usr/local/bin/sqlite3 /usr/bin/sqlite3

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# RUN sed -i '1i export LD_LIBRARY_PATH="/usr/local/lib/"' ~/.bashrc \
#     && source ~/.bashrc

COPY compose/django/base.py /usr/local/python3/lib/python3.8/site-packages/django/db/backends/sqlite3/base.py
RUN pip install requests
RUN ln -s /usr/local/python3/bin/uwsgi /usr/bin/uwsgi


EXPOSE 8080
CMD ["uwsgi", "--ini", "uwsgi.ini"]