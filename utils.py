#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 11:55
# Author: Wakesy
# Email : chenxi@szsandstone.com

import commands
import os
from config import log
# import gevent, gevent.subprocess
import sys
import imghdr
reload(sys)
sys.setdefaultencoding('utf-8')
from constant import IMG_TYPES

def proc_cmd(cmd):
    '''执行指令'''
    is_succeed, stdout = False, ''
    try:
        ret_code, stdout = commands.getstatusoutput(cmd)
        is_succeed = True
        log.debug("Process cmd: [%s] successfully, ret_code: %s, ret_msg:%s" % (cmd, ret_code, stdout))
    except Exception as e:
        log.error("Process cmd: [%s] failed, error: %s" % (cmd, e))
    return  is_succeed, stdout


# def proc_cmd2(logfunc, module, args, timeout=20, shell=False):
#     logfunc("Module: %s, cmd: %s, begin", module, " ".join(args))
#     proc = gevent.subprocess.Popen(args, shell=shell, close_fds=True,
#                                    stdout=gevent.subprocess.PIPE,
#                                    stderr=gevent.subprocess.PIPE)
#     try:
#         with gevent.Timeout(timeout, False):
#             stdout, stderr = proc.communicate(input=None)
#
#         if proc.returncode == None:
#             raise Exception("Timeout %s" % timeout)
#
#         logfunc("Module: %s, cmd: %s, retcode: %s, stdout: %s, stderr: %s",
#                 module, " ".join(args), proc.returncode, stdout, stderr)
#
#         return proc.returncode, stdout, stderr
#     except Exception, e:
#         logfunc("Module: %s, cmd: %s, Exception: %s ", module, " ".join(args), str(e))
#         if proc:
#             proc.kill()
#             proc.wait()
#         raise
#

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


if __name__ == '__main__':

    source_path = '/opt/python_projects/resources/common_files'
    # iterate_over_directory_process(source_path, get_img_type)


















