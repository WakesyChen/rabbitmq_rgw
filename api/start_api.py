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





api.add_resource(BackProcess, '/api/back_process', '/api/v1/back_process')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)