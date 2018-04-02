#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/25 12:01
# Author: Wakesy
# Email : chenxi@szsandstone.com

import json
import os
import traceback
from constant import *
from config import *
from s3_operator.s3_operator import S3Operator
from mq.consumer import MQConsumer
from utils import get_img_type, is_word_type
from background_process.convert_processor import ConvertProcesser
from background_process.check_processor import  CheckProcesser


class ProcessServer(MQConsumer):


    def  __init__(self, input_queue=''):

        super(ProcessServer, self).__init__(queue=input_queue)
        self.back_processer     = None  # 根据消息中的后处理类型确定
        self.check_processer    = CheckProcesser()
        self.convert_proccesser = ConvertProcesser()


    def call_back(self, channel, method, properties, body):
        '''重写Consumer的回调函数'''
        msg_args = json.loads(body)
        log.info("\nRecieved a msg: %s" % msg_args)
        if self.process(msg_args):
            channel.basic_ack(delivery_tag=method.delivery_tag)  # 后处理成功，确认消息使队列消息-1
            log.critical("Back process finished!")
        else:
            log.critical("Back process NOT finished!")


    def process(self, msg_args):
        try:

            s3_args = {}
            s3_args['access_key']  = S3_AK
            s3_args['secret_key']  = S3_SK
            s3_args['rgw_host']    = RGW_HOST
            s3_args['rgw_port']    = RGW_PORT
            s3_args['bucket_name'] = msg_args['bucket_name']
            object_key    = msg_args['object_key']
            action_type   = msg_args['action_type']
            new_file_name = msg_args['new_name']
            hit_action    = msg_args['hit_action']
            # 从s3下载，默认存放到DOWNLOAD_DIR中
            s3_operator   = S3Operator(**s3_args)
            s3_local_file = s3_operator.download_from_s3(object_key, DOWNLOAD_DIR)
            is_word_file  = is_word_type(s3_local_file)
            is_img_file   = True if get_img_type(s3_local_file) else False

            if action_type not in ALL_PROCESS_SUPPORT:
                log.warn("NOTICE: not support process type: %s" % action_type)
                return False

            elif action_type in CHECK_TYPES:
                # 审核目前只能为图片类型，并且审核类型和判定成功后的处理不能为空
                if not (is_img_file and hit_action):
                    log.warn("NOTICE: can only check images, unexpected args, file:%s, action_type:%s, new_file_name:%s"
                             % (s3_local_file, action_type, new_file_name))
                    return False
                self.back_processer = self.check_processer

            elif action_type in CONVERT_TYPES:
                # 转换目前只能为图片或者word文档类型，并且
                if not (is_word_file or is_img_file):
                    log.warn("NOTICE: can only convert images or word file, unexpected file :%s" % s3_local_file)
                    return False
                self.back_processer = self.convert_proccesser

            msg_args['s3_local_file'] = s3_local_file # 搭便车，多传两个参数过去
            msg_args['s3_operator']   = s3_operator
            if self.back_processer:
                # todo:考虑多线程或者协程，并发后处理
                if self.back_processer.back_process(**msg_args):
                    return True
        except Exception as error:
            log.error("Back process failed, error: %s, stop consuming." % traceback.format_exc())
            self.stop_recieve()
        return False



if __name__ == '__main__':

    try:
        process_server = ProcessServer(input_queue=S3_UPLOADED_MQ)
        process_server.start_recieve()
    except KeyboardInterrupt as error:
        log.info("Exit like a gentleman.error:%s" % error)



