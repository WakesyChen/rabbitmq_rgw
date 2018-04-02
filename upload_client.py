#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/24 19:43
# Author: Wakesy
# Email : chenxi@szsandstone.com

from s3_operator.s3_operator import S3Operator
from mq.publisher import MQPublisher
from config import *
from constant import *
from random import randint
import re
from utils import iterate_over_directory_process
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
'''
上传文件到s3，并记录到rabbitmq队列------消息publisher
'''


class UploadClient(object):

    def __init__(self, queue="", exchange="", exchange_type="", is_backup=False):

        self.s3_publisher = MQPublisher(queue=queue, exchange=exchange, exchange_type=exchange_type, is_backup=is_backup)
        self.s3_operator = S3Operator()
        log.info('init upload client successfully!')


    def upload_file_to_s3(self, file_path):
        cloud_path = '/'.join(file_path.split('/')[3:]) # for test

        if self.s3_operator:
            is_success = self.s3_operator.upload_to_s3(cloud_path, file_path)
            if is_success:
                self.publish_msg_to_queue(self.s3_publisher, cloud_path)
                return True
        return False


    def publish_msg_to_queue(self, publisher, cloud_path):
        '''推送消息到s3上传的队列'''
        if publisher and isinstance(publisher, MQPublisher):
            msg = {}
            file_name = (cloud_path.split('/'))[-1]
            doc_file  = re.sub(r'.doc[x]{0,1}', '.pdf', file_name)
            img_file  = re.sub((file_name.split('.'))[-1], 'gif', file_name)

            convert_type = {}
            convert_type['action_list']  = ['to_pdf', 'to_gif']
            convert_type['newname_list'] = [doc_file, img_file]
            msg['convert_type'] = convert_type
            msg['object_key']   = cloud_path
            msg['bucket_name']  = S3_BUCKET
            msg['access_key']   = S3_AK
            msg['secret_key']   = S3_SK
            msg['rgw_host']     = RGW_HOST
            msg['rgw_port']     = RGW_PORT
            msg['action_type']  =  CONVERT_PROCESS
            msg['newname_list'] =  CONVERT_PROCESS
            publisher.publish_msg(**msg)


if __name__ == '__main__':

    upload_client = UploadClient(queue=S3_UPLOADED_MQ, exchange=S3_EXCHANGE, exchange_type=S3_EXCHANGE_TYPE, is_backup=S3_BACKUP)
    upload_dir = "/opt/python_projects/resources/common_files"
    iterate_over_directory_process(upload_dir, upload_client.upload_file_to_s3)










