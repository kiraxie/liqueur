from .dll import Component


class Center(Component):
    _username = ''
    _password = ''

    def __init__(self, conf):
        super(Center, self).__init__('center')

        self._username = conf.username
        self._password = conf.password

    def set_log_path(self, bstrPath):
        return self._component.SKCenterLib_SetLogPath(bstrPath)

    def login(self):
        return self._component.SKCenterLib_Login(self._username, self._password)

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
