import json


class Config(object):
    def __init__(self):
        file = open('./www/config/config.json', "r")
        self.cfg = json.loads(file.read())

    def get_cfg(self):
        return self.cfg

    def change_and_save_cfg(self):
        file = open('./www/config/config.json', "w+")
        return file.write(json.dumps(self.cfg, ensure_ascii=False, indent=4))


config = Config()
