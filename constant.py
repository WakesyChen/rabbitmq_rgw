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

# 审核类型
CHECK_SEXY      = 'check_is_sexy'       # 黄色
CHECK_POLICY    = 'check_is_policy'     # 政治相关
CHECK_TERRORIST = 'check_is_terrorist' # 暴力恐怖
CHECK_TYPES = [CHECK_SEXY, CHECK_TERRORIST, CHECK_POLICY]

# 审核完成后的操作
# HIT_ACTION_DELETE  = 'delete'
# HIT_ACTION_NOTHING = 'nothing'
# HIT_ACTION_HIDE    = 'hide'
# HIT_ACTIONS = [HIT_ACTION_DELETE, HIT_ACTION_HIDE, HIT_ACTION_NOTHING]


# 转换类型
CONVERT_TO_PDF  = 'convert_to_pdf'   # word转pdf
CONVERT_TO_GIF  = 'convert_to_gif'   # 图片转为gif格式
CONVERT_TO_JPEG = 'convert_to_jpeg'  # 图片转为jpeg格式
CONVERT_TO_BMP  = 'convert_to_bmp'  # 图片转为bmp格式
# CONVERT_RESIZE  = 'resize'   # 重新调整尺寸
CONVERT_TYPES   = [CONVERT_TO_PDF, CONVERT_TO_GIF, CONVERT_TO_JPEG, CONVERT_TO_BMP]

ALL_PROCESS_SUPPORT = CHECK_TYPES + CONVERT_TYPES  # 支持的所有后处理类型


#===========================对应的操作指令========================

# word转pdf. word_path: word文档的地址; generate_dir: pdf生成的目录
CMD_WORD2PDF = "soffice --headless --convert-to pdf  {word_path}  --outdir  {generate_dir}"
# 图片转换格式 to_gif. img_path:图片地址; generate_path: 生成的gif图片路径
CMD_TO_GIF  = "ffmpeg  -i  {img_path}  {generate_path}"
# 图片转换格式 to_jpeg. 同上
CMD_TO_JPEG = "ffmpeg  -i  {img_path}  {generate_path}"
# 通用的转换格式指令
CMD_TO_COMMOM = "ffmpeg  -i  {img_path}  {generate_path}"


