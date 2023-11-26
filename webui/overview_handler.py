from base_handler import MOTGBaseHandler

class OverviewHandler(MOTGBaseHandler):
    def initialize(self, **kwargs):
        super().initialize('overview', **kwargs)
