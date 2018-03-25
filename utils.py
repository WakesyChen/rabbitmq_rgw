#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 11:55
# Author: Wakesy
# Email : chenxi@szsandstone.com


import time
import commands
import os
from config import log


def get_formated_time(timestamp=time.time()):

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))



def is_word_file(file_path):
    '''判断文件是否是word文档类型'''
    # todo:目前只是简单检查文件名后缀，实际需要检查文件内容来判断类型
    if not os.path.isfile(file_path):
        log.error('file not exists: %s' % file_path)
        return False

    if file_path.endswith('.doc') or file_path.endswith('.docx'):
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
            return True
    return False


if __name__ == '__main__':
    word_path = '/opt/python_projects/resources/docs/good_job.doc'
    pdf_path = '/opt/python_projects/resources/docs/'
    is_success = word_to_pdf(word_path, pdf_path)
    if is_success:
        log.info("word_to_pdf succeed!")
    else:
        log.info("word_to_pdf failed!")

