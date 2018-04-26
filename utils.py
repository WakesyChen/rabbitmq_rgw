#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 11:55
# Author: Wakesy
# Email : chenxi@szsandstone.com

import commands
import imghdr
import time
import subprocess
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from config import log
from constant import IMG_TYPES, CONVERT_POSTFIX


def proc_command(cmd="ping www.baidu.com", timeout=60):
    '''
    :param cmd: 执行的指令
    :param timeout: 指令的超时时间
    :return: is_succeed 执行是否执行成功，stdout指令结果的输出
    '''
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        time_begin = time.time()
        while True:
            if p.poll() is not None:  # poll执行完返回0，未执行完返回None
                break
            time_passed = time.time() - time_begin
            if time_passed > timeout:
                p.terminate()
                raise Exception("Timeout exception")
            time.sleep(0.1)
        is_succeed, stdout = True, p.stdout.read()  # 执行成功
        log.info("Succeeded excuting cmd:[%s], ret_msg:%s" % (cmd, stdout))
    except Exception as err:
        log.error("Failed excuting cmd:[%s], error:%s" % (cmd, err))
        is_succeed, stdout = False, "Failed excuting cmd:%s, error:%s" % (cmd, err)
    return is_succeed, stdout


def is_word_type(file_path):
    '''判断文件是否是word文档类型'''
    if not os.path.isfile(file_path):
        log.warn('s3_local_file not exists: %s' % file_path)
        return False
    has_doc_tag = file_path.endswith('.doc') or file_path.endswith('.docx')  # 根据后缀判断类型
    if has_doc_tag:
        log.debug('file_type:ms_word,file_path:%s' %  file_path)
        return True
    return False


def get_img_type( file_path):
    '''智能识别图片，其他的返回None'''
    try:
        if os.path.isfile(file_path):
            file_type = imghdr.what(file_path)
            if file_type in IMG_TYPES:
                # log.debug('file path: %s, file type: %s' % (file_path, file_type))
                return file_type
    except Exception as e:
        log.debug('get_img_type failed, error: %s' % e)
    return None


def iterate_over_directory_process(source_path, process_method):
    '''遍历某个文件夹'''
    if os.path.isfile(source_path):
        process_method(source_path)

    elif os.path.isdir(source_path):
        for file_name in os.listdir(source_path):
            new_path = os.path.join(source_path, file_name)
            iterate_over_directory_process(new_path, process_method)



def get_new_name_by_type(local_file_path, convert_type):
    # 根据文件转换类型，输出文件名
    file_name = local_file_path.split("/")[-1]
    new_file_name = file_name
    if convert_type in CONVERT_POSTFIX:
        new_postfix = CONVERT_POSTFIX[convert_type]
        paths_list = file_name.split('.')
        paths_list[-1] = new_postfix     # 替换之前的后缀
        new_file_name = ".".join(paths_list)

    return new_file_name


if __name__ == '__main__':
    is_success, ret_msg = proc_command("ipconfig",timeout=5)
    print "is_success:%s, ret_msg:%s" % (is_success, ret_msg)


















