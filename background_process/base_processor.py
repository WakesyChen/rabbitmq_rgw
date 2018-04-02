#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:39
# Author: Wakesy
# Email : chenxi@szsandstone.com

from config import log


class BaseProcesser(object):
    '''后处理'''


    def back_process(self, *args, **kwargs):
        '''必须指定转化类型'''
        pass


if __name__ == '__main__':

    test = {'a':1,'b':2,'c':3}
    for i in test:
        print i ,test[i]
        test.pop(i)
        print test
    pass