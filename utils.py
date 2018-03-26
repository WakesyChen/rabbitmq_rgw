#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 11:55
# Author: Wakesy
# Email : chenxi@szsandstone.com

import commands
import os
import hashlib
import magic
from config import log
from constant import IMG_TYPES, DOCUMENT_TYPES



def GetFileMd5(filename):
    '''根据文件内容生成md5值'''
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def get_file_type(file_path):
    '''返回文件类型'''
    file_type = magic.from_file(file_path, mime=True)
    log.debug(u'file_type:【%s】,file_path:%s' % (file_type, file_path))
    return file_type


def is_word_file(file_path):
    '''判断文件是否是word文档类型'''
    if not os.path.isfile(file_path):
        return False
    file_type = get_file_type(file_path)
    if file_type in DOCUMENT_TYPES:
        log.info(u'file_type:【%s】,file_path:%s' % (file_type, file_path))
        return True
    else:
        return False


def proc_cmd(cmd):
    '''执行指令'''
    is_succeed, output = False, ''
    try:
        ret_code, output = commands.getstatusoutput(cmd)
        is_succeed = True
        log.debug("Process cmd: [%s] successfully, ret_code: %s, ret_msg:%s" % (cmd, ret_code, output))
    except Exception as e:
        log.error("Process cmd: [%s] failed, error: %s" % (cmd, e))
    return  is_succeed, output


def word_to_pdf(word_path, pdf_path=''):
    '''将doc, docx转换为pdf，但需要提供window下的字体，否则可能会出现乱码
       不指定pdf_path， 则在执行脚本的地方生成
    '''
    if is_word_file(word_path):
        trans_cmd = "soffice --headless --convert-to pdf  {0} --outdir  {1}".format(word_path, pdf_path)
        is_succeed, output = proc_cmd(trans_cmd)
        SUCCESS_TAG = "writer_pdf_Export" # 执行成功，输出结果会带这个字段
        if is_succeed and SUCCESS_TAG in output:
            log.info("Transfer Micro Word to Pdf successfully.file")
            return True
    return False


def iterate_over_directory_process(source_path, process_method):
    '''遍历某个文件夹'''
    if os.path.isfile(source_path):
        process_method(source_path)

    elif os.path.isdir(source_path):
        for file_name in os.listdir(source_path):
            new_path = os.path.join(source_path, file_name)
            iterate_over_directory_process(new_path, process_method)


if __name__ == '__main__':

    # file_path = '/opt/python_projects/resources/docs/good_job.doc'
    # pdf_path = '/opt/python_projects/resources/docs/'
    # is_success = word_to_pdf(file_path, pdf_path)
    source_path = '/opt/python_projects/resources/common_files'
    iterate_over_directory_process(source_path, is_word_file)


















