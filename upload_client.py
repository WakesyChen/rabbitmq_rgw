#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/24 19:43
# Author: Wakesy
# Email : chenxi@szsandstone.com

from s3_operator.s3_operator import S3Operator
from mq.publisher import MQPublisher
from config import *
from utils import iterate_over_directory_process

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
                self.publish_msg_to_queue(self.s3_publisher, file_path, cloud_path)
                return True
        return False


    def publish_msg_to_queue(self, publisher, file_path, cloud_path):
        msg = {}
        if publisher and isinstance(publisher, MQPublisher):
            msg['file_path'] = file_path
            msg['obj_key'] = cloud_path
            msg['rgw_host'] = RGW_HOST
            msg['rgw_port'] = RGW_PORT
            msg['s3_ak'] = S3_AK
            msg['s3_sk'] = S3_SK
            msg['s3_bucket'] = S3_BUCKET
            msg['bucket_pref'] = BUCKET_PREF
            publisher.publish_msg(**msg)
        else:
            log.error('Publisher is not correct, drop msg:%s' % msg)


if __name__ == '__main__':

    upload_client = UploadClient(queue="s3_uploaded", exchange="tupu_exchange", exchange_type="fanout", is_backup=True)
    upload_dir = "/opt/python_projects/resources/common_files"
    iterate_over_directory_process(upload_dir, upload_client.upload_file_to_s3)










