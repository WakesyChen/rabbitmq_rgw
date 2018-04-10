#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:39
# Author: Wakesy
# Email : chenxi@szsandstone.com



class BaseProcessor(object):
    '''后处理'''


    def back_process(self, *args, **kwargs):
        '''必须指定转化类型'''
        pass
