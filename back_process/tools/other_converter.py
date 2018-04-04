#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/2 12:02
# Author: Wakesy
# Email : chenxi@szsandstone.com
import os
import re
from constant import CMD_WORD2PDF
from utils import proc_cmd
from config import log



def convert_word2pdf(word_path, generate_dir):
    '''格式转换word to pdf
       将doc, docx转换为pdf，但需要提供window下的字体，否则pdf文件内容可能会出现乱码
       若不指定generate_dir，则在执行脚本的地方生成;
       指定generate_dir，则在generate_dir下生成和word文件同名，后缀为pdf的文件
    '''
    pdf_path = ''
    if not os.path.isfile(word_path):
        log.warn(" convert_word2pdf, word_path not exists: %s" % word_path)
        return pdf_path
    try:
        trans_cmd = CMD_WORD2PDF.format(word_path=word_path, generate_dir=generate_dir)
        is_succeed, stdout = proc_cmd(trans_cmd)
        SUCCESS_TAG = "writer_pdf_Export"  # 执行成功，输出结果会带这个字段
        if is_succeed and SUCCESS_TAG in stdout:
            pdf_path = re.sub(r'.doc[x]{0,1}', '.pdf', word_path) # 生成的pdf路径
            log.debug("convert_word2pdf successfully, generate pdf: %s" % pdf_path)
    except Exception as error:
        log.error("convert_word2pdf failed, file: %s , error:%s" % (word_path, error))
    return pdf_path