# -*- coding:utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import boto
import boto.s3
import boto.s3.connection
from multiupload import upload_file_multipart
from config import log
import hashlib

MULTI_UPLOAD_THRESHOLD_SIZE = 50*1024*1024 # 大于50M分片上传

class S3Operator(object):

    def __init__(self, access_key='', secret_key='', rgw_host='', rgw_port=22, bucket_name=''):
        self.access_key = access_key
        self.secret_key = secret_key
        self.host    = rgw_host
        self.port    = rgw_port
        self.bucket  = bucket_name
        self.s3_conn = None
        self.init_s3_connection()

    def init_s3_connection(self):
        self.s3_conn = self.get_s3_connection()
        log.info("init_s3_connection succeed!")


    def get_s3_connection(self):
        if not self.s3_conn:
            try:
                self.s3_conn = boto.connect_s3(aws_access_key_id=self.access_key,
                                               aws_secret_access_key=self.secret_key,
                                               host=self.host,
                                               port=self.port,
                                               is_secure=False,
                                               calling_format=boto.s3.connection.OrdinaryCallingFormat())
            except Exception, e:
                self.s3_conn = None
                log.critical("Build_s3_connection failed: %s" % str(e))
        return self.s3_conn


    def upload_to_s3(self, cloud_path, file_path):

        try:
            if not self.get_s3_connection():
                log.error("FAILURE UPLOAD: S3 connection is not builded.")
                return False
            if self.check_from_s3(cloud_path):
                log.debug("S3 object already exists: %s" % cloud_path)
                return True

            md5id = self.GetFileMd5(file_path)
            bucket = self.s3_conn.get_bucket(self.bucket, validate=False)
            object_path = cloud_path.replace("\\", "/")
            if object_path[0] == '/':
                object_path = object_path
            else:
                object_path = '/' + object_path
            kobject = bucket.new_key(object_path)
            filesize = os.stat(file_path).st_size

            if filesize >= MULTI_UPLOAD_THRESHOLD_SIZE:
                upload_file_multipart(file_path, object_path, bucket, md5id)
                log.info("SUCCESS to S3: multipart way,  uploading file path: %s " % file_path)
            else:
                kobject.set_contents_from_filename(file_path, headers={'CONTENT-MD5' : md5id})
                log.info("SUCCESS to S3: singlefile way, uploading file path: %s" % file_path)
        except Exception, e:
            log.error("FAILURE to S3: error: %s, uploading file path: %s" % (e, file_path))
            return False
        return True

    def check_from_s3(self, object_key):
        '''检查s3中是否已经存在'''
        bucket = self.s3_conn.get_bucket(self.bucket, validate=False)
        kobject = bucket.get_key(object_key)
        return True if kobject else False



    def download_from_s3(self, object_key, download_dir):
        '''
        :param key_path: s3里面对象的key
        :param download_dir: 下载到本地的目录
        :return:
        '''
        local_path = '' # 文件从s3上下载下来后，保存到的本地路径
        try:
            if not self.get_s3_connection():
                log.error("FAILURE UPLOAD: S3 connection is not builded.")
                return False
            if not os.path.isdir(download_dir):
                os.makedirs(download_dir)

            if len(object_key.split('/')) < 2:
                file_name = object_key
            else:
                file_name = object_key.split('/')[-1] #取出文件名
            local_path = os.path.join(download_dir, file_name)
            log.info("File will be download: %s" % local_path)
            bucket = self.s3_conn.get_bucket(self.bucket, validate=False)
            kobject = bucket.get_key(object_key)
            kobject.get_contents_to_filename(local_path)
            log.info("Download file from s3_operator successfully" )
        except Exception as error:
            log.error("Download file from s3_operator failed, error:%s" % error)
        return local_path

    def GetFileMd5(self, file_path):
        '''根据文件内容生成md5值'''
        if not os.path.isfile(file_path):
            return
        myhash = hashlib.md5()
        f = file(file_path, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myhash.update(b)
        f.close()
        return myhash.hexdigest()


if __name__ == '__main__':

    pass



