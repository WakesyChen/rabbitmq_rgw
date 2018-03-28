#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 11:55
# Author: Wakesy
# Email : chenxi@szsandstone.com

import commands
import os
import hashlib
from config import log
import imghdr
import gevent, gevent.subprocess
from constant import *


def GetFileMd5(file_path):
    '''根据文件内容生成md5值'''
    if not os.path.isfile(file_path):
        return
    myhash = hashlib.md5()
    f = file(file_path,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def get_img_type(file_path):
    '''智能识别图片，其他的返回None'''
    file_type = imghdr.what(file_path)
    if file_type in IMG_TYPES:
        log.info('file_type: %s,file_path:%s' % (file_type, file_path))
        return file_type
    return None


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


def proc_cmd2(logfunc, module, args, timeout=20, shell=False):
    logfunc("Module: %s, cmd: %s, begin", module, " ".join(args))
    proc = gevent.subprocess.Popen(args, shell=shell, close_fds=True,
                                   stdout=gevent.subprocess.PIPE,
                                   stderr=gevent.subprocess.PIPE)
    try:
        with gevent.Timeout(timeout, False):
            stdout, stderr = proc.communicate(input=None)

        if proc.returncode == None:
            raise Exception("Timeout %s" % timeout)

        logfunc("Module: %s, cmd: %s, retcode: %s, stdout: %s, stderr: %s",
                module, " ".join(args), proc.returncode, stdout, stderr)

        return proc.returncode, stdout, stderr
    except Exception, e:
        logfunc("Module: %s, cmd: %s, Exception: %s ", module, " ".join(args), str(e))
        if proc:
            proc.kill()
            proc.wait()
        raise




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
    iterate_over_directory_process(source_path, get_img_type)


















