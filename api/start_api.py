#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/3 16:05
# Author: Wakesy
# Email : chenxi@szsandstone.com


import sys
import os
sys.path.append((os.path.abspath('../')))
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from back_process_api import BackProcess

app = Flask(__name__)
CORS(app, resources=r'/*')  # 允许AJAX跨域
api = Api(app)

# '''提供查询当前支持的后处理功能'''
# @app.route('api/back_process')
# def get_support_process():
#     back_process_info = {"support_actions": ALL_PROCESS_SUPPORT}  # 支持的后处理操作列表
#     return json.dumps(back_process_info, ensure_ascii=False)


api.add_resource(BackProcess, '/', '/api/back_process')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)