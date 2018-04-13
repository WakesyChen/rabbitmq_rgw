#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/9 10:20
# Author: Wakesy
# Email : chenxi@szsandstone.com


import os
import configobj
from flask_restful import Resource, request
from config import log
from utils import proc_cmd
from constant import BACK_PROC_CONF


# 接收文件的存放目录
DOWNLOAD_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "file_recieved")
BP_CONF_NAME = "back_process.conf"

class BackProcess(Resource):


    def get(self):

        support_process = get_support_process()
        data = {"support_process": support_process}
        return result_formatter(data=data)


    def post(self):

        file = request.files.get('file')
        if file:
            log.info("Upload file success, filename: %s" % file.filename)
            message, success = update_bp_config(file)
        else:
            message, success = "Expected keyname:'file', type: 'tar.gz', contains: 'back_process.conf' ", 0

        return result_formatter(message=message, success=success)



#=============================功能代码================================

def update_bp_config(file):
    '''更新后处理的配置文件'''
    try:

        file_path = os.path.join(DOWNLOAD_DIR, file.filename)
        file.save(file_path)
        success = 0
        new_conf,  message = get_new_conf(file.filename, file_path)
        if os.path.isfile(new_conf):
            bp_obj_now  = configobj.ConfigObj(BACK_PROC_CONF)
            bp_obj_new  = configobj.ConfigObj(new_conf)
            bp_conf_new = bp_obj_new['back_process']     # 接收到的配置文件中的back_process配置
            bp_conf_now = bp_obj_now['back_process']     # 当前back_process配置文件信息
            bp_conf_now.clear()
            bp_conf_now.update(bp_conf_new)
            bp_obj_now.write()
            message, success = "Update back process config SUCCESS!", 1

    except Exception as error:
        log.error("Update back process config ERROR: %s" % error)
        message, success = "Update back process config ERROR: %s" % error, -1

    return message, success


def get_new_conf(file_name, file_path):
    '''从接收到的文件中，获取配置文件'''
    new_conf, message= '', ''
    if os.path.isfile(file_path):
        if file_name == BP_CONF_NAME:         # 接收的是配置文件
            new_conf = file_path
        elif file_path.endswith('.tar.gz'):   # 接收的是tar.gz压缩包
            is_succeed, stdout = proc_cmd("tar -xzf %s -C %s" % (file_path, DOWNLOAD_DIR))
            if is_succeed:
                conf_path_in = os.path.join(file_path.strip('.tar.gz'), BP_CONF_NAME) # back_process.conf在压缩包里面
                conf_path_out = os.path.join(DOWNLOAD_DIR, BP_CONF_NAME)              # back_process.conf在压缩包外面
                if os.path.isfile(conf_path_in):
                    new_conf = conf_path_in
                elif os.path.isfile(conf_path_out):
                    new_conf = conf_path_out
                else:
                    message = "Update back process config FAILED, file doesn't contain 'back_process.conf'"
            else:
                message = "Update back process config FAILED, tar -xzf file failed: %s" % file_name
        else:
            message = "Update back process config FAILED, expected file type: tar.gz"
    return new_conf, message


def get_support_process():
    '''从后处理配置文件中，获取当前支持的功能'''
    support_process = []
    try:
        bp_config = configobj.ConfigObj(BACK_PROC_CONF)
        all_process_info = dict(bp_config['back_process'])
        # 根据后处理操作的类型分类
        support_process  = all_process_info.keys()
        log.info("support_process: %s" % support_process)
    except Exception as error:
        log.error("get process config failed ,error: %s" % error)
    return  support_process


def result_formatter(data=None, message="default success message", success=1):
    '''格式化请求返回'''
    result = {"message": message,
              "success": success,
              "data":data}
    return result



