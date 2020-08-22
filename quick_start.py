import os
import pathlib
from liqueur import Liqueur, AppConfig
from datetime import datetime
import signal


class ErrShouldBeMain(SystemError):
    pass


class ServiceExit(Exception):
    pass


def service_shutdown(signum, frame):
    raise ServiceExit


def main():
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    cfg = AppConfig(pathlib.Path('./config/liqueur.yaml').absolute())
    app = Liqueur(cfg)

    try:
        app.start()
    except ServiceExit:
        app.stop()


if __name__ != "__main__":
    raise ErrShouldBeMain
else:
    main()
