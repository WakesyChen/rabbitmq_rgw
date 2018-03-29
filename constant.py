#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/26 10:27
# Author: Wakesy
# Email : chenxi@szsandstone.com



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


#===========================后处理类型========================

# 默认类型
DEFAULT_PROCESS = 'default_process'

# 审核类型
CHECK_PROCESS  = 'check'
CHECK_SEXY     = 'is_sexy'  # 黄色
CHECK_POLICY   = 'is_policy' # 政治相关
CHECK_TERRORIST = 'is_terrorist' # 暴力恐怖
CHECK_TYPES = [CHECK_SEXY, CHECK_TERRORIST, CHECK_POLICY]
# 审核完成后的操作
HIT_ACTION_DELETE  = 'delete'
HIT_ACTION_NOTHING = 'nothing'
HIT_ACTION_HIDE    = 'hide'
HIT_ACTIONS = [HIT_ACTION_DELETE, HIT_ACTION_HIDE, HIT_ACTION_NOTHING]

# 转换类型
CONVERT_PROCESS  = 'transfer'
CONVERT_TO_PDF   = 'to_pdf'   # word转pdf
CONVERT_TO_GIF   = 'to_gif'   # 图片转为gif格式
CONVERT_TO_JPEG  = 'to_jpeg' # 图片转为gif格式
CONVERT_RESIZE   = 'resize'   # 重新调整尺寸
CONVERT_TYPES    = [CONVERT_TO_PDF, CONVERT_TO_GIF, CONVERT_TO_JPEG, CONVERT_RESIZE]


