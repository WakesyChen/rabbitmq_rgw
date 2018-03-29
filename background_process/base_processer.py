#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:39
# Author: Wakesy
# Email : chenxi@szsandstone.com

from config import log
from constant import DEFAULT_PROCESS

class BaseProcesser(object):
    '''后处理'''


    def back_process(self, *args, **kwargs):
        '''必须指定转化类型'''
        pass

if __name__ == '__main__':
    BaseProcesser().back_process()