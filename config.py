#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 16:01
# Author: Wakesy
# Email : chenxi@szsandstone.com

import logging

#==========================日志设置===============================

default_fmt = "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s"
default_level = logging.INFO
default_logpath = '/opt/python_project/tupu_process/log/rabbitmq.log'

log = logging.getLogger('root')
log.setLevel(level=default_level)
formatter = logging.Formatter(default_fmt)

# 设置 控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

#设置 文件日志写入
# file_handler = logging.FileHandler(filename=default_logpath)
# file_handler.setFormatter(formatter)
# log.addHandler(file_handler)


#===========================MQ配置=================================
RABBITMQ_CONF = {'host': '10.10.7.151',
                 'port': 5672,
                 'user': 'root',
                 'password': 'sandstone',
                 'vhost': 'sdsom',
                 'timeout': 5}

# " amqp://username:password@host:port/<virtual_host>[?query-string]"
MQ_CONN_URL = "amqp://{user}:{password}@{host}:{port}/{vhost}?socket_timeout={timeout}".format(**RABBITMQ_CONF)


#===========================S3配置=================================

S3_AK = 'A8M0F3P0DM1RAGY6P3NE'
S3_SK = '9NCO0iJHiRNXodq40gG89QWGlKe7xtAoaggPZoTC'
S3_BUCKET = 'doc_test'
BUCKET_PREF = '' # 对象前缀，作为key的一部分
#RGW服务IP
RGW_HOST = "10.10.7.151"
#RGW服务端口号
RGW_PORT = 9465

UPLOAD_PROCESS_NUM = 5
MULTI_THREAD_NUM = 5
CHUNK_SIZE = 4*1024*1024
# 大于50M分片上传
MULTI_UPLOAD_THRESHOLD_SIZE = 50*1024*1024


# 上传的目录
UPLOAD_DIR = "/opt/python_projects/resources/"
#下载的目录
DOWNLOAD_DIR = '/opt/python_projects/resources/download'



