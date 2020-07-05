import os
import pathlib
from liqueur import Liqueur, Config
import signal


class ErrShouldBeMain(SystemError):
    pass


class ServiceExit(Exception):
    pass


app = Liqueur(Config.from_yaml(pathlib.Path('./config/liqueur.yaml').absolute()))


@app.hook_kbar()
def k_handler(k):
    pass


@app.hook_tick()
def t_handler(t):
    pass


def service_shutdown(signum, frame):
    raise ServiceExit


def main():
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    try:
        app.run()
    except ServiceExit:
        app.stop()


if __name__ != "__main__":
    raise ErrShouldBeMain
else:
    main()
