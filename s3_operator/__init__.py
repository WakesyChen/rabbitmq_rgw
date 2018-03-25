#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/24 14:29
# Author: Wakesy
# Email : chenxi@szsandstone.com

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test(a='',b='',c=12):
    print a, b, c

if __name__ == '__main__':
    pp = {'c':12, "b":21, 'a':22, 'd':23}
    test(**pp)