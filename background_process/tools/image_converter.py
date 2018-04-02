#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/2 12:00
# Author: Wakesy
# Email : chenxi@szsandstone.com


import os
from constant import CMD_TO_GIF, CMD_TO_JPEG
from utils import proc_cmd
from config import log


def convert_img2gif(self, img_path, generate_path):
    '''图片格式转换gif'''

    trans_cmd = CMD_TO_GIF.format(img_path=img_path, generate_path=generate_path)
    is_succeed, stdout = proc_cmd(trans_cmd)
    if is_succeed and os.path.isfile(generate_path):
        log.info("NOTICE: convert image to gif successfully, img_path: %s" % img_path)
        return True
    else:
        log.error("NOTICE: convert image to gif failed, img_path: %s" % img_path)
        return False


def convert_img2jpeg(self, img_path, generate_path):
    '''图片格式转换jpeg'''

    trans_cmd = CMD_TO_JPEG.format(img_path=img_path, generate_path=generate_path)
    is_succeed, stdout = proc_cmd(trans_cmd)
    if is_succeed and os.path.isfile(generate_path):
        log.info("NOTICE: convert image to jpeg successfully, img_path: %s" % img_path)
        return True
    else:
        log.error("NOTICE: convert image to jpeg failed, img_path: %s" % img_path)
        return False


def convert_image_common(self, convert_type, img_path, generate_path):
    '''通用的图片格式转换'''

    trans_cmd = CMD_TO_JPEG.format(img_path=img_path, generate_path=generate_path)
    is_succeed, stdout = proc_cmd(trans_cmd)
    if is_succeed and os.path.isfile(generate_path):
        log.info("NOTICE: convert image to jpeg successfully, img_path: %s" % img_path)
        return True
    else:
        log.error("NOTICE: convert image to jpeg failed, img_path: %s" % img_path)
        return False