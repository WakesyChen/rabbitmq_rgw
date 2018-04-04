#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/3 16:05
# Author: Wakesy
# Email : chenxi@szsandstone.com

import json
import sys
import os
sys.path.append((os.path.abspath('../')))
from flask import Flask
from constant import ALL_PROCESS_SUPPORT, HIT_ACTIONS
app = Flask(__name__)

@app.route('/')
def test():
    return 'hello world'


back_process_url   = "/v1/api/back_process/support"
back_process_info  = {"support_actions": ALL_PROCESS_SUPPORT, # 支持的后处理操作列表
                      "hit_actions"    : HIT_ACTIONS,         # 审核类型需要用到，如鉴黄成功，可以选择删除，隐藏或者不处理
  }

'''提供'''
@app.route(back_process_url)
def get_support_process():
    return json.dumps(back_process_info, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)