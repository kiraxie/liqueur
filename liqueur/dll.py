import comtypes.client as cc
from .helper import VcredistHelper, CapitalAPIHelper

_DLL_INIT_FLAG = False
VCREDIST_VER_REQUIRED = '10.0.40219.325'
DLL_VER_REQUIRED = '2.13.20'


def _api_initialization(cls):
    def dll_assure(cls):
        global _DLL_INIT_FLAG

        if not _DLL_INIT_FLAG:
            vcredist = VcredistHelper(VCREDIST_VER_REQUIRED, '~/.liqueur')
            capital_api = CapitalAPIHelper(DLL_VER_REQUIRED, '~/.liqueur')

            vcredist.auto_install()
            capital_api.auto_install()

            cc.GetModule(capital_api.api_path)
            _DLL_INIT_FLAG = True

    return dll_assure


class Component:
    _component = None

    def __component_generator(self, name):
        import comtypes.gen.SKCOMLib as _api

        if name == 'center':
            _component = cc.CreateObject(_api.SKCenterLib, interface=_api.ISKCenterLib)
        elif name == 'quote':
            _component = cc.CreateObject(_api.SKQuoteLib, interface=_api.ISKQuoteLib)
        elif name == 'order':
            _component = cc.CreateObject(_api.SKOrderLib, interface=_api.ISKOrderLib)
        elif name == 'reply':
            _component = cc.CreateObject(_api.SKReplyLib, interface=_api.ISKReplyLib)
        else:
            raise ValueError('Invalid parament! [name: %s]' % name)

        return _component

    @_api_initialization
    def __init__(self):
        pass

    def hook_event(self, event):
        return cc.GetEvents(self._component, event)
