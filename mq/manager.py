#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/23 17:48
# Author: Wakesy
# Email : chenxi@szsandstone.com

import time
import sys
import os

sys.path.append(os.path.abspath('../'))
from config import log
from utils import proc_cmd


# 需要根据实际位置指定
rabbitmq_server = '/opt/rabbitmq_server/sbin/rabbitmq-server'
rabbitmqctl = '/opt/rabbitmq_server/sbin/rabbitmqctl'

class MQManager(object):


    def start(self):
        '''启动rabbitmq'''
        if not self.is_mq_running():
            SUCCESS_TAG = '-detached was passed'
            start_cmd = "{0}  -detached".format(rabbitmq_server)
            proc_succeed, proc_output = proc_cmd(start_cmd)
            if proc_succeed and SUCCESS_TAG in proc_output and self.is_mq_running():
                log.info("Rabbitmq started successfully!")
            else:
                log.error('Rabbitmq started Failed, ret_msg:%s' % proc_output)
        else:
            log.info('Rabbitmq already started, not need')


    def stop(self):
        if self.is_mq_running():
            SUCCESS_TAG = 'Error'
            stop_cmd = "{0} stop".format(rabbitmqctl)
            proc_succeed, proc_output = proc_cmd(stop_cmd)
            if proc_succeed and SUCCESS_TAG not in proc_output:
                log.info("Rabbitmq stoped successfully!")
            else:
                log.error('Rabbitmq stopped Failed, ret_msg:%s' % proc_output)
        else:
            log.info("Rabbitmq already stopped, not need")


    def restart(self):
        self.stop()
        time.sleep(3)  # 防止进程没关掉
        self.start()


    def is_mq_running(self):
        '检查mq是否已经运行'
        check_cmd = "ps -ef|grep rabbitmq|grep -v grep"
        proc_succeed, proc_output = proc_cmd(check_cmd)
        if proc_succeed and proc_output: # 查询成功，并且没有查到进程
            return True
        return False


if __name__ == '__main__':
    manager = MQManager()
    manager.restart()




