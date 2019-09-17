from .dll import Component


class Reply(Component):
    def __init__(self):
        super(Reply, self).__init__()
        self._component = self._Component__component_generator('reply')

    def connect_by_id(self, bstrUserID):
        return self._component.SKReplyLib_ConnectByID(bstrUserID)

    def close_by_id(self, bstrUserID):
        return self._component.SKReplyLib_CloseByID(bstrUserID)

    def is_connected_by_id(self, bstrUserID):
        return self._component.SKReplyLib_IsConnectedByID(bstrUserID)

    def solace_close_by_id(self, bstrUserID):
        return self._component.SKReplyLib_SolaceCloseByID(bstrUserID)
