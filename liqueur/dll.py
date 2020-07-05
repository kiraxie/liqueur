import comtypes.client as cc
from .util import VcredistHelper, CapitalAPIHelper

_DLL_INIT_FLAG = False
VCREDIST_VER_REQUIRED = '10.0.40219.325'
DLL_VER_REQUIRED = '2.13.23'


vcredist = VcredistHelper(VCREDIST_VER_REQUIRED, '~/.liqueur')
capital_api = CapitalAPIHelper(DLL_VER_REQUIRED, '~/.liqueur')

vcredist.auto_install()
capital_api.auto_install()
cc.GetModule(capital_api.api_path)


class InitialError(WindowsError):
    pass


class Component:
    _component = None

    def __init__(self, name):
        import comtypes.gen.SKCOMLib as _api
        if name == 'center':
            self._component = cc.CreateObject(_api.SKCenterLib, interface=_api.ISKCenterLib)
        elif name == 'quote':
            self._component = cc.CreateObject(_api.SKQuoteLib, interface=_api.ISKQuoteLib)
        elif name == 'order':
            self._component = cc.CreateObject(_api.SKOrderLib, interface=_api.ISKOrderLib)
        elif name == 'reply':
            self._component = cc.CreateObject(_api.SKReplyLib, interface=_api.ISKReplyLib)
        else:
            raise ValueError('Invalid parament! [name: %s]' % name)

    def hook_event(self, event):
        return cc.GetEvents(self._component, event)
