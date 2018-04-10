#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

from config import log
from base_processor import BaseProcessor


class CheckProcessor(BaseProcessor):


    def back_process(self, *args, **kwargs):
        super(CheckProcessor, self).back_process(**kwargs)
        log.info("CheckProcess hasn't been realized, please waiting...")
        return False



    def __repr__(self):
        return 'instance of class: <CheckProcessor>'

