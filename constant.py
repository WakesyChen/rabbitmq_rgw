#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/26 10:27
# Author: Wakesy
# Email : chenxi@szsandstone.com



#从s3上下载的文件，存放目录
DOWNLOAD_DIR = '/opt/python_projects/resources/download'


# magic 库支持的图片文件类型
IMG_JPEG  = 'image/jpeg'
IMG_GIF   = 'image/gif'
IMG_PNG   = 'image/png'
IMG_RGB   = 'image/rgb'
IMG_PGM   = 'image/pgm'
IMG_PBM   = 'image/pbm'
IMG_PPM   = 'image/ppm'
IMG_TIFF  = 'image/tiff'
IMG_RAST  = 'image/rast'
IMG_XBM   = 'image/xbm'
IMG_BMP   = 'image/bmp'
IMG_TYPES = [IMG_JPEG, IMG_GIF, IMG_PNG, IMG_RGB, IMG_PGM, IMG_PBM,
             IMG_PPM, IMG_TIFF, IMG_RAST,IMG_XBM, IMG_BMP]


# magic 库支持的文档类型
DOCUMENT_WORD  = 'application/msword'
DOCUMENT_EXCEL = 'application/vnd.ms-excel'
DOCUMENT_PDF   = 'application/mspdf'
DOCUMENT_TYPES = [DOCUMENT_WORD, DOCUMENT_EXCEL, DOCUMENT_PDF]