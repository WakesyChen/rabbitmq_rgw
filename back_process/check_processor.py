#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
from config import log
from base_processor import BaseProcesser
from constant import *


class CheckProcesser(BaseProcesser):


    def back_process(self, *args, **kwargs):
        super(CheckProcesser, self).back_process(**kwargs)
        log.info("CheckProcess hasn't been realized, please waiting...")



    def __repr__(self):
        return 'instance of class: <CheckProcess>'

