#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/26 11:19
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
import logging

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # 根目录（...../background_process）
# 对外api日志
API_LOG_PATH  = os.path.join(ROOT_DIR, "log/api.log")      # api日志
API_SCRIPT    = os.path.join(ROOT_DIR, "api/start_api.py") # api启动脚本
START_API_CMD = "nohup python %s > %s 2>&1 &" % (API_SCRIPT, API_LOG_PATH)            # 启动api的指令
STOP_API_CMD  = "ps -ef |grep start_api|grep -v grep|awk '{print $2}'|xargs kill -9"  # 停止api的指令


# 设置log
api_logger = logging.getLogger("api")
api_formatter = logging.Formatter("[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s]: %(message)s")
api_handler = logging.FileHandler(API_LOG_PATH)
api_handler.setFormatter(api_formatter)
api_logger.setLevel(logging.INFO)
api_logger.addHandler(api_handler)


if __name__ == "__main__":
    api_logger.info("test the info log")
    api_logger.error("test the error log")
    api_logger.warn("test the warn log")





