#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/4/2 12:00
# Author: Wakesy
# Email : chenxi@szsandstone.com


import os
from constant import COMMOM_IMG_TRANS
from utils import proc_cmd
from utils import get_img_type
from config import log


def convert_img2gif(img_path, generate_path):
    '''图片格式转换gif'''
    return convert_image_common(img_path, generate_path)


def convert_img2jpeg(img_path, generate_path):
    '''图片格式转换jpeg'''
    return convert_image_common(img_path, generate_path)


def convert_img2bmp(img_path, generate_path):
    '''图片格式转换bmp'''
    return convert_image_common(img_path, generate_path)



def convert_image_common(img_path, generate_path):
    '''通用的图片格式转换,目前支持转：gif, jpeg, bmp'''
    # 已生成就直接返回
    if get_img_type(generate_path):
        return True

    trans_cmd = COMMOM_IMG_TRANS.format(img_path=img_path, generate_path=generate_path)
    is_succeed, stdout = proc_cmd(trans_cmd)
    if is_succeed and os.path.isfile(generate_path):
        log.debug("convert image type successfully, img_path: %s" % img_path)
        return True
    else:
        log.warn("convert image type failed, img_path: %s" % img_path)
        return False
