#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/21 15:08
# Author: Wakesy
# Email : chenxi@szsandstone.com
import pika
import time
import uuid
import json
import os, sys
sys.path.append(os.path.abspath('../'))

from random import randint
from config import log
from config import MQ_CONN_URL

class MQPublisher(object):

    def __init__(self, queue='', exchange='direct_exchange', exchange_type='direct', routing_key='', is_backup=False):
        self.queue = queue  # 目前需求必须指定queue
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key or queue
        self.is_backup = is_backup # 是否备份当前队列消息
        self.channel = None
        self.mq_connection = None
        self.build_connection()


    def build_connection(self):
        try:
            self.mq_connection = pika.BlockingConnection(pika.URLParameters(MQ_CONN_URL))
            self.channel = self.mq_connection.channel()
            self.channel.exchange_declare(self.exchange, exchange_type=self.exchange_type, durable=True)
            assert self.queue, "Publisher must define queue at first!"
            # 声明队列, 绑定exchange和queue
            self.channel.queue_declare(queue=self.queue, durable=True) # 持久化队列
            self.channel.queue_bind(queue=self.queue, exchange=self.exchange)

            if self.is_backup:
                # 新建备份队列
                backup_queue = self.queue + "_backup"
                self.channel.queue_declare(queue=backup_queue, durable=True)
                self.channel.queue_bind(queue=backup_queue, exchange=self.exchange)
        except Exception as e:
            log.critical( "MQPublisher build connection failed: %s" % e)
            raise Exception, e


    def formated_content(self, **kwargs):
        content = {}
        message = ''
        try:
            content['start_time'] = str(time.time())  # 产生时间
            content['event_id'] = str(uuid.uuid1())  # 事件的唯一标识
            content['call_method'] = kwargs.get('call_method', '')  # 需要调用的方法
            content['call_args'] = kwargs.get('call_args', '') # 方法需要的参数
            # 文件上传到s3的信息
            content['rgw_host'] = kwargs.get('rgw_host', '')
            content['rgw_port'] = kwargs.get('rgw_port', '')
            content['s3_ak'] = kwargs.get('s3_ak', '')
            content['s3_sk'] = kwargs.get('s3_sk', '')
            content['s3_bucket'] = kwargs.get('s3_bucket', '')
            content['bucket_pref'] = kwargs.get('bucket_pref', '')
            content['obj_key'] = kwargs.get('obj_key', '')
            content['file_path'] = kwargs.get('file_path', '')
            message = json.dumps(content)
        except Exception as e:
            log.error("formt message failed: %s" % e)
        return message


    def publish(self, body):
        if not self.mq_connection:
            log.error('mq_connection is not builded, publish failed!')
            return 0
        try:
            properties = pika.BasicProperties(delivery_mode=2)  # 队列持久化，防止宕机消失
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       body=body,
                                       properties=properties
                                       )
            log.info('Publish msg successfuly,body:%s' % body)
        except Exception as e:
            log.exception("Publish msg failed, error:%s" % e)


    def publish_msg(self, **msg):
        '''对外提供的发送消息的方法'''
        if not msg:
            log.info('message is empty, cannot be published!')
            return
        body = self.formated_content(**msg)
        self.publish(body)

    def close(self):
        if self.mq_connection:
            self.mq_connection.close()


    def __del__(self):
        self.close()

if __name__ == '__main__':

    publisher = MQPublisher(queue="upload_history", exchange="tupu_exchange", exchange_type='fanout', is_backup=True)
    for i in range(5):
        msg = {}
        msg['content'] = 'Hello world: %s' % randint(0, 1000)
        publisher.publish_msg(**msg)
    publisher.close()
