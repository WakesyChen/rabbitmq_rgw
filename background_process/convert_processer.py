#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
import sys
import re
sys.path.append('../')
import imghdr
from copy import deepcopy
from base_processer import BaseProcesser
from mq.publisher import MQPublisher
from constant import *
from config import *
from utils import proc_cmd
import gevent
from gevent import monkey; gevent.monkey.patch_all()


class ConvertProcesser(BaseProcesser):
    '''进行相关的转换处理'''

    def __init__(self):
        self.mq_publisher = MQPublisher(BACK_PROCESSED_MQ)


    def back_process(self, *args, **kwargs):
        super(ConvertProcesser, self).back_process(*args, **kwargs)
        s3_local_file = kwargs.pop('s3_local_file')            # 文件从s3下载后，保存在本地文件的路径,pop下车~~('_')~~
        s3_operator   = kwargs.pop('s3_operator')              # S3Operator实例
        object_key    = kwargs['object_key']                   # 对象的s3主键（基于本地路径的部分路径）
        action_list   = kwargs['convert_type']['action_list']  # 具体转换动作，如['to_pdf', 'to_jpeg']
        newname_list  = kwargs['convert_type']['newname_list'] # 转换之后保存的格式，如 ['filename.pdf', 'filename.gif']

        if not (action_list and newname_list):
            log.error("Action_list or newname_list is empty, convertion is not needed.")
            return False

        types_mapped = dict(zip(action_list, newname_list))     # 类型转换后对应的文件名
        object_dir   = '/'.join(object_key.split('/')[:-1])      # 对象的目录
        local_dir    = '/'.join(s3_local_file.split('/')[:-1])   # 本地保存的目录
        is_word_file = self.is_word_file(s3_local_file)
        is_img_file  = True if self.get_img_type(s3_local_file) else False
        if not (is_word_file or is_img_file):
            log.debug('Only process word or image type files')
            return False
        converted_types = []  # 标识已经转换过的类型
        for action, new_file_name in types_mapped.items():
            new_object_key = os.path.join(object_dir, new_file_name)
            generate_path  = os.path.join(local_dir, new_file_name)       # 转换生成的文件路径
            # log.info("***new_object_key: %s, generate_path: %s" % (new_object_key, generate_path))
            if action not in ALL_PROCESS_SUPPORT:
                log.error('Not support back process: %s' % action)
                return False
            if action in converted_types:
                log.info('Already converted type:%s, jump' % action)
                continue

            if is_img_file and action in CONVERT_IMG_TYPES:
                if not self.convert_img_type(action, s3_local_file, generate_path):
                    return False

            if is_word_file and action == CONVERT_TO_PDF:
                # 直接在generate_dir目录下生成了pdf，以这个名字为准
                generate_path = self.convert_word2pdf(s3_local_file, local_dir)

            converted_types.append(action)
            if os.path.isfile(generate_path):   # 若成功生成了generate_path为名的文件，视为转换成功
                log.info('s3 upload file, key: %s,generate_path: %s ' % (new_object_key, generate_path))
                if s3_operator.upload_to_s3(new_object_key, generate_path): # 上传到s3中
                    msg_args = deepcopy(kwargs)
                    msg_args['object_key'] = new_object_key
                    self.mq_publisher.publish_msg(**msg_args)               # 上传新消息到处理成功的队列
                    return True
        log.info('ConvertProcesser is not successful.')
        return False


    def convert_word2pdf(self, s3_local_file, generate_dir):
        '''格式转换word to pdf'''
        pdf_path = ''
        if not os.path.isfile(s3_local_file):
            log.error('s3_local_file not exists: %s' % s3_local_file)
            return False
        if self.word_to_pdf(s3_local_file, generate_dir):
            log.info("Transfer Micro Word to Pdf successfully.")
            pdf_path = re.sub(r'.doc[x]{0, 1}', '.pdf', s3_local_file) # 生成的pdf路径
        return pdf_path


    def convert_img_type(self, target_type, img_path, generate_path):
        '''图片格式转换'''

        trans_cmd = "ffmpeg  -i  {0}  {1}".format(img_path, generate_path)
        is_succeed, stdout = proc_cmd(trans_cmd)
        if is_succeed and os.path.isfile(generate_path):
            log.info("Image [%s] convert [%s] successfully." % (img_path, target_type))
            return True
        else:
            log.info("Image [%s] convert [%s] failed." % (img_path, target_type))
            return False


    @staticmethod
    def is_word_file(file_path):
        '''判断文件是否是word文档类型'''
        if not os.path.isfile(file_path):
            log.error('s3_local_file not exists: %s' % file_path)
            return False
        has_doc_tag = file_path.endswith('.doc') or file_path.endswith('.docx')  # 根据后缀判断类型
        if has_doc_tag:
            log.info('file_type:ms_word,file_path:%s' %  file_path)
            return True
        return False


    def get_img_type(self, file_path):
        '''智能识别图片，其他的返回None'''
        try:
            if os.path.isfile(file_path):
                file_type = imghdr.what(file_path)
                if file_type in IMG_TYPES:
                    log.debug('file path: %s, file type: %s' % (file_path, file_type))
                    return file_type
        except Exception as e:
            log.debug('get_img_type failed, error: %s' % e)
        return None


    def word_to_pdf(self, word_path, generate_dir):
        '''将doc, docx转换为pdf，但需要提供window下的字体，否则可能会出现乱码
           若不指定pdf_path， 则在执行脚本的地方生成
        '''
        # if self.is_word_file(word_path):
        trans_cmd = "soffice --headless --convert-to pdf  {0} --outdir  {1}".format(word_path, generate_dir)
        is_succeed, stdout = proc_cmd(trans_cmd)
        SUCCESS_TAG = "writer_pdf_Export"  # 执行成功，输出结果会带这个字段
        if is_succeed and SUCCESS_TAG in stdout:
            return True
        return False


if __name__ == '__main__':

    proc = ConvertProcesser()
    word_path = '/opt/python_projects/resources/common_files/notes_1.doc'
    pdf_path = '/opt/python_projects/resources/common_files/'
    proc.back_process(word_path, pdf_path)
    proc.back_process(word_path, pdf_path)

