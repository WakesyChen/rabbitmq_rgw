#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/24 19:43
# Author: Wakesy
# Email : chenxi@szsandstone.com

from s3_operator.s3_operator import S3Operator
from mq.publisher import MQPublisher
from config import *

'''
上传文件到s3，并记录到rabbitmq队列------消息publisher
'''


class UploadClient(object):

    def __init__(self):
        self.s3_publisher = MQPublisher(queue="s3_success", exchange="tupu_exchange", exchange_type="fanout", is_backup=True)
        self.s3_failed_publisher = MQPublisher(queue="s3_failed")
        self.s3_operator = S3Operator()
        log.info('init upload client successfully!')


    def upload_file_to_s3(self, file_path, cloud_path):

        if self.s3_operator:
            is_success = self.s3_operator.upload_to_s3(cloud_path, file_path)
            if is_success:
                self.publish_msg_to_queue(self.s3_publisher, file_path, cloud_path)
                return True
        self.publish_msg_to_queue(self.s3_failed_publisher, file_path, cloud_path)
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

    root_dir = "/opt/python_projects/resources/"
    cloud_paths = ['/docs/computer_interface.doc', '/docs/good_job.doc', '/docs/notes_1.doc']
    upload_client = UploadClient()
    for cloud_path in cloud_paths:
        file_path = root_dir[:-1] + cloud_path
        upload_client.upload_file_to_s3(file_path, cloud_path)






