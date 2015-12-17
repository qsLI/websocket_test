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
from detect_opencv import detect


class CaptureThread(threading.Thread):
    def __init__(self,  q, interval=0):
        threading.Thread.__init__(self)
        self.cap = cv2.VideoCapture(-1)
        self.interval = interval
        self.q = q

    def run(self):
        while True:
            ret, img = self.cap.read()
            if img is None:
                time.sleep(1)
                continue
            faces = detect(img)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 3)
            self.q.encode_one_frame(img)
            time.sleep(self.interval)

    def __del__(self):
        self.cap.release()


class PushThread(threading.Thread):
    def __init__(self, q, interval=0):
        threading.Thread.__init__(self)
        self.q = q
        self.interval = interval

    def run(self):
        while True:
            img = self.q.decode_one_frame()
            if not clients:
                continue
            ret, img = cv2.imencode(".jpg", img)
            img = base64.b64encode(img)
            for client in clients:
                client.write_message(img)
            time.sleep(self.interval)


class IndexHandler(tornado.web.RequestHandler):
    """ server the index page """
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")


class WebSocketImgHandler(tornado.websocket.WebSocketHandler):
    """ websocket """
    def __init__(self, *args, **kwargs):
        super(WebSocketImgHandler, self).__init__(*args, **kwargs)

        # self.img = cv2.imread("w.jpg")
        print "init"

    def open(self, *args):
        print("open", "WebSocketChatHandler")
        clients.append(self)
        if cap_thread.ident:
            pass
        else:
            cap_thread.start()

    def on_message(self, message):
        """ handle message from websocket"""
        print message
        # img = copy.copy(self.img);
        # img = Q.decode_one_frame()
        # ret, img = cv2.imencode(".jpg", img)
        # img = base64.b64encode(img)
        # self.write_message(img)

    def on_close(self):
        clients.remove(self)


# capture thread
Q = RedisQueue("video")
clients = []
# thread to capture frame from camera
cap_thread = CaptureThread(Q)
cap_thread.setDaemon(True)
# thread to push to every client
push_thread = PushThread(Q)
push_thread.setDaemon(True)
push_thread.start()

if __name__ == "__main__":
    app = tornado.web.Application([(r'/ws', WebSocketImgHandler), (r'/', IndexHandler)])
    print app.settings
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
