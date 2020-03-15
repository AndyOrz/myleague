import configparser


def get_cfg_global():
    cfg_g = configparser.ConfigParser()
    cfg_g.read('./www/config/global.conf')
    return cfg_g


def get_sidebar_items():
    sidebar_items = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())
    sidebar_items.read('./www/config/sidebar_items.conf')
    return sidebar_items


def get_sidebar_items_bg():
    sidebar_items_bg = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())
    sidebar_items_bg.read('./www/config/sidebar_items_bg.conf')
    return sidebar_items_bg
