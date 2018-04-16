#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/26 10:27
# Author: Wakesy
# Email : chenxi@szsandstone.com
import os
import sys


# 脚本的根目录
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)
# 系统的配置文件
COMMON_CONF = os.path.join(ROOT_DIR, "common.conf")
# 后处理的配置文件
BACK_PROC_CONF = os.path.join(ROOT_DIR, "back_process/back_process.conf")
# MQ连接url格式
MQ_URL_FORMAT = "amqp://{user}:{password}@{host}:{port}/{vhost}?socket_timeout={timeout}"

CONVERT_TO_PDF  = 'convert_to_pdf'   # word转pdf


# imghdr 库支持的图片文件类型
IMG_JPEG  = 'jpeg'
IMG_GIF   = 'gif'
IMG_PNG   = 'png'
IMG_RGB   = 'rgb'
IMG_PGM   = 'pgm'
IMG_PBM   = 'pbm'
IMG_PPM   = 'ppm'
IMG_TIFF  = 'tiff'
IMG_RAST  = 'rast'
IMG_XBM   = 'xbm'
IMG_BMP   = 'bmp'
IMG_TYPES = [IMG_JPEG, IMG_GIF, IMG_PNG, IMG_RGB, IMG_PGM, IMG_PBM,
             IMG_PPM, IMG_TIFF, IMG_RAST,IMG_XBM, IMG_BMP]


# 转换类型对应的文件后缀
convert_postfix = {
    "convert_to_pdf" :"pdf",
    "convert_to_jpeg": "jpeg",
    "convert_to_bmp" : "bmp",
    "convert_to_gif" : "gif"
}

