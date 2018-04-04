#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/21 15:16
# Author: Wakesy
# Email : chenxi@szsandstone.com

import pika
import json
import sys
import os

sys.path.append(os.path.abspath('../'))
from config import MQ_CONN_URL, log

class MQConsumer(object):

    def __init__(self, queue='', exchange='', exchange_type='direct', routing_key=''):
        self.queue =queue
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key or queue
        self.mq_connection = None
        self.channel = None
        self.build_connection()


    def build_connection(self):
        try:
            self.mq_connection = pika.BlockingConnection(pika.URLParameters(MQ_CONN_URL))
            self.channel = self.mq_connection.channel()
            # 方法一：直接从给定的queue中取消息
            if self.queue:
                self.channel.queue_declare(queue=self.queue, durable=True)
            # 方法二：通过exchange建立临时队列，动态获取消息
            else:
                assert self.exchange, 'queue or exchange are not defined!'
                self.channel.exchange_declare(exchange=self.exchange,
                                              exchange_type=self.exchange_type,
                                              durable=True
                                              )
                result = self.channel.queue_declare(exclusive=True) # 声明匿名队列，断开连接后删除
                self.queue = result.method.queue
                self.channel.queue_bind(exchange=self.exchange, queue=self.queue)
            # 开始接收队列消息
            self.channel.basic_consume(consumer_callback=self.call_back,
                                       queue=self.queue,
                                       exclusive=True
                                       # no_ack=True  # 写的话，如果接收消息，机器宕机消息就丢了,
                                       # 一般不写。宕机则生产者检测到发给其他消费者
                                       )

        except Exception as e:
            log.error('Build connection failed: %s' % e)


    def call_back(self, channel, method, properties, body):
        '''用来接收消息的函数'''
        body = json.loads(body)
        channel.basic_ack(delivery_tag=method.delivery_tag) # 告诉生成者，消息处理完成
        log.info("Consumer recieved a message: %s" % str(body))


    def start_recieve(self):
        log.info("Consumer waiting for messages...")
        try:
            self.channel.start_consuming()
        except Exception as e:
            log.error(e)


    def stop_recieve(self):
        if self.channel:
            self.channel.stop_consuming()


    def __exit__(self):
        self.stop_recieve()


if __name__ == '__main__':

    consumer = MQConsumer(queue="object_process", exchange='amq.fanout', exchange_type='fanout')
    consumer.start_recieve()


