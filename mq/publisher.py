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
from constant import *
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
            content['start_time']  = str(time.time())  # 产生时间
            content['event_id']    = str(uuid.uuid1())  # 事件的唯一标识
            content['action_type'] = 'transfer'  # 处理类型（check or transfer）
            content['notify_url']  = '' # 审核结果通知地址 ## 发送审核结果到APP队列，让APP执行相应策略
            check_type = {} # 审核类型相关参数
            check_type['action_list'] = ['is_sexy','is_terrorist'] # 具体动作（check:, transfer:[”to_gif“， ”resize“，”to_pdf“，“rotate”]
            check_type['hit_action']  = 'nothing' # 审核命中（比如黄图或者恐怖活动），对存到MOS的源文件处理方式，比如“delete”，“hide”，“nothing”
            content['check_type']     = check_type
            convert_type = {} # 转换类型相关参数
            convert_type['action_list']  = ['to_pdf', 'to_gif']
            convert_type['newname_list'] = ['filename.pdf', 'filename.gif']  # transfer后的文件名(作为新的key)
            content['convert_type']      = convert_type
            # 对象存储s3的信息
            content['object_key']  = ''
            content['bucket_name'] = ''
            content['access_key']  = ''
            content['secret_key']  = ''
            content['rgw_host']    = ''
            content['rgw_port']    = 0
            content.update(kwargs)
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
            log.info('================Publish a msg successfuly, msg_content: %s' % body)
        except Exception as e:
            log.exception("Publish msg failed, error: %s" % e)


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
