import logging
from .codes import log_level


class AppLog:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cfg):
        logging.basicConfig(
            level=log_level[cfg.level],
            format='[%(asctime)s][%(name)-7s][%(levelname)s] %(message)s',
            datefmt='%Y%m%d %H:%M:%S')

        for mod_name, level in cfg.mod_level.items():
            logging.getLogger(mod_name).setLevel(log_level[level])

    @staticmethod
    def get(mod_name):
        return Log(mod_name)


class Log:
    __logger = None

    def __init__(self, mod_name):
        self.__logger = logging.getLogger(mod_name)

    def debug(self, message):
        self.__logger.debug(message)

    def info(self, message):
        self.__logger.info(message)

    def warn(self, message):
        self.__logger.warning(message)

    def error(self, message):
        self.__logger.error(message)

    def crit(self, message):
        self.__logger.critical(message)
