import os
from tornado.web import RequestHandler

class MOTGBaseHandler(RequestHandler):
    def initialize(self, html_name, **kwargs):
        self.html_name = html_name
        self.html_path = kwargs["html_path"]

    def get(self, *args):
        return self.render(os.path.join(self.html_path, f'{self.html_name}.html'), handler=self, args=args)
