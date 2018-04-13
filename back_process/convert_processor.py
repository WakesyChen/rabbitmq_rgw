#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/28 10:38
# Author: Wakesy
# Email : chenxi@szsandstone.com

import os
import re
import traceback
import configobj
from base_processor import BaseProcessor
from utils import get_img_type, is_word_type, proc_cmd
from config import log
from constant import CONVERT_TO_PDF, BACK_PROC_CONF


class ConvertProcessor(BaseProcessor):
    '''进行相关的转换处理'''

    def back_process(self, *args, **kwargs):

        super(ConvertProcessor, self).back_process(*args, **kwargs)
        s3_operator      = kwargs.pop('s3_operator')     # S3Operator实例,pop下车~~('_')~~
        s3_local_file    = kwargs.pop('s3_local_file')   # 文件从s3下载后，保存在本地文件的路径
        object_key       = kwargs['object_key']          # 对象的s3主键（基于本地路径的部分路径）
        action_type      = kwargs['action_type']         # 具体转换动作，如'convert_to_pdf', 'check_is_sexy'
        new_file_name    = kwargs['new_name']            # 转换之后保存的格式，如 'filename.pdf'
        object_dir     = '/'.join(object_key.split('/')[:-1])      # 对象的目录
        local_dir      = '/'.join(s3_local_file.split('/')[:-1])   # 本地保存的目录
        generate_path  = os.path.join(local_dir, new_file_name)    # 转换生成的文件路径
        new_object_key = os.path.join(object_dir, new_file_name)   # 生成的文件对应s3上的key

        generate_file_path = self.common_convert(action_type=action_type, source_path=s3_local_file,
                                                 generate_path=generate_path, generate_dir=local_dir)
        if os.path.isfile(generate_file_path):
            if s3_operator.upload_to_s3(new_object_key, generate_file_path):  # 上传到s3中

                return True
            # 删除生成的文件
            os.remove(generate_file_path)
        return False


    def common_convert(self, action_type='', source_path='', generate_path='', generate_dir=''):
        '''
        :param action_type  : 处理类型
        :param source_path  : 待处理的文件路径
        :param generate_path: 指定处理之后生成的新文件路径
        :param generate_dir : 指定处理之后生成新文件的目录（word转pdf时用）
        :param operate_cmd  : 处理的指令
        :return: 处理生成的新文件路径
        '''
        generate_file_path = ''
        try:
            is_word_file  = is_word_type(source_path)
            is_img_file   = True if get_img_type(source_path) else False
            bp_conf_obj   = configobj.ConfigObj(BACK_PROC_CONF)
            all_back_proc = bp_conf_obj['back_process']
            operate_info  = all_back_proc.get(action_type)                     # 配置文件中获取，该处理类型的信息
            operate_cmd   = operate_info.get("operate_cmd")                    # 处理执行的指令，如:"ffmpeg  -i  %s  %s"
            operate_file  = operate_info.get("operate_file")                   # 操作的文件类型
            convert_cmd   = operate_cmd % (source_path, generate_path)
            if action_type == CONVERT_TO_PDF:
                if is_word_file and operate_file == 'doc':
                    # word转pdf
                    convert_cmd = operate_cmd % (source_path, generate_dir)
                    SUCCESS_TAG = "writer_pdf_Export"                          # 执行成功，输出结果会带这个字段
                    is_succeed, stdout = proc_cmd(convert_cmd)
                    if is_succeed and SUCCESS_TAG in stdout:
                        generate_file_path = re.sub(r'.doc[x]{0,1}', '.pdf', source_path)
            else:
                if is_img_file and operate_file == 'image':
                    # 图片格式转换
                    is_succeed, stdout = proc_cmd(convert_cmd)
                    if is_succeed:
                        generate_file_path = generate_path
        except:
            log.error("Error happended when converting file, error:%s" % traceback.format_exc())
        return generate_file_path






