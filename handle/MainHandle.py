from tornado.web import RequestHandler


class MainHandle(RequestHandler):

    def get(self, *args, **kwargs):
        self.write('hello, we are YOCB, thanks to join us')

    def post(self, *args, **kwargs):
        self.write('hello, we are YOCB, thanks to join us')
