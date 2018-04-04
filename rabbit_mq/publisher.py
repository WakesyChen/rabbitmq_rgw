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

from config import MQ_CONN_URL, log
class MQPublisher(object):

    def __init__(self, queue='', exchange='direct_exchange', exchange_type='direct', routing_key='', is_backup=False):
        self.queue         = queue    # 目前需求必须指定queue
        self.exchange      = exchange
        self.exchange_type = exchange_type
        self.routing_key   = routing_key or queue
        self.is_backup     = is_backup # 是否备份当前队列消息
        self.channel       = None
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


    def publish(self, body):
        if not self.mq_connection:
            log.error('mq_connection is not builded, publish failed!')
            return 0
        try:
            properties = pika.BasicProperties(delivery_mode=2)  # 队列持久化，防止宕机消失
            publish_success = self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       body=body,
                                       properties=properties
                                       )
            if publish_success:
                log.info('Publish message success, msg_content:%s' % body)
            else:
                log.error("Publish message failed, msg_content:%s" % body)
        except Exception as e:
            publish_success = False
            log.error("Error happenned when publish msg,  error: %s, body: %s" % (e, body))
        return publish_success


    def publish_msg(self, **msg):
        '''对外提供的发送消息的方法'''
        body = self.formated_content(**msg)
        self.publish(body)


    def formated_content(self, **kwargs):
        content = {}
        message = ''
        try:
            content['start_time']   = str(time.time())   # 产生时间
            content['event_id']     = str(uuid.uuid1())  # 事件的唯一标识
            content['notify_url']   = ''                 # 审核结果通知地址
            content['action_type']  = 'convert_to_pdf'   # 后处理类型，转换类型如："convert_to_pdf";审核类型如："check_is_sexy"
            content['hit_action']   = 'nothing'          # 审核处理需要，鉴定为黄色，或者暴恐等后要执行的操作；如果是转换类型，则为空
            content['new_name']     = 'doc_file.pdf'     # 转换处理需要，规定文件转换之后的名字；如果是审核类型，则为空
            content['object_key']   = ''
            content['bucket_name']  = ''
            content.update(kwargs)
            message = json.dumps(content)
        except Exception as e:
            log.error("formt message failed: %s" % e)
        return message


    def close(self):
        if self.mq_connection:
            self.mq_connection.close()


    def __del__(self):
        self.close()

