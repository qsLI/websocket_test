# coding=utf-8
import redis
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

if __name__ == "__main__":
    q = RedisQueue('test')
    q.put('hello,world')
    print q.get()
    print q.get()