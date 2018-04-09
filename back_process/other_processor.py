#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/9 17:33
# Author: Wakesy
# Email : chenxi@szsandstone.com


from config import log
from base_processor import BaseProcesser


class OtherProcesser(BaseProcesser):


    def back_process(self, *args, **kwargs):
        super(OtherProcesser, self).back_process(**kwargs)
        log.info("OtherProcesser hasn't been realized, please waiting...")
        return False

    def __repr__(self):
        return 'instance of class: <OtherProcesser>'

