#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/9 10:20
# Author: Wakesy
# Email : chenxi@szsandstone.com


import os
import configobj
from flask_restful import Resource, request
from api_config import START_API_CMD, STOP_API_CMD, api_logger as log
from utils import proc_command
from constant import BACK_PROC_CONF, DOWNLOAD_DIR
BP_CONF_NAME = "back_process.conf"


class BackProcess(Resource):

    def get(self):
        support_function = get_support_function()
        data = {"support_process": support_function}
        return result_formatter(data=data)


    def post(self):
        file = request.files.get('file')
        if file:
            log.info("Upload file success, filename: %s" % file.filename)
            message, success = update_bp_config(file)
        else:
            message, success = "Expected keyname:'file', type: 'tar.gz', contains: 'back_process.conf' ", 0
        return result_formatter(message=message, success=success)


    def delete(self):
        action_name = request.args.get("action_name")
        message, success = remove_support_function(action_name)
        return result_formatter(message=message, success=success)


def start_api():
    is_success, ret_msg = proc_command(START_API_CMD)
    print is_success, ret_msg

def stop_api():
    is_success, ret_msg = proc_command(STOP_API_CMD)
    print is_success, ret_msg


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
            message, success = "Succeeded updating back process config ", 1

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
            is_succeed, stdout = proc_command("tar -xzf %s -C %s" % (file_path, DOWNLOAD_DIR))
            if is_succeed:
                conf_path_in = os.path.join(file_path.strip('.tar.gz'), BP_CONF_NAME) # back_process.conf在压缩包里面
                conf_path_out = os.path.join(DOWNLOAD_DIR, BP_CONF_NAME)              # back_process.conf在压缩包外面
                if os.path.isfile(conf_path_in):
                    new_conf = conf_path_in
                elif os.path.isfile(conf_path_out):
                    new_conf = conf_path_out
                else:
                    message = "Failed update back process config, file doesn't contain 'back_process.conf'"
            else:
                message = "Failed update back process config, tar -xzf file failed: %s" % file_name
        else:
            message = "Failed updating back process config , expected file type: tar.gz"
    return new_conf, message


def remove_support_function(action_name):
    '''删除某个后处理功能'''
    message, success = "Succeeded removing function: %s" % action_name, 1
    try:
        bp_config = configobj.ConfigObj(BACK_PROC_CONF)
        del bp_config['back_process'][action_name]
        bp_config.write()
        log.info(message)
    except Exception as error:
        message, success = "Failed removing function: %s, error:%s" % (action_name, error), -1
        log.error(message)
    return message, success


def get_support_function():
    '''从后处理配置文件中，获取当前支持的功能'''
    support_function = []
    try:
        bp_config = configobj.ConfigObj(BACK_PROC_CONF)
        all_process_info = dict(bp_config['back_process'])
        # 根据后处理操作的类型分类
        support_function  = all_process_info.keys()
        log.info("support_function: %s" % support_function)
    except Exception as error:
        log.error("Failed getting process config ,error: %s" % error)
    return  support_function


def result_formatter(data=None, message="default success message", success=1):
    '''格式化请求返回,success:1 成功，0失败，-1异常'''
    result = {"message": message,
              "success": success,
              "data":data}
    return result



