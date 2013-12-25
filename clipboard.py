import logging
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=33333, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/sync", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="HHHHHHHHHHHHHHHHHHHHHHHHHHSDAFSDFASDFdsaf",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", msg=ChatSocketHandler.content)

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = {}
    content = ""

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        uid = str(uuid.uuid4())
        ChatSocketHandler.waiters[self] = uid
        self.write_message(uid)

    def on_close(self):
        del ChatSocketHandler.waiters[self]

    @classmethod
    def send_updates(cls, author):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter, uid in cls.waiters.items():
            if uid == author:
                logging.info("pass")
                continue
            try:
                waiter.write_message(cls.content)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        logging.info("got message from %s" % parsed["uid"])
        ChatSocketHandler.content = parsed["body"]
        ChatSocketHandler.send_updates(parsed["uid"])

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
