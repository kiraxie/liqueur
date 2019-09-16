from .dll import Component


class Center(Component):
    def __init__(self):
        super(Center, self).__init__()
        self._component = self._Component__component_generator('center')

    def hook_event(self, event):
        return cc.GetEvents(self._component, event)

    def set_log_path(self, bstrPath):
        return self._component.SKCenterLib_SetLogPath(bstrPath)

    def login(self, bstrUserID, bstrPassword):
        return self._component.SKCenterLib_Login(bstrUserID, bstrPassword)

    def get_return_code_msg(self, nCode):
        return self._component.SKCenterLib_GetReturnCodeMessage(nCode)

    def debug(self, bDebug):
        return self._component.SKCenterLib_Debug(bDebug)

    def reset_server(self, bstrServer):
        return self._component.SKCenterLib_ResetServer(bstrServer)

    def get_last_log_info(self):
        return self._component.SKCenterLib_GetLastLogInfo()

    def set_authority(self, nAuthorityFlag):
        return self._component.SKCenterLib_SetAuthority(nAuthorityFlag)

    def login_order_m(self, bstrUserID, bstrPassword):
        return self._component.SKCenterLib_LoginOrderM(bstrUserID, bstrPassword)
