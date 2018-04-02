#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('../')
from copy import deepcopy
from base_processor import BaseProcesser
from mq.publisher import MQPublisher
from constant import *
from config import *
from utils import get_img_type, is_word_type
from tools.image_converter import convert_img2gif, convert_img2jpeg, convert_image_common
from tools.other_converter import convert_word2pdf


class ConvertProcesser(BaseProcesser):
    '''进行相关的转换处理'''

    def __init__(self):
        self.mq_publisher = MQPublisher(BACK_PROCESSED_MQ)


    def back_process(self, *args, **kwargs):
        super(ConvertProcesser, self).back_process(*args, **kwargs)
        self.s3_operator = kwargs.pop('s3_operator')     # S3Operator实例
        s3_local_file    = kwargs.pop('s3_local_file')   # 文件从s3下载后，保存在本地文件的路径,pop下车~~('_')~~
        object_key       = kwargs['object_key']          # 对象的s3主键（基于本地路径的部分路径）
        action_type      = kwargs['action_type']         # 具体转换动作，如'convert_to_pdf', 'check_is_sexy'
        new_file_name    = kwargs['new_name']            # 转换之后保存的格式，如 'filename.pdf'
        is_word_file   = is_word_type(s3_local_file)
        is_img_file    = True if get_img_type(s3_local_file) else False
        object_dir     = '/'.join(object_key.split('/')[:-1])      # 对象的目录
        local_dir      = '/'.join(s3_local_file.split('/')[:-1])   # 本地保存的目录
        generate_path  = os.path.join(local_dir, new_file_name)    # 转换生成的文件路径
        new_object_key = os.path.join(object_dir, new_file_name)   # 生成的文件对应s3上的key
        log.info('NOTICE: start to  %s' % action_type)

        if is_word_file and action_type == CONVERT_TO_PDF:
            # word文档转化为pdf
            generate_path = convert_word2pdf(s3_local_file, local_dir)
            if os.path.isfile(generate_path):
                if self.process_after_convert(action_type, new_object_key, generate_path, **kwargs):
                    return True

        if is_img_file and action_type == CONVERT_TO_GIF:
            # 图片类型转化为gif
            if convert_img2gif(s3_local_file, generate_path):
                if self.process_after_convert(action_type, new_object_key, generate_path, **kwargs):
                    return True

        if is_img_file and action_type == CONVERT_TO_JPEG:
            # 图片类型转化为jpeg
            if convert_img2jpeg(s3_local_file, generate_path):
                if self.process_after_convert(action_type, new_object_key, generate_path, **kwargs):
                    return True

        log.warn('NOTICE: %s  failed.' % action_type)
        return False


    def process_after_convert(self, action, new_object_key, generate_path, **kwargs):
        '''
        :param action: 执行的转换动作
        :param new_object_key: 转换生成的文件路径
        :param generate_path:  生成的文件对应s3上的key
        :param kwargs: 发送到mq的消息内容
        '''
        log.info('NOTICE: convert %s success, start to upload to s3 and publish msg...' % action)
        if self.s3_operator.upload_to_s3(new_object_key, generate_path):  # 上传到s3中
            msg_args = deepcopy(kwargs)
            msg_args['object_key'] = new_object_key
            self.mq_publisher.publish_msg(**msg_args)  # 上传新消息到处理成功的队列



if __name__ == '__main__':

    pass
    # proc = ConvertProcesser()
    # word_path = '/opt/python_projects/resources/common_files/中文的.doc'
    # pdf_path = '/opt/python_projects/resources/common_files/'
    # trans_cmd = CMD_WORD2PDF.format(word_path=word_path, generate_dir=pdf_path)
    # print trans_cmd



