from base_handler import MOTGBaseHandler

class ControlHandler(MOTGBaseHandler):
    def initialize(self, **kwargs):
        super().initialize('control', **kwargs)
