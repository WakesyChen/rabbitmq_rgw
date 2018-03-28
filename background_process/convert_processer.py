#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
import sys
sys.path.append('../')
from config import log
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
        local_file_path = kwargs['local_file_path'] # 文件从s3下载后，保存在本地文件的路径
        object_key = kwargs['object_key'] # 文件从s3下载后，保存在本地文件的路径
        s3_operator = kwargs['s3_operator'] # S3Operator实例
        action_list = kwargs['convert_type']['action_list']  # 具体转换动作，如[CONVERT_TO_PDF, CONVERT_TO_JPEG]
        newname_list = kwargs['convert_type']['newname_list'] # 转换之后保存的格式，如 ['filename.pdf', 'filename.gif']
        if not os.path.isfile(local_file_path):
            log.error("File not exists:%s" % local_file_path)
            return False
        if not action_list or not newname_list:
            log.error("Action_list or newname_list is empty, convertion is not needed.")
            return False
        types_mapped = dict(zip(action_list, newname_list))  # 类型转换后对应的文件名
        object_dir = ''.join(object_key.split('/')[:-1])  # 对象的目录
        if CONVERT_TO_PDF in types_mapped:
            new_object_key = object_dir + types_mapped[CONVERT_TO_PDF]
            # todo:发送到消息队列的消息内容，要进行调整
            self.process_word2pdf(s3_operator, local_file_path, kwargs)
        elif CONVERT_TO_JPEG in types_mapped:
            new_object_key = object_dir + types_mapped[CONVERT_TO_JPEG]
        else:
            new_object_key = object_key # 其他暂设为不变


    def process_word2pdf(self, s3_operator, local_file_path, msg_args):

        '''格式转换word to pdf'''
        if not os.path.isfile(local_file_path):
            log.error('local_file_path not exists: %s' % local_file_path)
            return False
        if self.word_to_pdf(local_file_path, DOWNLOAD_DIR):
            obj_key = msg_args['obj_key']
            new_obj_key, new_file_path = self.get_new_path(obj_key, local_file_path)
            # 上传pdf到s3中
            if s3_operator.upload_to_s3(new_obj_key, new_file_path):
                # 上传新消息到处理成功的队列
                msg_args['obj_key'] = new_obj_key
                msg_args['file_path'] = new_file_path
                msg_args['old_event_id'] = msg_args['event_id']  # 记录之前的事件id
                self.mq_publisher.publish_msg(**msg_args)
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


    def get_new_path(self, obj_key, local_file_path):
        '''
        :param obj_key: 当前的对象在s3中的key值
        :param local_file_path: 该对象从s3下载到本地，存储的实际路径
        :return:new_key:根据对象处理过后的类型，修改key后缀生成的新key
        :return:new_file_path:对象在本地处理后，存储的实际路径
        '''

        if obj_key.endswith('.doc'):
            new_key = obj_key.replace('.doc', '.pdf')
            new_file_path = local_file_path.replace('.doc', '.pdf')
        elif obj_key.endswith('.docx'):
            new_key = obj_key.replace('.docx', '.pdf')
            new_file_path = local_file_path.replace('.docx', '.pdf')
        else:
            new_key = obj_key
            new_file_path = local_file_path
        return new_key, new_file_path


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


if __name__ == '__main__':

    proc = ConvertProcesser()
    word_path = '/opt/python_projects/resources/common_files/notes_1.doc'
    pdf_path = '/opt/python_projects/resources/common_files/'
    proc.back_process(word_path, pdf_path)
    proc.back_process(word_path, pdf_path)

