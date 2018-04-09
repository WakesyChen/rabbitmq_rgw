#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/9 10:20
# Author: Wakesy
# Email : chenxi@szsandstone.com

import json
import os
from flask_restful import Resource, request
from config import log, DOWNLOAD_DIR, ALL_PROCESS_SUPPORT


def result_formatter(data=None, message="default success message", success=1):
    result = {"message": message,
              "success": success,
              "data":data}
    # return json.dumps(result, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


class BackProcess(Resource):

    def get(self):
        data = {"support_process": ALL_PROCESS_SUPPORT}
        return result_formatter(data=data)

    def post(self):
        try:
            file = request.files.get('file')
            if file:
                file.save(os.path.join(DOWNLOAD_DIR, file.filename))  # 保存到DOWNLOAD_DIR中
                message = "Upload file success, filename: %s" % file.filename
                return result_formatter(message=message ,success=1)
            else:
                message = "Post request only except file uploading, no file found."
                return result_formatter(message=message, success=0)
        except Exception as error:
            message = "Internal server error: %s" % error
            return result_formatter(message=message, success=-1)


