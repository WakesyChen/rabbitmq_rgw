#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
from config import log
from base_processer import BaseProcesser
from constant import *

class CheckProcesser(BaseProcesser):


    def back_process(self, *args, **kwargs):
        super(CheckProcesser, self).back_process(**kwargs)
        print kwargs['pp']
        log.info('CheckProcess args:%s, %s' % (args[0], args[1]))

    def __repr__(self):
        return 'instance of class: <CheckProcess>'


if __name__ == '__main__':
    check_proc = CheckProcesser()
    check_proc.back_process('123','231', pp=CheckProcesser())
    # check_proc.back_process(app='juice',ove='jack')
