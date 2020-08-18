import yaml
from .util import Attributes


class AppConfig(Attributes):
    def __init__(self, path):
        with open(path, 'r') as file:
            super(AppConfig, self).__init__(yaml.load(file, Loader=yaml.FullLoader))
