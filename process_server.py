#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/25 12:01
# Author: Wakesy
# Email : chenxi@szsandstone.com

import json
import time
import os
from config import log, DOWNLOAD_DIR
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
        if self.back_process(msg_args):
            channel.basic_ack(delivery_tag=method.delivery_tag)  # 后处理成功，确认消息使队列消息-1
            log.info("Back process successed! Consumer confirmed a message: %s" % str(msg_args))
        else:
            log.info("Back   process  failed! Consumer denied a message: %s" % str(msg_args))


    def back_process(self, msg_args):
        time.sleep(3)
        try:
            s3_args = {}
            s3_args['rgw_host'] = msg_args.get('rgw_host', '')
            s3_args['rgw_port'] = msg_args.get('rgw_port', '')
            s3_args['s3_ak'] = msg_args.get('s3_ak', '')
            s3_args['s3_sk'] = msg_args.get('s3_sk', '')
            s3_args['s3_bucket'] = msg_args.get('s3_bucket', '')
            s3_operator = S3Operator(**s3_args)
            obj_key = msg_args['obj_key']
            # 1、从s3下载，默认存放到DOWNLOAD_DIR中
            download_dir = DOWNLOAD_DIR
            local_file_path = s3_operator.download_from_s3(obj_key, download_dir)
            if os.path.isfile(local_file_path):
                # 2、格式转换word to pdf
                if word_to_pdf(local_file_path, download_dir):
                    # 3、上传pdf到s3中
                    new_obj_key, new_file_path = self.get_new_path(obj_key, local_file_path)
                    if s3_operator.upload_to_s3(new_obj_key, new_file_path):
                        # 4、上传消息到处理成功的队列
                        msg_args['obj_key'] = new_obj_key
                        msg_args['file_path'] = new_file_path
                        msg_args['old_event_id'] = msg_args['event_id'] # 记录之前的事件id
                        self.mq_publisher.publish_msg(**msg_args)
                        log.info("====================processed success===================")
                        return True
        except Exception as e:
            self.stop_recieve()
            log.critical("Back process failed, error: %s, stop consuming." % e)
        return False


    def get_new_path(self, obj_key, local_file_path):
        # todo:正则优化

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
        process_server = ProcessServer(input_queue='s3_success', output_queue='back_processed')
        process_server.start_recieve()
    except KeyboardInterrupt as error:
        log.info("Exit like a gentleman.error:%s" % error)



