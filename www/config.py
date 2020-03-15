import configparser


class Config(object):
    def __init__(self):
        self.cfg_g = configparser.ConfigParser()
        self.cfg_g.read('./www/config/global.conf')
        self.sidebar_items = configparser.ConfigParser()
        self.sidebar_items.read('./www/config/sidebar_items.conf')
        self.sidebar_items_bg = configparser.ConfigParser()
        self.sidebar_items_bg.read('./www/config/sidebar_items_bg.conf')

    def get_cfg_global(self):
        return self.cfg_g

    def get_sidebar_items(self):
        return self.sidebar_items

    def get_sidebar_items_bg(self):
        return self.sidebar_items_bg


config = Config()