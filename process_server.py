#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time  : 2018/3/25 12:01
# Author: Wakesy
# Email : chenxi@szsandstone.com
import json
from config import *
from constant import BACK_PROC_CONF
from copy import deepcopy
from s3_operator.s3_operator import S3Operator
from rabbit_mq.consumer  import MQConsumer
from rabbit_mq.publisher import MQPublisher
from back_process.convert_processor import ConvertProcessor
from back_process.check_processor   import CheckProcessor

# 后处理配置信息
ALL_PROCESS_INFO    = None    # 所有后处理信息
ALL_PROCESS_SUPPORT = []      # 当前支持的后处理类型
CHECK_TYPES   = []            # 审核类型
CONVERT_TYPES = []            # 转换类型

class ProcessServer(MQConsumer):

    def  __init__(self, input_queue=''):
        super(ProcessServer, self).__init__(queue=input_queue)
        self.back_processer = None  # 根据消息中的后处理类型确定
        self.process_success_mq = MQPublisher(PROCESS_SUCCESS_MQ)
        self.process_failed_mq  = MQPublisher(PROCESS_FAILED_MQ)


    def call_back(self, channel, method, properties, body):
        '''重写Consumer的回调函数'''
        msg_args = json.loads(body)
        object_key = msg_args.get("object_key", '')
        log.info("======Recieved a msg: %s" % msg_args)
        if not self.init_back_proc_config():         # 加载配置出错，退出系统
            log.error("init_back_proc_config FAILED, exit system")
            self.process_success_mq.close()
            self.process_failed_mq.close()
            sys.exit(-4)

        if self.process(**msg_args):
            log.critical("NOTICE: back process SUCCESS, object_key: %s" % object_key)

            self.process_success_mq.publish_msg(**msg_args)
        else:
            log.critical("NOTICE: back process FAILED,  object_key: %s" % object_key)
            self.process_failed_mq.publish_msg(**msg_args)
        channel.basic_ack(delivery_tag=method.delivery_tag)  # 后处理结束确认消息使队列消息-1


    def process(self, **kwargs):
        try:
            msg_args = deepcopy(kwargs)
            s3_args = {}
            s3_args['access_key']  = S3_AK
            s3_args['secret_key']  = S3_SK
            s3_args['rgw_host']    = RGW_HOST
            s3_args['rgw_port']    = RGW_PORT
            s3_args['bucket_name'] = msg_args['bucket_name']     # 其他参数可以从配置中取，bucket_name只能从消息中拿
            object_key    = msg_args['object_key']
            action_type   = msg_args['action_type']
            s3_operator   = S3Operator(**s3_args)
            s3_local_file = s3_operator.download_from_s3(object_key, DOWNLOAD_DIR) # 从s3下载，默认存放到DOWNLOAD_DIR中
            log.info("object_key:%s, process type: %s" % (object_key, action_type))
            if not os.path.isfile(s3_local_file):
                log.warn("NOTICE: file downloaded from s3 does'nt exist: %s" % s3_local_file)
                return False

            if action_type not in ALL_PROCESS_SUPPORT:
                log.warn("NOTICE: not support process type: %s" % action_type)
                return False
            elif action_type in CONVERT_TYPES:
                # 转换处理类型
                self.back_processer = ConvertProcessor()
            elif action_type in CHECK_TYPES:
                # 审核处理类型，待完善
                self.back_processer = CheckProcessor()
            else:
                # 其他处理类型，待完善
                pass

            msg_args['s3_local_file'] = s3_local_file # 搭便车，多传两个参数过去
            msg_args['s3_operator']   = s3_operator
            if self.back_processer:
                if self.back_processer.back_process(**msg_args):
                    # 处理结束后，删除源文件
                    log.info("****remove source file:%s" % s3_local_file)
                    os.remove(s3_local_file)
                    return True

        except:
            log.error("Back process failed, error: %s, stop consuming." % traceback.format_exc())
            self.stop_recieve()
        return False


    def init_back_proc_config(self):
        '''获取back_process的信息'''
        global ALL_PROCESS_INFO, ALL_PROCESS_SUPPORT, CHECK_TYPES, CONVERT_TYPES
        try:
            process_conf_obj = configobj.ConfigObj(BACK_PROC_CONF, encoding='utf-8')
            ALL_PROCESS_INFO = dict(process_conf_obj['back_process'])
            ALL_PROCESS_SUPPORT = ALL_PROCESS_INFO.keys()
            # 根据后处理操作的类型分类
            for bp_name in ALL_PROCESS_SUPPORT:
                bp_type = ALL_PROCESS_INFO[bp_name]["operate_type"]
                if bp_type == 'check':
                    CHECK_TYPES.append(bp_name)
                elif bp_type == 'convert':
                    CONVERT_TYPES.append(bp_name)
            log.info('init_back_proc_config success, support process:%s' % ALL_PROCESS_SUPPORT)
            return True
        except:
            log.error("get back_process config failed, error: %s" % traceback.format_exc())
        return False



if __name__ == '__main__':

    try:
        process_server = ProcessServer(input_queue=S3_UPLOADED_MQ)
        process_server.start_recieve()
    except KeyboardInterrupt as error:
        log.info("Exit like a gentleman.error:%s" % error)



