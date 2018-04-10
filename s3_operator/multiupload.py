#!/var/lib/sdsom/venv/bin/python
# -*- coding: utf-8 -*-


import math
import os
from filechunkio import FileChunkIO
import threading
import Queue


CHUNK_SIZE = 4*1024*1024
MULTI_THREAD_NUM = 5

class Chunk:
    num = 0
    offset = 0
    len = 0
    def __init__(self, n, o, l):  
        self.num = n
        self.offset = o
        self.len = l


def init_queue(filesize):
    chunkcnt = int(math.ceil(filesize*1.0/CHUNK_SIZE))
    q = Queue.Queue(maxsize = chunkcnt)
    for i in range(0,chunkcnt):
        offset = CHUNK_SIZE*i
        len = min(CHUNK_SIZE, filesize-offset)
        c = Chunk(i+1, offset, len)
        q.put(c)
    return q


def upload_chunk_func(filepath, mp_handler, chunk_queue, id, md5id):
    while (not chunk_queue.empty()):
        chunk = chunk_queue.get()
        fp = FileChunkIO(filepath, 'r', offset=chunk.offset, bytes=chunk.len)
        mp_handler.upload_part_from_file(fp, headers={'CONTENT-MD5' : md5id}, part_num=chunk.num)
        fp.close()
        chunk_queue.task_done()


def upload_file_multipart(filepath, keyname, bucket, md5id, threadcnt=MULTI_THREAD_NUM):
    filesize = os.stat(filepath).st_size
    mp_handler = bucket.initiate_multipart_upload(keyname)
    chunk_queue = init_queue(filesize)
    for i in range(0, threadcnt):
        t = threading.Thread(target=upload_chunk_func, args=(filepath, mp_handler, chunk_queue, i, md5id))
        t.setDaemon(True)
        t.start()

    chunk_queue.join()
    mp_handler.complete_upload()
