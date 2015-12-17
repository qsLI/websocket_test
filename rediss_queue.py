# coding=utf-8
import redis
from StringIO import StringIO
import numpy as np
import cv2


class RedisQueue(object):
    def __init__(self, name, namespace='queue', **redis_kwargs):
        self.__db = redis.StrictRedis()
        self.key = '%s:%s' % (namespace, name)

    def put(self, item):
        self.__db.rpush(self.key, item)

    def get(self, type=True, timeout=None):
        if type:
            item =  self.__db.blpop(self.key, timeout)
        else:
            item = self.__db.lpop(self.key)
        if item:
            # print item
            item = item[1]
        return item

    def size(self):
        return self.__db.llen(self.key)

    def decode_one_frame(self):
        """ decode a frame from message queue """
        img = self.get()
        sio = StringIO(img)
        img = np.load(sio)
        img = cv2.imdecode(img, cv2.CV_LOAD_IMAGE_COLOR)
        return img

    def encode_one_frame(self, img):
        """ encode a frame to message queue"""
        ret, img = cv2.imencode(".jpg", img)
        sio = StringIO()
        np.save(sio, img)
        self.put(sio.getvalue())


if __name__ == "__main__":
    q = RedisQueue('test')
    q.put('hello,world')
    print q.get()
    print q.get()