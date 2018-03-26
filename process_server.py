#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/25 12:01
# Author: Wakesy
# Email : chenxi@szsandstone.com

import json
import time
import os
from config import log
import traceback
from constant import DOWNLOAD_DIR
from s3_operator.s3_operator import S3Operator
from mq.publisher import MQPublisher
from mq.consumer import MQConsumer
from utils import word_to_pdf
'''
从rabbitmq队列里面获取消息，然后访问s3获取文件；-----consumer
拿到文件后进行后处理，若处理成功，则推到另一队列 -----publisher
'''

class ProcessServer(MQConsumer):

    def  __init__(self, input_queue='', output_queue=''):
        super(ProcessServer, self).__init__(queue=input_queue)
        self.mq_publisher = MQPublisher(output_queue) # 记录后处理成功的消息


    def call_back(self, channel, method, properties, body):
        '''重写Consumer的回调函数'''
        msg_args = json.loads(body)
        obj_key = msg_args.get('obj_key', '')
        event_id = msg_args.get('event_id', '')
        if self.back_process(msg_args):
            channel.basic_ack(delivery_tag=method.delivery_tag)  # 后处理成功，确认消息使队列消息-1
            log.info("Back process successed! Consumer confirmed a message, obj_key: %s, event_id:%s" % (obj_key, event_id))
        else:
            log.info("Back process has'nt been done, obj_key: %s, event_id:%s" % (obj_key, event_id))


    def back_process(self, msg_args):
        '''后处理的总函数，目前支持的后处理有：
        1、将word文档转化成pdf
        '''
        try:
            s3_args = {}
            s3_args['rgw_host'] = msg_args.get('rgw_host', '')
            s3_args['rgw_port'] = msg_args.get('rgw_port', '')
            s3_args['s3_ak'] = msg_args.get('s3_ak', '')
            s3_args['s3_sk'] = msg_args.get('s3_sk', '')
            s3_args['s3_bucket'] = msg_args.get('s3_bucket', '')
            obj_key = msg_args['obj_key']
            s3_operator = S3Operator(**s3_args)

            # 从s3下载，默认存放到DOWNLOAD_DIR中
            local_file_path = s3_operator.download_from_s3(obj_key, DOWNLOAD_DIR)
            # 1、格式转换word to pdf
            if self.process_word2pdf(s3_operator, local_file_path, msg_args):
                return True

        except Exception as e:
            self.stop_recieve()
            log.critical("Back process failed, error: %s, stop consuming." % traceback.format_exc())
        return False


    def process_word2pdf(self, s3_operator, local_file_path, msg_args):
        '''格式转换word to pdf'''
        if not os.path.isfile(local_file_path):
            log.error('local_file_path not exists: %s' % local_file_path)
            return False

        if word_to_pdf(local_file_path, DOWNLOAD_DIR):
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




if __name__ == '__main__':
    try:
        process_server = ProcessServer(input_queue='s3_uploaded', output_queue='back_processed')
        process_server.start_recieve()
    except KeyboardInterrupt as error:
        log.info("Exit like a gentleman.error:%s" % error)



