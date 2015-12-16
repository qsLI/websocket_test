import tornado.ioloop
import tornado.web
import tornado.websocket
import cv2
import base64
import copy

clients = []
""" server the index page """


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")


""" websocket """


class WebSocketImgHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocketImgHandler, self).__init__(*args, **kwargs)
        self.img = cv2.imread("w.jpg")

    def open(self, *args):
        print("open", "WebSocketChatHandler")
        clients.append(self)

    def on_message(self, message):

        """ handle message from websocket"""
        print message
        img = copy.copy(self.img);
        cv2.putText(img, '6', (100, 100), cv2.FONT_HERSHEY_COMPLEX, 4, (255, 255, 0), 2)
        ret, img = cv2.imencode(".jpg", img)
        img = base64.b64encode(img)
        self.write_message(img)


def on_close(self):
    clients.remove(self)


if __name__ == "__main__":
    app = tornado.web.Application([(r'/ws', WebSocketImgHandler), (r'/', IndexHandler)])
    app.listen(80)
    tornado.ioloop.IOLoop.instance().start()
