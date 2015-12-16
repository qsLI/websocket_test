import tornado.ioloop
import tornado.web
import tornado.websocket
import cv2
import base64,time
import copy
import threading
import numpy as np
from StringIO import StringIO
from rediss_queue import RedisQueue


class CaptureThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.cap = cv2.VideoCapture(-1)
        self.q = q

    def run(self):
        while True:
            ret, img = self.cap.read()
            if img is None:
                time.sleep(1)
                continue
            ret, img = cv2.imencode(".jpg", img)
            sio = StringIO()
            np.save(sio, img)
            self.q.put(sio.getvalue())

    def __del__(self):
        self.cap.release()


class IndexHandler(tornado.web.RequestHandler):
    """ server the index page """
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")

# capture thread
Q = RedisQueue("video")
cap_thread = CaptureThread(Q)
cap_thread.setDaemon(True)


class WebSocketImgHandler(tornado.websocket.WebSocketHandler):
    """ websocket """
    def __init__(self, *args, **kwargs):
        super(WebSocketImgHandler, self).__init__(*args, **kwargs)
        # self.img = cv2.imread("w.jpg")
        print "init"

    def open(self, *args):
        print("open", "WebSocketChatHandler")
        if cap_thread.ident:
            pass
        else:
            cap_thread.start()

    def on_message(self, message):
        """ handle message from websocket"""
        # print message
        # img = copy.copy(self.img);
        img = self.decode_one_frame()
        ret, img = cv2.imencode(".jpg", img)
        img = base64.b64encode(img)
        self.write_message(img)

    @staticmethod
    def decode_one_frame():
        """ decode a frame from message queue """
        img = Q.get()
        sio = StringIO(img)
        img = np.load(sio)
        img = cv2.imdecode(img, cv2.CV_LOAD_IMAGE_COLOR)
        return img

    def on_close(self):
        pass


if __name__ == "__main__":
    app = tornado.web.Application([(r'/ws', WebSocketImgHandler), (r'/', IndexHandler)])
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
