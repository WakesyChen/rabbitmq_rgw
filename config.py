#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 16:01
# Author: Wakesy
# Email : chenxi@szsandstone.com
import os
import traceback
import sys
import configobj
from constant import MQ_URL_FORMAT, CONFIG_FILE
import logging

'''从配置文件中读取的配置信息，供全局使用'''


log = None
# S3配置
S3_AK = ''
S3_SK = ''
S3_BUCKET = ''
RGW_HOST  = ''
RGW_PORT  = None
DOWNLOAD_DIR = ''          # 从s3上下载的文件，存放目录

# MQ配置
MQ_CONN_URL        = ''    # MQ连接URL参数
S3_UPLOADED_MQ     = ''    # s3上传的文件队列
S3_BACKUP          = False # 设置备份队列，保存接收到的所有消息
S3_EXCHANGE        = ''    # 上传的路由exchange
S3_EXCHANGE_TYPE   = ''    # 绑定相同exchange队列都会接收到消息
PROCESS_SUCCESS_MQ = ''    # 后处理成功的队列
PROCESS_FAILED_MQ  = ''    # 后处理失败的队列


# 后处理配置信息,back_process缩写BP
ALL_PROCESS_INFO      = None    # 所有后处理信息
ALL_PROCESS_SUPPORT = []        # 当前支持的后处理类型


'''初始化日志'''
def init_log_config():

    try:
        global log
        print "CONFIG_FILE: ", CONFIG_FILE
        process_conf_obj = configobj.ConfigObj(CONFIG_FILE, encoding='utf-8')
        log_conf = dict(process_conf_obj['logging'])
        log_name = log_conf['log_name']
        log_fmt = log_conf['log_format']
        log_level = log_conf['log_level']
        log_path = log_conf['log_path']
        # 设置控制台日志输出
        log = logging.getLogger(log_name)
        formatter = logging.Formatter(log_fmt)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        # 设置文件日志输出
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        log.setLevel(level=log_level)
        log.addHandler(file_handler)
        # 加上console打印，测试用
        log.addHandler(console_handler)
        log.info('init_log_config success')
        return True
    except :
        print "init_log_config failed, error:%s" % traceback.format_exc()
    return  False


'''获取mq配置'''
def get_mq_config():

    global MQ_CONN_URL, S3_UPLOADED_MQ, S3_BACKUP, S3_EXCHANGE
    global S3_EXCHANGE_TYPE, PROCESS_SUCCESS_MQ, PROCESS_FAILED_MQ
    try:
        process_conf_obj = configobj.ConfigObj(CONFIG_FILE, encoding='utf-8')
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
        PROCESS_FAILED_MQ  = rabbitmq_conf['process_success_mq']   # 后处理失败的队列
        log.info('get_mq_config success')
        return True
    except :
        log.error("get_mq_config failed, error:%s" % traceback.format_exc())
    return False


'''获取s3配置'''
def get_s3_config():

    global S3_AK, S3_SK, S3_BUCKET, RGW_HOST, RGW_PORT, DOWNLOAD_DIR
    try:
        process_conf_obj = configobj.ConfigObj(CONFIG_FILE, encoding='utf-8')
        s3_conf = process_conf_obj['s3']
        S3_AK = s3_conf['access_key']
        S3_SK = s3_conf['secret_key']
        S3_BUCKET = s3_conf['bucket_name']
        RGW_HOST = s3_conf['rgw_host']
        RGW_PORT = int(s3_conf['rgw_port'])
        DOWNLOAD_DIR = s3_conf['download_dir']  # 从s3上下载的文件，存放目录
        log.info('get_s3_config success')
        return True
    except :
        log.error("get_s3_config failed, error:%s" % traceback.format_exc())
    return False


'''获取back_process的信息'''
def get_bp_config():
    global ALL_PROCESS_INFO, ALL_PROCESS_SUPPORT
    try:
        process_conf_obj = configobj.ConfigObj(CONFIG_FILE, encoding='utf-8')
        ALL_PROCESS_INFO = dict(process_conf_obj['back_process'])
        ALL_PROCESS_SUPPORT = ALL_PROCESS_INFO.keys()
        log.info('get_bp_config success')
        log.info('ALL_PROCESS_SUPPORT:%s' % ALL_PROCESS_SUPPORT)
        return True
    except :
        log.error("get back_process config failed, error: %s" % traceback.format_exc())
    return False


# 初始化配置
if not init_log_config():
    sys.exit(-1)

if not get_mq_config():
    sys.exit(-2)

if not get_s3_config():
    sys.exit(-3)

if not get_bp_config():
    sys.exit(-4)

if __name__ == '__main__':

    # print globals()
    pass
    log = logging.getLogger('process')
    log.info("hellowword")
    log.warn("ewqeqweq21312321weqe")






