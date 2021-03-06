#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 16:01
# Author: Wakesy
# Email : chenxi@szsandstone.com
import os
import traceback
import sys
import configobj
from constant import MQ_URL_FORMAT, COMMON_CONF, ROOT_DIR
import logging

'''从配置文件中读取的配置信息，供全局使用'''

# S3配置
S3_AK = ''
S3_SK = ''
S3_BUCKET = ''
RGW_HOST  = ''
RGW_PORT  = None

# MQ配置
MQ_CONN_URL        = ''    # MQ连接URL参数
S3_UPLOADED_MQ     = ''    # s3上传的文件队列
S3_BACKUP          = False # 设置备份队列，保存接收到的所有消息
S3_EXCHANGE        = ''    # 上传的路由exchange
S3_EXCHANGE_TYPE   = ''    # 绑定相同exchange队列都会接收到消息
PROCESS_SUCCESS_MQ = ''    # 后处理成功的队列
PROCESS_FAILED_MQ  = ''    # 后处理失败的队列


'''初始化日志'''
# 设置控制台日志输出
log = logging.getLogger("process")
formatter = logging.Formatter("[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s]: %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
# 设置文件日志输出
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "log/process_server.log"))
file_handler.setFormatter(formatter)
log.setLevel(level=logging.INFO)
log.addHandler(file_handler)
# 加上console打印，测试用
log.addHandler(console_handler)


'''获取mq配置'''
def get_mq_config():
    try:
        global MQ_CONN_URL, S3_UPLOADED_MQ, S3_BACKUP, S3_EXCHANGE
        global S3_EXCHANGE_TYPE, PROCESS_SUCCESS_MQ, PROCESS_FAILED_MQ
        process_conf_obj = configobj.ConfigObj(COMMON_CONF, encoding='utf-8')
        rabbitmq_conf = process_conf_obj['rabbitmq']
        mq_config     = {'host'    : rabbitmq_conf['mq_host'],
                         'port'    : int(rabbitmq_conf['mq_port']),
                         'user'    : rabbitmq_conf['mq_user'],
                         'password': rabbitmq_conf['mq_pwd'],
                         'vhost'   : rabbitmq_conf['mq_vhost'],
                         'timeout' : rabbitmq_conf['mq_timeout']}

        MQ_CONN_URL = MQ_URL_FORMAT.format(**mq_config)
        S3_UPLOADED_MQ     = rabbitmq_conf['s3_uploaded_mq']       # s3上传的文件队列
        S3_BACKUP          = bool(rabbitmq_conf['s3_backup'])      # 设置备份队列，保存接收到的所有消息
        S3_EXCHANGE        = rabbitmq_conf['s3_exchange']          # 上传的路由exchange
        S3_EXCHANGE_TYPE   = rabbitmq_conf['s3_exchange_type']     # 绑定相同exchange队列都会接收到消息
        PROCESS_SUCCESS_MQ = rabbitmq_conf['process_success_mq']   # 后处理成功的队列
        PROCESS_FAILED_MQ  = rabbitmq_conf['process_failed_mq']    # 后处理失败的队列
        log.debug('get_mq_config success')
        return True
    except :
        log.error("get_mq_config failed, error:%s" % traceback.format_exc())
    return False


'''获取s3配置'''
def get_s3_config():
    try:
        global S3_AK, S3_SK, S3_BUCKET, RGW_HOST, RGW_PORT
        process_conf_obj = configobj.ConfigObj(COMMON_CONF, encoding='utf-8')
        s3_conf = process_conf_obj['s3']
        S3_AK = s3_conf['access_key']
        S3_SK = s3_conf['secret_key']
        S3_BUCKET = s3_conf['bucket_name']
        RGW_HOST = s3_conf['rgw_host']
        RGW_PORT = int(s3_conf['rgw_port'])
        log.debug('get_s3_config success')
        return True
    except :
        log.error("get_s3_config failed, error:%s" % traceback.format_exc())
    return False

if not get_mq_config():
    sys.exit(-2)

if not get_s3_config():
    sys.exit(-3)









