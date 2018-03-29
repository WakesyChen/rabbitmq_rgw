#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
import sys
import re
sys.path.append('../')
from config import log
from copy import deepcopy
from base_processer import BaseProcesser
from mq.publisher import MQPublisher
from constant import *
from config import *
from utils import proc_cmd


class ConvertProcesser(BaseProcesser):
    '''进行相关的转换处理'''
    def __init__(self):
        self.mq_publisher= MQPublisher(BACK_PROCESSED_MQ)


    def back_process(self, *args, **kwargs):

        super(ConvertProcesser, self).back_process(*args, **kwargs)
        local_file_path = kwargs.pop('local_file_path') # 文件从s3下载后，保存在本地文件的路径
        s3_operator  = kwargs.pop('s3_operator') # S3Operator实例
        object_key   = kwargs['object_key']
        action_list  = kwargs['convert_type']['action_list']  # 具体转换动作，如[CONVERT_TO_PDF, CONVERT_TO_JPEG]
        newname_list = kwargs['convert_type']['newname_list'] # 转换之后保存的格式，如 ['filename.pdf', 'filename.gif']
        if not os.path.isfile(local_file_path):
            log.error("File not exists:%s" % local_file_path)
            return False
        if not action_list or not newname_list:
            log.error("Action_list or newname_list is empty, convertion is not needed.")
            return False

        types_mapped = dict(zip(action_list, newname_list))  # 类型转换后对应的文件名
        object_dir   = ''.join(object_key.split('/')[:-1])   # 对象的目录
        if CONVERT_TO_PDF in types_mapped:
            new_object_key = object_dir + types_mapped[CONVERT_TO_PDF]
            pdf_path = self.process_word2pdf(local_file_path)
            # 1、上传pdf到s3中
            if pdf_path and s3_operator.upload_to_s3(new_object_key, pdf_path):
                # 2、上传新消息到处理成功的队列
                msg_args = deepcopy(kwargs)
                msg_args['object_key'] = new_object_key
                self.mq_publisher.publish_msg(**msg_args)
                return True
        if CONVERT_TO_JPEG in types_mapped:

            new_object_key = object_dir + types_mapped[CONVERT_TO_JPEG]

            #todo:完成图片格式转换
            # self.convert_img_type(convert_img_type, )
            pass
        return False


    def process_word2pdf(self, local_file_path):
        '''格式转换word to pdf'''
        pdf_path = ''
        if not os.path.isfile(local_file_path):
            log.error('local_file_path not exists: %s' % local_file_path)
            return False
        if self.word_to_pdf(local_file_path, DOWNLOAD_DIR):
            partern = r'.doc[x]{0, 1}'
            replace = '.pdf'
            pdf_path = re.sub(partern, replace, local_file_path) # 生成的pdf路径
        return pdf_path


    def convert_img_type(self, target_type, img_path, result_path):
        '''图片格式转换'''
        if not os.path.isfile(img_path):
            log.error('local_file_path not exists: %s' % img_path)
            return False

        trans_cmd = "ffmpeg  -i  {0}  {1}".format(img_path, result_path)
        is_succeed, stdout = proc_cmd(trans_cmd)
        if is_succeed:
            log.info("Transfer Micro Word to Pdf successfully.")
            return True
        return False


    @staticmethod
    def is_word_file(file_path):
        '''判断文件是否是word文档类型'''
        if not os.path.isfile(file_path):
            return False
        has_doc_tag = file_path.endswith('.doc') or file_path.endswith('.docx')  # 根据后缀判断类型
        if has_doc_tag:
            log.info('file_type:[%s],file_path:%s' % ('ms_word', file_path))
            return True
        return False

    def word_to_pdf(self, word_path, generate_dir):
        '''将doc, docx转换为pdf，但需要提供window下的字体，否则可能会出现乱码
           若不指定pdf_path， 则在执行脚本的地方生成
        '''
        if self.is_word_file(word_path):
            trans_cmd = "soffice --headless --convert-to pdf  {0} --outdir  {1}".format(word_path, generate_dir)
            is_succeed, stdout = proc_cmd(trans_cmd)
            SUCCESS_TAG = "writer_pdf_Export"  # 执行成功，输出结果会带这个字段
            if is_succeed and SUCCESS_TAG in stdout:
                log.info("Transfer Micro Word to Pdf successfully.")
                return True
        return False


if __name__ == '__main__':

    proc = ConvertProcesser()
    word_path = '/opt/python_projects/resources/common_files/notes_1.doc'
    pdf_path = '/opt/python_projects/resources/common_files/'
    proc.back_process(word_path, pdf_path)
    proc.back_process(word_path, pdf_path)

