#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/25 12:01
# Author: Wakesy
# Email : chenxi@szsandstone.com

import json
import traceback
from constant import *
from config import *
from s3_operator.s3_operator import S3Operator
from mq.consumer import MQConsumer
from background_process.convert_processer import ConvertProcesser


class ProcessServer(MQConsumer):


    def  __init__(self, input_queue=''):

        super(ProcessServer, self).__init__(queue=input_queue)
        self.back_processer  = None  # 根据消息中的后处理类型确定
        self.check_processer = ConvertProcesser()
        self.convert_proccesser = ConvertProcesser()



    def call_back(self, channel, method, properties, body):
        '''重写Consumer的回调函数'''
        msg_args = json.loads(body)
        obj_key = msg_args.get('obj_key', '')
        event_id = msg_args.get('event_id', '')
        if self.process(msg_args):
            channel.basic_ack(delivery_tag=method.delivery_tag)  # 后处理成功，确认消息使队列消息-1
            log.info("Back process successed! Consumer confirmed a message, obj_key: %s, event_id:%s" % (obj_key, event_id))
        else:
            log.info("Back process has'nt been done, obj_key: %s, event_id:%s" % (obj_key, event_id))


    def process(self, msg_args):
        try:
            s3_args = {}
            s3_args['access_key']  = msg_args['access_key']
            s3_args['secret_key']  = msg_args['secret_key']
            s3_args['bucket_name'] = msg_args['bucket_name']
            s3_args['rgw_host']    = msg_args['rgw_host']
            s3_args['rgw_port']    = msg_args['rgw_port']
            action_type = msg_args['action_type']
            object_key  = msg_args['object_key']
            # 1、从s3下载，默认存放到DOWNLOAD_DIR中
            s3_operator = S3Operator(**s3_args)
            local_file_path = s3_operator.download_from_s3(object_key, DOWNLOAD_DIR)

            # 2、根据消息中的处理类型，进行对应的后处理
            if action_type == CHECK_PROCESS:
                self.back_processer = self.check_processer
            elif action_type == CONVERT_PROCESS:
                self.back_processer = self.convert_proccesser

            # 搭便车，多传两个参数过去
            msg_args['local_file_path'] = local_file_path
            msg_args['s3_operator'] = s3_operator
            if self.back_processer:
                if self.back_processer.back_process(**msg_args):
                    return True
        except:
            self.stop_recieve()
            log.critical("Back process failed, error: %s, stop consuming." % traceback.format_exc())
        return False


if __name__ == '__main__':

    try:
        process_server = ProcessServer(input_queue=S3_UPLOADED_MQ)
        process_server.start_recieve()
    except KeyboardInterrupt as error:
        log.info("Exit like a gentleman.error:%s" % error)



