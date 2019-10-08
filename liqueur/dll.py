import comtypes.client as cc
from packaging import version
import skcom.helper as helper

_DLL_INIT_FLAG = False
_VCREDIST_VER_REQUIRED = '10.0.40219.325'
_DLL_VER_REQUIRED = '2.13.18'


def _skcom_init(cls):
    def dll_assure(cls):
        global _DLL_INIT_FLAG

        if not _DLL_INIT_FLAG:
            helper.set_silent(True)
            req_vcredist_ver = version.parse(_VCREDIST_VER_REQUIRED)
            curr_vcredist_ver = helper.verof_vcredist()
            if req_vcredist_ver != curr_vcredist_ver:
                helper.install_vcredist()

                # Get vcredist version again
                if req_vcredist_ver != helper.verof_vcredist():
                    raise EnvironmentError('Vcredist auto install failed!')

            req_dll_ver = version.parse(_DLL_VER_REQUIRED)
            curr_dll_ver = helper.verof_skcom()

            if curr_dll_ver == version.parse('0.0.0.0'):
                helper.install_skcom(_DLL_VER_REQUIRED)
            elif curr_dll_ver != req_dll_ver:
                helper.clean_mod()
                helper.remove_skcom()
                helper.install_skcom(_DLL_VER_REQUIRED)

            if helper.verof_skcom() != req_dll_ver:
                raise EnvironmentError('Capital API auto install failed!')

            if not helper.has_valid_mod():
                cc.GetModule(helper.get_dll_abs_path())

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

    @_skcom_init
    def __init__(self):
        pass

    def hook_event(self, event):
        return cc.GetEvents(self._component, event)
