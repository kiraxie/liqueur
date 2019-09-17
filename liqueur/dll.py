import comtypes.client as cc
import comtypes.gen.SKCOMLib as _api


_DLL_INIT_FLAG = False


def _skcom_init(cls):
    def wrapped(cls):
        global _DLL_INIT_FLAG
        if not _DLL_INIT_FLAG:
            cc.GetModule('./SKCOM.dll')
            _DLL_INIT_FLAG = True
    return wrapped


class Component:
    _component = None

    def __component_generator(self, name):
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

    @_skcom_init
    def __init__(self):
        pass

    def hook_event(self, event):
        return cc.GetEvents(self._component, event)


def new_stock_quote():
    return _api.SKSTOCK()
