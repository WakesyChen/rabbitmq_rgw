#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 16:01
# Author: Wakesy
# Email : chenxi@szsandstone.com
import os
import configobj
import traceback
import logging
#对外提供的log
log = logging.getLogger('process')

config_file = os.path.abspath('./back_process.conf')
process_conf_obj = configobj.ConfigObj(config_file, encoding='utf-8')



def init_log(process_conf_obj):
    log_conf = dict(process_conf_obj['logging'])
    log_fmt = log_conf['LOG_FORMAT']
    log_level = log_conf['LOG_LEVEL']
    log_path = log_conf['LOG_PATH']
    # 设置控制台日志输出
    formatter = logging.Formatter(log_fmt)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # 设置文件日志输出
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    log.setLevel(level=log_level)

    log.addHandler(file_handler)
    log.addHandler(console_handler)  # 测试加上console打印

try:
    '''从配置文件取出的信息'''

    #==========================日志设置===============================



    #===========================S3配置=================================
    s3_conf = process_conf_obj['s3']

    S3_AK = s3_conf['S3_AK']
    S3_SK = s3_conf['S3_SK']
    S3_BUCKET = s3_conf['S3_BUCKET']
    RGW_HOST  = s3_conf['RGW_HOST']
    RGW_PORT  = int(s3_conf['RGW_PORT'])
    DOWNLOAD_DIR = s3_conf['DOWNLOAD_DIR'] #从s3上下载的文件，存放目录

    #===========================MQ配置=================================
    rabbitmq_conf = process_conf_obj['rabbitmq']
    mq_config     = {'host'    : rabbitmq_conf['MQ_HOST'],
                     'port'    : int(rabbitmq_conf['MQ_PORT']),
                     'user'    : rabbitmq_conf['MQ_USER'],
                     'password': rabbitmq_conf['MQ_PWD'],
                     'vhost'   : rabbitmq_conf['MQ_VHOST'],
                     'timeout' : rabbitmq_conf['MQ_TIMEOUT']}

    mq_conn_url = rabbitmq_conf['MQ_CONN_URL']
    MQ_CONN_URL = mq_conn_url.format(**mq_config)

    S3_UPLOADED_MQ     = rabbitmq_conf['S3_UPLOADED_MQ']       # s3上传的文件队列
    S3_BACKUP          = bool(rabbitmq_conf['S3_BACKUP'])      # 设置备份队列，保存接收到的所有消息
    S3_EXCHANGE        = rabbitmq_conf['S3_EXCHANGE']          # 上传的路由exchange
    S3_EXCHANGE_TYPE   = rabbitmq_conf['S3_EXCHANGE_TYPE']     # 绑定相同exchange队列都会接收到消息
    PROCESS_SUCCESS_MQ = rabbitmq_conf['PROCESS_SUCCESS_MQ']   # 后处理成功的队列
    PROCESS_FAILED_MQ  = rabbitmq_conf['PROCESS_SUCCESS_MQ']   # 后处理失败的队列
except:
    print "Config file error: %s" % traceback.format_exc()

if __name__ == '__main__':



    pass
    log = logging.getLogger('process')
    log.info("hellowword")
    log.warn("ewqeqweq21312321weqe")






